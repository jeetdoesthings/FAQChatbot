"""
Event Poster Generator Engine (Unit U4)
Generates high-resolution, aesthetically styled departmental event posters.
"""
import os
import math
import random
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from src.config import POSTERS_DIR, DEPARTMENT_TITLE, COLLEGE_TITLE, SUPPORT_EMAIL

THEMES = {
    "Cyber Deep Blue": {
        "bg_top": (10, 15, 30),
        "bg_bottom": (15, 23, 42),
        "accent": (56, 189, 248),      # Cyan
        "highlight": (129, 140, 248),   # Indigo
        "card_bg": (30, 41, 59, 210),
        "text_primary": (255, 255, 255),
        "text_secondary": (203, 213, 225),
        "badge_bg": (14, 116, 144)
    },
    "Emerald AI": {
        "bg_top": (6, 25, 20),
        "bg_bottom": (15, 35, 28),
        "accent": (52, 211, 153),      # Emerald green
        "highlight": (45, 212, 191),   # Teal
        "card_bg": (20, 50, 40, 210),
        "text_primary": (255, 255, 255),
        "text_secondary": (209, 250, 229),
        "badge_bg": (16, 149, 106)
    },
    "Neon Purple Tech": {
        "bg_top": (20, 10, 35),
        "bg_bottom": (35, 15, 55),
        "accent": (216, 180, 254),     # Purple
        "highlight": (244, 114, 182),   # Pink
        "card_bg": (45, 25, 65, 210),
        "text_primary": (255, 255, 255),
        "text_secondary": (245, 208, 254),
        "badge_bg": (147, 51, 234)
    }
}

class EventPosterGenerator:
    def __init__(self, output_dir: Path = POSTERS_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.width = 1080
        self.height = 1440

    def _get_font(self, size: int, bold: bool = False):
        """Attempts to load high quality system fonts with graceful fallback."""
        font_candidates = [
            "/System/Library/Fonts/SFPro-Bold.otf" if bold else "/System/Library/Fonts/SFPro-Regular.otf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _create_gradient_background(self, theme: Dict[str, Any]) -> Image.Image:
        """Renders a smooth vertical gradient image with cybernetic grid accents."""
        base = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(base)

        top_col = theme["bg_top"]
        bot_col = theme["bg_bottom"]

        # Vertical color gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(top_col[0] * (1 - ratio) + bot_col[0] * ratio)
            g = int(top_col[1] * (1 - ratio) + bot_col[1] * ratio)
            b = int(top_col[2] * (1 - ratio) + bot_col[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b, 255))

        # Geometric matrix network / lattice background overlay
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        grid_spacing = 60
        grid_color = (theme["accent"][0], theme["accent"][1], theme["accent"][2], 18)

        for x in range(0, self.width, grid_spacing):
            draw_ov.line([(x, 0), (x, self.height)], fill=grid_color, width=1)
        for y in range(0, self.height, grid_spacing):
            draw_ov.line([(0, y), (self.width, y)], fill=grid_color, width=1)

        # Tech node sparkles
        random.seed(42)
        for _ in range(35):
            nx = random.randint(50, self.width - 50)
            ny = random.randint(80, self.height - 80)
            radius = random.randint(2, 6)
            node_color = (theme["accent"][0], theme["accent"][1], theme["accent"][2], random.randint(40, 160))
            draw_ov.ellipse([nx - radius, ny - radius, nx + radius, ny + radius], fill=node_color)

        return Image.alpha_composite(base, overlay)

    def generate(
        self,
        event_title: str = "AI-CONFLUX 2026",
        tagline: str = "National Symposium & 36-Hour AI Hackathon",
        date_str: str = "October 24-25, 2026",
        venue_str: str = "Auditorium Hall & AI Compute Labs",
        organizer: str = f"{DEPARTMENT_TITLE}\n{COLLEGE_TITLE}",
        highlights: str = "₹1,50,000 Cash Prizes • Industry Mentors • Free Food & Swag • IEEE Certificates",
        theme_name: str = "Cyber Deep Blue",
        speaker_str: str = "Keynote: Prof. R. K. Sharma & Industry AI Leaders"
    ) -> str:
        """
        Creates an event poster and saves it to disk.
        Returns the absolute path to the generated image file.
        """
        theme = THEMES.get(theme_name, THEMES["Cyber Deep Blue"])
        poster = self._create_gradient_background(theme)
        draw = ImageDraw.Draw(poster)

        # 1. Header Banner & Institution Info
        f_dept = self._get_font(26, bold=True)
        f_inst = self._get_font(22, bold=False)

        draw.text((self.width // 2, 70), "FACULTY OF TECHNOLOGY & ENGINEERING", font=f_dept, fill=theme["accent"], anchor="mm")
        draw.text((self.width // 2, 105), DEPARTMENT_TITLE.upper(), font=f_inst, fill=theme["text_secondary"], anchor="mm")

        # Decorative neon line under header
        draw.line([(180, 135), (self.width - 180, 135)], fill=theme["highlight"], width=3)

        # 2. Category Badge ("DEPARTMENT TECHNICAL FLAGSHIP")
        badge_y = 190
        badge_w = 420
        badge_h = 44
        bx1 = (self.width - badge_w) // 2
        bx2 = bx1 + badge_w
        draw.rounded_rectangle([bx1, badge_y, bx2, badge_y + badge_h], radius=20, fill=theme["badge_bg"], outline=theme["accent"], width=2)
        f_badge = self._get_font(18, bold=True)
        draw.text((self.width // 2, badge_y + 22), "ANNUAL DEPARTMENT FLAGSHIP EVENT", font=f_badge, fill=(255, 255, 255), anchor="mm")

        # 3. Main Event Title
        f_title = self._get_font(68, bold=True)
        # Glow shadow
        draw.text((self.width // 2 + 3, 310 + 3), event_title.upper(), font=f_title, fill=(0, 0, 0, 180), anchor="mm")
        draw.text((self.width // 2, 310), event_title.upper(), font=f_title, fill=theme["text_primary"], anchor="mm")

        # 4. Tagline / Subtitle
        f_tagline = self._get_font(32, bold=False)
        draw.text((self.width // 2, 385), tagline, font=f_tagline, fill=theme["accent"], anchor="mm")

        # 5. Highlights Card
        card_y = 450
        card_w = self.width - 140
        card_h = 100
        cx1 = (self.width - card_w) // 2
        cx2 = cx1 + card_w
        draw.rounded_rectangle([cx1, card_y, cx2, card_y + card_h], radius=20, fill=theme["card_bg"], outline=theme["highlight"], width=2)
        
        f_high_title = self._get_font(18, bold=True)
        draw.text((self.width // 2, card_y + 28), "EVENT HIGHLIGHTS & PERKS", font=f_high_title, fill=theme["accent"], anchor="mm")
        f_high_body = self._get_font(22, bold=False)
        draw.text((self.width // 2, card_y + 65), highlights, font=f_high_body, fill=theme["text_primary"], anchor="mm")

        # 6. Date, Venue & Speaker Info Grid Cards
        grid_y = 590
        info_items = [
            ("DATE & DURATION", date_str),
            ("VENUE & LABS", venue_str),
            ("DISTINGUISHED SPEAKER", speaker_str),
            ("ELIGIBILITY", "Open to All AI, CS & Engineering Students")
        ]

        card_gap = 20
        c_w = (self.width - 140 - card_gap) // 2
        c_h = 135

        for i, (label, val) in enumerate(info_items):
            row = i // 2
            col = i % 2
            rx1 = cx1 + col * (c_w + card_gap)
            ry1 = grid_y + row * (c_h + card_gap)
            rx2 = rx1 + c_w
            ry2 = ry1 + c_h

            draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=16, fill=theme["card_bg"], outline=theme["accent"], width=2)
            f_lbl = self._get_font(18, bold=True)
            draw.text((rx1 + 25, ry1 + 30), label, font=f_lbl, fill=theme["accent"], anchor="lm")
            f_val = self._get_font(21, bold=False)
            
            # Simple text wrap if needed
            if len(val) > 28:
                draw.text((rx1 + 25, ry1 + 68), val[:28], font=f_val, fill=theme["text_primary"], anchor="lm")
                draw.text((rx1 + 25, ry1 + 96), val[28:], font=f_val, fill=theme["text_primary"], anchor="lm")
            else:
                draw.text((rx1 + 25, ry1 + 78), val, font=f_val, fill=theme["text_primary"], anchor="lm")

        # 7. QR / Registration Panel at Bottom
        reg_y = 960
        reg_h = 240
        draw.rounded_rectangle([cx1, reg_y, cx2, reg_y + reg_h], radius=24, fill=theme["card_bg"], outline=theme["highlight"], width=3)

        # Draw a simulated high-tech QR code matrix
        qr_size = 170
        qr_x = cx1 + 45
        qr_y = reg_y + (reg_h - qr_size) // 2
        draw.rectangle([qr_x, qr_y, qr_x + qr_size, qr_y + qr_size], fill=(255, 255, 255), outline=theme["accent"], width=3)
        # Internal QR blocks
        qr_draw = ImageDraw.Draw(poster)
        block_s = 14
        random.seed(101)
        for qy in range(qr_y + 10, qr_y + qr_size - 10, block_s):
            for qx in range(qr_x + 10, qr_x + qr_size - 10, block_s):
                if random.random() > 0.45:
                    qr_draw.rectangle([qx, qy, qx + block_s - 2, qy + block_s - 2], fill=(15, 23, 42))

        # QR Corner Finder patterns
        for fx, fy in [(qr_x + 10, qr_y + 10), (qr_x + qr_size - 50, qr_y + 10), (qr_x + 10, qr_y + qr_size - 50)]:
            qr_draw.rectangle([fx, fy, fx + 38, fy + 38], fill=(15, 23, 42))
            qr_draw.rectangle([fx + 8, fy + 8, fx + 30, fy + 30], fill=(255, 255, 255))
            qr_draw.rectangle([fx + 14, fy + 14, fx + 24, fy + 24], fill=(15, 23, 42))

        # Text beside QR
        text_x = qr_x + qr_size + 45
        f_reg_head = self._get_font(28, bold=True)
        draw.text((text_x, reg_y + 55), "SCAN QR TO REGISTER", font=f_reg_head, fill=theme["accent"], anchor="lm")
        f_reg_sub = self._get_font(22, bold=False)
        draw.text((text_x, reg_y + 100), "• Limited seats per team (Max 4 Members)", font=f_reg_sub, fill=theme["text_primary"], anchor="lm")
        draw.text((text_x, reg_y + 135), "• Free registration for all verified students", font=f_reg_sub, fill=theme["text_primary"], anchor="lm")
        draw.text((text_x, reg_y + 175), f"Contact: {SUPPORT_EMAIL}", font=f_reg_sub, fill=theme["highlight"], anchor="lm")

        # 8. Footer Info
        f_foot = self._get_font(18, bold=False)
        draw.text((self.width // 2, self.height - 70), "Official Notification • Department of AI & Data Science • Academic Year 2026", font=f_foot, fill=theme["text_secondary"], anchor="mm")
        draw.text((self.width // 2, self.height - 40), f"Office: Room 304, Technology Block • Inquiries: {SUPPORT_EMAIL}", font=f_foot, fill=theme["text_secondary"], anchor="mm")

        # Save output
        clean_title = "".join(c for c in event_title if c.isalnum() or c in ("-", "_")).lower()
        output_filename = f"poster_{clean_title}.png"
        output_path = self.output_dir / output_filename

        poster_rgb = poster.convert("RGB")
        poster_rgb.save(str(output_path), quality=95)
        print(f"[PosterGenerator] Generated event poster at: {output_path}")
        return str(output_path)

if __name__ == "__main__":
    gen = EventPosterGenerator()
    out = gen.generate(
        event_title="AI-CONFLUX 2026",
        tagline="National 36-Hour AI Hackathon & Tech Symposium",
        date_str="February 20-21, 2026",
        venue_str="NVIDIA High Performance Compute Labs",
        highlights="₹1,50,000 Prizes • 24/7 Cloud GPUs • Swag & Mentors",
        theme_name="Cyber Deep Blue"
    )
    print("Poster created successfully:", out)
