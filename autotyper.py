import keyboard
import pyautogui
import cv2
import pytesseract
import time
import os
import win32gui
import win32con
import numpy as np

# Calculate the region for top-middle of 1920x1200 display
# Assuming captions are roughly 400px wide and 70px tall
SCREEN_X = 760  # (1920 - 400) / 2
SCREEN_Y = 50  # Reasonable caption position from top
SCREEN_W = 400  # Width of caption area
SCREEN_H = 70  # Height of caption area

# Typing speed (WPM)
TYPING_SPEED = 875

# Add global variable for last detected word
latest_word = None


def type_word(word):
    char_delay = 60 / (TYPING_SPEED * 5)  # 5 characters per word average
    pyautogui.write(str(word), interval=char_delay)


def set_window_on_top():
    # Get console window handle and set it to be always on top
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )


def on_right_ctrl_press(event):
    global latest_word
    print("Right CTRL pressed - Processing...")
    try:
        # Create directory if it doesn't exist
        save_dir = r"D:\SpellingGameMacroPictures"
        os.makedirs(save_dir, exist_ok=True)
        image_path = os.path.join(save_dir, "caption.png")

        # Take screenshot with higher resolution (scaled up 2x)
        scale = 2  # Scale factor for higher resolution
        screenshot = pyautogui.screenshot(
            region=(SCREEN_X, SCREEN_Y, SCREEN_W, SCREEN_H)
        )

        # Convert to OpenCV format
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Increase resolution while maintaining aspect ratio
        height, width = img.shape[:2]
        img_high_res = cv2.resize(
            img, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC
        )

        # Apply image processing to enhance text
        gray = cv2.cvtColor(img_high_res, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save the processed image for debugging
        cv2.imwrite(image_path, thresh)

        # Configure Tesseract to detect words with their positions
        custom_config = r"--oem 3 --psm 6"
        pytesseract.pytesseract.tesseract_cmd = (
            r"%localappdata%\Programs\Tesseract-OCR\tesseract.exe"
        )

        # Get all words with their positions
        data = pytesseract.image_to_data(
            thresh, config=custom_config, output_type=pytesseract.Output.DICT
        )

        # Debug: Print all detected text and their positions
        print("\n--- DEBUG: Detected Text ---")
        for i in range(len(data["text"])):
            word = data["text"][i].strip()
            if word:  # Only print non-empty detections
                conf = int(data["conf"][i])
                x, y, w, h = (
                    data["left"][i],
                    data["top"][i],
                    data["width"][i],
                    data["height"][i],
                )
                print(
                    f"Text: '{word}'",
                    f"Confidence: {conf}%",
                    f"Position: ({x}, {y}, {w}, {h})",
                )

        # Find the rightmost word
        rightmost_word = None
        max_right = -1

        for i in range(len(data["text"])):
            word = data["text"][i].strip()
            conf = int(data["conf"][i])
            if word and conf > 30:  # Lowered confidence threshold to 30%
                x = int(data["left"][i]) + int(
                    data["width"][i]
                )  # Right edge of the word
                print(f"Considering word: '{word}' at x={x}, confidence={conf}%")
                if x > max_right:
                    max_right = x
                    rightmost_word = word

        if rightmost_word:
            # Clean the word (be less aggressive with cleaning)
            clean_word = "".join(c for c in rightmost_word if c.isalnum() or c in "'-")
            if clean_word and len(clean_word) > 1:  # Require at least 2 characters
                type_word(clean_word)
                print(f"\nSUCCESSFUL: '{clean_word}' typed on keyboard.")
            else:
                print(
                    f"\nERROR: Word '{rightmost_word}' became invalid after cleaning: '{clean_word}'"
                )
        else:
            print("\nERROR: No words detected in caption.")

        # Save the image with bounding boxes for debugging
        debug_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        for i in range(len(data["text"])):
            if int(data["conf"][i]) > 30:  # Only draw high confidence boxes
                x, y, w, h = (
                    data["left"][i],
                    data["top"][i],
                    data["width"][i],
                    data["height"][i],
                )
                cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        debug_path = os.path.join(
            os.path.dirname(image_path), "debug_" + os.path.basename(image_path)
        )
        cv2.imwrite(debug_path, debug_img)
        print(f"Debug image saved to: {debug_path}")

    except Exception as e:
        print(f"ERROR: {str(e)}")

    print("\nPress Right CTRL to type again...")


# Setup keyboard hooks
keyboard.on_press_key("right ctrl", on_right_ctrl_press, suppress=True)
keyboard.on_press_key("esc", lambda e: exit(0), suppress=True)

# Set console window always on top
set_window_on_top()

print("Press 'Right CTRL' to capture and type, 'ESC' to exit")
print("Waiting for Right CTRL input to start...")
keyboard.wait("esc")
