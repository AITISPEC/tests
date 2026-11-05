import threading
import time
from pynput import keyboard
from pynput.mouse import Button, Controller

# Инициализируем контроллер мыши
mouse = Controller()

# Флаг: True — цикл кликов активен, False — остановлен
clicking = False
# Блокировка для безопасной работы с потоками
lock = threading.Lock()

# Задержка между кликами (в секундах)
CLICK_DELAY = 0.8


def click_loop():
	"""Бесконечно кликает ЛКМ с паузой CLICK_DELAY, пока clicking == True."""
	global clicking
	print("[ВКЛ] Автокликер запущен")
	while True:
		with lock:
			if not clicking:
				break
		mouse.click(Button.left, 1)
		# Спим маленькими порциями, чтобы быстро реагировать на выключение
		elapsed = 0.0
		step = 0.05
		while elapsed < CLICK_DELAY:
			with lock:
				if not clicking:
					break
			time.sleep(step)
			elapsed += step
	print("[ВЫКЛ] Автокликер остановлен")


def toggle_clicker():
	global clicking
	with lock:
		if not clicking:
			clicking = True
			threading.Thread(target=click_loop, daemon=True).start()
		else:
			clicking = False


def on_press(key):
	try:
		# F4 — старт/стоп автокликера
		if key == keyboard.Key.f4:
			threading.Thread(target=toggle_clicker, daemon=True).start()

		# ESC — выход
		if key == keyboard.Key.esc:
			global clicking
			with lock:
				clicking = False
			print("Выход из программы...")
			return False
	except Exception as e:
		print(f"Ошибка: {e}")


print("Скрипт запущен.")
print(f"Нажмите F4 — вкл/выкл автокликер ЛКМ (задержка {CLICK_DELAY} сек).")
print("Нажмите ESC для полного закрытия скрипта.")

with keyboard.Listener(on_press=on_press) as listener:
	listener.join()
