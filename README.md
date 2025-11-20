# Chrome Queue Manager

A Python automation tool that helps you get the best queue position when dealing with websites that use queuing systems. It opens multiple Chrome tabs, clears cookies to get fresh queue positions, and automatically finds the tab with the lowest queue number.

## What Does This Do?

When you visit a website with a queue (like ticket sales, limited releases, etc.), you're assigned a queue position. This tool:

1. **Opens multiple tabs** (e.g., 10 tabs) to the same website
2. **Clears cookies before each refresh** so each tab gets a NEW, independent queue position
3. **Continuously monitors** all tabs until queue numbers appear
4. **Finds the best position** and automatically switches to the tab with the lowest queue number
5. **Leaves the browser open** on your best tab so you can continue from there

## Quick Start Guide

### Step 1: Install Python Requirements

1. Make sure you have **Python 3.7 or higher** installed ([Download Python](https://www.python.org/downloads/))

2. Open a terminal/command prompt in this folder and run:
```bash
pip install -r requirements.txt
```

This installs Selenium (for browser automation). ChromeDriver is automatically managed.

### Step 2: Configure the Script

Open [queue_manager.py](queue_manager.py) and edit the `main()` function at the bottom (starts around line 467):

**Required Settings:**

```python
TARGET_URL = "https://example.com"  # Replace with your target website
NUM_TABS = 10  # How many tabs to open (more tabs = more chances at a good position)
```

**Find Your Queue Pattern:**

Look at the website and find how it displays queue numbers. Common examples:

- If the site says **"Queue: 1234"**, use: `QUEUE_PATTERN = r'Queue[:\s]+(\d+)'`
- If it says **"Number in line: 1234"**, use: `QUEUE_PATTERN = r'Number in line[:\s]+(\d+)'`
- If it says **"Position in queue: 1234"**, use: `QUEUE_PATTERN = r'Position in queue[:\s]+(\d+)'`
- If it says **"Users ahead of you: 1234"**, use: `QUEUE_PATTERN = r'Users ahead of you[:\s]+(\d+)'`

The pattern needs to match the text that comes BEFORE the number, and `(\d+)` captures the actual number.

### Step 3: Run the Script

```bash
python queue_manager.py
```

**What happens:**
1. Chrome opens with your specified number of tabs
2. All tabs load the website
3. Cookies are cleared from each tab
4. Each tab refreshes with a delay between refreshes (to avoid rate limiting)
5. The script continuously scans all tabs every 5 seconds for queue numbers
6. When queue numbers appear, it shows you which tab has the best (lowest) position
7. The browser stays open on the best tab - **you take it from here!**

Press Enter in the terminal when you're done to close the browser.

## Detailed Configuration

### Basic Settings

Edit these in the `main()` function in [queue_manager.py](queue_manager.py):

```python
TARGET_URL = "https://example.com"  # Your target website
NUM_TABS = 10  # Number of tabs to open (recommended: 5-15)
```

### Chrome Profile (Optional - Advanced)

By default, the script uses a clean Chrome profile. If you want to use your regular Chrome profile (with existing extensions, login sessions, etc.):

```python
CHROME_PROFILE = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
```

**Important:** When using your regular Chrome profile, **close ALL Chrome windows** before running the script, otherwise you'll get a profile lock error.

### Queue Number Pattern (Regex)

The script uses regular expressions (regex) to find queue numbers on the page. You need to customize this based on how YOUR website displays queue numbers.

**How to find the right pattern:**

1. Visit the website manually and wait until you see a queue number
2. Note the EXACT text that appears (e.g., "Number of users in line ahead of you: 1234")
3. Create a pattern that matches that text

**Example patterns:**

```python
# Example 1: "Queue: 123" or "Queue 123"
QUEUE_PATTERN = r'queue[:\s]+(\d+)'

# Example 2: "Position in queue: 123"
QUEUE_PATTERN = r'position in queue[:\s]+(\d+)'

# Example 3: "Number of users in line ahead of you: 123"
QUEUE_PATTERN = r'Number of users in line ahead of you:[\s\S]*?(\d+)'

# Example 4: "Queue #123" or "Queue123"
QUEUE_PATTERN = r'queue\s*#?\s*(\d+)'

# Example 5: "123 in line"
QUEUE_PATTERN = r'(\d+)\s+in line'
```

The `(\d+)` part captures the actual number. The text before it should match what appears on the page (case insensitive).

### Advanced Options

You can customize the behavior in `manager.run_full_cycle()`:

```python
manager.run_full_cycle(
    queue_pattern=QUEUE_PATTERN,
    use_continuous_monitoring=True,  # Keep checking until queue numbers appear
    check_interval=5,  # Check every 5 seconds
    max_attempts=1000,  # Maximum number of checks (1000 = ~83 minutes if checking every 5 sec)
    use_cookie_editor=False,  # Use Selenium's built-in cookie deletion (recommended)
    pause_before_cookies=False  # Pause to manually install extensions (usually not needed)
)
```

## Complete Example

Here's a complete example configuration for a typical queue website:

```python
def main():
    # Configuration
    TARGET_URL = "https://yourwebsite.com/queue"
    NUM_TABS = 10

    # Optional: Use your regular Chrome profile (remember to close Chrome first!)
    # CHROME_PROFILE = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
    CHROME_PROFILE = None  # Use None for a clean profile (recommended)

    # Set this to match how YOUR website shows queue numbers
    QUEUE_PATTERN = r'Queue[:\s]+(\d+)'

    # Create and run the manager
    manager = QueueManager(
        url=TARGET_URL,
        num_tabs=NUM_TABS,
        chrome_profile_path=CHROME_PROFILE
    )

    manager.run_full_cycle(
        queue_pattern=QUEUE_PATTERN,
        use_cookie_editor=False,  # Use Selenium method (recommended)
        max_attempts=1000  # Keep monitoring for up to ~83 minutes
    )
```

## Common Issues & Solutions

### "No queue numbers found"

**Problem:** The script can't find queue numbers on the page.

**Solutions:**
1. **Check your regex pattern** - Visit the website manually, find where the queue number appears, and update `QUEUE_PATTERN` to match that exact text
2. **Wait longer** - Some sites take time to load queue info. The script continuously monitors every 5 seconds, so just wait
3. **Check the website** - Make sure the website actually displays queue numbers in the page text (not in an image)

**How to debug:**
- Look at the terminal output - it shows what the script is finding
- The pattern is case-insensitive, so "Queue" matches "queue", "QUEUE", etc.

### "Profile is already in use" or "Chrome didn't start"

**Problem:** Chrome profile is locked by another Chrome instance.

**Solution:** Close ALL Chrome windows before running the script. Or use `CHROME_PROFILE = None` to use a clean profile.

### "ChromeDriver error"

**Problem:** ChromeDriver version mismatch.

**Solution:** Update Chrome to the latest version. Selenium 4.15+ automatically manages ChromeDriver, but it needs Chrome to be recent.

### The script stops too early

**Problem:** Script stops checking before queue numbers appear.

**Solution:** Increase `max_attempts` in `run_full_cycle()`:
```python
max_attempts=2000  # Check for longer (2000 attempts × 5 seconds = ~2.7 hours)
```

### Browser closes immediately

**Problem:** Script finishes and closes the browser before you can use it.

**Solution:** The script should pause with "Press Enter to close the browser...". If it's closing immediately, there might be an error. Check the terminal output for error messages.

## How It Works (Technical Details)

### The Process Flow

1. **Browser Initialization** (`start_browser()`)
   - Opens Chrome with anti-automation detection disabled
   - Can load your Chrome profile or use a clean one

2. **Tab Opening** (`open_tabs()`)
   - Opens N tabs (specified by `NUM_TABS`)
   - Each tab navigates to your target URL

3. **Cookie Deletion** (`delete_cookies()`)
   - Clears cookies, localStorage, and sessionStorage from all tabs
   - This ensures each tab gets a fresh queue position

4. **Staggered Refresh** (`refresh_all_tabs()`)
   - Refreshes each tab with delays between them (default: 3 seconds)
   - Clears cookies again right before each individual refresh
   - This prevents getting the same queue ID across multiple tabs

5. **Continuous Monitoring** (`monitor_tabs_continuously()`)
   - Scans all tabs every 5 seconds (configurable)
   - Uses regex to find queue numbers in page text
   - Continues until queue numbers appear or max attempts reached

6. **Best Tab Selection** (`find_best_tab()`)
   - Compares all queue numbers found
   - Switches to the tab with the lowest number
   - Displays the winner in the terminal

### Key Functions

- **`start_browser()`** - Initializes Chrome with custom options
- **`open_tabs()`** - Opens multiple tabs with the target URL
- **`delete_cookies()`** - Clears cookies using Selenium (recommended)
- **`delete_cookies_with_extension()`** - Alternative method using Cookie-Editor extension
- **`refresh_all_tabs()`** - Refreshes all tabs with delays and optional cookie clearing
- **`scan_queue_numbers()`** - Scans all tabs for queue positions using regex
- **`monitor_tabs_continuously()`** - Continuously checks tabs until queue numbers appear
- **`find_best_tab()`** - Identifies and switches to the tab with the lowest queue
- **`run_full_cycle()`** - Orchestrates the complete automation workflow

## Tips for Best Results

### 1. Use enough tabs
- **5-10 tabs**: Good for most situations
- **10-15 tabs**: Better odds of getting a low queue position
- **Too many tabs**: May trigger rate limiting or anti-bot detection

### 2. Timing is everything
- Run the script RIGHT when the queue opens (if you know the time)
- The earlier you run it, the lower the queue numbers will be overall

### 3. Test your regex pattern first
- Visit the site manually and check how queue numbers are displayed
- Update `QUEUE_PATTERN` to match exactly
- The script shows what it finds, so you can adjust if needed

### 4. Avoid anti-bot detection
- Don't use an excessive number of tabs (stay under 15-20)
- The script already includes delays between refreshes
- Using your Chrome profile can make the browser appear more "normal"

### 5. Monitor the terminal output
- The script prints detailed logs of what it's doing
- Watch for error messages or "No queue found" warnings
- If queue numbers aren't appearing, check your regex pattern

## Advanced Usage

### Continuous Re-Monitoring

The script already monitors continuously by default. If you want to refresh and re-check periodically (to see if better positions open up):

```python
# Inside queue_manager.py, modify the run_full_cycle method
# This is already implemented with use_continuous_monitoring=True
```

### Testing Your Regex Pattern

To test if your regex pattern works without running the full script, you can add this to the bottom of [queue_manager.py](queue_manager.py):

```python
import re
page_text = "Your queue position: 1234"  # Replace with actual text from the website
pattern = r'queue position[:\s]+(\d+)'  # Your pattern
matches = re.findall(pattern, page_text, re.IGNORECASE)
print(f"Found: {matches}")  # Should print: ['1234']
```

### Using Cookie-Editor Extension (Advanced)

By default, the script uses Selenium's built-in cookie deletion, which works well. If you prefer to use the Cookie-Editor extension:

1. Install Cookie-Editor in your Chrome profile
2. Go to `chrome://extensions/` and enable "Developer mode"
3. Copy the extension ID (looks like: `hlkenndednhfkekhgcdicdfddnkalmdm`)
4. Update your configuration:

```python
USE_COOKIE_EDITOR = True
COOKIE_EDITOR_ID = "your-extension-id-here"
CHROME_PROFILE = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
```

Note: The Selenium method is more reliable for most use cases.

## Frequently Asked Questions

**Q: Is this legal?**
A: This tool automates a web browser, similar to browser extensions or testing tools. However, some websites prohibit automation in their Terms of Service. Use responsibly and check the website's terms before using.

**Q: Will this guarantee me a low queue position?**
A: No guarantees. The tool gives you multiple chances by opening multiple tabs, but queue positions are still assigned randomly or by arrival time by the website.

**Q: Can websites detect this?**
A: Possibly. The script includes some anti-detection measures (disabling automation flags, using delays), but sophisticated anti-bot systems may still detect it. Using your regular Chrome profile helps it look more normal.

**Q: Why does it clear cookies?**
A: Many queue systems use cookies to remember your queue position. By clearing cookies between tabs, each tab gets a NEW queue position rather than reusing the same one.

**Q: Can I run this on Mac or Linux?**
A: Yes! The script is cross-platform. Just update the file paths (use forward slashes `/` instead of backslashes `\` on Mac/Linux).

**Q: How do I stop the script while it's running?**
A: Press `Ctrl+C` in the terminal to stop the script. The browser will close automatically.

## Requirements

- **Python 3.7+** ([Download](https://www.python.org/downloads/))
- **Google Chrome** (latest version recommended)
- **Selenium** (installed via `pip install -r requirements.txt`)

ChromeDriver is automatically managed by Selenium 4.15+, so you don't need to download it separately.

## License

Free to use and modify for personal use.

## Disclaimer

This tool is for educational purposes. Ensure you comply with the website's Terms of Service before using automation. Some websites explicitly prohibit automated access. Use responsibly and at your own risk.
