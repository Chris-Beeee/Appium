#verification that the emulator is working, and all essential dependencies are installed and configured correctly

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

@pytest.fixture(scope="function")
def driver():
    # 1. Define the desired capabilities
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    
    # You will need to replace this with your actual device or emulator name.
    # You can find this by running 'adb devices' in your terminal.
    options.device_name = 'emulator-5554' 
    
    # We are using the built-in Android Settings app for this initial test
    # so that you don't need a specific APK just to verify setup.
    options.app_package = 'com.android.settings'
    options.app_activity = '.Settings'
    
    # 2. Initialize the Appium driver (pointing to your local Appium server)
    # Ensure your Appium server is running in another terminal before executing this!
    # (Command: `appium`)
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
    
    # 3. Provide the driver to the test
    yield driver
    
    # 4. Clean up and close the session after the test finishes
    driver.quit()

def test_open_settings_app(driver):
    # This test simply launches the settings app and verifies the package name is correct.
    assert driver.current_package == 'com.android.settings'
    print("Settings app opened successfully!")
