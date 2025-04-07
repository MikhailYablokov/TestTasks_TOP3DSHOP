from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Вывод в консоль
    ]
)
logger = logging.getLogger(__name__)

class Selectors:
    """Класс с CSS-селекторами для сайта Creality"""
    PRODUCT_ITEM = ".product-item"
    PRODUCT_LINK = "a"
    PRODUCT_TITLE = ".product-main h1"
    PRODUCT_PRICE = ".product-price-on-sale .price"
    SHIPPING_INFO_ITEMS = ".product-info-item"  # Все элементы с информацией
    SHIPPING_TITLE = ".product-info-item-title span"  # Заголовок внутри элемента
    SHIPPING_CONTENT = ".product-info-item-content span"  # Содержимое даты

# Настройка Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# Шаг 1: Сбор ссылок
url = "https://store.creality.com/collections/scanners"
driver.get(url)
time.sleep(3)

scanner_links = []
products = driver.find_elements(By.CSS_SELECTOR, Selectors.PRODUCT_ITEM)
for product in products:
    try:
        link_element = product.find_element(By.TAG_NAME, Selectors.PRODUCT_LINK)
        href = link_element.get_attribute("href")
        if href and "/products/" in href:
            scanner_links.append(href)
    except Exception as e:
        logger.error(f"Ошибка при сборе ссылки: {str(e)}")

logger.info("Найденные ссылки на сканеры:")
for link in scanner_links:
    logger.info(link)

# Шаг 2: Сбор данных
scanner_data = []
wait = WebDriverWait(driver, 10)
for link in scanner_links:
    driver.get(link)
    time.sleep(2)
    try:
        name = driver.find_element(By.CSS_SELECTOR, Selectors.PRODUCT_TITLE).text.strip()
        price = driver.find_element(By.CSS_SELECTOR, Selectors.PRODUCT_PRICE).text.strip()

        # Поиск даты доставки
        shipping_info = "Not specified"
        info_items = driver.find_elements(By.CSS_SELECTOR, Selectors.SHIPPING_INFO_ITEMS)
        for item in info_items:
            try:
                title = item.find_element(By.CSS_SELECTOR, Selectors.SHIPPING_TITLE).text.strip()
                if title == "Estimated Shipping Date":
                    shipping_info = item.find_element(By.CSS_SELECTOR, Selectors.SHIPPING_CONTENT).text.strip()
                    break
            except:
                continue

        scanner_data.append({
            "Name": name,
            "Price": price,
            "Shipping": shipping_info,
            "Link": link
        })
        logger.info(f"Обработан товар: Name: {name}, Price: {price}, Shipping: {shipping_info}, Link: {link}")
    except Exception as e:
        logger.error(f"Ошибка при обработке {link}: {str(e)}")

# Закрытие драйвера
driver.quit()

# Создание DataFrame
df = pd.DataFrame(scanner_data)

# Сохранение в CSV и Excel
df.to_csv("scanner_details.csv", index=False)
df.to_excel("scanner_details.xlsx", index=False)

# Форматированный вывод
logger.info("\nИтоговая таблица:")
col_widths = {"Name": 50, "Price": 20, "Shipping": 25, "Link": 70}
header = (
    f"{'Name':<{col_widths['Name']}} | "
    f"{'Price':<{col_widths['Price']}} | "
    f"{'Shipping':<{col_widths['Shipping']}} | "
    f"{'Link':<{col_widths['Link']}}"
)
logger.info("-" * len(header))
logger.info(header)
logger.info("-" * len(header))
for _, row in df.iterrows():
    logger.info(
        f"{row['Name']:<{col_widths['Name']}} | "
        f"{row['Price']:<{col_widths['Price']}} | "
        f"{row['Shipping']:<{col_widths['Shipping']}} | "
        f"{row['Link']:<{col_widths['Link']}}"
    )
logger.info("-" * len(header))