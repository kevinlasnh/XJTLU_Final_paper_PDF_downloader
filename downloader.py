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
                'error': f"Event loop error: {str(e)}"
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
            update_status("Starting browser...")
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
                        update_status(f"Captured PDF data: {len(pdf_data)} bytes")
                    except Exception as e:
                        update_status(f"Failed to capture PDF: {e}")
            
            page.on('response', handle_response)
            
            update_status("Navigating to PDF viewer...")
            
            # Navigate to the viewer page
            response = await page.goto(viewer_url, wait_until='domcontentloaded')
            
            if response and response.status >= 400:
                result['error'] = f"HTTP error {response.status} when accessing viewer page"
                await context.close()
                return result
            
            update_status("Waiting for PDF to load...")
            
            # Wait for PDF.js to load the document
            try:
                # Wait for the viewer container
                await page.wait_for_selector('#viewer', timeout=15000)
                
                # Wait for network to be mostly idle (PDF should be loaded)
                await page.wait_for_load_state('networkidle', timeout=30000)
                
                # Additional wait for any late network requests
                await asyncio.sleep(2)
                
                # Check if there's an error message in the viewer
                error_wrapper = await page.query_selector('.errorWrapper')
                if error_wrapper and await error_wrapper.is_visible():
                    error_msg = await page.query_selector('#errorMessage')
                    if error_msg:
                        result['error'] = f"PDF viewer error: {await error_msg.inner_text()}"
                    else:
                        result['error'] = "PDF viewer reported an error. Link may have expired."
                    await context.close()
                    return result
                
                # Check for common error indicators
                page_content = await page.content()
                if 'errorMessage' in page_content and ('expired' in page_content.lower() or 'invalid' in page_content.lower()):
                    result['error'] = "The PDF link appears to have expired or is invalid."
                    await context.close()
                    return result
                
            except PlaywrightTimeout:
                # Check for error messages in the viewer
                error_wrapper = await page.query_selector('.errorWrapper')
                if error_wrapper:
                    error_msg = await page.query_selector('#errorMessage')
                    if error_msg:
                        result['error'] = f"PDF load error: {await error_msg.inner_text()}"
                    else:
                        result['error'] = "Timeout - PDF may have failed to load. Link likely expired."
                else:
                    result['error'] = "Timeout waiting for PDF. Link may have expired."
                await context.close()
                return result
            
            await context.close()
            
            # Save the captured PDF data
            if pdf_data and len(pdf_data) > 1000:  # Valid PDF should be > 1KB
                update_status("Saving PDF file...")
                
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(pdf_data)
                
                # Verify the file
                if save_path.exists() and save_path.stat().st_size > 0:
                    result['success'] = True
                    result['file_path'] = str(save_path)
                    result['file_size'] = save_path.stat().st_size
                    update_status("Download complete!")
                else:
                    result['error'] = "PDF file was not saved correctly"
            elif pdf_data and len(pdf_data) <= 1000:
                result['error'] = f"Received invalid PDF data ({len(pdf_data)} bytes). Link may have expired."
            else:
                result['error'] = "Could not capture PDF data. The link has likely expired - please get a fresh URL from the browser."
                
        except PlaywrightTimeout as e:
            result['error'] = f"Operation timed out: {str(e)}"
        except Exception as e:
            result['error'] = f"Browser error: {str(e)}"
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
