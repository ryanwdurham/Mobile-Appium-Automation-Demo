from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import time

DEVICE_ID = "R3CWA06JF5H"
WAIT = 15

def find(driver, by, value, timeout=WAIT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        raise Exception(f"Could not find element: {value}")

def get_toggle_state(driver, label):
    """Returns True if toggle is ON, False if OFF"""
    try:
        toggle = find(driver, AppiumBy.XPATH,
            f'//*[@text="{label}"]/following-sibling::android.widget.Switch '
            f'| //android.widget.Switch[@content-desc="{label}"]')
        return toggle.get_attribute("checked") == "true"
    except:
        return None

def tap_toggle(driver, label):
    """Tap a toggle switch by its label text"""
    toggle = find(driver, AppiumBy.XPATH,
        f'//*[@text="{label}"]/following-sibling::android.widget.Switch '
        f'| //*[@text="{label}"]/..//android.widget.Switch '
        f'| //android.widget.Switch[@content-desc="{label}"]')
    toggle.click()
    time.sleep(2)

# Launch Settings
print("Launching Settings...")
subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "force-stop", "com.android.settings"])
time.sleep(1)
subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "start", "-n",
    "com.android.settings/.Settings"])
time.sleep(3)

# Connect to Appium
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = DEVICE_ID
options.automation_name = "UiAutomator2"
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

try:
    # Click Connections
    print("Clicking Connections...")
    connections = find(driver, AppiumBy.XPATH,
        '//*[@text="Connections"]')
    connections.click()
    time.sleep(2)

    # ── Airplane Mode ─────────────────────────────────────────────────────────
    print("\n--- Airplane Mode ---")
    print("Turning Airplane Mode ON...")
    tap_toggle(driver, "Airplane mode")
    print("Airplane Mode is ON!")
    time.sleep(2)

    print("Turning Airplane Mode OFF...")
    tap_toggle(driver, "Airplane mode")
    print("Airplane Mode is OFF!")
    time.sleep(2)

    # ── Wi-Fi ─────────────────────────────────────────────────────────────────
    print("\n--- Wi-Fi ---")
    print("Turning Wi-Fi OFF...")
    tap_toggle(driver, "Wi-Fi")
    print("Wi-Fi is OFF!")
    time.sleep(2)

    print("Turning Wi-Fi ON...")
    tap_toggle(driver, "Wi-Fi")
    print("Wi-Fi is ON!")
    time.sleep(2)

    # ── Bluetooth ─────────────────────────────────────────────────────────────
    print("\n--- Bluetooth ---")
    print("Turning Bluetooth OFF...")
    tap_toggle(driver, "Bluetooth")
    print("Bluetooth is OFF!")
    time.sleep(2)

    print("Turning Bluetooth ON...")
    tap_toggle(driver, "Bluetooth")
    print("Bluetooth is ON!")
    time.sleep(2)

    print("\nAll steps completed successfully!")

except Exception as e:
    print(f"\nError: {e}")

finally:
    print("\nClosing Settings...")
    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "force-stop", "com.android.settings"])
    driver.quit()
    print("Done!")