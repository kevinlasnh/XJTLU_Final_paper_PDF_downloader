"""
URL Parser for XJTLU ETD PDF Downloader
Extracts metadata from viewer URLs for filename generation.
"""

from typing import Tuple
from urllib.parse import urlparse, parse_qs, unquote


def parse_viewer_url(viewer_url: str) -> dict:
    """
    Parse the XJTLU ETD viewer URL and extract metadata.
    
    With the Playwright approach, we don't need to construct the PDF API URL
    ourselves - the browser will handle that. We just extract metadata for
    filename generation.
    
    Args:
        viewer_url: The full viewer URL containing the file parameter
        
    Returns:
        dict with keys:
            - viewer_url: The original viewer URL (cleaned)
            - record_id: The document record ID (for filename)
            - db_code: The database code (e.g., EXAMXJTLU)
            - success: Boolean indicating if parsing was successful
            - error: Error message if parsing failed
    """
    result = {
        'viewer_url': None,
        'record_id': None,
        'db_code': None,
        'success': False,
        'error': None
    }
    
    try:
        # Clean the URL (remove fragment like #page=1&zoom=...)
        clean_url = viewer_url.split('#')[0].strip()
        result['viewer_url'] = clean_url
        
        # Parse the main URL
        parsed = urlparse(clean_url)
        
        # Get query parameters from the viewer URL
        query_params = parse_qs(parsed.query)
        
        # The 'file' parameter contains the encoded PDF API path
        if 'file' not in query_params:
            result['error'] = "URL missing 'file' parameter. Make sure to copy the full viewer URL."
            return result
        
        # Decode the file parameter to extract record info
        file_param = query_params['file'][0]
        decoded_file_path = unquote(file_param)
        
        # Extract record info from the decoded path
        file_parsed = urlparse(decoded_file_path)
        file_query = parse_qs(file_parsed.query)
        
        if 'recordId' in file_query:
            result['record_id'] = file_query['recordId'][0]
        if 'dbCode' in file_query:
            result['db_code'] = file_query['dbCode'][0]
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = f"URL parse error: {str(e)}"
    
    return result


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate if the URL is a valid XJTLU ETD viewer URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        tuple of (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "Please enter a URL"
    
    url = url.strip()
    
    if not url.startswith('http'):
        return False, "URL must start with http:// or https://"
    
    if 'etd.xjtlu.edu.cn' not in url:
        return False, "URL must be from etd.xjtlu.edu.cn"
    
    if 'viewer.html' not in url and 'file=' not in url:
        return False, "URL is not a valid PDF viewer link"
    
    return True, ""


if __name__ == "__main__":
    # Test with sample URL
    test_url = "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3FdbCode%3DEXAMXJTLU%26recordId%3D15798%26dbId%3D3%26flag%3D0%26timestamp%3D1765788896%26signature%3D94adec6e1c4211f29b92eeb00b4c1b358127bbac3601581d378bbbdda885af13%26clientIp%3D180.208.58.213#page=1&zoom=auto"
    
    result = parse_viewer_url(test_url)
    print("Parse Result:")
    print(f"  Success: {result['success']}")
    print(f"  Record ID: {result['record_id']}")
    print(f"  DB Code: {result['db_code']}")
    print(f"  Clean URL: {result['viewer_url'][:60]}...")
