from PIL import Image, ImageDraw, ImageFont

# Загружаем фон
img = Image.open("background.png")
draw = ImageDraw.Draw(img)

# Загружаем шрифт (нужен файл шрифта, например, arial.ttf в папке со скриптом)
try:
	font = ImageFont.truetype("./fonts/GOST2304_TypeB.ttf", 22)
except:
	font = ImageFont.load_default()

# Текст спецификации
spec_text = """Спецификация

1. Каркасы: Lamarty 16 мм, декор: Серый
2. Фасады: Senosan, декор низ: 85385 Silver metallic, декор верх: 1982 White
3. Столешница: Slotex Elga, декор: Quartzite 8099
4. Петли: Salice, модель: Silentia 700+
5. Ящики: Boyard, модель: CTAPT white
6. Посудосушилка: Boyard, модель: SU/02 800
7. Подъемники: Top-stays, модель: SE00AM01
8. Ручки: Boyard, модель: РЭИ RT109BL
9. Освещение:
   - БП 60W
   - LED-лента COB 8мм 480 LED/м, 13Вт/м 3000K
   - выключатель HW.012.AD003

Технолог-конструктор: Егоровых Н.Б.
Монтаж: Егоровых Н.Б.
Заказ № 2601"""

# Координаты левого верхнего угла текста (подберите под ваш размер картинки)
text_x, text_y = 150, 200
draw.text((text_x, text_y), spec_text, fill="black", font=font)

# Вставляем QR-код
try:
	qr = Image.open("qr.png").convert("RGBA")
	qr = qr.resize((160, 160))  # Подберите размер под рамку
	# Координаты вставки QR-кода
	img.paste(qr, (1100, 580), qr)
except FileNotFoundError:
	print("Файл qr.png не найден, пропускаем вставку QR-кода.")

# Сохраняем результат
img.save("final_specification.png")
print("Готово! Файл сохранен как final_specification.png")
