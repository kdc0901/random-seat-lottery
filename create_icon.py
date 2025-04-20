import os
from PIL import Image, ImageDraw, ImageFont
import subprocess

def create_icon(size):
    # Create a new image with white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw blue circle
    circle_color = '#2196F3'  # Material Blue
    padding = size // 8
    draw.ellipse([padding, padding, size - padding, size - padding], 
                 fill=circle_color)
    
    # Add text for larger sizes
    if size >= 64:
        try:
            # Try to load the system font (AppleGothic for macOS)
            font_size = size // 4
            font = ImageFont.truetype('/System/Library/Fonts/AppleGothic.ttf', font_size)
            
            # Add Korean text "추첨"
            text = "추첨"
            # Get text size
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Calculate text position to center it
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Draw text in white
            draw.text((x, y), text, fill='white', font=font)
            
        except Exception as e:
            print(f"Warning: Could not load font or draw text: {e}")
    
    return image

def main():
    # Create icons directory if it doesn't exist
    icons_dir = 'icons.iconset'
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # Generate icons in different sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        icon = create_icon(size)
        
        # Save normal size
        icon.save(f'{icons_dir}/icon_{size}x{size}.png')
        
        # Save @2x version for retina display (except for 1024)
        if size < 512:
            icon_2x = create_icon(size * 2)
            icon_2x.save(f'{icons_dir}/icon_{size}x{size}@2x.png')
    
    # Convert to .icns using iconutil (macOS only)
    try:
        subprocess.run(['iconutil', '-c', 'icns', icons_dir])
        print("Successfully created icons.icns")
    except Exception as e:
        print(f"Error creating .icns file: {e}")

if __name__ == '__main__':
    main() 