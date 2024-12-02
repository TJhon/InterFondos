import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.options import Options
import time, os


SAVE_INTEBANK = "data/interbank"
funds = "interfondos_funds_name.csv"


class InterfondosScraper:
    EXCHANGE_OPTION = "/html/body/app-root/app-history-calculator/div/app-content/section[2]/div[2]/div[1]/div/div[1]/div/div[2]/select"
    ITERFONDOS = "/html/body/app-root/app-history-calculator/div/app-content/section[2]/div[2]/div[1]/div/div[2]/div/div[2]/select"

    def __init__(self, url="https://www.interfondos.com.pe/grafico-desempeno"):
        """
        Initialize the scraper with a webdriver and navigate to the specified URL
        """
        self.driver = webdriver.Edge()
        self.driver.get(url)
        self.driver.implicitly_wait(4)

    def get_fondos(self, moneda):
        """
        Retrieve fund options for a given currency

        :param moneda: Currency type
        :return: List of fund dictionaries
        """
        sub_select = self.driver.find_element(By.XPATH, self.ITERFONDOS)
        options = sub_select.find_elements(By.TAG_NAME, "option")

        sub_select_data = [
            {
                "value": opt.get_attribute("value").strip(),
                "text": opt.text.strip(),
                "moneda": moneda,
            }
            for opt in options
        ]
        return sub_select_data

    def scrape_funds(self):
        """
        Scrape fund options for different currencies

        :return: pandas DataFrame with fund information
        """

        main_select = self.driver.find_element(By.XPATH, self.EXCHANGE_OPTION)
        main_select_object = Select(main_select)

        # Get first currency option
        first_option = main_select_object.first_selected_option.text.strip()
        first_funds = self.get_fondos(first_option)

        # Switch to second currency option
        main_select_object.select_by_index(1)
        time.sleep(2)
        second_option = main_select_object.first_selected_option.text.strip()
        second_funds = self.get_fondos(second_option)

        # Combine and convert to DataFrame
        all_funds = first_funds + second_funds
        return pd.DataFrame(all_funds)

    def close(self):
        """
        Close the webdriver
        """
        self.driver.quit()


def main():
    try:

        scraper = InterfondosScraper()

        funds_df = scraper.scrape_funds()
        os.makedirs(SAVE_INTEBANK, exist_ok=True)
        funds_df.to_csv(f"{SAVE_INTEBANK}/{funds}", index=False)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure driver is closed
        scraper.close()


if __name__ == "__main__":
    main()
