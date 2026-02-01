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

# Take screenshot
browser.screenshot("page.png")

# Get links
links = browser.get_links()

# Click something
browser.click("a.login", "css")

# Fill a form
browser.fill("#username", "myuser", "id")
browser.fill("#password", "secret", "id")
browser.click("button[type='submit']", "css")

# Get new state
browser.screenshot("after_login.png")
```

**Option B: curl / REST API**

```bash
# Navigate
curl -X POST http://localhost:5000/goto \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Screenshot
curl http://localhost:5000/screenshot > page.png

# Get links
curl http://localhost:5000/elements/links | jq

# Click
curl -X POST http://localhost:5000/click \
  -H "Content-Type: application/json" \
  -d '{"selector": "a.login", "type": "css"}'

# Fill form
curl -X POST http://localhost:5000/fill \
  -H "Content-Type: application/json" \
  -d '{"selector": "#username", "value": "myuser", "type": "id"}'
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
curl http://localhost:5000/screenshot > page.png
# (Open page.png to see the page)

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
curl http://localhost:5000/screenshot > new_page.png
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
| `/goto` | POST | Navigate to URL | `{"url": "https://..."}` |
| `/screenshot` | GET | Get PNG screenshot | Downloads PNG file |
| `/elements/links` | GET | List all links | Returns JSON |
| `/elements/forms` | GET | List form fields | Returns JSON |
| `/elements/buttons` | GET | List buttons | Returns JSON |
| `/click` | POST | Click element | `{"selector": "...", "type": "css"}` |
| `/fill` | POST | Fill form field | `{"selector": "...", "value": "..."}` |
| `/execute` | POST | Run JavaScript | `{"script": "return document.title"}` |
| `/back` | POST | Go back | History navigation |
| `/forward` | POST | Go forward | History navigation |
| `/refresh` | POST | Reload page | Refresh current page |

## Selector Types

When using `/click` or `/fill`, specify the selector type:

- `css` - CSS selector (default): `.class`, `#id`, `a[href*='login']`
- `xpath` - XPath: `//div[@class='content']`
- `id` - ID: `username` (without the #)
- `name` - Name attribute: `email`
- `link_text` - Exact link text: `Click Here`
- `partial_link_text` - Partial link text: `Click`

## Common Workflows

### View a Page

```python
browser.goto("https://example.com")
browser.screenshot("page.png")
# Now look at page.png to see what's there
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
# List form fields to see what's available
forms = browser.get_forms()
print(forms)

# Fill fields by name or id
browser.fill("input[name='username']", "myuser", "css")
browser.fill("input[name='password']", "secret", "css")

# Submit
browser.click("button[type='submit']", "css")

# Verify
browser.screenshot("after_submit.png")
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

1. **Screenshots are your eyes** - Always take a screenshot after navigation to see what loaded
2. **Wait for content** - Dynamic pages load slowly; add `time.sleep(2)` after navigation
3. **Browser persists** - The session stays alive between commands
4. **Check status** - Use `/status` endpoint to see current state
5. **JavaScript is powerful** - Use `/execute` for complex data extraction

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
