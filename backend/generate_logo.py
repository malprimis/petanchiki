# generate_logo.py
import os
from PIL import Image, ImageDraw, ImageFont

# Параметры изображения
width, height = 200, 150
background_color = (255, 255, 255)
primary_color = (0, 102, 204)  # синий
secondary_color = (255, 193, 7)  # жёлтый

# Создаем изображение
image = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(image)

# Рисуем стилизованный кошелёк или график
# Кошелька (прямоугольник с дугой сверху)
draw.rectangle([20, 60, 180, 130], fill=primary_color, outline=(0, 0, 0), width=2)
draw.arc([80, 20, 120, 60], start=0, end=180, fill=secondary_color, width=5)

# Добавим текст (опционально)
try:
    font = ImageFont.truetype("arial.ttf", 20)
except:
    font = ImageFont.load_default()

draw.text((50, 100), "FinTrack", fill=(0, 0, 0), font=font)

# Сохраняем логотип
os.makedirs("static", exist_ok=True)
image.save("static/logo.png")
print("✅ Логотип сохранён как static/logo.png")