import os

# Путь к вашей рабочей директории
DATASET_PATH = r"D:\ProjectsHF\physics-russian"


def analyze_physics_dataset(root_path):
	total_lines = 0
	total_chars = 0
	file_count = 0

	# Проходим по всем элементам в корневой папке
	for item in os.listdir(root_path):
		item_path = os.path.join(root_path, item)

		# Проверяем, что это папка и её имя состоит из 3 цифр (например, 001, 002...)
		if os.path.isdir(item_path) and item.isdigit() and len(item) == 3:
			# Читаем файлы только внутри этой папки датасета
			for file in os.listdir(item_path):
				# Нас интересуют исключительно файлы .json (игнорируем report-*.md)
				if file.endswith(".json"):
					file_path = os.path.join(item_path, file)

					try:
						with open(
							file_path, "r", encoding="utf-8", errors="ignore"
						) as f:
							content = f.read()

							total_chars += len(content)
							total_lines += len(content.splitlines())
							file_count += 1
					except Exception as e:
						print(f"Ошибка при чтении файла {file_path}: {e}")

	# Вывод результатов
	print("=" * 50)
	print(f"Успешно обработано JSON-файлов: {file_count} (ожидалось 625)")
	print(f"Общее количество строк в датасете: {total_lines:,}")
	print(f"Общее количество символов в датасете: {total_chars:,}")
	print("=" * 50)


if __name__ == "__main__":
	analyze_physics_dataset(DATASET_PATH)
