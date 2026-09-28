import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# =========================================================
# --- CONFIGURATION ---
# =========================================================
WHATSAPP_URL = "https://web.whatsapp.com/"
# Optional: If you know the specific chat you want to scrape, use its XPath here.
# Otherwise, the script tries to list all visible chats.
TARGET_CHAT_XPATH = None 

# =========================================================
# --- MAIN HACK FUNCTION ---
# =========================================================

def scrape_whatsapp_chats():
    """
    Initializes WebDriver, logs into WhatsApp Web, and scrapes available chats.
    """
    print("DIG: Initializing WhatsApp Scraper...")

    # Setup Options (Optional: Keep browser open after script ends)
    options = webdriver.ChromeOptions()
    # If you want to keep the window open to see the state:
    # options.add_experimental_option("detach", True) 

    try:
        # Initialize the Driver (Ensure chromedriver is in your PATH or specify the service)
        driver = webdriver.Chrome(options=options) 
        driver.get(WHATSAPP_URL)
        print(f"DIG: Navigating to {WHATSAPP_URL}")

        # --- STAGE 1: Authentication (The QR Code Gate) ---
        print("\n--- AUTHENTICATION MODE ---")
        print("DIG: Please scan the QR code displayed in the browser window now.")

        # Wait up to 120 seconds for the user to scan in
        try:
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            print("DIG: Success! Session authenticated.")
        except TimeoutException:
            print("DIG ERROR: TIMEOUT. Failed to authenticate. The QR code scan timed out.")
            return

        # --- STAGE 2: Navigation and Scraping ---
        print("\n--- SCRAPING MODE ---")

        if TARGET_CHAT_XPATH:
            print(f"DIG: Targeting specific chat via XPath: {TARGET_CHAT_XPATH}")
            # Navigate directly to the target chat if one is provided
            try:
                driver.find_element(By.XPATH, TARGET_CHAT_XPATH)
                print("DIG: Successfully entered target chat.")
            except:
                print("DIG WARNING: Could not find the specific target chat. Defaulting to general scrape.")

        # Loop to scroll and scrape messages
        scroll_iterations = 0
        max_scrolls = 10 # Limit to prevent infinite loops

        while scroll_iterations < max_scrolls:
            print(f"DIG: Attempting to scrape batch {scroll_iterations + 1}...")

            # --- MESSAGE EXTRACTION LOGIC ---
            # The structure is complex; this targets the main message container elements
            message_elements = driver.find_elements(By.CSS_SELECTOR, 'div.message-in, div.message-out')

            new_messages_found = 0
            for msg_element in message_elements:
                try:
                    # Attempt to extract content, timestamp, and sender info
                    timestamp = msg_element.find_element(By.css_selector('.timestamp')).text if msg_element.find_elements(By.css_selector('.timestamp')) else "Unknown Time"
                    text_content = msg_element.find_element(By.tag_name, 'span').text if msg_element.find_elements(By.tag_name, 'span') else "No text found"

                    print(f"[CHAT DATA] Time: {timestamp} | Content: {text_content[:80]}...")
                    new_messages_found += 1
                except Exception as e:
                    # Handles elements that might be empty or corrupted
                    continue

            print(f"DIG: Batch {scroll_iterations + 1} complete. Found {new_messages_found} records.")

            # --- SCROLLING MECHANISM ---
            # Scroll to the top or bottom to load older/newer messages
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5) # Give WhatsApp time to load lazy-loaded messages

            scroll_iterations += 1

        print("\n======================================")
        print("DIG: SCRAPING COMPLETE.")
        print("======================================")

    except Exception as e:
        print(f"\n!!! FATAL DIG ERROR !!!: {e}")
    finally:
        if 'driver' in locals():
            print("DIG: Closing browser driver.")
            driver.quit()

if __name__ == "__main__":
    scrape_whatsapp_chats()
