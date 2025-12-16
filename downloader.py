"""
PDF Downloader for XJTLU ETD System
Uses Playwright browser automation to bypass IP/signature verification.
"""

import asyncio
import time
from pathlib import Path
from typing import Callable, Optional
from playwright.async_api import async_playwright, Browser, TimeoutError as PlaywrightTimeout


class PDFDownloader:
    """
    Downloads PDF files from XJTLU ETD system using browser automation.
    This approach bypasses server-side IP and signature validation by using
    a real browser context.
    """
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        """
        Initialize the Playwright-based downloader.
        
        Args:
            headless: Run browser in headless mode (no visible window)
            timeout: Default timeout in milliseconds for page operations
        """
        self.headless = headless
        self.timeout = timeout
    
    def download(
        self,
        viewer_url: str,
        save_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """
        Download a PDF file by intercepting the actual PDF data from network requests.
        Wrapper that runs the async download in a new event loop.
        
        Args:
            viewer_url: The full viewer URL (including file= parameter)
            save_path: Path where the PDF should be saved
            progress_callback: Optional callback function(status_message)
            
        Returns:
            dict with download result
        """
        # Create a new event loop for this thread to avoid conflicts
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._download_async(viewer_url, save_path, progress_callback)
            )
            loop.close()
            return result
        except Exception as e:
            return {
                'success': False,
                'file_path': None,
                'file_size': 0,
                'error': f"程序内部错误：{str(e)}（请尝试重新运行程序）"
            }
    
    async def _download_async(
        self,
        viewer_url: str,
        save_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """
        Async implementation of PDF download.
        """
        result = {
            'success': False,
            'file_path': None,
            'file_size': 0,
            'error': None
        }
        
        pdf_data = None
        
        def update_status(msg: str):
            if progress_callback:
                progress_callback(msg)
        
        playwright = None
        browser = None
        
        try:
            update_status("正在启动浏览器...")
            playwright = await async_playwright().start()
            # Use full chromium instead of headless shell to avoid spawn EFTYPE error
            browser = await playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create a new browser context and page
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                accept_downloads=True
            )
            page = await context.new_page()
            page.set_default_timeout(self.timeout)
            
            # Intercept PDF file responses from the API
            async def handle_response(response):
                nonlocal pdf_data
                content_type = response.headers.get('content-type', '')
                url = response.url
                
                # Check if this is the PDF file response
                is_pdf = 'pdf' in content_type.lower() or 'octet-stream' in content_type.lower()
                is_api = 'BrowserFile' in url or 'api/v1/File' in url
                
                if is_pdf and is_api:
                    try:
                        pdf_data = await response.body()
                        update_status(f"已捕获PDF数据: {len(pdf_data)} 字节")
                    except Exception as e:
                        update_status(f"捕获PDF失败: {e}")
            
            page.on('response', handle_response)
            
            update_status("正在打开PDF查看器页面...")
            
            # Navigate to the viewer page
            response = await page.goto(viewer_url, wait_until='domcontentloaded')
            
            if response and response.status >= 400:
                result['error'] = f"网络错误 {response.status}：无法访问页面（可能链接已过期或网络有问题）"
                await context.close()
                return result
            
            update_status("等待PDF加载中...请稍候")
            
            # Wait for PDF.js to load the document
            try:
                # Wait for the viewer container
                await page.wait_for_selector('#viewer', timeout=15000)
                
                # Wait for network to be mostly idle (PDF should be loaded)
                await page.wait_for_load_state('networkidle', timeout=30000)
                
                # Additional wait for any late network requests
                await asyncio.sleep(2)
                
                # Only check for errors if we haven't captured PDF data yet
                # If PDF data is already captured, we can skip error checking
                if not pdf_data or len(pdf_data) < 1000:
                    # Check if there's an error message in the viewer
                    error_wrapper = await page.query_selector('.errorWrapper')
                    if error_wrapper and await error_wrapper.is_visible():
                        error_msg = await page.query_selector('#errorMessage')
                        if error_msg:
                            result['error'] = f"PDF查看器报错: {await error_msg.inner_text()}（链接可能已过期）"
                        else:
                            result['error'] = "PDF查看器出错：链接可能已过期，请重新获取新链接"
                        await context.close()
                        return result
                    
                    # Check for common error indicators
                    page_content = await page.content()
                    if 'errorMessage' in page_content and ('expired' in page_content.lower() or 'invalid' in page_content.lower()):
                        result['error'] = "链接已过期或无效：请回到ETD网站重新打开PDF并复制新链接"
                        await context.close()
                        return result
                
            except PlaywrightTimeout:
                # Check for error messages in the viewer
                error_wrapper = await page.query_selector('.errorWrapper')
                if error_wrapper:
                    error_msg = await page.query_selector('#errorMessage')
                    if error_msg:
                        result['error'] = f"PDF加载错误: {await error_msg.inner_text()}"
                    else:
                        result['error'] = "超时：PDF加载失败，链接可能已过期。\n❗ 如频繁超时，请尝试关闭VPN/代理后再试"
                else:
                    result['error'] = "超时：等待PDF加载超时。\n❗ 如频繁超时，请关闭VPN/梯子/代理后重试"
                await context.close()
                return result
            
            await context.close()
            
            # Save the captured PDF data
            if pdf_data and len(pdf_data) > 1000:  # Valid PDF should be > 1KB
                update_status("正在保存PDF文件...")
                
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(pdf_data)
                
                # Verify the file
                if save_path.exists() and save_path.stat().st_size > 0:
                    result['success'] = True
                    result['file_path'] = str(save_path)
                    result['file_size'] = save_path.stat().st_size
                    update_status("✅ 下载完成！")
                else:
                    result['error'] = "PDF文件保存失败：文件未正确写入磁盘（请检查磁盘空间和权限）"
            elif pdf_data and len(pdf_data) <= 1000:
                result['error'] = f"收到无效PDF数据（仅{len(pdf_data)}字节）：链接可能已过期，请重新获取"
            else:
                result['error'] = "无法获取PDF数据：链接很可能已过期，请回到浏览器重新打开PDF并复制新链接"
                
        except PlaywrightTimeout as e:
            result['error'] = f"操作超时：{str(e)}\n\n❗ 如频繁超时，请尝试：\n1. 关闭电脑上的VPN/梯子/代理\n2. 确保网络连接正常\n3. 重新获取新的PDF链接"
        except Exception as e:
            error_msg = str(e)
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                result['error'] = f"浏览器超时：{error_msg}\n\n❗ 请关闭VPN/梯子/代理后重试"
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                result['error'] = f"网络错误：{error_msg}\n\n请检查网络连接是否正常"
            else:
                result['error'] = f"浏览器错误：{error_msg}"
        finally:
            # Cleanup
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
        
        return result
    
    def get_suggested_filename(self, viewer_url: str, record_id: Optional[str] = None) -> str:
        """
        Generate a suggested filename for the PDF.
        
        Args:
            viewer_url: The viewer URL (might contain hints for filename)
            record_id: Optional record ID to include in filename
            
        Returns:
            Suggested filename string
        """
        if record_id:
            return f"XJTLU_Document_{record_id}.pdf"
        return "XJTLU_Document.pdf"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


if __name__ == "__main__":
    print("PDFDownloader module (Playwright async-based) loaded")
    print("Use download() method - it handles async internally")
