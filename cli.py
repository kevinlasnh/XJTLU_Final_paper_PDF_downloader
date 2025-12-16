#!/usr/bin/env python3
"""
XJTLU PDF Downloader - Command Line Interface
命令行版本，适用于 macOS/Linux 等不便安装 Tkinter GUI 依赖的系统

功能：
- 单个/批量下载 XJTLU ETD 系统的 PDF 试卷
- 自动处理文件名冲突
- 彩色终端输出（支持的终端）
- 交互式和参数两种模式

用法：
    交互模式：python3 cli.py
    参数模式：python3 cli.py -u "URL1" -u "URL2" -o ./downloads
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

# 导入核心模块
from url_parser import validate_url, parse_viewer_url
from downloader import PDFDownloader


# ANSI 颜色代码
class Colors:
    """终端颜色支持"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def disable(cls):
        """禁用颜色（Windows 或不支持的终端）"""
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.RED = ''
        cls.BOLD = ''
        cls.UNDERLINE = ''
        cls.END = ''


def print_banner():
    """打印程序横幅"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════╗
║         XJTLU 期末试卷下载器 (CLI 版本)                    ║
║         PDF Downloader for XJTLU ETD System                ║
╚═══════════════════════════════════════════════════════════╝{Colors.END}
""")


def print_success(msg: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_warning(msg: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_info(msg: str):
    """打印信息消息"""
    print(f"{Colors.CYAN}ℹ {msg}{Colors.END}")


def print_progress(msg: str):
    """打印进度消息（会被覆盖）"""
    # 使用 \r 回到行首，允许覆盖
    print(f"\r{Colors.BLUE}⏳ {msg}{Colors.END}", end='', flush=True)


def progress_callback(msg: str):
    """下载进度回调函数"""
    print_progress(msg)


def get_unique_filepath(filepath: Path) -> Path:
    """
    如果文件已存在，生成一个不冲突的文件名
    例如: file.pdf -> file_1.pdf -> file_2.pdf
    """
    if not filepath.exists():
        return filepath
    
    base = filepath.stem
    ext = filepath.suffix
    parent = filepath.parent
    counter = 1
    
    while True:
        new_name = f"{base}_{counter}{ext}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def download_single(url: str, output_dir: Path, downloader: PDFDownloader) -> bool:
    """
    下载单个 PDF
    
    Args:
        url: PDF 查看器 URL
        output_dir: 保存目录
        downloader: PDFDownloader 实例
        
    Returns:
        是否成功
    """
    # 验证 URL
    is_valid, error = validate_url(url)
    if not is_valid:
        print_error(error)
        return False
    
    # 解析 URL 获取元数据
    parsed = parse_viewer_url(url)
    if not parsed['success']:
        print_error(f"URL 解析失败: {parsed['error']}")
        return False
    
    # 生成文件名
    record_id = parsed.get('record_id', 'unknown')
    db_code = parsed.get('db_code', 'EXAM')
    filename = f"{db_code}_{record_id}.pdf"
    
    # 确保目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理文件名冲突
    filepath = get_unique_filepath(output_dir / filename)
    
    print_info(f"开始下载: {filename}")
    print_info(f"保存到: {filepath}")
    
    # 执行下载
    result = downloader.download(
        viewer_url=parsed['viewer_url'],
        save_path=str(filepath),
        progress_callback=progress_callback
    )
    
    # 换行（因为进度条使用了 \r）
    print()
    
    if result['success']:
        file_size_kb = result['file_size'] / 1024
        print_success(f"下载成功! 文件大小: {file_size_kb:.1f} KB")
        print_success(f"保存位置: {result['file_path']}")
        return True
    else:
        print_error(f"下载失败: {result['error']}")
        # 如果是超时错误，给出提示
        if '超时' in str(result['error']) or 'timeout' in str(result['error']).lower():
            print_warning("提示: 请检查网络连接，并确保关闭了 VPN/代理")
        return False


def interactive_mode(output_dir: Path):
    """
    交互式模式 - 用户逐个输入 URL
    """
    print_info("交互式模式 - 输入 URL 进行下载")
    print_info("输入 'q' 或 'quit' 退出程序")
    print_info("输入 'batch' 进入批量模式（一次粘贴多个 URL）")
    print()
    
    downloader = PDFDownloader(headless=True)
    success_count = 0
    fail_count = 0
    
    while True:
        try:
            print(f"\n{Colors.BOLD}请输入 PDF 查看器 URL:{Colors.END}")
            user_input = input("> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('q', 'quit', 'exit'):
                break
            
            if user_input.lower() == 'batch':
                # 批量模式
                print_info("批量模式 - 每行输入一个 URL，输入空行结束")
                urls = []
                while True:
                    line = input().strip()
                    if not line:
                        break
                    urls.append(line)
                
                if urls:
                    print_info(f"共 {len(urls)} 个 URL，开始批量下载...")
                    for i, url in enumerate(urls, 1):
                        print(f"\n{Colors.BOLD}[{i}/{len(urls)}]{Colors.END}")
                        if download_single(url, output_dir, downloader):
                            success_count += 1
                        else:
                            fail_count += 1
                continue
            
            # 单个 URL 下载
            if download_single(user_input, output_dir, downloader):
                success_count += 1
            else:
                fail_count += 1
                
        except KeyboardInterrupt:
            print("\n")
            print_warning("用户中断")
            break
        except EOFError:
            break
    
    # 打印统计
    print()
    print(f"{Colors.BOLD}═══════════════════════════════════════{Colors.END}")
    print(f"下载统计: {Colors.GREEN}成功 {success_count}{Colors.END} / {Colors.RED}失败 {fail_count}{Colors.END}")
    print(f"保存目录: {output_dir.absolute()}")


def batch_mode(urls: List[str], output_dir: Path):
    """
    批量模式 - 从命令行参数获取 URL 列表
    """
    print_info(f"批量模式 - 共 {len(urls)} 个 URL")
    print_info(f"保存目录: {output_dir.absolute()}")
    print()
    
    downloader = PDFDownloader(headless=True)
    success_count = 0
    fail_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(urls)}] 正在处理...{Colors.END}")
        if download_single(url, output_dir, downloader):
            success_count += 1
        else:
            fail_count += 1
    
    # 打印统计
    print()
    print(f"{Colors.BOLD}═══════════════════════════════════════{Colors.END}")
    print(f"下载统计: {Colors.GREEN}成功 {success_count}{Colors.END} / {Colors.RED}失败 {fail_count}{Colors.END}")
    print(f"保存目录: {output_dir.absolute()}")
    
    # 返回是否全部成功
    return fail_count == 0


def file_mode(file_path: str, output_dir: Path):
    """
    文件模式 - 从文件读取 URL 列表（每行一个）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print_error(f"无法读取文件: {e}")
        return False
    
    if not urls:
        print_error("文件中没有有效的 URL")
        return False
    
    print_info(f"从文件读取了 {len(urls)} 个 URL")
    return batch_mode(urls, output_dir)


def main():
    """主函数"""
    # 检测终端是否支持颜色
    if sys.platform == 'win32':
        # Windows 需要特殊处理
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            Colors.disable()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='XJTLU 期末试卷 PDF 下载器 (CLI 版本)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  交互模式:
    python3 cli.py
    
  下载单个文件:
    python3 cli.py -u "https://etd.xjtlu.edu.cn/..."
    
  批量下载:
    python3 cli.py -u "URL1" -u "URL2" -u "URL3"
    
  从文件读取 URL:
    python3 cli.py -f urls.txt
    
  指定输出目录:
    python3 cli.py -u "URL" -o ~/Downloads/papers
"""
    )
    
    parser.add_argument(
        '-u', '--url',
        action='append',
        dest='urls',
        help='PDF 查看器 URL（可多次使用以批量下载）'
    )
    
    parser.add_argument(
        '-f', '--file',
        dest='url_file',
        help='包含 URL 列表的文件路径（每行一个 URL）'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='./downloads',
        help='PDF 保存目录（默认: ./downloads）'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用彩色输出'
    )
    
    args = parser.parse_args()
    
    # 禁用颜色
    if args.no_color:
        Colors.disable()
    
    # 打印横幅
    print_banner()
    
    # 准备输出目录
    output_dir = Path(args.output_dir).expanduser().resolve()
    
    # 根据参数选择模式
    if args.url_file:
        # 文件模式
        success = file_mode(args.url_file, output_dir)
        sys.exit(0 if success else 1)
    elif args.urls:
        # 批量模式
        success = batch_mode(args.urls, output_dir)
        sys.exit(0 if success else 1)
    else:
        # 交互模式
        interactive_mode(output_dir)


if __name__ == '__main__':
    main()
