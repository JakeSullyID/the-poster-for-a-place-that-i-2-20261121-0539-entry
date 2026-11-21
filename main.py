from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

def create_poster():
    width, height = 768, 1024
    img = Image.new("RGB", (width, height), (15, 20, 35))
    draw = ImageDraw.Draw(img)

    horizon_y = 440

    # 1. Sky Gradient: Deep navy at top transitioning through rich rose and warm peach
    for y in range(horizon_y):
        t = y / horizon_y
        if t < 0.32:
            s = t / 0.32
            r = int(12 + s * (90 - 12))
            g = int(18 + s * (48 - 18))
            b = int(40 + s * (75 - 40))
        elif t < 0.68:
            s = (t - 0.32) / 0.36
            r = int(90 + s * (225 - 90))
            g = int(48 + s * (115 - 48))
            b = int(75 + s * (95 - 75))
        else:
            s = (t - 0.68) / 0.32
            r = int(225 + s * (255 - 225))
            g = int(115 + s * (180 - 115))
            b = int(95 + s * (145 - 95))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Full Moon in upper right sky with radiant soft glow
    moon_x, moon_y, moon_r = 580, 125, 38
    for r in range(moon_r + 24, moon_r, -1):
        alpha = (r - moon_r) / 24.0
        col = (int(255 - alpha * 15), int(245 - alpha * 25), int(220 - alpha * 45))
        draw.ellipse([moon_x - r, moon_y - r, moon_x + r, moon_y + r], fill=col)
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(255, 252, 235))

    # 3. Soft Atmospheric Dusk Clouds
    cloud_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(cloud_layer)
    c_draw.ellipse([60, 50, 400, 150], fill=(255, 175, 155, 50))
    c_draw.ellipse([280, 90, 680, 210], fill=(235, 135, 145, 40))
    c_draw.ellipse([130, 150, 480, 250], fill=(185, 95, 115, 35))
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(28))
    img.paste(Image.alpha_composite(img.convert("RGBA"), cloud_layer).convert("RGB"))
    draw = ImageDraw.Draw(img)

    # 4. Bioluminescent Teal Water against Dusk Sky
    for y in range(horizon_y, height):
        t = (y - horizon_y) / (height - horizon_y)
        r = int(16 + t * 14)
        g = int(62 + t * 38)
        b = int(72 + t * 48)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Rich Gold Reflection Path from Full Moon down across water
    for y in range(horizon_y, height):
        dist_y = y - horizon_y
        fade = max(0.0, 1.0 - dist_y / (height - horizon_y))
        path_width = int(22 + dist_y * 0.45)
        for rx in range(int(moon_x - path_width), int(moon_x + path_width)):
            if 0 <= rx < width:
                dx = abs(rx - moon_x) / max(1, path_width)
                intensity = int(150 * fade * (1.0 - dx))
                if intensity > 4:
                    base_col = img.getpixel((rx, y))
                    nr = min(255, base_col[0] + intensity)
                    ng = min(255, base_col[1] + int(intensity * 0.92))
                    nb = min(255, base_col[2] + int(intensity * 0.45))
                    draw.point((rx, y), fill=(nr, ng, nb))

    # Water shimmer / ripples
    for y in range(horizon_y + 10, height, 16):
        draw.line([(0, y), (width, y)], fill=(32, 115, 125))

    # 5. LOGARITHMIC SPIRAL NAUTILUS SHELL LANDMARK
    shell_cx, shell_cy = 384, 330

    # Generate logarithmic spiral points
    # r = 12 * e^(0.22 * theta)
    # theta from 0 to about 4.5 * pi, stop when r reaches ~210
    spiral_theta = []
    spiral_center_pts = []
    inner_pts = []
    outer_pts = []

    d_theta = 0.02
    theta = 0.0
    while theta <= 4.5 * math.pi:
        r = 12.0 * math.exp(0.22 * theta)
        if r > 210:
            break
        spiral_theta.append((theta, r))
        cx = shell_cx + r * math.cos(theta)
        cy = shell_cy + r * math.sin(theta)
        spiral_center_pts.append((cx, cy))
        
        # Inner and outer offset curves (18 pixels inside and outside)
        r_in = max(0.0, r - 18.0)
        r_out = r + 18.0
        inner_pts.append((shell_cx + r_in * math.cos(theta), shell_cy + r_in * math.sin(theta)))
        outer_pts.append((shell_cx + r_out * math.cos(theta), shell_cy + r_out * math.sin(theta)))
        theta += d_theta

    # Construct the spiral band polygon: outer points forward, then inner points backward
    band_polygon = outer_pts + list(reversed(inner_pts))
    if len(band_polygon) > 2:
        draw.polygon(band_polygon, fill=(22, 28, 45))

    # Draw the thick (10 pixel) gold/cream curve down the centre of the navy band
    if len(spiral_center_pts) > 1:
        draw.line(spiral_center_pts, fill=(255, 230, 180), width=10)

    # Chambers: Warm gold arched windows placed ON the spiral curve at increasing theta
    window_thetas = [0.8, 1.4, 2.0, 2.6, 3.2, 3.8, 4.4, 5.0, 5.6, 6.2]
    for i, w_th in enumerate(window_thetas):
        w_r = 12.0 * math.exp(0.22 * w_th)
        if w_r > 210:
            continue
        wx = shell_cx + w_r * math.cos(w_th)
        wy = shell_cy + w_r * math.sin(w_th)
        
        # Window size growing with radius
        # Small near centre (~6px), large at outer turn (~16px)
        w_size = int(6 + (w_r / 210.0) * 12)
        
        # Draw arched window centered on curve
        # Arched shape: rectangle at bottom, semicircle on top
        box = [wx - w_size, wy - w_size * 1.4, wx + w_size, wy + w_size * 0.4]
        draw.rectangle([wx - w_size, wy - w_size * 0.5, wx + w_size, wy + w_size * 0.5], fill=(255, 220, 130))
        draw.pieslice([wx - w_size, wy - w_size * 1.5, wx + w_size, wy + w_size * 0.5], start=180, end=360, fill=(255, 200, 90))
        # Inner warm glow
        draw.ellipse([wx - w_size * 0.5, wy - w_size * 0.5, wx + w_size * 0.5, wy + w_size * 0.5], fill=(255, 245, 200))

    # Tiny Lit Town sitting on lower ledges / base near horizon
    town_base_y = horizon_y + 12
    for tx_offset in range(-190, 210, 26):
        th_h = 16 + (abs(tx_offset) % 16)
        th_w = 15
        th_x = shell_cx + tx_offset
        th_y = town_base_y - th_h
        draw.rectangle([th_x, th_y, th_x + th_w, town_base_y], fill=(38, 45, 58))
        draw.polygon([(th_x - 3, th_y), (th_x + th_w/2, th_y - 11), (th_x + th_w + 3, th_y)], fill=(58, 48, 58))
        draw.rectangle([th_x + 3, th_y + 5, th_x + 7, th_y + 11], fill=(255, 225, 140))
        draw.rectangle([th_x + 9, th_y + 5, th_x + 13, th_y + 11], fill=(255, 225, 140))

    # Water reflections for the shell and town
    for ry in range(horizon_y + 2, horizon_y + 130, 3):
        fade = 1.0 - (ry - horizon_y) / 130.0
        draw.line([(shell_cx - 160, ry), (shell_cx + 160, ry)], fill=(42 + int(105*fade), 148 + int(52*fade), 138 + int(32*fade)))

    # 6. Foreground Shore and Tiny Boats (Foreground figure deleted)
    draw.polygon([(0, 960), (width, 960), (width, 1024), (0, 1024)], fill=(18, 22, 32))
    draw.arc([-100, 920, width + 100, 1040], start=180, end=360, fill=(28, 35, 48), width=26)

    # Tiny sailboats
    boat_positions = [(130, 515), (590, 555), (455, 615), (280, 540)]
    for bx, by in boat_positions:
        draw.polygon([(bx - 10, by), (bx + 10, by), (bx + 7, by + 5), (bx - 7, by + 5)], fill=(28, 34, 48))
        draw.polygon([(bx, by), (bx, by - 16), (bx + 8, by - 4)], fill=(245, 240, 230))
        draw.line([(bx - 6, by + 7), (bx + 6, by + 7)], fill=(255, 205, 125))

    # 7. Typography (VELMARA large at top, THE GLOWING BAY subtitle)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 82)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Title: VELMARA
    title_text = "VELMARA"
    t_bbox = font_title.getbbox(title_text)
    tw = t_bbox[2] - t_bbox[0]
    th = t_bbox[3] - t_bbox[1]
    tx = (width - tw) // 2
    ty = 45

    draw.text((tx + 2, ty + 2), title_text, font=font_title, fill=(8, 10, 18))
    draw.text((tx, ty), title_text, font=font_title, fill=(248, 243, 235))

    # Subtitle: THE GLOWING BAY
    sub_raw = "THE GLOWING BAY"
    sub_text = "     ".join(list(sub_raw))
    s_bbox = font_sub.getbbox(sub_text)
    sw = s_bbox[2] - s_bbox[0]
    sx = (width - sw) // 2
    sy = ty + th + 18

    rule_y = sy + 8
    draw.line([(sx - 55, rule_y), (sx - 15, rule_y)], fill=(225, 215, 195), width=1)
    draw.line([(sx + sw + 15, rule_y), (sx + sw + 55, rule_y)], fill=(225, 215, 195), width=1)
    draw.text((sx + 2, sy + 2), sub_text, font=font_sub, fill=(8, 10, 18))
    draw.text((sx, sy), sub_text, font=font_sub, fill=(215, 225, 218))

    # 8. Vintage Poster Frame & Subtle Grain
    border_width = 12
    draw.rectangle([0, 0, width - 1, height - 1], outline=(235, 225, 205), width=border_width)
    draw.rectangle([border_width - 1, border_width - 1, width - border_width, height - border_width], outline=(55, 45, 55), width=1)

    # Subtle grain
    for y in range(border_width, height - border_width, 3):
        for x in range(border_width, width - border_width, 3):
            noise = (math.sin(x * 12.9898 + y * 78.233) * 43758.5453) % 1.0
            if noise < 0.18:
                c = img.getpixel((x, y))
                factor = 0.85 if noise < 0.09 else 1.12
                nr = min(255, max(0, int(c[0] * factor)))
                ng = min(255, max(0, int(c[1] * factor)))
                nb = min(255, max(0, int(c[2] * factor)))
                img.putpixel((x, y), (nr, ng, nb))

    import os
    os.makedirs("/output", exist_ok=True)
    output_path = "/output/entry.png"
    img.save(output_path, "PNG")
    img.save("entry.png", "PNG")
    print(f"Poster successfully written to {output_path} and entry.png")

if __name__ == "__main__":
    create_poster()
