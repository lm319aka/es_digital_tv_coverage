"""
Spanish Digital Terrestrial Television (DTT) Coverage Checker

This module provides functionality to check DTT coverage information for Spanish postal codes
using the official Spanish government website: https://television.digital.gob.es/

It uses Selenium with undetected-chromedriver to automate web interactions and extract coverage data.
"""
import time
# import logging
import pprint
# import json
import os
from init_selenium.init_driver import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tdtc.log')
    ]
)
logger = logging.getLogger(__name__)

WEB_URL = "https://television.digital.gob.es/2DD-5G/Paginas/Que-tengo-que-hacer.aspx"


def erase_keystrokes(dr: webdriver.Chrome, wt: WebDriverWait):
    """
    Erase any existing keystrokes in the postal code input field.
    
    Args:
        dr: Selenium WebDriver instance
        wt: WebDriverWait instance for explicit waits
        
    Raises:
        TimeoutException: If the input field is not found or not interactable
    """
    try:
        # Wait for the postal code input field to be clickable and erase previous input
        wt.until(ec.element_to_be_clickable((By.ID, "cp"))).send_keys(5 * Keys.BACKSPACE)

    except TimeoutException:
        time.sleep(.2)
        try:
            wt.until(ec.element_to_be_clickable((By.ID, "cp"))).send_keys(5 * Keys.BACKSPACE)
        except TimeoutException:
            logger.error("Postal code input field not found or not interactable.")
            #raise TimeoutException("Postal code input field not found or not interactable.")
        #raise TimeoutException("Coverage not found")
    except StaleElementReferenceException:
        time.sleep(.2)
        try:
            wt.until(ec.element_to_be_clickable((By.ID, "cp"))).send_keys(5 * Keys.BACKSPACE)
        except StaleElementReferenceException:
            logger.error("Postal code input field not found or not interactable.")
        #raise TimeoutException("Postal code input field is stale or not interactable.")


def extract_coverage_tdt(dr: webdriver.Chrome, wt: WebDriverWait) -> tuple[str, str, list]:
    """
    Extract DTT coverage information from the website after a postal code has been searched.
    
    Args:
        dr: Selenium WebDriver instance
        wt: WebDriverWait instance for explicit waits
        
    Returns:
        tuple: Contains (postal_code, population, coverage_data) where:
            - postal_code (str): The postal code being queried
            - population (str): The population center name
            - coverage_data (list): List of tuples with (multiple_digital, center, channel, first_option) information
            
    Raises:
        TimeoutException: If the coverage data elements are not found
    """
    try:
        # dr.refresh()
        # Extract postal code and population information
        elems = wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultados")))[0]
        cp_elem, pb_elem = elems.find_elements(By.CSS_SELECTOR, "dd")
        cp = cp_elem.text
        pb = pb_elem.text

        logger.info(f"Processing population: {pb}")
        try:
            mult_dig = [i.text for i in wt.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "td[headers='multiple-digital']")))]
            center = [i.text for i in
                      wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "td[headers='centro']")))]
            channel = [i.text for i in
                      wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "td[headers='canal']")))]
            
            first_op_len_code = 'return document.getElementsByClassName("datos")[0].getElementsByTagName("tbody")[0].getElementsByTagName("tr").length'
            first_op_len = dr.execute_script(first_op_len_code)
            first_op_list = [True for _ in range(first_op_len)] + [False for _ in range(len(channel) - first_op_len)]

            ordered_data = list(zip(mult_dig, center, channel, first_op_list))

            logger.debug(f"Coverage data: {pprint.pformat(ordered_data, width=120)}")
        except TimeoutException:
            ordered_data = []
        # time.sleep(.1)

        return cp, pb, ordered_data

    except TimeoutException:
        raise TimeoutException("Coverage not found")


def coverage_tdt(cp: str, drivers: tuple[webdriver.Chrome, WebDriverWait] = None) -> tuple[dict, webdriver.Chrome, WebDriverWait]:
    """
    Get DTT coverage information for a given Spanish postal code.
    
    Args:
        cp (str): Spanish postal code (5 digits)
        drivers (tuple, optional): Tuple containing (WebDriver, WebDriverWait) for reuse. 
                                 If None, a new browser instance will be created.
                                  
    Returns:
        tuple: (coverage_data, driver, wait) where:
            - coverage_data (dict): Dictionary containing coverage information
            - driver: Selenium WebDriver instance
            - wait: WebDriverWait instance
            
    Raises:
        AssertionError: If the postal code is not a valid Spanish postal code
    """
    # Check if the postal code is valid and within the valid range
    assert 999 < int(cp) < 53000, f"Invalid postal code: {cp}"

    # Create a new driver instance
    is_there_cookies = False
    if not drivers:
        cookies = None
        # We cannot continue without cookies or program will crash
        # A cookies file is created after the first run automatically in the same directory
        # TODO: tdtc_cookies.json is a very vage path, should be in a temp directory or user should specify directory
        try:
            with open("tdtc_cookies.json", "r") as f:
                cookies = json.load(f)
                is_there_cookies = True
                logger.debug("Loaded cookies from file")
        except FileNotFoundError:
            pass

        dr, wt = create_driver(window_size=WINDOW_MAX, undetectable=True, wait_time=2, cookies=cookies,
                               initial_url=WEB_URL)
    else:
        dr, wt = drivers
        erase_keystrokes(dr, wt)
    # time.sleep(.2)

    if not is_there_cookies:
        try:
            wt.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cookies-action='acceptAll']"))).click()
        except TimeoutException:
            pass

    with open("tdtc_cookies.json", "w") as f:
        json.dump(dr.get_cookies(), f)

    # Start the process of searching for coverage data
    wt.until(ec.element_to_be_clickable((By.ID, "cp"))).send_keys(str(cp))
    # logger.info(f"writting postal code: {cp}")
    wt.until(ec.element_to_be_clickable((By.ID, "btnBuscar"))).click()
    # logger.info("clicking search button")

    try:
        wt.until(ec.presence_of_element_located((By.XPATH, '//span[.="El texto introducido no corresponde a ningún Código Postal"]')))
        return {
            "Postal code": cp,
            "Populations": []
        }, dr, wt
    except TimeoutException:
        try:
            ret_cp, ret_pb, ordered_data = extract_coverage_tdt(dr, wt)
            logger.info(f"single population: {cp}")
            return {
                "Postal code": cp,
                "Populations":
                    [{"Population": ret_pb,
                    "Data": ordered_data}]
            }, dr, wt

        # If TimeoutException occurs, it means there are multiple populations for the postal code
        except TimeoutException:
            try:
                num_options = len(wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "option"))))
            # This postal code has no populations
            except TimeoutException:
                logger.info(f"no population: {cp}")
                return {
                    "Postal code": cp,
                    "Populations": []
                }, dr, wt
            
            json_data = {
                "Postal code": cp,
                "Populations": []
            }

            logger.info(f"Found {num_options} population options for postal code {cp}")
            for num in range(num_options):
                selector = wt.until(ec.presence_of_element_located((By.ID, "cmbPoblaciones")))
                options = wt.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "option")))
                option = options[num]
                logger.info(f"Processing option {num + 1}/{num_options}: {option.text}")
                selector.click()
                option.click()
                wt.until(ec.element_to_be_clickable((By.ID, "btnBuscar"))).click()
                time.sleep(.15)
                try:
                    cp_ret, pb_ret, ordered_data = extract_coverage_tdt(dr, wt)
                    json_data["Populations"].append({
                        "Population": pb_ret,
                        "Data": ordered_data
                    })
                    logger.debug(f"Successfully processed population: {pb_ret}")
                except Exception as e:
                    logger.error(f"Error processing population option {option.text}: {str(e)}")
                time.sleep(.1)
                dr.execute_script("window.history.back();")
            logger.debug(f"Final data for postal code {cp}: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
            logger.info(f"multiple populations: {cp}")
            return json_data, dr, wt


def get_all_coverage_data(output_file: str,
                          progress_file: str,
                          start: int = None,
                          end: int = None
                          ) -> None:
    """
    Collect DTT coverage data for a range of Spanish postal codes.
    
    This function processes postal codes sequentially, saving results to a JSONL file and
    maintaining progress to allow resuming interrupted operations.
    
    Args:
        output_file (str): Path to save the JSONL output file
        start (int, optional): Starting postal code (inclusive). If None, will resume from progress file.
        end (int, optional): Ending postal code (inclusive). Defaults to 52999.
        progress_file (str): File to store progress for resuming interrupted operations.
        
    Note:
        The function saves results incrementally, so even if interrupted, previously processed
        postal codes will be preserved in the output file.
    """
    # Resume from the last ID in the progress file if start is None
    if start is None and os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            last_id = f.read().strip()
            if last_id.isdigit():
                start = int(last_id) + 1
                logger.info(f"Resuming from last processed postal code: {start}")
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
    _, drr, wtt = coverage_tdt("09999")

    with open(output_file, "a", encoding="utf-8") as f:  # Open file in append mode

        for postal_code in range(start, end + 1):  # Iterate through the specified range
            if postal_code < 10000:
                postal_code_str = f"0{postal_code}"  # Format postal code as 5 digits
            else:
                postal_code_str = str(postal_code)

            # Save the current postal code to the progress file
            with open(progress_file, "w", encoding="utf-8") as progress_f:
                progress_f.write(str(postal_code))

            # try:
            logger.info(f"Processing postal code: {postal_code_str}")
            data, drr, wtt = coverage_tdt(postal_code_str, drivers=(drr, wtt))
            # logger.debug(f"Data for postal code: {data}")
            if data["Populations"]:
                # Write the data to the file as a JSON object
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
                logger.info(f"data for postal code: {data}")
                logger.info(f"Successfully processed and saved data for postal code: {postal_code_str}")

            # except TimeoutException:
            #     logger.warning(f"Timeout while processing postal code: {postal_code_str}. Skipping...")
            # except Exception as e:
            #     logger.error(f"Unexpected error processing postal code {postal_code_str}: {str(e)}")


    logger.info(f"Data collection completed. Results saved to {os.path.abspath(output_file)}")
    logger.info(f"Logs are available in {os.path.abspath('tdtc.log')}")

if __name__ == "__main__":
    import sys

    postal_code_data = sys.argv[1] if len(sys.argv) > 1 else exit(1)
    pprint.pprint(coverage_tdt(postal_code_data))
    