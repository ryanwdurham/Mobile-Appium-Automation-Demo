#!/usr/bin/env python3
"""
Google Maps Automation — Samsung Android 16 (Demo Version)
===========================================================
Fast, clean, demo-ready. Target runtime: ~60 seconds.

Flow:
  Home screen -> App drawer -> Maps -> Search "Rattlesnake Ridge"
  -> Directions -> Scroll turn-by-turn -> Start

Prerequisites:
  pip install Appium-Python-Client
  npm install -g appium
  appium driver install uiautomator2
  adb devices      <- phone must be listed
  appium           <- run in a separate terminal first
"""

import time
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---- CONFIG ------------------------------------------------------------------
DESTINATION   = "Rattlesnake Ridge"
APPIUM_SERVER = "http://127.0.0.1:4723"
# ------------------------------------------------------------------------------


def build_driver():
    opts = UiAutomator2Options()
    opts.platform_name          = "Android"
    opts.automation_name        = "UiAutomator2"
    opts.no_reset               = True
    opts.auto_grant_permissions = True
    opts.new_command_timeout    = 120
    return webdriver.Remote(APPIUM_SERVER, options=opts)


def adb_type(text: str):
    """Type via ADB — bypasses Appium send_keys, works 100% of the time."""
    escaped = text.replace(" ", "%s")
    subprocess.run(f'adb shell input text "{escaped}"', shell=True)


def wait_tap(driver, xpath, timeout=10):
    """Wait for element then tap it. Returns True on success, False on timeout."""
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
        )
        el.click()
        return True
    except TimeoutException:
        return False


def tap_first(driver, xpaths, timeout=8):
    """Try each xpath in order, tap the first one found."""
    for xpath in xpaths:
        if wait_tap(driver, xpath, timeout=timeout):
            return True
    return False


def scroll_down(driver, swipes=4, duration_ms=600):
    """Scroll down through the directions list."""
    size = driver.get_window_size()
    x    = size["width"]  // 2
    top  = int(size["height"] * 0.25)
    bot  = int(size["height"] * 0.75)
    for _ in range(swipes):
        driver.swipe(x, bot, x, top, duration=duration_ms)
        time.sleep(0.4)


# ==============================================================================
def run():
    print("Starting Google Maps demo...\n")
    driver = build_driver()

    try:
        # STEP 1: Home screen
        print("  [1] Going to home screen...")
        driver.press_keycode(3)
        time.sleep(1.5)

        # STEP 2: Open app drawer
        print("  [2] Opening app drawer...")
        size = driver.get_window_size()
        driver.swipe(size["width"] // 2, int(size["height"] * 0.80),
                     size["width"] // 2, int(size["height"] * 0.20), duration=300)
        time.sleep(1.2)

        # STEP 3: Tap Maps
        print("  [3] Opening Maps...")
        found = tap_first(driver, [
            '//*[@content-desc="Maps" and @resource-id="com.sec.android.app.launcher:id/icon"]',
            '//*[@content-desc="Maps"]',
        ], timeout=6)
        if not found:
            raise RuntimeError("Maps icon not found!")

        # Wait for Maps to load — watch for the search bar to appear
        print("      Waiting for Maps to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="Search here"]'
            ))
        )
        time.sleep(0.5)

        # STEP 4: Tap search bar
        print("  [4] Tapping search bar...")
        tap_first(driver, [
            '//android.widget.TextView[@text="Search here"]',
            '//*[@resource-id="com.google.android.apps.maps:id/search_omnibox_text_box"]',
        ])
        time.sleep(1.2)

        # STEP 5: Focus the EditText
        print("  [5] Focusing input...")
        try:
            WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((
                    AppiumBy.ID,
                    "com.google.android.apps.maps:id/search_omnibox_edit_text"
                ))
            ).click()
        except TimeoutException:
            pass
        time.sleep(0.5)

        # STEP 6: Type destination via ADB
        print(f"  [6] Typing '{DESTINATION}'...")
        adb_type(DESTINATION)
        time.sleep(2.5)  # let autocomplete load

        # STEP 7: Tap suggestion or press Enter
        print("  [7] Submitting search...")
        found = tap_first(driver, [
            f'//android.widget.TextView[contains(@text,"Rattlesnake")]',
            '//android.widget.TextView[contains(@resource-id,"search_list_child_text_line_1")]',
            '//android.widget.TextView[contains(@resource-id,"primary_text")]',
            '//android.widget.TextView[contains(@resource-id,"line_1")]',
        ], timeout=3)
        if not found:
            driver.press_keycode(66)  # Enter
        time.sleep(3)  # map loads with pin

        # STEP 8: Tap Directions
        print("  [8] Tapping Directions...")
        tap_first(driver, [
            '//*[@content-desc="Directions"]',
            '//*[@text="Directions"]',
            '//*[contains(@resource-id,"directions_fab")]',
        ])
        time.sleep(2.5)

        # STEP 9: Scroll turn-by-turn directions
        print("  [9] Scrolling directions...")
        scroll_down(driver, swipes=4, duration_ms=600)
        time.sleep(0.5)

        # STEP 10: Tap Start
        print("  [10] Tapping Start...")
        tap_first(driver, [
            '//*[@content-desc="Start"]',
            '//*[@text="Start"]',
            '//*[@text="START"]',
            '//*[contains(@resource-id,"start_button")]',
        ])
        time.sleep(3)  # let navigation screen fully load

        # STEP 11: Tap the 2-arrow overview icon — single tap, bottom-right
        print("  [11] Tapping 2-arrow overview icon (bottom-right)...")
        driver.tap([(990, 1980)])
        time.sleep(5)  # hold result on screen for 5 seconds

        # STEP 12: Force-close Maps completely via ADB
        print("  [12] Force-closing Maps...")
        subprocess.run("adb shell am force-stop com.google.android.apps.maps", shell=True)

        print("\nDone! Demo complete.")

    except Exception as e:
        print(f"\nFailed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("Session closed.")


if __name__ == "__main__":
    run()