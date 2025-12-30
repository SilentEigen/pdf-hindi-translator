from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create a simple gradient icon with PDF and translation symbols"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background (purple to blue)
    for y in range(size):
        progress = y / size
        r = int(102 + (118 - 102) * progress)
        g = int(126 + (75 - 126) * progress)
        b = int(234 + (162 - 234) * progress)
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
    
    # Draw document shape (white)
    margin = size // 5
    doc_width = size - (2 * margin)
    doc_height = int(doc_width * 1.3)
    
    # Center the document
    doc_x = margin
    doc_y = (size - doc_height) // 2
    
    # Document rectangle
    draw.rounded_rectangle(
        [(doc_x, doc_y), (doc_x + doc_width, doc_y + doc_height)],
        radius=size//20,
        fill='white'
    )
    
    # Draw lines on document
    line_margin = size // 10
    for i in range(3):
        y_pos = doc_y + line_margin + (i * (doc_height - 2*line_margin) // 4)
        draw.rectangle(
            [(doc_x + line_margin, y_pos), (doc_x + doc_width - line_margin, y_pos + 2)],
            fill=(102, 126, 234)
        )
    
    # Draw translation arrow/globe symbol
    center_x = doc_x + doc_width // 2
    center_y = doc_y + doc_height // 2
    radius = size // 10
    draw.ellipse(
        [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
        outline=(102, 126, 234),
        width=max(1, size//64)
    )
    
    img.save(output_path)
    print(f"✓ Created {output_path}")

# Create output directory
icons_dir = "chrome-extension/icons"
os.makedirs(icons_dir, exist_ok=True)

# Generate icons
create_icon(16, os.path.join(icons_dir, "icon16.png"))
create_icon(48, os.path.join(icons_dir, "icon48.png"))
create_icon(128, os.path.join(icons_dir, "icon128.png"))

print("\n🎨 All icons created successfully!")
