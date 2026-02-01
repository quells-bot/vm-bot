#!/usr/bin/env python3
"""
Simple client for Browser Controller API
Makes it easy to interact with the browser from Python
"""

import requests
import json
from typing import Optional, Dict, Any

class BrowserClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, **kwargs)
        return response.json()

    def status(self) -> Dict:
        """Get browser status"""
        return self._request('GET', '/status')

    def start(self) -> Dict:
        """Start browser"""
        return self._request('POST', '/start')

    def stop(self) -> Dict:
        """Stop browser"""
        return self._request('POST', '/stop')

    def goto(self, url: str) -> Dict:
        """Navigate to URL"""
        return self._request('POST', '/goto', json={'url': url})

    def screenshot(self, save_to: Optional[str] = None) -> bytes:
        """Get screenshot"""
        response = requests.get(f"{self.base_url}/screenshot")
        data = response.content
        if save_to:
            with open(save_to, 'wb') as f:
                f.write(data)
        return data

    def get_links(self) -> Dict:
        """Get all links on page"""
        return self._request('GET', '/elements/links')

    def get_forms(self) -> Dict:
        """Get all form fields"""
        return self._request('GET', '/elements/forms')

    def get_buttons(self) -> Dict:
        """Get all buttons"""
        return self._request('GET', '/elements/buttons')

    def click(self, selector: str, selector_type: str = 'css') -> Dict:
        """Click element"""
        return self._request('POST', '/click', json={
            'selector': selector,
            'type': selector_type
        })

    def fill(self, selector: str, value: str, selector_type: str = 'css', clear: bool = True) -> Dict:
        """Fill form field"""
        return self._request('POST', '/fill', json={
            'selector': selector,
            'value': value,
            'type': selector_type,
            'clear': clear
        })

    def execute(self, script: str) -> Dict:
        """Execute JavaScript"""
        return self._request('POST', '/execute', json={'script': script})

    def back(self) -> Dict:
        """Go back"""
        return self._request('POST', '/back')

    def forward(self) -> Dict:
        """Go forward"""
        return self._request('POST', '/forward')

    def refresh(self) -> Dict:
        """Refresh page"""
        return self._request('POST', '/refresh')

    # High-level convenience methods

    def browse(self, url: str, screenshot_path: Optional[str] = None) -> Dict:
        """Navigate and optionally take screenshot"""
        result = self.goto(url)
        if screenshot_path:
            self.screenshot(screenshot_path)
        return result

    def search_links(self, text: str) -> list:
        """Find links containing text"""
        links = self.get_links()
        if links['status'] == 'success':
            return [
                link for link in links['links']
                if text.lower() in link['text'].lower() or text.lower() in link['href'].lower()
            ]
        return []

    def find_form_field(self, name: str = None, field_id: str = None, placeholder: str = None) -> Optional[Dict]:
        """Find a form field by name, id, or placeholder"""
        forms = self.get_forms()
        if forms['status'] == 'success':
            for field in forms['fields']:
                if name and field.get('name') == name:
                    return field
                if field_id and field.get('id') == field_id:
                    return field
                if placeholder and field.get('placeholder') == placeholder:
                    return field
        return None


# Example usage as a standalone script
if __name__ == '__main__':
    import sys

    browser = BrowserClient()

    # Example interactive session
    print("🌐 Browser Client - Interactive Mode")
    print("=" * 50)

    # Check status
    status = browser.status()
    print(f"Status: {status}")

    # Start if not running
    if status['status'] != 'running':
        print("\n🚀 Starting browser...")
        browser.start()

    # Navigate to example page
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://example.com"

    print(f"\n🌐 Navigating to {url}...")
    result = browser.goto(url)
    print(f"Current page: {result.get('title')} - {result.get('url')}")

    # Take screenshot
    print("\n📸 Taking screenshot...")
    browser.screenshot('/tmp/browser_screenshot.png')
    print("Screenshot saved to /tmp/browser_screenshot.png")

    # List links
    print("\n🔗 Links on page:")
    links = browser.get_links()
    if links['status'] == 'success':
        for link in links['links'][:10]:  # First 10
            if link['visible']:
                print(f"  [{link['index']}] {link['text'][:50]} -> {link['href'][:60]}")

    # List form fields
    print("\n📝 Form fields:")
    forms = browser.get_forms()
    if forms['status'] == 'success' and forms['count'] > 0:
        for field in forms['fields'][:5]:  # First 5
            if field['visible']:
                print(f"  [{field['index']}] {field['type']} - {field.get('name', field.get('id', 'unnamed'))}")
    else:
        print("  No form fields found")

    print("\n✅ Done! Browser session is still running.")
    print("💡 Use the BrowserClient class in your own scripts to control the browser.")
