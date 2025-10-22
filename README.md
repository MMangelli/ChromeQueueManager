# Chrome Queue Manager

A Python automation tool that opens multiple Chrome tabs, clears cookies, and scans for the lowest queue position across all tabs.

## Features

- Opens multiple Chrome tabs simultaneously
- Deletes cookies (supports both Selenium built-in and EditThisCookie extension)
- Refreshes all tabs automatically
- Scans all tabs for queue numbers using customizable regex patterns
- Identifies and switches to the tab with the lowest queue position

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by Selenium 4.15+)

## Installation

1. Clone or download this repository

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Configuration

Edit the `main()` function in [queue_manager.py](queue_manager.py) to configure:

### Basic Settings

```python
TARGET_URL = "https://example.com"  # Your target website
NUM_TABS = 5  # Number of tabs to open
```

### Chrome Profile (Optional)

To use your existing Chrome profile with EditThisCookie already installed:

```python
CHROME_PROFILE = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
```

**Note**: When using a Chrome profile, make sure Chrome is closed before running the script.

### Queue Number Pattern

Customize the regex pattern based on how queue numbers appear on your website:

```python
# Example patterns:
QUEUE_PATTERN = r'queue[:\s]+(\d+)'  # Matches "Queue: 123" or "Queue 123"
QUEUE_PATTERN = r'position in queue[:\s]+(\d+)'  # Matches "Position in queue: 123"
QUEUE_PATTERN = r'queue\s*#?\s*(\d+)'  # Matches "Queue #123" or "Queue123"
QUEUE_PATTERN = r'(\d+)\s+in line'  # Matches "123 in line"
```

## Usage

Run the script:

```bash
python queue_manager.py
```

The script will:
1. Open Chrome with the specified number of tabs
2. Navigate to the target URL in each tab
3. Clear cookies from all tabs
4. Refresh all tabs
5. Scan each tab for queue numbers
6. Display the tab with the lowest queue position
7. Keep the browser open for you to proceed

Press Enter when prompted to close the browser.

## How It Works

### QueueManager Class

The main class that handles all automation:

- **`start_browser()`**: Initializes Chrome with custom options
- **`open_tabs()`**: Opens multiple tabs with the target URL
- **`delete_cookies_manual()`**: Uses Selenium to delete all cookies
- **`delete_cookies_via_extension()`**: Placeholder for EditThisCookie automation
- **`refresh_all_tabs()`**: Refreshes all opened tabs
- **`scan_queue_numbers()`**: Scans all tabs for queue positions using regex
- **`find_best_tab()`**: Identifies and switches to the tab with lowest queue
- **`run_full_cycle()`**: Executes the complete automation workflow

## EditThisCookie Extension

### Method 1: Use Chrome Profile (Recommended)

If EditThisCookie is already installed in your Chrome:

```python
CHROME_PROFILE = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
```

### Method 2: Extension File

If you have the .crx file:

```python
EXTENSION_PATH = r"C:\path\to\EditThisCookie.crx"
```

### Current Implementation

Currently, the script uses Selenium's built-in `delete_all_cookies()` method, which works reliably across all websites. The EditThisCookie integration can be enhanced if specific extension features are needed.

## Troubleshooting

### ChromeDriver Issues

Selenium 4.15+ automatically manages ChromeDriver. If you encounter issues, ensure Chrome is up to date.

### Profile Lock Error

If you get a profile lock error, close all Chrome instances before running the script.

### No Queue Numbers Found

1. Check that your regex pattern matches the queue number format on the website
2. Increase the timeout in `scan_queue_numbers(timeout=10)`
3. The page might use JavaScript to load queue numbers - add a delay after refresh

### Anti-Bot Detection

Some websites detect automation. To help avoid this:
- Use your Chrome profile (makes the browser look more "normal")
- Add delays between actions
- Consider using undetected-chromedriver (install separately)

## Advanced Customization

### Continuous Monitoring

To continuously scan for queue positions, modify `run_full_cycle()`:

```python
while True:
    self.refresh_all_tabs()
    time.sleep(5)
    queue_data = self.scan_queue_numbers(queue_pattern=queue_pattern)
    self.find_best_tab(queue_data)
    time.sleep(30)  # Wait 30 seconds before next scan
```

### Custom Scanning Logic

Override `scan_queue_numbers()` to implement custom logic for finding queue positions based on your specific website structure.

## License

Free to use and modify for personal use.

## Disclaimer

This tool is for educational purposes. Ensure you have permission to automate interactions with any website you target. Respect website terms of service and rate limits.
