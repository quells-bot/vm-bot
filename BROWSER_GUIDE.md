# Browser Controller - Quick Reference

## What Is This?

A stateful browser automation system that lets you:
- View any webpage (via screenshots)
- Interact with pages (click, type, navigate)
- Keep browser state between commands
- Extract data from pages

## Quick Start

### 1. Start the Server (if not already running)

```bash
python3 tools/browser_controller.py &
```

The server runs on `http://localhost:5000`

### 2. Use It

**Option A: Python Client**

```python
from tools.browser_client import BrowserClient

browser = BrowserClient()

# Navigate
browser.goto("https://example.com")

# Take screenshot (returns base64 in JSON)
response = browser.screenshot()
# response = {'status': 'success', 'screenshot': 'data:image/png;base64,...', 'url': '...', 'title': '...'}

# Discover form fields first (recommended!)
forms = browser.get_forms()
# Shows all inputs with their names, ids, types, and selectors

# Fill a form
browser.fill("#username", "myuser", "id")
browser.fill("#password", "secret", "id")
browser.click("button[type='submit']", "css")

# Get links
links = browser.get_links()
```

**Option B: curl / REST API**

```bash
# Navigate (with optional wait time)
curl -X POST 'http://localhost:5000/goto?wait=3' \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Screenshot (returns base64 JSON)
curl http://localhost:5000/screenshot | jq
# Returns: {"status": "success", "screenshot": "data:image/png;base64,...", "url": "...", "title": "..."}

# Discover form fields (RECOMMENDED FIRST STEP)
curl http://localhost:5000/elements/forms | jq
# Shows all form fields with their names, ids, types, and how to select them

# Fill form
curl -X POST http://localhost:5000/fill \
  -H "Content-Type: application/json" \
  -d '{"selector": "#username", "value": "myuser", "type": "id"}'

# Click (with optional wait)
curl -X POST 'http://localhost:5000/click?wait=2' \
  -H "Content-Type: application/json" \
  -d '{"selector": "button", "type": "css"}'

# Get links
curl http://localhost:5000/elements/links | jq
```

### Interactive curl Workflow

The real power is using curl interactively. Here's a real example navigating Wikipedia:

```bash
# 1. Start the browser
curl -X POST http://localhost:5000/start

# 2. Go to Wikipedia
curl -X POST http://localhost:5000/goto \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org"}'

# 3. Take a screenshot to see what's there
curl http://localhost:5000/screenshot | jq -r '.screenshot'
# Returns base64 image data that Claude can view directly

# 4. Find today's featured article link with JavaScript
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "const a = document.querySelector(\"#mp-tfa p a\"); return a ? a.href : null;"}' | jq

# 5. Click on it
curl -X POST http://localhost:5000/click \
  -H "Content-Type: application/json" \
  -d '{"selector": "#mp-tfa p a", "type": "css"}'

# 6. Check where you are
curl http://localhost:5000/status | jq

# 7. Extract content (e.g., second paragraph)
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "const p = document.querySelectorAll(\".mw-parser-output > p\"); return p[1] ? p[1].textContent : null;"}' | jq -r '.result'

# 8. Click a link by text
curl -X POST http://localhost:5000/click \
  -H "Content-Type: application/json" \
  -d '{"selector": "siege", "type": "link_text"}'

# 9. Take another screenshot
curl http://localhost:5000/screenshot | jq -r '.screenshot'
```

**Key tips:**
- The browser **keeps its state** between curl commands
- Use `jq` to prettify JSON responses
- Use `jq -r '.result'` to extract just the result value
- Screenshots let you "see" what's on the page before deciding what to do next
- JavaScript via `/execute` is powerful for finding and extracting data
- Check `/status` anytime to see current URL and title

## API Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/status` | GET | Check browser state | `curl localhost:5000/status` |
| `/start` | POST | Start browser | `curl -X POST localhost:5000/start` |
| `/stop` | POST | Stop browser | `curl -X POST localhost:5000/stop` |
| `/goto?wait=N` | POST | Navigate to URL | `{"url": "https://..."}` + optional ?wait=seconds |
| `/screenshot` | GET | Get base64 screenshot | Returns JSON with base64 image data |
| `/elements/links` | GET | List all links | Returns JSON |
| `/elements/forms` | GET | **List form fields** | **Returns JSON with selectors** ⭐ |
| `/elements/buttons` | GET | List buttons | Returns JSON |
| `/click?wait=N` | POST | Click element | `{"selector": "...", "type": "css"}` + optional ?wait |
| `/fill?wait=N` | POST | Fill form field | `{"selector": "...", "value": "..."}` + optional ?wait |
| `/execute` | POST | Run JavaScript | `{"script": "return document.title"}` |
| `/back?wait=N` | POST | Go back | History navigation + optional ?wait |
| `/forward?wait=N` | POST | Go forward | History navigation + optional ?wait |
| `/refresh?wait=N` | POST | Reload page | Refresh current page + optional ?wait |

**New in v1.1:**
- All POST endpoints now support optional `?wait=N` query parameter (in seconds)
- `/screenshot` now returns base64 JSON instead of raw PNG
- Default wait times: goto=2s, click=1s, fill=0.5s, back/forward=1s, refresh=2s

## Selector Types

When using `/click` or `/fill`, specify the selector type:

- `css` - CSS selector (default): `.class`, `#id`, `a[href*='login']`
- `xpath` - XPath: `//div[@class='content']`
- `id` - ID: `username` (without the #)
- `name` - Name attribute: `email`
- `link_text` - Exact link text: `Click Here`
- `partial_link_text` - Partial link text: `Click`

## Common Workflows

### Discover Forms (Do This First!)

Before filling out forms, use `/elements/forms` to see what's available:

```python
# Get all form fields
forms = browser.get_forms()
for field in forms['fields']:
    if field['visible']:
        print(f"{field['type']}: {field['name'] or field['id']} - {field['input_type']}")
```

```bash
# curl version
curl http://localhost:5000/elements/forms | jq '.fields[] | select(.visible == true)'
```

This shows you:
- Field types (input, textarea, select)
- Names and IDs (use these as selectors!)
- Input types (text, password, email, etc.)
- Current values
- Available options (for dropdowns)

### View a Page

```python
browser.goto("https://example.com")
result = browser.screenshot()
# result['screenshot'] contains base64 image: 'data:image/png;base64,...'
# result['url'] and result['title'] show current page info
```

### Find and Click a Link

```python
# Get all links
links = browser.get_links()
for link in links['links']:
    if 'login' in link['text'].lower():
        print(f"Found login link: {link['href']}")

# Click it
browser.click("a", "link_text")  # by exact text
# or
browser.click("a[href*='login']", "css")  # by CSS selector
```

### Fill Out a Form

```python
# STEP 1: Discover what form fields exist (IMPORTANT!)
forms = browser.get_forms()
for field in forms['fields']:
    print(f"Field: {field['name']} (type: {field['input_type']}, id: {field['id']})")

# STEP 2: Fill fields using the names/ids you discovered
browser.fill("username", "myuser", "name")  # Using name attribute
browser.fill("password", "secret", "name")   # Using name attribute

# STEP 3: Submit
browser.click("button[type='submit']", "css")

# STEP 4: Verify
response = browser.screenshot()
# Screenshot is now in response['screenshot'] as base64
```

```bash
# curl version
# 1. Discover fields
curl http://localhost:5000/elements/forms | jq

# 2. Fill them
curl -X POST http://localhost:5000/fill \
  -H "Content-Type: application/json" \
  -d '{"selector": "username", "value": "myuser", "type": "name"}'

# 3. Submit (with wait for page load)
curl -X POST 'http://localhost:5000/click?wait=2' \
  -H "Content-Type: application/json" \
  -d '{"selector": "button[type=\"submit\"]", "type": "css"}'
```

### Extract Data with JavaScript

```python
result = browser.execute("return document.title")
print(result['result'])  # Page title

# More complex extraction
script = """
return Array.from(document.querySelectorAll('a'))
    .map(a => ({text: a.textContent, href: a.href}))
    .slice(0, 10);
"""
links = browser.execute(script)
print(links['result'])
```

## Tips

1. **Discover forms first** - Use `/elements/forms` before filling forms to see what selectors to use
2. **Screenshots are your eyes** - Screenshots now return base64 JSON with URL and title
3. **Use wait parameters** - Add `?wait=N` to control timing instead of manual sleeps: `/click?wait=3`
4. **Browser persists** - The session stays alive between commands
5. **Check status** - Use `/status` endpoint to see current state
6. **JavaScript is powerful** - Use `/execute` for complex data extraction
7. **NEVER truncate base64 data** - Do NOT pipe screenshot base64 into `head`, `tail`, or otherwise truncate it (e.g., `head -c 100`). Truncated base64 is invalid and cannot be decoded. This will poison your context with broken data. Always use the complete base64 string.

## Files

- `tools/browser_controller.py` - Flask server (run this)
- `tools/browser_client.py` - Python client library (import this)
- `docs/diary/2026-02-01-browser.md` - Development diary

## Stopping

```bash
# Stop the browser session (keeps server running)
curl -X POST http://localhost:5000/stop

# Stop the server
pkill -f "python3 tools/browser_controller.py"
```
