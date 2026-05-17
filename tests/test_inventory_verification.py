import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException


def get_mock_backend_inventory():
    """
    Simulates making a requests.get('https://api.mybackend.com/inventory')
    Returns the expected inventory data from the database.
    """
    return [
        {"title": "Sauce Labs Backpack", "price": "$ 29.99"},
        {"title": "Sauce Labs Bike Light", "price": "$ 9.99"},
        {"title": "Sauce Labs Bolt T-Shirt", "price": "$ 15.99"},
        {"title": "Sauce Labs Fleece Jacket", "price": "$ 49.99"},
        {"title": "Sauce Labs Onesie", "price": "$ 7.99"},
        {"title": "Test.allTheThings() T-Shirt", "price": "$ 15.99"}
    ]

def test_open_app():
    # Define connection options
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'emulator-5554'  # Usually 'emulator-5554' or just 'Android Emulator'

    # Open specific app
    options.app_package = 'com.saucelabs.mydemoapp.android'
    options.app_activity = '.view.activities.SplashActivity'

    # Prevents Appium from resetting the app's data each time you run the script
    options.no_reset = True

    # 3. Connect to the Appium server (usually running on localhost:4723)
    appium_server_url = 'http://127.0.0.1:4723'
    error_msg = None

    try:
        print("\nConnecting to Appium and launching the app...")
        # This line initializes the driver and OPENS the app on your emulator
        driver = webdriver.Remote(command_executor=appium_server_url, options=options)

        # Force the app to the foreground just in case the emulator is stuck on the home screen
        try:
            driver.activate_app('com.saucelabs.mydemoapp.android')
        except Exception:
            pass # Ignore if already running

        print("App opened successfully!")

        # --- Interacting with the App ---
        from appium.webdriver.common.appiumby import AppiumBy
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time

        TARGET_ITEM_COUNT = 20  # CONFIGURABLE

        print(f"\nScanning the front page for up to {TARGET_ITEM_COUNT} items...")

        # Wait up to 10 seconds for the first product title to appear on screen
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.saucelabs.mydemoapp.android:id/titleTV'))
        )

        print("Ensuring we are at the top of the page...")
        try:
            # Scroll to the very beginning of the list (max 5 swipes)
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                'new UiScrollable(new UiSelector().scrollable(true)).scrollToBeginning(5)')
            time.sleep(2)
        except Exception:
            pass  # We are likely already at the top

        scraped_items = []
        seen_titles = set()

        while len(scraped_items) < TARGET_ITEM_COUNT:
            # Find all item containers currently visible on the screen
            containers = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.saucelabs.mydemoapp.android:id/titleTV']/..")

            items_found_this_scroll = 0

            # Loop through visible item containers
            for container in containers:
                try:
                    title_element = container.find_element(AppiumBy.XPATH, ".//android.widget.TextView[@resource-id='com.saucelabs.mydemoapp.android:id/titleTV']")
                    title_text = title_element.text
                    
                    price_element = container.find_element(AppiumBy.XPATH, ".//android.widget.TextView[@resource-id='com.saucelabs.mydemoapp.android:id/priceTV']")
                    price_text = price_element.text
                except Exception:
                    # If we can't find the title or price, the item is cut off by the scroll boundary.
                    # We safely skip it for now; it will be fully visible after the next scroll!
                    continue

                # Safely check for the visual rating container inside this exact parent
                try:
                    rating_containers = container.find_elements(AppiumBy.XPATH, ".//android.view.ViewGroup[@resource-id='com.saucelabs.mydemoapp.android:id/rattingV']")
                    if len(rating_containers) > 0:
                        rating_status = "[Rating visual present]"
                    else:
                        rating_status = "[No rating element]"
                except Exception:
                    rating_status = "[Error reading rating element]"

                # If we haven't seen this item before, add it to our list!
                if title_text and title_text not in seen_titles:
                    seen_titles.add(title_text)
                    scraped_items.append((title_text, price_text, rating_status))
                    items_found_this_scroll += 1

                    # Stop immediately if we hit our target mid-screen
                    if len(scraped_items) >= TARGET_ITEM_COUNT:
                        break

            # If we hit our target, break out of the scrolling loop entirely
            if len(scraped_items) >= TARGET_ITEM_COUNT:
                break

            # If we didn't find any new items on this screen, we've probably hit the bottom of the app
            if items_found_this_scroll == 0:
                print("\nReached the bottom of the list. No more new items found.")
                break

            # Scroll down to reveal more items!
            print(f"  Found {len(scraped_items)} items so far. Scrolling down for more...")
            try:
                # Use native Android UIAutomator scroll for reliability
                driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                    'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()')
            except Exception:
                print("\nReached the bottom of the list. No more items to scroll to.")
                break

            time.sleep(2)  # Give the UI a moment to settle after scrolling

        # Print the final results
        print(f"\n--- Successfully Found {len(scraped_items)} Items ---")
        for idx, (title, price, rating) in enumerate(scraped_items):
            print(f"Item {idx + 1}: {title} | Price: {price} | {rating}")
        print("----------------------------------\n")

        # --- BACKEND VERIFICATION ---
        print("\n" + "=" * 60)
        print("Starting Backend Verification...")
        backend_data = get_mock_backend_inventory()
        
        # Convert backend data into a dictionary for fast lookup by title
        backend_dict = {item['title']: item['price'] for item in backend_data}
        
        verification_failures = []
        warnings = []
        verified = []
        
        for title, price, rating in scraped_items:
            # We only verify items that exist in our mock backend data for this demo
            if title in backend_dict:
                expected_price = backend_dict[title]
                if price != expected_price:
                    verification_failures.append(f"PRICE MISMATCH: '{title}'. UI says {price}, Backend says {expected_price}")
                else:
                    verified.append(f"VERIFIED: '{title}' price matches backend.")
            else:
                warnings.append(f"WARNING: '{title}' found in UI but not in our Mock Database!")
                
        # 1. Print any critical failures FIRST so they are right at the top
        if verification_failures:
            print("\n" + "!" * 60)
            print(">>> BACKEND VERIFICATION FAILED <<<")
            print("!" * 60 + "\n")
            for failure in verification_failures:
                print(failure)
            print("\n" + "!" * 60)
        else:
            print("\n[OK] Backend Verification Passed! All UI data matches the database.")
            
        # 2. Print the detailed logs below the failures
        print("\n--- Verification Details ---")
        for v in verified:
            print(v)
        for w in warnings:
            print(w)
            
        print("=" * 60 + "\n")
        # ----------------------------

        if verification_failures:
            pytest.fail("Backend verification failed due to price mismatches. See console logs above.", pytrace=False)

        time.sleep(2)

    except Exception as e:
        if not error_msg:
            import traceback
            traceback.print_exc()
            error_msg = f"Test crashed unexpectedly: {str(e)}"

    finally:
        # Always remember to quit the driver to free up resources
        if 'driver' in locals() and driver is not None:
            driver.quit()
            print("Driver closed.")

    if error_msg:
        pytest.fail(error_msg, pytrace=False)