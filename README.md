Selenium Parser для сайта Creality
---
Этот скрипт используется для сбора информации о сканерах с сайта Creality Store. Он извлекает данные о товаре, такие как название, цена, предполагаемая дата доставки и ссылка на продукт. Данные сохраняются в форматах CSV и Excel.

## Описание:
Этот скрипт собирает информацию о сканерах с сайта Creality Store. Он заходит на страницу с товарами, извлекает ссылки на страницы с деталями каждого товара, а затем для каждой страницы собирает данные, такие как название товара, его цену и предполагаемую дату доставки. Все собранные данные сохраняются в формате CSV и Excel для дальнейшего использования. В процессе работы скрипт выводит логи в консоль, показывая ссылки на товары и информацию о каждом обработанном товаре.

# Установка:
```bash
pip install -r requirements.txt
```

# Запуск:

```bash
python T1_SeleniumParser.py
```

# Работа программы:
![image](https://github.com/user-attachments/assets/d252d7d7-69d9-48dc-9182-3fc7b881180c)


Standardize Image
---
Этот скрипт обрабатывает изображения из папки input_images, удаляет дубликаты, основываясь на коэффициенте сходства SSIM, и сохраняет уникальные изображения в папке output_images. Для каждого изображения из группы дублей выбирается версия с наибольшей шириной. Затем изображения изменяются по размеру до ширины 800 пикселей, конвертируются в формат RGB (если необходимо) и оптимизируются для уменьшения размера файла. Обработанные изображения сохраняются в формате JPEG с качеством 85%.

# Запуск:
```bash
python T2_StandardizeImage.py
```

# Работа программы:

Prompt Sequence
---
Этот скрипт автоматизирует процесс обработки видео с YouTube. Он извлекает аудио из видео, транскрибирует его с помощью модели Whisper и генерирует ответы на заранее заданные промпты с использованием API Together.ai. Скрипт поддерживает загрузку промптов из файлов, скачивание аудио с YouTube, обработку аудио для транскрипции и сохранение транскрипций и ответов в текстовые файлы. Логи сохраняются в файл для отслеживания выполнения. Выходные данные включают ответы на каждый промпт, связанные с содержанием видео.

# Запуск
```bash
python T3_PromptSequence.py
```
Также необходимо получить API-token together ai. Создать файл .env и вставить строку:
```
TOGETHER_API_KEY=<YOUR-API-KEY>
```

# Работа программы






