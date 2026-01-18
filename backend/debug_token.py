
import requests
import re
import sys

def check_site(url):
    print(f"Checking {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text
        print(f"Status: {resp.status_code}")
        print(f"Length: {len(html)}")
        

        matches = re.findall(r'token', html, re.IGNORECASE)
        print(f"Found 'token' {len(matches)} times.")
        
        # Print a few contexts
        iter = re.finditer(r'.{0,50}token.{0,50}', html, re.IGNORECASE)
        for i, m in enumerate(iter):
            if i > 5: break
            print(f"Ctx {i}: {m.group(0)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_site("https://www.fashionnova.com")
    # check_site("https://tennisexpress.com")
