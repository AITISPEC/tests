import threading
import time
from pynput import keyboard
from pynput.mouse import Button, Controller

# Инициализируем контроллер мыши
mouse = Controller()

# Флаг состояния: True — мышь зажата, False — отпущена
is_pressed = False
# Блокировка для безопасной работы с потоками
lock = threading.Lock()


def toggle_mouse():
    global is_pressed
    with lock:
        if not is_pressed:
            is_pressed = True
            print("[ВКЛ] ЛКМ зажата")
            mouse.press(Button.left)
        else:
            is_pressed = False
            mouse.release(Button.left)
            print("[ВЫКЛ] ЛКМ отпущена")


def on_press(key):
    try:
        # Устанавливаем клавишу F4 как переключатель
        if key == keyboard.Key.f4:
            # Запускаем в отдельном потоке, чтобы не блокировать клавиатурный хук
            threading.Thread(target=toggle_mouse).start()

        # Экстренный выход из скрипта по нажатию клавиши ESC
        if key == keyboard.Key.esc:
            print("Выход из программы...")
            # На всякий случай отпускаем мышь перед выходом
            mouse.release(Button.left)
            return False  # Останавливает слушатель клавиатуры
    except Exception as e:
        print(f"Ошибка: {e}")


# Запуск отслеживания клавиатуры
print("Скрипт запущен.")
print("Нажмите F4 для включения/выключения зажатия ЛКМ.")
print("Нажмите ESC для полного закрытия скрипта.")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
