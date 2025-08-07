from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(output_path='icon.ico'):
    # Create a new image with a white background
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple blue circle with a white border
    border = 10
    circle_bbox = [border, border, size - border, size - border]
    draw.ellipse(circle_bbox, fill='#0078d7', outline='white', width=5)
    
    # Add text (VPT for VinnyPix Typing)
    try:
        # Try to load a font (this will work if you have Arial installed)
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fall back to default font if Arial is not available
        font = ImageFont.load_default()
    
    text = "VPT"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save as ICO file
    img.save(output_path, format='ICO', sizes=[(256, 256)])
    print(f"Icon created at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    # Ensure the internal directory exists
    os.makedirs('internal', exist_ok=True)
    
    # Create the icon in the internal directory
    icon_path = os.path.join('internal', 'icon.ico')
    create_icon(icon_path)
