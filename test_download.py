"""
Automated Test Script for XJTLU PDF Downloader (Playwright async-based)
Verifies core logic by bypassing the GUI.
"""

import sys
from pathlib import Path
from url_parser import parse_viewer_url, validate_url
from downloader import PDFDownloader, format_file_size


def run_test(target_dir: str, pdf_url: str, headless: bool = False):
    """
    Run automated download test.
    
    Args:
        target_dir: Directory to save the PDF
        pdf_url: The viewer URL to download from
        headless: Whether to run browser in headless mode
    """
    print("-" * 60)
    print("Starting automated test (Playwright async-based)...")
    print(f"Target directory: {target_dir}")
    print(f"Test URL: {pdf_url[:70]}...")
    print(f"Headless mode: {headless}")
    
    # 1. Validate URL
    print("\n[1/4] Validating URL...")
    is_valid, err_msg = validate_url(pdf_url)
    if not is_valid:
        print(f"❌ Validation failed: {err_msg}")
        return False
    print("✅ URL format is valid")
    
    # 2. Parse URL
    print("\n[2/4] Parsing URL...")
    parse_result = parse_viewer_url(pdf_url)
    
    if not parse_result['success']:
        print(f"❌ Parse failed: {parse_result['error']}")
        return False
        
    print(f"✅ Parse successful!")
    print(f"   Record ID: {parse_result['record_id']}")
    print(f"   DB Code: {parse_result['db_code']}")

    # 3. Setup Directory
    print("\n[3/4] Preparing directory...")
    save_path = Path(target_dir)
    try:
        save_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ready: {save_path}")
    except Exception as e:
        print(f"❌ Cannot create directory: {e}")
        return False

    # 4. Download File
    print("\n[4/4] Downloading file via Playwright...")
    downloader = PDFDownloader(headless=headless)
    
    filename = downloader.get_suggested_filename(
        parse_result['viewer_url'], 
        parse_result['record_id']
    )
    full_path = save_path / filename
    
    print(f"   Target file: {full_path}")
    
    # Progress callback
    def progress(msg):
        print(f"   >> {msg}")
    
    result = downloader.download(
        parse_result['viewer_url'], 
        str(full_path),
        progress_callback=progress
    )
    
    if result['success']:
        print(f"\n✅ Download successful!")
        print(f"   File size: {format_file_size(result['file_size'])}")
        print(f"   Saved to: {result['file_path']}")
        return True
    else:
        print(f"\n❌ Download failed: {result['error']}")
        return False


def main():
    # Default configuration
    target_dir = r"D:/workspace/cloud/google_drive/2025/Y4 first semester/EEE339/Final_paper"
    pdf_url = "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3FdbCode%3DEXAMXJTLU%26recordId%3D15797%26dbId%3D3%26flag%3D0%26timestamp%3D1765792574%26signature%3Df030d3445c383f4377c3b2c03ab5119699d62567ff26f2ad9c98a1b7bf6056f8%26clientIp%3D180.208.58.213"
    
    # Parse command line arguments
    headless = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "--visible":
            headless = False
        elif sys.argv[1] == "--help":
            print("Usage: python test_download.py [--visible]")
            print("  --visible  Show browser window during download")
            return
    
    success = run_test(target_dir, pdf_url, headless=headless)
    
    print("\n" + "=" * 60)
    if success:
        print("TEST PASSED ✅")
    else:
        print("TEST FAILED ❌")
    print("=" * 60)


if __name__ == "__main__":
    main()
