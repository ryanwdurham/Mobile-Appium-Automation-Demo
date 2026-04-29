from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import subprocess
import time

# Launch Google Messages via adb
subprocess.run([
    "adb", "-s", "R3CWA06JF5H", "shell", "am", "start", "-n",
    "com.google.android.apps.messaging/.ui.ConversationListActivity"
])
time.sleep(3)

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "R3CWA06JF5H"
options.automation_name = "UiAutomator2"
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
driver.implicitly_wait(15)

try:
    # Tap compose/start chat button
    compose = driver.find_element(AppiumBy.XPATH,
        '//*[@content-desc="Start chat" or @content-desc="Compose"]'
    )
    compose.click()
    time.sleep(2)

    # Type phone number into ContactSearchField (exact ID from your UI dump)
    to_field = driver.find_element(AppiumBy.XPATH,
        '//*[@resource-id="ContactSearchField"]'
    )
    to_field.click()
    to_field.send_keys("4252708480")
    time.sleep(2)

    # Press Enter to confirm number
    driver.press_keycode(66)
    time.sleep(2)

    # Type the message
    msg_field = driver.find_element(AppiumBy.XPATH,
        '//*[@resource-id="com.google.android.apps.messaging:id/compose_message_text"]'
    )
    msg_field.click()
    msg_field.send_keys("Hello World!")
    time.sleep(1)

    # Tap Send
    send = driver.find_element(AppiumBy.XPATH,
        '//*[@content-desc="Send SMS" or @content-desc="Send message"]'
    )
    send.click()

    print("✅ Message sent!")
    time.sleep(3)

finally:
    driver.quit()