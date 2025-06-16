# COBERTURA TDT
# https://television.digital.gob.es/2DD-5G/Paginas/Que-tengo-que-hacer.aspx
import time
from init_selenium.init_driver import *
import pprint
import json
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

# from typing import Any

WEB_URL = "https://television.digital.gob.es/2DD-5G/Paginas/Que-tengo-que-hacer.aspx"


def erase_keystrokes(dr: webdriver.Chrome, wt: WebDriverWait):
    """
    Erase keystrokes in the input field.
    """
    # Wait for the element to be present
    try:
        # Wait for the element to be present
        wt.until(ec.element_to_be_clickable((By.ID, "cp"))).send_keys(5 * Keys.BACKSPACE)

    except TimeoutException:
        raise TimeoutException("Coverage not found")


def extract_coverage_tdt(dr: webdriver.Chrome, wt: WebDriverWait):
    """
    Extract coverage information from the TDT website when cp has been introduced.
    """
    # Wait for the element to be present
    try:
        # Wait for the element to be present
        # cp_elem, pb = wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultados")))[0].text.split(" ")[::2]
        # print(f"Postal code: {cp}")
        elems = wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultados")))[0]
        cp_elem, pb_elem = elems.find_elements(By.CSS_SELECTOR, "dd")
        cp = cp_elem.text
        pb = pb_elem.text

        print(f"Population: {pb}")
        try:
            mult_dig = [i.text for i in wt.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "td[headers='multiple-digital']")))]
            center = [i.text for i in
                      wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "td[headers='centro']")))]
            chanel = [i.text for i in
                      wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "td[headers='canal']")))]
            ordered_data = list(zip(mult_dig, center, chanel))
            pprint.pprint(ordered_data)
        except TimeoutException:
            ordered_data = []
        time.sleep(.1)

        return cp, pb, ordered_data

    except TimeoutException:
        raise TimeoutException("Coverage not found")


def coverage_tdt(cp: str, drivers: tuple[webdriver.Chrome, WebDriverWait] = None):
    """
    https://television.digital.gob.es/2DD-5G/Paginas/Que-tengo-que-hacer.aspx
    """
    assert 999 < int(cp) < 53000, "Invalid postal code"
    # dr, wt = create_driver(window_size=MIN, undetectable=True)
    is_there_cookies = False
    if not drivers:
        cookies = None
        # We cannot continue without cookies else program will crash
        try:
            with open("tdtc_cookies.json", "r") as f:
                cookies = json.load(f)
                is_there_cookies = True
                print(cookies)
        except FileNotFoundError:
            pass

        dr, wt = create_driver(window_size=WINDOW_MAX, undetectable=True, wait_time=3, cookies=cookies,
                               initial_url=WEB_URL)
    else:
        dr, wt = drivers
        erase_keystrokes(dr, wt)
    time.sleep(.2)

    if not is_there_cookies:
        wt.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cookies-action='acceptAll']"))).click()

    with open("tdtc_cookies.json", "w") as f:
        json.dump(dr.get_cookies(), f)
    # try:
    #     wt.until(ec.element_to_be_clickable((By.XPATH, "//button[.=Aceptar sólo necesarias']"))).click()
    # except (NoSuchElementException, ElementClickInterceptedException):
    #     print("No cookies button found or not clickable, continuing...")

    wt.until(ec.element_to_be_clickable((By.ID, "cp"))).send_keys(str(cp))
    # try:

    wt.until(ec.element_to_be_clickable((By.ID, "btnBuscar"))).click()

    # except ElementClickInterceptedException:
    #     print("Element not clickable, trying again...")
    #     time.sleep(.3)
    #     wt.until(ec.element_to_be_clickable((By.ID, "btnBuscar"))).click()

    # if wt.until(ec.presence_of_element_located((By.XPATH, "//span[.='El texto introducido no corresponde a ningún Código Postal']"))):
    #     print("Coverage found")

    try:
        ret_cp, ret_pb, ordered_data = extract_coverage_tdt(dr, wt)

        return {
            "Postal code": cp,
            "Populations":
                [{"Population": ret_pb,
                  "Data": ordered_data}]
        }, dr, wt
    except TimeoutException:
        # try:
        # selector = wt.until(ec.presence_of_element_located((By.ID, "cmbPoblaciones")))
        num_options = len(wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "option"))))
        # print(len(options))
        # print(options)

        json_data = {
            "Postal code": cp,
            "Populations": []
        }

        print("options:", num_options)
        for num in range(num_options):
            selector = wt.until(ec.presence_of_element_located((By.ID, "cmbPoblaciones")))
            options = wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "option")))
            option = options[num]
            print(option.text)
            selector.click()
            option.click()
            wt.until(ec.element_to_be_clickable((By.ID, "btnBuscar"))).click()
            time.sleep(.2)
            cp_ret, pb_ret, ordered_data = extract_coverage_tdt(dr, wt)
            json_data["Populations"].append({
                "Population": pb_ret,
                "Data": ordered_data
            })
            time.sleep(.1)
            dr.execute_script("window.history.back();")
            # erase_keystrokes(dr, wt)
        print(json_data)
        return json_data, dr, wt

        # except Exception as e:
        #     if not drivers:
        #         dr.quit()
        #     else:
        #         return {}

    # time.sleep(3)
    # input("Press Enter to continue...")
    # dr.quit()


def get_all_coverage_data(output_file: str = "coverage_data.jsonl",
                          start: int = None,
                          end: int = None,
                          progress_file: str = "progress.txt") -> None:
    """
    Collects coverage data for postal codes in a given range and saves each result incrementally to a JSONL file.
    Resumes from the last processed postal code if start is None and progress_file exists.
    """
    # Resume from the last ID in the progress file if start is None
    if start is None and os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            last_id = f.read().strip()
            if last_id.isdigit():
                start = int(last_id) + 1
                print(f"Resuming from last postal code: {start}")
            else:
                raise ValueError("Invalid data in progress file. Please check its contents.")

    elif start is None:
        start = 1000  # Default start postal code if no progress file exists

    if end is None:
        end = 52999  # Default end postal code if not specified

    assert start < end, "Start postal code must be less than end postal code"
    assert start > 999, "Start postal code must be greater than 999"
    assert end < 53000, "End postal code must be less than 53000"

    # Initialize drivers for the first time
    _, drr, wtt = coverage_tdt("01006")

    with open(output_file, "a", encoding="utf-8") as f:  # Open file in append mode

        for postal_code in range(start, end + 1):  # Iterate through the specified range
            if postal_code < 10000:
                postal_code_str = f"0{postal_code}"  # Format postal code as 5 digits
            else:
                postal_code_str = str(postal_code)

            # Save the current postal code to the progress file
            with open(progress_file, "w", encoding="utf-8") as progress_f:
                progress_f.write(str(postal_code))

            try:
                print(f"Processing postal code: {postal_code_str}")
                data, drr, wtt = coverage_tdt(postal_code_str, drivers=(drr, wtt))

                if data:
                    # Write the data to the file as a JSON object
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    print(f"Saved data for postal code: {postal_code_str}")

            except TimeoutException:
                print(f"Timeout for postal code: {postal_code_str}. Skipping...")

    print(f"Data collection completed. Results saved to {output_file}")


if __name__ == "__main__":
    # Para todas las comunidades autonomas
    # get_all_coverage_data("coverage_data.json")
    data = coverage_tdt("01000")
    print(data)
    # Solo para Castilla y León
    # castilla_y_leon_codes = {
    #     "León": ["24000", "24999"],
    #     "Salamanca": ["37000", "37999"],
    #     "Valladolid": ["47000", "47999"],
    #     "Zamora": ["49000", "49999"],
    #     "Palencia": ["34000", "34999"],
    #     "Soria": ["42000", "42999"],
    #     "Ávila": ["05000", "05999"],
    #     "Burgos": ["09000", "09999"],
    #     "Segovia": ["40000", "40999"]
    # }

    # Collect data for all provinces and save to a JSON file
    # all_data = {}
    # for province, (a, b) in castilla_y_leon_codes.items():
    #     print(f"Processing province: {province}")
    #     get_all_coverage_data(
    #         output_file="CYL_tdtc.json",  # Do not save to individual files
    #         start=int(a),
    #         end=int(b),
    #         progress_file="progress_CYL.txt"
    #     )
