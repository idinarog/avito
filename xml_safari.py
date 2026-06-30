import time
from selenium import webdriver
from selenium.webdriver.common.by import By

XML_URL = "https://raw.githubusercontent.com/idinarog/avitoxml/main/avito_feed_1_20260630_000431.xml"


def check_xml():
    driver = webdriver.Safari()

    try:
        print("🌐 Открываем Avito...")
        driver.get("https://autoload.avito.ru/format/xmlcheck/")

        time.sleep(3)

        print("✏️ Вставляем XML...")
        input_field = driver.find_element(By.NAME, "xml_url")
        input_field.send_keys(XML_URL)

        print("🚀 Отправляем...")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("⏳ Ждем...")
        time.sleep(7)

        result = driver.find_element(By.TAG_NAME, "body").text

        print("\n📊 РЕЗУЛЬТАТ:\n")
        print(result[:2000])

    except Exception as e:
        print("❌ Ошибка:", e)

    finally:
        driver.quit()


if __name__ == "__main__":
    check_xml()