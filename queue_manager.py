"""
Chrome Queue Manager
Automates opening multiple Chrome tabs, clearing cookies, and finding the lowest queue position
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class QueueManager:
    def __init__(self, url, num_tabs=5, chrome_profile_path=None):
        """
        Initialize the Queue Manager

        Args:
            url (str): The URL to open in multiple tabs
            num_tabs (int): Number of tabs to open
            chrome_profile_path (str): Path to Chrome profile (optional)
        """
        self.url = url
        self.num_tabs = num_tabs
        self.driver = None
        self.tabs = []

        # Setup Chrome options
        self.chrome_options = Options()

        # Load Chrome profile if provided (this will have your extensions)
        if chrome_profile_path:
            self.chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")

        # Optional: Run in background (comment out if you want to see the browser)
        # self.chrome_options.add_argument('--headless')

        # Disable automation flags
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

    def start_browser(self):
        """Initialize the Chrome browser"""
        print("Starting Chrome browser...")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        print("Browser started successfully!")

    def open_tabs(self):
        """Open multiple tabs with the target URL"""
        print(f"Opening {self.num_tabs} tabs...")

        # First tab
        self.driver.get(self.url)
        self.tabs.append(self.driver.current_window_handle)

        # Additional tabs
        for i in range(1, self.num_tabs):
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[i])
            self.driver.get(self.url)
            self.tabs.append(self.driver.current_window_handle)
            print(f"Opened tab {i + 1}/{self.num_tabs}")

        print(f"All {self.num_tabs} tabs opened!")

    def delete_cookies(self):
        """
        Delete cookies using Selenium's built-in method
        """
        print("Deleting cookies from all tabs...")
        for i, tab in enumerate(self.tabs):
            self.driver.switch_to.window(tab)
            self.driver.delete_all_cookies()
            print(f"Cookies deleted from tab {i + 1}")

    def delete_cookies_with_extension(self, extension_id=None, wait_time=3):
        """
        Delete cookies using Cookie-Editor extension by automating clicks

        Args:
            extension_id (str): Chrome extension ID for Cookie-Editor (find in chrome://extensions)
            wait_time (int): Time to wait for extension popup to load
        """
        print("Deleting cookies using Cookie-Editor extension...")

        for i, tab in enumerate(self.tabs):
            self.driver.switch_to.window(tab)

            try:
                if extension_id:
                    # Open Cookie-Editor extension popup directly
                    extension_url = f"chrome-extension://{extension_id}/popup.html"
                    self.driver.execute_script(f"window.open('{extension_url}', '_blank');")

                    # Switch to the extension popup window
                    time.sleep(1)
                    popup_handle = self.driver.window_handles[-1]
                    self.driver.switch_to.window(popup_handle)

                    # Wait for popup to load
                    time.sleep(wait_time)

                    # Try to find and click the delete all cookies button
                    try:
                        # Cookie-Editor typically has a "Delete All" button or trash icon
                        # This may need adjustment based on the extension's UI
                        delete_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Delete') or contains(@title, 'Delete')]"))
                        )
                        delete_button.click()
                        print(f"Tab {i + 1}: Clicked delete button in Cookie-Editor")
                    except:
                        print(f"Tab {i + 1}: Could not find delete button, trying alternative method...")

                    # Close the popup
                    self.driver.close()

                    # Switch back to original tab
                    self.driver.switch_to.window(tab)
                else:
                    # Fallback: Use keyboard shortcut to open extension (if configured)
                    # Then use keyboard navigation to delete cookies
                    print(f"Tab {i + 1}: Extension ID not provided, using manual method")
                    print(f"Tab {i + 1}: Please click the Cookie-Editor icon and delete cookies manually")
                    time.sleep(5)  # Give user time to manually click

                print(f"Tab {i + 1}: Cookies deletion attempted via extension")

            except Exception as e:
                print(f"Tab {i + 1}: Error using extension - {str(e)}")
                print(f"Tab {i + 1}: Falling back to Selenium delete_all_cookies()")
                self.driver.switch_to.window(tab)
                self.driver.delete_all_cookies()

    def refresh_all_tabs(self):
        """Refresh all opened tabs"""
        print("Refreshing all tabs...")
        for i, tab in enumerate(self.tabs):
            self.driver.switch_to.window(tab)
            self.driver.refresh()
            print(f"Refreshed tab {i + 1}")
            time.sleep(1)  # Small delay between refreshes

    def scan_queue_numbers(self, queue_pattern=r'queue[:\s]+(\d+)', timeout=10):
        """
        Scan all tabs for queue numbers and return the lowest one

        Args:
            queue_pattern (str): Regex pattern to find queue numbers
            timeout (int): How long to wait for page load

        Returns:
            dict: Dictionary with tab index and queue numbers
        """
        print("\nScanning for queue numbers...")
        queue_data = {}

        for i, tab in enumerate(self.tabs):
            self.driver.switch_to.window(tab)

            try:
                # Wait for page to load
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Get page text
                page_text = self.driver.find_element(By.TAG_NAME, "body").text

                # Search for queue number using regex
                matches = re.findall(queue_pattern, page_text, re.IGNORECASE)

                if matches:
                    # Convert to integers and get the first match (or all matches)
                    queue_numbers = [int(match) for match in matches]
                    queue_data[i] = {
                        'tab_handle': tab,
                        'queue_numbers': queue_numbers,
                        'lowest_queue': min(queue_numbers),
                        'url': self.driver.current_url
                    }
                    print(f"Tab {i + 1}: Found queue number(s): {queue_numbers}")
                else:
                    print(f"Tab {i + 1}: No queue number found")
                    queue_data[i] = {
                        'tab_handle': tab,
                        'queue_numbers': [],
                        'lowest_queue': float('inf'),
                        'url': self.driver.current_url
                    }

            except TimeoutException:
                print(f"Tab {i + 1}: Timeout waiting for page to load")
                queue_data[i] = {
                    'tab_handle': tab,
                    'queue_numbers': [],
                    'lowest_queue': float('inf'),
                    'url': 'timeout'
                }
            except Exception as e:
                print(f"Tab {i + 1}: Error scanning - {str(e)}")
                queue_data[i] = {
                    'tab_handle': tab,
                    'queue_numbers': [],
                    'lowest_queue': float('inf'),
                    'url': 'error'
                }

        return queue_data

    def find_best_tab(self, queue_data):
        """
        Find the tab with the lowest queue number

        Args:
            queue_data (dict): Dictionary from scan_queue_numbers()

        Returns:
            tuple: (tab_index, queue_number)
        """
        if not queue_data:
            print("No queue data available!")
            return None, None

        best_tab = min(queue_data.items(), key=lambda x: x[1]['lowest_queue'])
        tab_index, data = best_tab

        if data['lowest_queue'] == float('inf'):
            print("\nNo valid queue numbers found in any tab!")
            return None, None

        print(f"\n{'='*50}")
        print(f"BEST TAB: Tab {tab_index + 1}")
        print(f"Queue Position: {data['lowest_queue']}")
        print(f"URL: {data['url']}")
        print(f"{'='*50}\n")

        # Switch to the best tab
        self.driver.switch_to.window(data['tab_handle'])

        return tab_index, data['lowest_queue']

    def monitor_tabs_continuously(self, queue_pattern=r'queue[:\s]+(\d+)',
                                   check_interval=5, max_attempts=None,
                                   stop_on_first_find=False):
        """
        Continuously monitor all tabs for queue numbers until they appear

        Args:
            queue_pattern (str): Regex pattern to find queue numbers
            check_interval (int): Seconds to wait between scans
            max_attempts (int): Maximum number of scan attempts (None for unlimited)
            stop_on_first_find (bool): Stop monitoring once any queue number is found

        Returns:
            dict: Final queue data from the last successful scan
        """
        attempt = 0
        found_any = False

        print(f"\n{'='*50}")
        print("Starting continuous monitoring...")
        print(f"Check interval: {check_interval} seconds")
        if max_attempts:
            print(f"Maximum attempts: {max_attempts}")
        else:
            print("Will monitor indefinitely until queue numbers found")
        print(f"{'='*50}\n")

        while True:
            attempt += 1
            print(f"\n--- Scan Attempt {attempt} ---")

            queue_data = self.scan_queue_numbers(queue_pattern=queue_pattern)

            # Check if any valid queue numbers were found
            valid_queues = [data for data in queue_data.values()
                          if data['lowest_queue'] != float('inf')]

            if valid_queues:
                found_any = True
                num_found = len(valid_queues)
                print(f"\n✓ Found queue numbers in {num_found}/{len(self.tabs)} tabs!")

                if stop_on_first_find:
                    print("Stopping monitoring (stop_on_first_find=True)")
                    return queue_data

                # Show summary of all found queues
                print("\nCurrent queue positions:")
                for idx, data in queue_data.items():
                    if data['lowest_queue'] != float('inf'):
                        print(f"  Tab {idx + 1}: Queue {data['lowest_queue']}")
                    else:
                        print(f"  Tab {idx + 1}: Waiting...")

                # If all tabs have queue numbers, we're done
                if num_found == len(self.tabs):
                    print("\n✓ All tabs now showing queue numbers!")
                    return queue_data
            else:
                print(f"\nNo queue numbers found yet. Waiting {check_interval} seconds...")

            # Check if we've reached max attempts
            if max_attempts and attempt >= max_attempts:
                print(f"\nReached maximum attempts ({max_attempts})")
                if found_any:
                    print("Returning partial results...")
                else:
                    print("No queue numbers found in any attempt")
                return queue_data

            # Wait before next scan
            time.sleep(check_interval)

    def run_full_cycle(self, queue_pattern=r'queue[:\s]+(\d+)',
                       use_continuous_monitoring=True, check_interval=5, max_attempts=60,
                       use_cookie_editor=False, cookie_editor_id=None):
        """
        Run the complete cycle: open tabs, clear cookies, refresh, scan queues

        Args:
            queue_pattern (str): Regex pattern to find queue numbers
            use_continuous_monitoring (bool): Use continuous monitoring instead of single scan
            check_interval (int): Seconds between monitoring checks (if continuous monitoring enabled)
            max_attempts (int): Maximum monitoring attempts (None for unlimited)
            use_cookie_editor (bool): Use Cookie-Editor extension instead of Selenium's delete_all_cookies
            cookie_editor_id (str): Extension ID for Cookie-Editor (find in chrome://extensions)
        """
        try:
            self.start_browser()
            time.sleep(2)  # Let browser initialize

            self.open_tabs()
            time.sleep(5)  # Wait for all tabs to fully load

            if use_cookie_editor:
                self.delete_cookies_with_extension(extension_id=cookie_editor_id)
            else:
                self.delete_cookies()
            time.sleep(2)

            self.refresh_all_tabs()
            time.sleep(3)  # Wait for pages to load after refresh

            if use_continuous_monitoring:
                # Use continuous monitoring - keeps checking until queue numbers appear
                queue_data = self.monitor_tabs_continuously(
                    queue_pattern=queue_pattern,
                    check_interval=check_interval,
                    max_attempts=max_attempts
                )
            else:
                # Single scan only
                queue_data = self.scan_queue_numbers(queue_pattern=queue_pattern)

            self.find_best_tab(queue_data)

            print("\nProcess complete! Browser will remain open.")
            print("Close the browser manually when done.")

            # Keep browser open
            input("\nPress Enter to close the browser...")

        except Exception as e:
            print(f"Error during execution: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                print("Browser closed.")


def main():
    """Main execution function"""

    # Configuration
    TARGET_URL = "https://eventswithdisney.queue-it.net/?PKformID=0x900487abcd&c=eventswithdisney&e=twdcstorepin25nov20"
    NUM_TABS = 5  # Number of tabs to open

    # Optional: Path to your Chrome profile (required if using Cookie-Editor extension)
    # Example for Windows: r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
    # Leave as None to use default profile
    # IMPORTANT: Close all Chrome windows before running if using a profile path!
    CHROME_PROFILE = None  # Set to None to avoid profile lock issues

    # Cookie-Editor Extension Configuration
    # To find your extension ID:
    # 1. Open Chrome and go to chrome://extensions/
    # 2. Enable "Developer mode" (toggle in top right)
    # 3. Find "Cookie-Editor" and copy the ID (looks like: hlkenndednhfkekhgcdicdfddnkalmdm)
    USE_COOKIE_EDITOR = False  # Set to True to use Cookie-Editor extension (requires CHROME_PROFILE)
    COOKIE_EDITOR_ID = None  # Example: "hlkenndednhfkekhgcdicdfddnkalmdm"

    # Regex pattern to find queue numbers on the page
    # Adjust this based on how queue numbers appear on your target website
    # Examples:
    # - "Queue: 123" -> r'queue[:\s]+(\d+)'
    # - "Position in queue: 123" -> r'position in queue[:\s]+(\d+)'
    # - "Queue #123" -> r'queue\s*#?\s*(\d+)'
    QUEUE_PATTERN = r'queue[:\s]+(\d+)'

    # Create and run queue manager
    manager = QueueManager(
        url=TARGET_URL,
        num_tabs=NUM_TABS,
        chrome_profile_path=CHROME_PROFILE
    )

    manager.run_full_cycle(
        queue_pattern=QUEUE_PATTERN,
        use_cookie_editor=USE_COOKIE_EDITOR,
        cookie_editor_id=COOKIE_EDITOR_ID
    )


if __name__ == "__main__":
    main()
