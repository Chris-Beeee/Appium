import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="function")
def driver():
    """
    Setup the Appium Android driver using the built-in Android Settings app.
    This provides a universally available app for these examples without needing a custom APK.
    """
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'emulator-5554' 
    options.app_package = 'com.android.settings'
    options.app_activity = '.Settings'
    
    # Initialize the Appium driver (Requires Appium server running locally)
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
    
    yield driver
    
    # Clean up and close the session after the test finishes
    driver.quit()


def test_find_and_click_element(driver):
    """
    Example 1: Locating an element by XPath and interacting with it.
    This test finds the 'Network & internet' setting and clicks it.
    """
    # Wait up to 10 seconds for the element to be present before interacting.
    # This is crucial for mobile testing as apps can be slow to render.
    wait = WebDriverWait(driver, 10)
    
    # Find the element using an XPath that looks for text on the screen
    network_element = wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='Network & internet']"))
    )
    
    # Click the located element
    network_element.click()
    
    # Verify we moved to a new screen by checking if a related element is now present (e.g., Internet)
    wifi_element = wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='Internet']"))
    )
    assert wifi_element.is_displayed()


def test_element_interactions(driver):
    """
    Example 2: Locating an element by ID, typing text, and clearing text.
    We will use the search bar at the top of the Settings app.
    """
    wait = WebDriverWait(driver, 10)
    
    # Many apps use Accessibility IDs (Content Description in Android). 
    # In the Settings app, the search bar icon is accessible by Accessibility ID.
    search_icon = wait.until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Search settings"))
    )
    search_icon.click()
    
    # Now we find the actual text input field by its native resource ID
    search_src_text = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "com.android.settings:id/search_src_text"))
    )
    
    # Type into the search field
    search_src_text.send_keys("Display")
    
    # Verify the text was successfully typed
    assert search_src_text.text == "Display"
    
    # Clear the text
    search_src_text.clear()
    assert search_src_text.text != "Display"


def test_scroll_gesture(driver):
    """
    Example 3: Performing a scroll gesture using Android UiAutomator.
    Mobile screens are small, so finding elements often requires scrolling.
    """
    # We use UIAutomator's built-in scrollable property to find a scrollable view and scroll 
    # forward until we find an element containing the text "About".
    # This is a very powerful, Android-specific locater strategy.
    
    try:
        about_element = driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("About"))'
        )
        assert about_element.is_displayed()
        about_element.click()
    except Exception as e:
        pytest.fail(f"Could not scroll to or find the About section: {e}")


def test_take_screenshot(driver, tmp_path):
    """
    Example 4: Taking a screenshot during a test.
    This is extremely useful for debugging failures. You would typically do this inside
    a pytest hook when a test fails, but you can also do it manually at any time.
    """
    # Create a temporary path for the screenshot
    screenshot_file = tmp_path / "settings_screen.png"
    
    # Save a screenshot of the current screen to the file path
    driver.save_screenshot(str(screenshot_file))
    
    # Verify the file was created and isn't empty
    assert screenshot_file.exists()
    assert screenshot_file.stat().st_size > 0
