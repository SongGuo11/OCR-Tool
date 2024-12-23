from PIL import Image, ImageDraw, ImageFont

# 创建一个 256x256 的图像
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# 绘制圆形背景
circle_color = (65, 105, 225)  # 皇家蓝
draw.ellipse([10, 10, size-10, size-10], fill=circle_color)

# 添加文字
try:
    font = ImageFont.truetype("arial.ttf", size=100)
except:
    font = ImageFont.load_default()

text = "OCR"
text_color = (255, 255, 255)  # 白色

# 计算文字位置使其居中
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
text_position = ((size - text_width) // 2, (size - text_height) // 2)

# 绘制文字
draw.text(text_position, text, font=font, fill=text_color)

# 保存为ICO文件
image.save('icon.ico', format='ICO', sizes=[(256, 256)])