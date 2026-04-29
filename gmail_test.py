from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import time

DEVICE_ID = "R3CWA06JF5H"
WAIT = 5

def find(driver, by, value, timeout=WAIT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        raise Exception(f"Could not find element: {value}")

def dismiss_popups(driver):
    popup_texts = ["Got it", "OK", "Skip", "Not now", "No thanks", "Close", "Later", "Allow"]

    buttons = driver.find_elements(AppiumBy.XPATH, "//*[@text]")  # grab ALL text elements once

    for btn in buttons:
        try:
            text = btn.text
            if text in popup_texts and btn.is_displayed():
                btn.click()
                print(f"  Dismissed: '{text}'")
        except:
            pass

# Launch Gmail
print("Launching Gmail...")
subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "force-stop", "com.google.android.gm"])
time.sleep(1)
subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "start", "com.google.android.gm"])
time.sleep(1)

# Connect to Appium
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = DEVICE_ID
options.automation_name = "UiAutomator2"
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

try:
    # Dismiss popups quickly
    print("Checking for popups...")
    dismiss_popups(driver)

    # Click Compose button
    print("Clicking Compose...")
    compose = find(driver, AppiumBy.XPATH,
        '//*[@content-desc="Compose" or @resource-id="com.google.android.gm:id/compose_button"]')
    compose.click()
    time.sleep(1)

    # Enter To address - find EditText inside the chip group
    print("Entering To address...")
    to_field = find(driver, AppiumBy.XPATH,
        '//*[@resource-id="com.google.android.gm:id/peoplekit_autocomplete_chip_group"]'
        '//android.widget.EditText')
    to_field.click()
    to_field.send_keys("ryanwdurham@yahoo.com")
    driver.press_keycode(66)  # Enter to confirm address
    time.sleep(1)

    # Enter Subject
    print("Entering Subject...")
    subject = find(driver, AppiumBy.XPATH,
        '//*[@resource-id="com.google.android.gm:id/subject" or @hint="Subject"]')
    subject.click()
    subject.send_keys("Automation Test Email")
    time.sleep(1)

    # Enter email body
    print("Entering email body...")

    tap_area = find(driver, AppiumBy.ID,
        "com.google.android.gm:id/composearea_tap_trap_bottom")
    tap_area.click()

    time.sleep(1)

    edit_texts = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")

    body = edit_texts[-1]  # Gmail usually puts body last
    body.click()
    body.send_keys("This is a automation test email\n\nI hope you are having a great day!")

    time.sleep(1)


    # Click Send
    print("Sending email...")
    send = find(driver, AppiumBy.XPATH,
        '//*[@content-desc="Send" or @resource-id="com.google.android.gm:id/send"]')
    send.click()
    print("Email sent!")
    time.sleep(3)

    print("\nAll steps completed successfully!")

except Exception as e:
    print(f"\nError: {e}")

finally:
    print("\nClosing Gmail...")
    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "force-stop", "com.google.android.gm"])
    driver.quit()
    print("Done!")