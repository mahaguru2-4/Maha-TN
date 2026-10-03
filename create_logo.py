import os
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    # 1. Full Horizontal Logo (800 x 200)
    w, h = 800, 200
    img = Image.new("RGBA", (w, h), (10, 17, 40, 255)) # Dark navy #0A1128
    draw = ImageDraw.Draw(img)
    
    # Draw decorative gold border/accent line at bottom
    gold_color = (212, 175, 55, 255) # #D4AF37
    gold_light = (243, 198, 143, 255)
    
    draw.rectangle([(20, 15), (780, 185)], outline=(30, 41, 75, 255), width=2)
    draw.line([(20, 185), (780, 185)], fill=gold_color, width=3)
    
    # Draw Scales / Shield emblem on the left
    cx, cy = 95, 100
    # Shield outline
    shield_pts = [
        (cx, cy - 55),
        (cx + 45, cy - 35),
        (cx + 38, cy + 25),
        (cx, cy + 55),
        (cx - 38, cy + 25),
        (cx - 45, cy - 35)
    ]
    draw.polygon(shield_pts, outline=gold_color, fill=(16, 25, 53, 255), width=3)
    
    # Central beam of scale
    draw.line([(cx, cy - 30), (cx, cy + 30)], fill=gold_light, width=3)
    # Horizontal crossbar
    draw.line([(cx - 25, cy - 15), (cx + 25, cy - 15)], fill=gold_light, width=3)
    # Scale left pan
    draw.line([(cx - 25, cy - 15), (cx - 35, cy + 5)], fill=gold_color, width=2)
    draw.line([(cx - 25, cy - 15), (cx - 15, cy + 5)], fill=gold_color, width=2)
    draw.arc([(cx - 40, cy), (cx - 10, cy + 15)], start=0, end=180, fill=gold_color, width=2)
    # Scale right pan
    draw.line([(cx + 25, cy - 15), (cx + 15, cy + 5)], fill=gold_color, width=2)
    draw.line([(cx + 25, cy - 15), (cx + 35, cy + 5)], fill=gold_color, width=2)
    draw.arc([(cx + 10, cy), (cx + 40, cy + 15)], start=0, end=180, fill=gold_color, width=2)
    
    # Try to load standard fonts or use default
    font_large = None
    font_sub = None
    try:
        # Standard Windows fonts
        font_large = ImageFont.truetype("arialbd.ttf", 52)
        font_sub = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_large = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    # Brand Text
    draw.text((170, 52), "LEGALEASE", fill=gold_color, font=font_large)
    draw.text((172, 118), "AI-POWERED LEGAL DOCUMENT GENERATOR", fill=(226, 232, 240, 255), font=font_sub)
    draw.text((620, 58), "TM", fill=gold_light, font=font_sub)

    os.makedirs("assets/logo", exist_ok=True)
    os.makedirs("frontend/assets", exist_ok=True)
    
    img.save("assets/logo/legalease_logo.png")
    img.save("frontend/assets/legalease_logo.png")
    
    # 2. Square Emblem (300 x 300)
    sq_size = 300
    sq_img = Image.new("RGBA", (sq_size, sq_size), (10, 17, 40, 255))
    sq_draw = ImageDraw.Draw(sq_img)
    scx, scy = 150, 140
    
    # Shield outline
    sq_pts = [
        (scx, scy - 90),
        (scx + 75, scy - 55),
        (scx + 65, scy + 45),
        (scx, scy + 95),
        (scx - 65, scy + 45),
        (scx - 75, scy - 55)
    ]
    sq_draw.polygon(sq_pts, outline=gold_color, fill=(16, 25, 53, 255), width=5)
    sq_draw.line([(scx, scy - 55), (scx, scy + 55)], fill=gold_light, width=4)
    sq_draw.line([(scx - 45, scy - 25), (scx + 45, scy - 25)], fill=gold_light, width=4)
    # Left pan
    sq_draw.line([(scx - 45, scy - 25), (scx - 60, scy + 10)], fill=gold_color, width=3)
    sq_draw.line([(scx - 45, scy - 25), (scx - 30, scy + 10)], fill=gold_color, width=3)
    sq_draw.arc([(scx - 65, scy + 5), (scx - 25, scy + 25)], start=0, end=180, fill=gold_color, width=3)
    # Right pan
    sq_draw.line([(scx + 45, scy - 25), (scx + 30, scy + 10)], fill=gold_color, width=3)
    sq_draw.line([(scx + 45, scy - 25), (scx + 60, scy + 10)], fill=gold_color, width=3)
    sq_draw.arc([(scx + 25, scy + 5), (scx + 65, scy + 25)], start=0, end=180, fill=gold_color, width=3)
    
    try:
        font_sq = ImageFont.truetype("arialbd.ttf", 24)
    except Exception:
        font_sq = ImageFont.load_default()
    sq_draw.text((75, 255), "LEGALEASE", fill=gold_color, font=font_sq)
    
    sq_img.save("assets/logo/legalease_emblem.png")
    sq_img.save("frontend/assets/legalease_emblem.png")
    print("Logos successfully created in assets/logo and frontend/assets!")

if __name__ == "__main__":
    generate_logo()
