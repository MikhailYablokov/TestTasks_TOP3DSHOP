# Web Scraping для сайта Creality

Этот скрипт используется для сбора информации о сканерах с сайта Creality Store. Он извлекает данные о товаре, такие как название, цена, предполагаемая дата доставки и ссылка на продукт. Данные сохраняются в форматах CSV и Excel.

Описание:
---
Этот скрипт собирает информацию о сканерах с сайта Creality Store. Он заходит на страницу с товарами, извлекает ссылки на страницы с деталями каждого товара, а затем для каждой страницы собирает данные, такие как название товара, его цену и предполагаемую дату доставки. Все собранные данные сохраняются в формате CSV и Excel для дальнейшего использования. В процессе работы скрипт выводит логи в консоль, показывая ссылки на товары и информацию о каждом обработанном товаре.

Установка:
---
```bash
pip install -r requirements.txt
```

Запуск:
---
```bash
python scraper.py
```

