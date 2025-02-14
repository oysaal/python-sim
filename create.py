from PIL import Image, ImageDraw
# Simple green triangle
img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle([8,8, 24,24], fill=(255, 0, 0))
img.save('assets/buoys/red_can.png')