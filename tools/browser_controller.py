#!/usr/bin/env python3
"""
Flask-based browser controller
Provides a REST API to control a persistent Firefox session
"""

from flask import Flask, jsonify, request, send_file
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import io
import base64
import time
from datetime import datetime

app = Flask(__name__)

# Global browser instance
browser = None
screenshot_path = "/tmp/browser_screenshot.png"

def get_browser():
    """Get or create browser instance"""
    global browser
    if browser is None:
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-dev-shm-usage')
        firefox_options.add_argument('--window-size=1920,1080')

        service = Service('/usr/local/bin/geckodriver')
        browser = webdriver.Firefox(service=service, options=firefox_options)
    return browser

@app.route('/status')
def status():
    """Check if browser is running and get current state"""
    global browser
    if browser is None:
        return jsonify({
            'status': 'stopped',
            'browser': None
        })

    try:
        current_url = browser.current_url
        title = browser.title
        return jsonify({
            'status': 'running',
            'url': current_url,
            'title': title,
            'window_size': browser.get_window_size()
        })
    except WebDriverException:
        browser = None
        return jsonify({
            'status': 'error',
            'message': 'Browser session died'
        })

@app.route('/start', methods=['POST'])
def start():
    """Start browser session"""
    try:
        b = get_browser()
        return jsonify({
            'status': 'success',
            'message': 'Browser started'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/stop', methods=['POST'])
def stop():
    """Stop browser session"""
    global browser
    if browser:
        browser.quit()
        browser = None
        return jsonify({
            'status': 'success',
            'message': 'Browser stopped'
        })
    return jsonify({
        'status': 'success',
        'message': 'Browser was not running'
    })

@app.route('/goto', methods=['POST'])
def goto():
    """Navigate to URL"""
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'status': 'error', 'message': 'URL required'}), 400

    try:
        b = get_browser()
        b.get(url)
        time.sleep(2)  # Wait for page to load
        return jsonify({
            'status': 'success',
            'url': b.current_url,
            'title': b.title
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/screenshot')
def screenshot():
    """Get current screenshot"""
    try:
        b = get_browser()
        b.save_screenshot(screenshot_path)
        return send_file(screenshot_path, mimetype='image/png')
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/screenshot/base64')
def screenshot_base64():
    """Get screenshot as base64"""
    try:
        b = get_browser()
        png = b.get_screenshot_as_png()
        b64 = base64.b64encode(png).decode('utf-8')
        return jsonify({
            'status': 'success',
            'screenshot': b64,
            'url': b.current_url,
            'title': b.title
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/elements/links')
def get_links():
    """Get all links on current page"""
    try:
        b = get_browser()
        links = b.find_elements(By.TAG_NAME, 'a')

        result = []
        for i, link in enumerate(links[:100]):  # Limit to first 100
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                visible = link.is_displayed()

                if href:  # Only include links with href
                    result.append({
                        'index': i,
                        'href': href,
                        'text': text,
                        'visible': visible
                    })
            except:
                pass

        return jsonify({
            'status': 'success',
            'count': len(result),
            'links': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/elements/forms')
def get_forms():
    """Get all form fields on current page"""
    try:
        b = get_browser()

        # Find all input elements
        inputs = b.find_elements(By.TAG_NAME, 'input')
        textareas = b.find_elements(By.TAG_NAME, 'textarea')
        selects = b.find_elements(By.TAG_NAME, 'select')

        result = []

        # Process inputs
        for i, elem in enumerate(inputs):
            try:
                result.append({
                    'type': 'input',
                    'index': len(result),
                    'input_type': elem.get_attribute('type'),
                    'name': elem.get_attribute('name'),
                    'id': elem.get_attribute('id'),
                    'placeholder': elem.get_attribute('placeholder'),
                    'value': elem.get_attribute('value'),
                    'visible': elem.is_displayed()
                })
            except:
                pass

        # Process textareas
        for i, elem in enumerate(textareas):
            try:
                result.append({
                    'type': 'textarea',
                    'index': len(result),
                    'name': elem.get_attribute('name'),
                    'id': elem.get_attribute('id'),
                    'placeholder': elem.get_attribute('placeholder'),
                    'value': elem.text,
                    'visible': elem.is_displayed()
                })
            except:
                pass

        # Process selects
        for i, elem in enumerate(selects):
            try:
                options = [opt.text for opt in elem.find_elements(By.TAG_NAME, 'option')]
                result.append({
                    'type': 'select',
                    'index': len(result),
                    'name': elem.get_attribute('name'),
                    'id': elem.get_attribute('id'),
                    'options': options,
                    'visible': elem.is_displayed()
                })
            except:
                pass

        return jsonify({
            'status': 'success',
            'count': len(result),
            'fields': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/elements/buttons')
def get_buttons():
    """Get all buttons on current page"""
    try:
        b = get_browser()
        buttons = b.find_elements(By.TAG_NAME, 'button')
        submit_inputs = b.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')

        result = []

        for i, btn in enumerate(buttons + submit_inputs):
            try:
                result.append({
                    'index': i,
                    'text': btn.text.strip(),
                    'type': btn.get_attribute('type'),
                    'id': btn.get_attribute('id'),
                    'name': btn.get_attribute('name'),
                    'visible': btn.is_displayed()
                })
            except:
                pass

        return jsonify({
            'status': 'success',
            'count': len(result),
            'buttons': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/click', methods=['POST'])
def click():
    """Click an element by selector"""
    data = request.get_json()
    selector = data.get('selector')
    selector_type = data.get('type', 'css')  # css, xpath, link_text, etc.

    if not selector:
        return jsonify({'status': 'error', 'message': 'Selector required'}), 400

    try:
        b = get_browser()

        # Map selector types to By constants
        by_map = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'tag': By.TAG_NAME,
            'class': By.CLASS_NAME
        }

        by_type = by_map.get(selector_type, By.CSS_SELECTOR)
        element = b.find_element(by_type, selector)
        element.click()

        time.sleep(1)  # Wait for click action

        return jsonify({
            'status': 'success',
            'message': 'Element clicked',
            'current_url': b.current_url
        })
    except NoSuchElementException:
        return jsonify({
            'status': 'error',
            'message': 'Element not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/fill', methods=['POST'])
def fill():
    """Fill a form field"""
    data = request.get_json()
    selector = data.get('selector')
    selector_type = data.get('type', 'css')
    value = data.get('value', '')
    clear_first = data.get('clear', True)

    if not selector:
        return jsonify({'status': 'error', 'message': 'Selector required'}), 400

    try:
        b = get_browser()

        by_map = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME
        }

        by_type = by_map.get(selector_type, By.CSS_SELECTOR)
        element = b.find_element(by_type, selector)

        if clear_first:
            element.clear()

        element.send_keys(value)

        return jsonify({
            'status': 'success',
            'message': 'Field filled'
        })
    except NoSuchElementException:
        return jsonify({
            'status': 'error',
            'message': 'Element not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/execute', methods=['POST'])
def execute_script():
    """Execute JavaScript"""
    data = request.get_json()
    script = data.get('script')

    if not script:
        return jsonify({'status': 'error', 'message': 'Script required'}), 400

    try:
        b = get_browser()
        result = b.execute_script(script)

        return jsonify({
            'status': 'success',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/back', methods=['POST'])
def go_back():
    """Go back in browser history"""
    try:
        b = get_browser()
        b.back()
        time.sleep(1)
        return jsonify({
            'status': 'success',
            'url': b.current_url
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/forward', methods=['POST'])
def go_forward():
    """Go forward in browser history"""
    try:
        b = get_browser()
        b.forward()
        time.sleep(1)
        return jsonify({
            'status': 'success',
            'url': b.current_url
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/refresh', methods=['POST'])
def refresh():
    """Refresh current page"""
    try:
        b = get_browser()
        b.refresh()
        time.sleep(2)
        return jsonify({
            'status': 'success',
            'url': b.current_url
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Browser Controller API',
        'version': '1.0',
        'endpoints': {
            'GET /status': 'Get browser status',
            'POST /start': 'Start browser session',
            'POST /stop': 'Stop browser session',
            'POST /goto': 'Navigate to URL (body: {url: "..."})',
            'GET /screenshot': 'Get screenshot as PNG',
            'GET /screenshot/base64': 'Get screenshot as base64',
            'GET /elements/links': 'List all links',
            'GET /elements/forms': 'List all form fields',
            'GET /elements/buttons': 'List all buttons',
            'POST /click': 'Click element (body: {selector: "...", type: "css"})',
            'POST /fill': 'Fill form field (body: {selector: "...", value: "...", type: "css"})',
            'POST /execute': 'Execute JavaScript (body: {script: "..."})',
            'POST /back': 'Go back',
            'POST /forward': 'Go forward',
            'POST /refresh': 'Refresh page'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Browser Controller API")
    print("📡 Server will run on http://localhost:5000")
    print("🌐 Visit http://localhost:5000 for API documentation")
    app.run(host='0.0.0.0', port=5000, debug=True)
