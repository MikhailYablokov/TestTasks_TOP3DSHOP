import os
import cv2
import numpy as np
from PIL import Image
from collections import defaultdict

input_folder = 'input_images'
output_folder = 'output_images'

os.makedirs(output_folder, exist_ok=True)
print(f"Создана выходная папка: {output_folder}")


# Функция для изменения размера и оптимизации
def process_image(image_path, output_path, target_width=800):
    with Image.open(image_path) as img:
        print(f"Обрабатывается {image_path}, исходный размер: {img.width}x{img.height}, режим: {img.mode}")
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            print(f"Конвертировано из RGBA в RGB для {image_path}")
        if img.width > target_width:
            ratio = target_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
            print(f"Изменен размер {image_path} до {target_width}x{new_height}")
        else:
            print(f"Размер {image_path} не изменен (меньше или равен {target_width}px)")
        img.save(output_path, optimize=True, quality=85)
        print(f"Сохранено оптимизированное изображение: {output_path}")


# Функция для вычисления SSIM между двумя изображениями
def compute_ssim(img1_path, img2_path):
    # Загружаем изображения через OpenCV
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        print(f"Ошибка загрузки одного из изображений: {img1_path} или {img2_path}")
        return 0

    # Приводим к одному размеру (меньшему из двух)
    min_height = min(img1.shape[0], img2.shape[0])
    min_width = min(img1.shape[1], img2.shape[1])
    img1 = cv2.resize(img1, (min_width, min_height))
    img2 = cv2.resize(img2, (min_width, min_height))

    # Конвертируем в градации серого
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Вычисляем SSIM
    score = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
    print(f"SSIM между {img1_path} и {img2_path}: {score}")
    return score


# Шаг 2: Удаление дублей с приоритетом на большее разрешение
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
print(f"Найдено файлов в {input_folder}: {len(image_files)} -> {image_files}")

if not image_files:
    print("Ошибка: в папке input_images нет подходящих файлов!")
    exit()

# Группируем дубли с использованием SSIM
threshold = 0.9  # Порог схожести
groups = []
processed = set()

for i, file1 in enumerate(image_files):
    if file1 in processed:
        continue
    group = [file1]
    file1_path = os.path.join(input_folder, file1)

    for j, file2 in enumerate(image_files[i + 1:], start=i + 1):
        if file2 in processed:
            continue
        file2_path = os.path.join(input_folder, file2)
        similarity = compute_ssim(file1_path, file2_path)
        if similarity >= threshold:
            group.append(file2)
            processed.add(file2)

    processed.add(file1)
    if group:
        groups.append(group)

# Выбираем изображение с максимальной шириной из каждой группы
unique_images = []
for group in groups:
    print(f"Группа дублей: {group}")
    sorted_group = sorted(group, key=lambda x: Image.open(os.path.join(input_folder, x)).width, reverse=True)
    print(f"Отсортировано по ширине: {sorted_group}")
    unique_images.append(os.path.join(input_folder, sorted_group[0]))
    print(f"Выбрано: {sorted_group[0]}")

# Шаги 3 и 4: Изменение размера и оптимизация
print(f"Уникальные изображения для обработки: {unique_images}")
for i, image_path in enumerate(unique_images[:2]):
    output_filename = f'processed_image_{i + 1}.jpg'
    output_path = os.path.join(output_folder, output_filename)
    process_image(image_path, output_path)

print(f"Обработано изображений: {min(len(unique_images), 2)}")
print(f"Файлы сохранены в: {output_folder}")
print("Названия файлов: processed_image_1.jpg, processed_image_2.jpg")