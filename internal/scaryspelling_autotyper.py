import os
# Set Qt environment variables before any other imports
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "Round"

import keyboard
import pyautogui
import cv2
import pytesseract
import time
import win32gui
import win32con
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import webbrowser
from tkinter import font as tkfont

# Global theme variables
THEME = {
    'bg': '#f0f0f0',
    'fg': '#000000',
    'button_bg': '#e0e0e0',
    'button_fg': '#000000',
    'highlight': '#0078d7',
    'window_bg': '#ffffff',
    'text': '#000000',
    'name': 'light'  # 'light' or 'dark'
}

# Caption area coordinates
# Top-left corner: (556, 12)
# Bottom-right corner: (1182, 71)
SCREEN_X = 556  # X coordinate of top-left corner
SCREEN_Y = 12   # Y coordinate of top-left corner
SCREEN_W = 626  # Width (1182 - 556)
SCREEN_H = 59   # Height (71 - 12)

# Global variable for typing speed
TYPING_SPEED = 1200

# Add global variable for last detected word
latest_word = None

def type_word(word, wpm=None):
    if wpm is None:
        wpm = TYPING_SPEED
    char_delay = 60 / (wpm * 5)  # 5 characters per word average
    pyautogui.write(str(word), interval=char_delay)

def set_window_on_top():
    # Get console window handle and set it to be always on top
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def on_insert_key_press(event):
    global latest_word
    print("\n--- Insert key pressed - Starting capture process ---")
    try:
        # Create directory if it doesn't exist
        save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "spelling bee pics")
        print(f"Attempting to create/access directory: {save_dir}")
        try:
            os.makedirs(save_dir, exist_ok=True)
            print(f"Directory exists/created: {os.path.exists(save_dir)}")
        except Exception as e:
            print(f"ERROR creating directory: {e}")
            return
            
        image_path = os.path.join(save_dir, "caption.png")
        print(f"Will save screenshot to: {image_path}")
        print(f"Screen capture area: X={SCREEN_X}, Y={SCREEN_Y}, W={SCREEN_W}, H={SCREEN_H}")

        # Take screenshot with higher resolution (scaled up 2x)
        scale = 2  # Scale factor for higher resolution
        print("Attempting to take screenshot...")
        try:
            screenshot = pyautogui.screenshot(region=(SCREEN_X, SCREEN_Y, SCREEN_W, SCREEN_H))
            print("Screenshot captured successfully")
        except Exception as e:
            print(f"ERROR taking screenshot: {e}")
            print("This might be due to invalid screen coordinates or display scaling issues.")
            print("Please check if the coordinates match your screen resolution.")
            return
        
        # Convert to OpenCV format
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Increase resolution while maintaining aspect ratio
        height, width = img.shape[:2]
        img_high_res = cv2.resize(img, (width * scale, height * scale), 
                                interpolation=cv2.INTER_CUBIC)
        
        # Apply image processing to enhance text
        gray = cv2.cvtColor(img_high_res, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Save the processed image for debugging
        print("Attempting to save processed image...")
        try:
            success = cv2.imwrite(image_path, thresh)
            if success:
                print(f"Successfully saved processed image to: {image_path}")
                print(f"File exists: {os.path.exists(image_path)}")
                print(f"File size: {os.path.getsize(image_path) if os.path.exists(image_path) else 0} bytes")
            else:
                print("ERROR: Failed to save processed image (cv2.imwrite returned False)")
        except Exception as e:
            print(f"ERROR saving processed image: {e}")
            import traceback
            traceback.print_exc()
        
        # Configure Tesseract to detect words with their positions
        custom_config = r'--oem 3 --psm 6'
        
        # Try to find Tesseract in the following order:
        # 1. Check the Python config file created by the installer
        # 2. Check the text config file
        # 3. Check common installation paths
        # 4. Check if it's in the system PATH
        
        tesseract_paths = []
        
        # Get the application directory (one level up from the internal directory)
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 1. Check Python config file created by the installer
        config_py_path = os.path.join(app_dir, 'tesseract_config.py')
        if os.path.isfile(config_py_path):
            try:
                # Import the config file from the application directory
                import sys
                sys.path.insert(0, app_dir)
                import tesseract_config
                
                # Use the configuration from the imported module
                pytesseract.pytesseract.tesseract_cmd = tesseract_config.TESSERACT_CMD
                if hasattr(tesseract_config, 'TESSDATA_PREFIX'):
                    os.environ['TESSDATA_PREFIX'] = tesseract_config.TESSDATA_PREFIX
                
                # Test if it works by getting version
                version = pytesseract.get_tesseract_version()
                print(f"Using Tesseract from config: {tesseract_config.TESSERACT_CMD} (v{version})")
                return  # Successfully configured Tesseract
                
            except Exception as e:
                print(f"Warning: Could not load Tesseract config: {e}")
        
        # 2. Check text config file
        config_path = os.path.join(app_dir, 'tesseract_path.txt')
        if os.path.isfile(config_path):
            try:
                with open(config_path, 'r') as f:
                    custom_path = f.read().strip()
                    if os.path.isfile(custom_path):
                        tesseract_paths.append(custom_path)
                        print(f"Found Tesseract path in config: {custom_path}")
            except Exception as e:
                print(f"Warning: Could not read Tesseract path from config: {e}")
        
        # 3. Add common installation paths
        tesseract_paths.extend([
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local')), 'Programs', 'Tesseract-OCR', 'tesseract.exe'),
            'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
            'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
            os.path.expanduser('~\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe')
        ])
        
        # 3. Try to find tesseract in PATH
        tesseract_paths.append('tesseract')
        
        tesseract_found = False
        for tesseract_path in tesseract_paths:
            try:
                if tesseract_path == 'tesseract':
                    # Special case: Try to find tesseract in PATH
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    # Test if it works by getting version
                    version = pytesseract.get_tesseract_version()
                    print(f"Found Tesseract in PATH: {tesseract_path} (v{version})")
                    tesseract_found = True
                    break
                elif os.path.isfile(tesseract_path):
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    # Test if it works by getting version
                    version = pytesseract.get_tesseract_version()
                    print(f"Found Tesseract at: {tesseract_path} (v{version})")
                    tesseract_found = True
                    break
            except (pytesseract.TesseractNotFoundError, Exception) as e:
                if 'tesseract is not installed' not in str(e).lower():
                    print(f"Tesseract found but error getting version: {e}")
                continue
        
        if not tesseract_found:
            error_msg = """
            ERROR: Tesseract-OCR is not installed or not found in any standard location.
            
            The application will now attempt to install it for you. Please wait...
            """
            print(error_msg)
            
            # Try to install Tesseract automatically
            try:
                import subprocess
                import sys
                import tempfile
                import urllib.request
                
                installer_url = "https://github.com/UB-Mannheim/tesseract/wiki/tesseract-ocr-w64-setup-5.3.0.20221222.exe"
                installer_path = os.path.join(tempfile.gettempdir(), "tesseract-ocr-installer.exe")
                
                print(f"Downloading Tesseract installer from {installer_url}...")
                urllib.request.urlretrieve(installer_url, installer_path)
                
                print("Installing Tesseract (this may take a few minutes)...")
                install_dir = os.path.join(os.environ.get('LOCALAPPDATA'), 'Programs', 'Tesseract-OCR')
                result = subprocess.run(
                    [installer_path, '/S', f'/D={install_dir}'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    tesseract_path = os.path.join(install_dir, 'tesseract.exe')
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    print(f"Successfully installed Tesseract to: {tesseract_path}")
                    tesseract_found = True
                else:
                    print(f"Failed to install Tesseract. Error: {result.stderr}")
                    
            except Exception as e:
                print(f"Automatic installation failed: {e}")
                print("\nPlease install Tesseract-OCR manually from one of these sources:")
                print("1. Official installer: https://github.com/UB-Mannheim/tesseract/wiki")
                print("2. Chocolatey: choco install tesseract")
                print("\nAfter installation, please restart the application.")
                return
        
        # Get all words with their positions
        try:
            data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)
        except Exception as e:
            print(f"ERROR running Tesseract OCR: {e}")
            print("Please verify that Tesseract is properly installed and in your system PATH.")
            return
        
        # Debug: Print all detected text and their positions
        print("\n--- DEBUG: Detected Text ---")
        for i in range(len(data['text'])):
            word = data['text'][i].strip()
            if word:  # Only print non-empty detections
                conf = int(data['conf'][i])
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                print(f"Text: '{word}'", f"Confidence: {conf}%", f"Position: ({x}, {y}, {w}, {h})")
        
        # Find words in the bottom row (lower half of the image)
        height = img_high_res.shape[0]
        mid_y = height // 2  # Middle Y coordinate to separate rows
        
        # First, find the lowest Y coordinate to identify the bottom row
        bottom_row_y = 0
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 30:  # Only consider confident detections
                y = int(data['top'][i])
                if y > bottom_row_y:
                    bottom_row_y = y
        
        # Allow some tolerance for the bottom row detection
        y_tolerance = 10  # pixels
        bottom_row_words = []
        
        # Collect all words in the bottom row
        for i in range(len(data['text'])):
            word = data['text'][i].strip()
            conf = int(data['conf'][i])
            if word and conf > 30:  # Only consider confident detections
                y = int(data['top'][i])
                # Check if this word is in the bottom row (within tolerance)
                if abs(y - bottom_row_y) <= y_tolerance:
                    x = int(data['left'][i]) + int(data['width'][i])  # Right edge of the word
                    bottom_row_words.append({
                        'word': word,
                        'right_x': x,
                        'y': y,
                        'conf': conf
                    })
        
        # Find the rightmost word in the bottom row
        rightmost_word = None
        if bottom_row_words:
            # Sort by right edge position (x + width)
            bottom_row_words.sort(key=lambda w: w['right_x'], reverse=True)
            rightmost_word = bottom_row_words[0]['word']
            print(f"Selected word '{rightmost_word}' from bottom row")
        
        if rightmost_word:
            # Clean the word (be less aggressive with cleaning)
            clean_word = ''.join(c for c in rightmost_word if c.isalnum() or c in "'-")
            if clean_word and len(clean_word) > 1:  # Require at least 2 characters
                type_word(clean_word)
                print(f"\nSUCCESSFUL: '{clean_word}' typed on keyboard.")
            else:
                print(f"\nERROR: Word '{rightmost_word}' became invalid after cleaning: '{clean_word}'")
        else:
            print("\nERROR: No words detected in caption.")
            
        # Save the image with bounding boxes for debugging
        debug_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 30:  # Only draw high confidence boxes
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        debug_path = os.path.join(os.path.dirname(image_path), "debug_" + os.path.basename(image_path))
        cv2.imwrite(debug_path, debug_img)
        print(f"Debug image saved to: {debug_path}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    print("\nPress Right CTRL to type again...")

def show_game_selection():
    """Show the game selection screen.
    Returns the selected game name or None if closed."""
    root = tk.Tk()
    root.title("Select Game")
    root.resizable(False, False)
    
    # Center the window
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Make the window stay on top
    root.attributes('-topmost', True)
    
    # Configure style
    style = ttk.Style()
    style.configure('Game.TButton', font=('Helvetica', 14), padding=20)
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add title
    title = ttk.Label(main_frame, text="Select a Game", font=('Helvetica', 18, 'bold'))
    title.pack(pady=(0, 30))
    
    # Result variable
    selected_game = [None]  # Using a list to store the result (mutable)
    
    # Add game buttons
    def select_game(game_name):
        selected_game[0] = game_name
        root.destroy()
    
    # Scary Spelling button
    scary_btn = ttk.Button(
        main_frame,
        text="Scary Spelling",
        style='Game.TButton',
        command=lambda: select_game("scary_spelling")
    )
    scary_btn.pack(fill=tk.X, pady=(0, 15))
    
    # Word Bomb button
    word_bomb_btn = ttk.Button(
        main_frame,
        text="Word Bomb",
        style='Game.TButton',
        command=lambda: select_game("word_bomb")
    )
    word_bomb_btn.pack(fill=tk.X)
    
    # Add settings button (cog wheel) in top-right corner
    def open_settings():
        # This will be implemented in the next step
        messagebox.showinfo("Settings", "Settings will be available soon!")
    
    settings_btn = ttk.Button(
        root,
        text="⚙",
        width=2,
        command=open_settings
    )
    settings_btn.place(relx=0.95, rely=0.02, anchor='ne')
    
    # Prevent closing with the X button
    def on_closing():
        pass  # Do nothing when X is clicked
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Make the window modal
    root.grab_set()
    
    # Start the main loop
    root.mainloop()
    
    # Handle Word Bomb selection
    if selected_game[0] == "word_bomb":
        messagebox.showinfo("Coming Soon", "We cannot load this at the moment because it will be added later in development!")
        return None
    
    return selected_game[0]

def show_instructions_popup():
    """Show a popup asking if user is following the official instructions guide.
    Returns the selected game name if successful, None otherwise."""
    root = tk.Tk()
    root.title("Important Notice")
    root.resizable(False, False)
    
    # Center the window
    window_width = 400
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Make the window stay on top
    root.attributes('-topmost', True)
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add label
    label = ttk.Label(main_frame, text="Are you following the official instructions guide?", wraplength=350, justify="center")
    label.pack(pady=(0, 20))
    
    # Add buttons frame
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Add buttons
    result = [None]  # Using a list to store the result (mutable)
    
    def on_yes():
        root.destroy()
        # Show game selection
        result[0] = show_game_selection()
    
    def on_no():
        # Show the link in a label
        link = tk.Label(main_frame, text="Please read the official guide: Click here", fg="blue", cursor="hand2")
        link.pack(pady=(10, 0))
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/VinnyPixYT/AutoTyperRBLX/blob/main/README.md"))
    
    yes_btn = ttk.Button(btn_frame, text="Yes", command=on_yes)
    yes_btn.pack(side=tk.LEFT, expand=True, padx=5)
    
    no_btn = ttk.Button(btn_frame, text="No", command=on_no)
    no_btn.pack(side=tk.LEFT, expand=True, padx=5)
    
    # Prevent closing with the X button
    def on_closing():
        pass  # Do nothing when X is clicked
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Make the window modal
    root.grab_set()
    
    # Start the main loop
    root.mainloop()
    
    return result[0]

def create_settings_window(parent):
    """Create and show the settings window."""
    settings_win = tk.Toplevel(parent)
    settings_win.title("Settings")
    settings_win.resizable(False, False)
    
    # Center the window
    window_width = 600
    window_height = 400
    screen_width = settings_win.winfo_screenwidth()
    screen_height = settings_win.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    settings_win.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Make the window stay on top of parent
    settings_win.transient(parent)
    settings_win.grab_set()
    
    # Create main container
    main_container = ttk.Frame(settings_win)
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Sidebar
    sidebar = ttk.Frame(main_container, width=150, style='Sidebar.TFrame')
    sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
    
    # Main content area
    content = ttk.Frame(main_container)
    content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
    
    # Sidebar buttons
    def show_settings_panel(panel_name):
        # Hide all panels
        for child in content.winfo_children():
            child.pack_forget()
        
        # Show selected panel
        if panel_name == 'appearance':
            appearance_panel.pack(fill=tk.BOTH, expand=True)
    
    appearance_btn = ttk.Button(
        sidebar, 
        text="Appearance", 
        command=lambda: show_settings_panel('appearance'),
        width=15
    )
    appearance_btn.pack(pady=(0, 5), fill=tk.X)
    
    # Appearance Panel
    appearance_panel = ttk.Frame(content)
    
    # Theme selection
    ttk.Label(
        appearance_panel, 
        text="Theme",
        font=('Helvetica', 10, 'bold')
    ).pack(anchor=tk.W, pady=(0, 10))
    
    theme_var = tk.StringVar(value=THEME['name'])
    
    def update_theme(*args):
        theme = theme_var.get()
        if theme == 'dark':
            THEME.update({
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'button_bg': '#3d3d3d',
                'button_fg': '#ffffff',
                'highlight': '#4a9cff',
                'window_bg': '#1e1e1e',
                'text': '#ffffff',
                'name': 'dark'
            })
        else:
            THEME.update({
                'bg': '#f0f0f0',
                'fg': '#000000',
                'button_bg': '#e0e0e0',
                'button_fg': '#000000',
                'highlight': '#0078d7',
                'window_bg': '#ffffff',
                'text': '#000000',
                'name': 'light'
            })
        apply_theme(parent)
    
    theme_frame = ttk.Frame(appearance_panel)
    theme_frame.pack(fill=tk.X, pady=(0, 20))
    
    ttk.Label(
        theme_frame, 
        text="Color Theme:",
        width=15
    ).pack(side=tk.LEFT, padx=(0, 10))
    
    theme_menu = ttk.OptionMenu(
        theme_frame,
        theme_var,
        THEME['name'],
        'light',
        'dark',
        command=update_theme
    )
    theme_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Show appearance panel by default
    show_settings_panel('appearance')
    
    return settings_win

def apply_theme(root):
    """Apply the current theme to the application."""
    style = ttk.Style()
    
    # Configure ttk styles
    if THEME['name'] == 'dark':
        style.theme_use('alt')  # Use alt theme for dark mode
        style.configure('.', 
                      background=THEME['bg'],
                      foreground=THEME['fg'],
                      fieldbackground=THEME['window_bg'],
                      selectbackground=THEME['highlight'],
                      selectforeground=THEME['fg'],
                      insertcolor=THEME['fg'])
        
        style.configure('TFrame', background=THEME['bg'])
        style.configure('TLabel', background=THEME['bg'], foreground=THEME['text'])
        style.configure('TButton', 
                       background=THEME['button_bg'],
                       foreground=THEME['button_fg'],
                       bordercolor=THEME['highlight'])
        
        # Configure button states
        style.map('TButton',
                 background=[('active', THEME['highlight'])],
                 foreground=[('active', THEME['button_fg'])])
    else:
        style.theme_use('default')  # Use default theme for light mode
    
    # Update root window background
    if hasattr(root, 'configure'):
        try:
            root.configure(bg=THEME['bg'])
        except:
            pass
    
    # Update all widgets
    for widget in root.winfo_children():
        update_widget_theme(widget)

def update_widget_theme(widget):
    """Update a widget and its children to match the current theme."""
    widget_type = str(type(widget))
    
    # Skip ttk widgets as they're handled by the style
    if 'ttk' in widget_type:
        pass
    # Handle standard Tkinter widgets
    elif 'Label' in widget_type:
        try:
            widget.config(bg=THEME['bg'])
            widget.config(fg=THEME['text'])
        except:
            pass
    elif 'Button' in widget_type:
        try:
            widget.config(bg=THEME['button_bg'])
            widget.config(fg=THEME['button_fg'])
            widget.config(highlightbackground=THEME['highlight'])
        except:
            pass
    elif 'Frame' in widget_type or 'Canvas' in widget_type:
        try:
            widget.config(bg=THEME['bg'])
        except:
            pass
    
    # Update all children
    for child in widget.winfo_children():
        update_widget_theme(child)

def create_gui():
    # Show the instructions popup first
    game_selection = show_instructions_popup()
    if not game_selection:
        # If they didn't select a game or cancelled, exit
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Game Required", "Please select a game to continue.")
        root.destroy()
        return None
    
    # Create the main window
    root = tk.Tk()
    root.title("Autotyper Control")
    root.resizable(False, False)
    
    # Center the window
    window_width = 400
    window_height = 250  # Increased height to accommodate settings button
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Make the window stay on top
    root.attributes('-topmost', True)
    
    # Add settings button (cog wheel) in top-right corner
    def open_settings():
        settings_win = create_settings_window(root)
        # Center the settings window relative to the main window
        settings_win.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() - settings_win.winfo_width()) // 2
        y = root.winfo_y() + (root.winfo_height() - settings_win.winfo_height()) // 2
        settings_win.geometry(f"+{x}+{y}")
    
    settings_btn = ttk.Button(
        root,
        text="⚙",
        width=2,
        command=open_settings
    )
    settings_btn.place(relx=0.95, rely=0.02, anchor='ne')
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Game title
    game_title = ttk.Label(
        main_frame, 
        text="Scary Spelling",
        font=('Helvetica', 16, 'bold')
    )
    game_title.pack(anchor=tk.W, pady=(0, 15))
    
    # WPM Label
    wpm_label = ttk.Label(main_frame, text="Words Per Minute (WPM):")
    wpm_label.pack(anchor=tk.W, pady=(0, 5))
    
    # Current WPM display
    current_wpm = tk.StringVar(value=f"Current: {TYPING_SPEED} WPM")
    current_wpm_label = ttk.Label(main_frame, textvariable=current_wpm)
    current_wpm_label.pack(anchor=tk.W, pady=(0, 10))
    
    # WPM Slider
    wpm_frame = ttk.Frame(main_frame)
    wpm_frame.pack(fill=tk.X, pady=(0, 10))
    
    min_label = ttk.Label(wpm_frame, text="1")
    min_label.pack(side=tk.LEFT, padx=(0, 5))
    
    wpm_slider = ttk.Scale(wpm_frame, from_=1, to=1500, orient=tk.HORIZONTAL, length=300)
    wpm_slider.set(TYPING_SPEED)
    wpm_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    max_label = ttk.Label(wpm_frame, text="1500")
    max_label.pack(side=tk.LEFT, padx=(5, 0))
    
    # Instructions label
    instructions = ttk.Label(
        main_frame, 
        text="Press 'Insert' to type, 'Esc' to exit", 
        font=('Helvetica', 9)
    )
    instructions.pack(pady=(10, 20))
    
    # Exit button
    def on_exit():
        root.destroy()
    
    exit_btn = ttk.Button(main_frame, text="Exit", command=on_exit)
    exit_btn.pack(pady=(0, 10))
    
    # Update WPM when slider changes
    def update_wpm(event=None):
        global TYPING_SPEED
        TYPING_SPEED = int(wpm_slider.get())
        current_wpm.set(f"Current: {TYPING_SPEED} WPM")
        print(f"WPM set to: {TYPING_SPEED}")
    
    wpm_slider.bind("<ButtonRelease-1>", update_wpm)
    
    # Apply theme
    apply_theme(root)
    
    return root

def main():
    global TYPING_SPEED
    try:
        # Create the GUI first
        window = create_gui()
        
        # If window is None, it means user didn't confirm the instructions
        if window is None:
            print("Application closed. Please read the instructions and restart.")
            return
            
        print("Starting Autotyper GUI...")
        print("Press 'Insert' to type, 'Esc' to exit")
        
        # Setup keyboard hooks
        keyboard.on_press_key('insert', on_insert_key_press, suppress=True)
        keyboard.on_press_key('esc', lambda e: exit(0), suppress=True)
        print("Keyboard hooks set up. Press 'Insert' to capture screen, 'Esc' to exit.")
        
        # Set console window to be always on top
        set_window_on_top()
        
        # Start the main event loop
        window.mainloop()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'window' in locals() and window is not None:
            window.destroy()
        keyboard.unhook_all()
        raise

if __name__ == "__main__":
    main()
