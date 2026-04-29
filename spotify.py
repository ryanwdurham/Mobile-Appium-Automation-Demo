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

def dismiss_popups(driver):
    for text in ["Got it", "OK", "Not now", "No thanks", "Close", "Later"]:
        try:
            btn = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((AppiumBy.XPATH, f'//*[@text="{text}"]'))
            )
            btn.click()
            print(f"  Dismissed: '{text}'")
            time.sleep(1)
        except:
            pass

# Launch Spotify
print("Launching Spotify...")
subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "force-stop", "com.spotify.music"])
time.sleep(1)
subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "start", "com.spotify.music"])
time.sleep(5)

# Connect to Appium
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = DEVICE_ID
options.automation_name = "UiAutomator2"
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

try:
    # Dismiss popups
    print("Checking for popups...")
    dismiss_popups(driver)

    # Click Search tab at bottom nav
    print("Opening Search tab...")
    search_tab = find(driver, AppiumBy.ACCESSIBILITY_ID, "Search, Tab 2 of 4")
    search_tab.click()
    time.sleep(2)

    # Tap the search input field by coordinates (bounds [159,325][788,387])
    print("Tapping search input field...")
    driver.tap([(473, 356)])
    time.sleep(2)

    # Type song name into the EditText that appears
    print("Typing 'voodoo child'...")
    search_input = find(driver, AppiumBy.XPATH, '//android.widget.EditText')
    search_input.send_keys("voodoo child")
    time.sleep(1)
    driver.press_keycode(66)
    print("Searching...")
    time.sleep(3)

    # Click the song Voodoo Child (Slight Return)
    print("Clicking Voodoo Child (Slight Return)...")
    song = find(driver, AppiumBy.XPATH,
        '//*[contains(@text, "Voodoo Child") or contains(@content-desc, "Voodoo Child")]')
    song.click()
    print("Song clicked!")
    time.sleep(4)

    # Verify song is playing
    print("Verifying song is playing...")
    try:
        find(driver, AppiumBy.XPATH,
            '//*[contains(@content-desc, "Pause")]', timeout=8)
        print("VERIFIED: Song is playing!")
    except:
        print("WARNING: Could not verify playing state")

    print("\nAll steps completed successfully!")
    time.sleep(5)

except Exception as e:
    print(f"\nError: {e}")

finally:
    print("\nClosing Spotify...")
    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "am", "force-stop", "com.spotify.music"])
    driver.quit()
    print("Done!")