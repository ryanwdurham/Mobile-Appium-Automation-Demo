from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time

# Launch Google Messages via adb — force it back to the conversation list
subprocess.run([
    "adb", "-s", "R3CWA06JF5H", "shell", "am", "start", "-n",
    "com.google.android.apps.messaging/.ui.ConversationListActivity"
])
time.sleep(5)  # Give it time to fully land on the conversation list

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "R3CWA06JF5H"
options.automation_name = "UiAutomator2"
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
driver.implicitly_wait(8)  # Balanced — not too slow, not too short

def wait_for(by, value, timeout=10):
    """Explicit wait for a single element — faster and more precise than implicit."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def try_find(strategies):
    """Try multiple (by, value) locator pairs and return the first match."""
    for by, value in strategies:
        try:
            el = driver.find_element(by, value)
            if el:
                return el
        except NoSuchElementException:
            continue
    raise NoSuchElementException(
        f"Could not find element with any of: {strategies}"
    )

try:
    # ── Tap compose / start chat button ──────────────────────────────────────
    print("📱 Google Messages opened")
    # Find the compose button — works whether we're on the list or a conversation
    compose = try_find([
        (AppiumBy.XPATH, '//*[@content-desc="Start chat"]'),
        (AppiumBy.XPATH, '//*[@content-desc="Compose"]'),
        (AppiumBy.XPATH, '//*[@content-desc="New conversation"]'),
        (AppiumBy.ANDROID_UIAUTOMATOR,
         'new UiSelector().descriptionContains("chat")'),
        (AppiumBy.ANDROID_UIAUTOMATOR,
         'new UiSelector().descriptionContains("Compose")'),
    ])
    compose.click()
    time.sleep(2)

    # ── Type phone number ─────────────────────────────────────────────────────
    to_field = driver.find_element(AppiumBy.XPATH,
        '//*[@resource-id="ContactSearchField"]'
    )
    to_field.click()
    to_field.send_keys("4252708480")
    print("📞 Phone number entered: 4252708480")
    time.sleep(2)

    # Press Enter to confirm number
    driver.press_keycode(66)
    time.sleep(2)

    # ── Type the message ──────────────────────────────────────────────────────
    msg_field = driver.find_element(AppiumBy.XPATH,
        '//*[@resource-id="com.google.android.apps.messaging:id/compose_message_text"]'
    )
    msg_field.click()
    msg_field.send_keys("Hello World! This is a automated text message!")
    print("✏️  Message text entered")
    time.sleep(1)

    # ── Tap the attach button ─────────────────────────────────────────────────
    # Try several locators — use whichever one works on your device
    attach_btn = try_find([
        # Most reliable: content-desc from your inspector
        (AppiumBy.XPATH, '//*[@content-desc="Show attach content screen"]'),
        # UiAutomator selector from inspector (instance 16)
        (AppiumBy.ANDROID_UIAUTOMATOR,
         'new UiSelector().className("android.view.View").instance(16)'),
        # XPath from inspector
        (AppiumBy.XPATH,
         '//android.view.View[@resource-id="ComposeRowIcon:Shortcuts"]/android.view.View[2]'),
    ])
    attach_btn.click()
    print("📎 Attach screen opened")
    time.sleep(2)

    # ── Tap "Gallery" ─────────────────────────────────────────────────────────
    gallery_btn = try_find([
        # Text label is the safest pick
        (AppiumBy.XPATH, '//android.widget.TextView[@text="Gallery"]'),
        # resource-id on the TextView
        (AppiumBy.XPATH,
         '//*[@resource-id="com.google.android.apps.messaging:id/shortcut_title" and @text="Gallery"]'),
        # resource-id on the icon above it
        (AppiumBy.XPATH,
         '//*[@resource-id="com.google.android.apps.messaging:id/shortcut_icon"]'),
    ])
    gallery_btn.click()
    print("🖼️  Gallery opened")
    time.sleep(4)

    # ── Select dolls.jpg ──────────────────────────────────────────────────────
    # dolls.jpg = index [8] in the content-desc list (3rd photo, after a video).
    photo = driver.find_elements(AppiumBy.XPATH,
        '//*[starts-with(@content-desc, "Photo taken on") or '
        'starts-with(@content-desc, "Video taken on")]'
    )[2]  # index 2 = 3rd media item = dolls.jpg (Apr 27 photo)
    # Elements are clickable=false in the tree but respond to tap via location
    loc = photo.location
    size = photo.size
    cx = loc['x'] + size['width'] // 2
    cy = loc['y'] + size['height'] // 2
    driver.tap([(cx, cy)])
    print(f"✅ Tapped dolls.jpg at ({cx}, {cy})")
    time.sleep(3)

    # ── Tap "Done" / confirm button ───────────────────────────────────────────
    # The confirm button is typically one of the last clickable elements.
    clickable = driver.find_elements(AppiumBy.XPATH, '//*[@clickable="true"]')
    tapped_done = False
    for idx in [-1, -2, -3, -4]:
        try:
            btn = clickable[idx]
            loc = btn.location
            size = btn.size
            cx = loc['x'] + size['width'] // 2
            cy = loc['y'] + size['height'] // 2
            # Done button should be in the bottom portion of the screen
            if cy > 1500:
                driver.tap([(cx, cy)])
                print(f"✅ Tapped Done candidate at ({cx}, {cy}) [index {idx}]")
                tapped_done = True
                break
        except Exception:
            continue
    if not tapped_done:
        # Fallback: tap known bottom-left area where Done typically lives
        print("⚠️  Falling back to coordinate tap for Done button")
        driver.tap([(894, 1991)])
    time.sleep(2)

    print("✅ Image attached")
    time.sleep(2)

    # ── Tap Send ──────────────────────────────────────────────────────────────
    # Inspector shows: android.view.View[@resource-id="Compose:Draft:Send"]
    #                    └─ android.view.View[@content-desc="Send MMS"]
    send = try_find([
        # Most precise: child view with content-desc under the Send container
        (AppiumBy.XPATH,
         '//android.view.View[@resource-id="Compose:Draft:Send"]'
         '/android.view.View[@content-desc="Send MMS"]'),
        # Slightly broader: any view with content-desc Send MMS anywhere
        (AppiumBy.XPATH, '//android.view.View[@content-desc="Send MMS"]'),
        # Fallback for SMS (no attachment case)
        (AppiumBy.XPATH, '//android.view.View[@content-desc="Send SMS"]'),
    ])
    send.click()
    print("✅ Message sent!")
    time.sleep(3)

finally:
    driver.quit()