from PIL import Image, ImageDraw, ImageFont, Image

font = ImageFont.load_default()

def new_canvas(W, H, bg=(28,28,32)):
    return Image.new("RGB", (W, H), bg), ImageDraw.Draw(Image.new("RGB", (W, H), bg))

def safe_round_rect(d, rect, r, fill=None, outline=None, width=1):
    try:
        d.rounded_rectangle(rect, radius=r, fill=fill, outline=outline, width=width)
    except Exception:
        d.rectangle(rect, fill=fill, outline=outline, width=width)

def draw_button(d, rect, label, pressed=False):
    x0,y0,x1,y1 = rect
    fill = (70,72,84) if pressed else (48,50,58)
    outline = (255,255,255) if pressed else (210,210,210)
    safe_round_rect(d, (x0,y0,x1-1,y1-1), 10, fill=fill, outline=outline, width=2)
    tw = d.textlength(label, font=font)
    d.text(((x0+x1)//2 - tw//2, (y0+y1)//2 - 6), label, font=font, fill=(240,240,240))

def draw_led(d, x, y, on):
    if on: d.ellipse((x-5,y-5,x+5,y+5), fill=(0,255,120))
    else:  d.ellipse((x-5,y-5,x+5,y+5), outline=(110,110,110))

def point_in(rect, x, y):
    x0,y0,x1,y1 = rect
    return x0 <= x < x1 and y0 <= y < y1
