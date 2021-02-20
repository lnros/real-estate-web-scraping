import os
import time

import pandas as pd
from selenium import webdriver
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

URL = 'https://www.onmap.co.il/en'
PROPERTY_TYPE_IDX = 1
NUM_OF_ROOMS_IDX = 0
FLOOR_IDX = 1
SIZE_IDX = 2
PARKING_SPACES_IDX = 3
SCROLL_PAUSE_TIME = 2
COLUMNS = ['Property_type', 'Address', 'Price[NIS]', 'Rooms', 'Floor', 'Area[m^2]', 'Parking_spots']


def create_driver():
    # silent web_driver log
    os.environ['WDM_LOG_LEVEL'] = '0'
    opts = webdriver.ChromeOptions()
    opts.headless = True
    return webdriver.Chrome(ChromeDriverManager().install(), options=opts)


def scroll(driver, verbose=False):
    prev_len = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")
    scroll_num = 1
    while True:
        ele_to_scroll = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")[-1]
        driver.execute_script("arguments[0].scrollIntoView();", ele_to_scroll)
        if verbose:
            print(f"Scroll nº {scroll_num}\n")
        time.sleep(SCROLL_PAUSE_TIME)
        new_len = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")
        if prev_len == new_len:
            break
        prev_len = new_len
        scroll_num += 1


def scrap_url(driver, url, to_print=True, save=False, verbose=False):
    if verbose:
        print(f'Accessing {url}')
    driver.get(url)
    if verbose:
        print(f"Scrolling down {url}")
    scroll(driver)
    if verbose:
        print(f"Scraping {url}")
    prices = (price.text for price in driver.find_elements_by_xpath("//span[@class='cWr2cxa0k3zKePxbqpw3L']"))
    prop_types = (prop_type.text.split('\n')[PROPERTY_TYPE_IDX] for prop_type in
                  driver.find_elements_by_xpath("//div[@class='_1bluUEiq7lEDSV1yeF9mjl']"))
    addresses = (address.text for address in driver.find_elements_by_xpath("//div[@property='address']"))
    nums_rooms = (num_rooms.text.split()[NUM_OF_ROOMS_IDX] for num_rooms in
                  driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    floors = (floor.text.split()[FLOOR_IDX] for floor in
              driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    sizes = (size.text.split()[SIZE_IDX] for size in
             driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    parking_spaces = (parking.text.split()[PARKING_SPACES_IDX] if len(parking.text.split()) > PARKING_SPACES_IDX else 0
                      for parking in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    if to_print:
        zipped = zip(prices, prop_types, addresses, nums_rooms, floors, sizes, parking_spaces)
        for price, prop_type, address, num_rooms, floor, size, parking in zipped:
            print(f"Price: {price}, Type: {prop_type}, Address: {address}, "
                  f"Nº Rooms: {num_rooms}, Floor: {floor}, Size {size}, Parking: {parking_spaces}")

    if save:
        filename = f"{url.split('/')[-1]}.csv"
        if verbose:
            print(f'Saving {filename}')
        df = pd.DataFrame(data=[prop_types, addresses, prices, nums_rooms, floors, sizes, parking_spaces],
                          columns=COLUMNS)
        df.to_csv(filename)


def main():
    urls = {'buy': URL + '/homes/buy',
            'rent': URL + '/homes/rent'}
    # html arranged differently
    # 'commercial': URL + '/commercial/rent/',
    # 'new homes': URL + '/projects/'}
    driver = create_driver()
    for url in tqdm(urls.values()):
        scrap_url(driver, url, to_print=True, verbose=True)

    # prev_len = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")
    # prices = []
    # prop_types = []
    # addresses = []
    # nums_rooms = []
    # floors = []
    # sizes = []
    # parking_spaces = []
    # scroll = 1
    # while True:
    #     print(scroll)
    #     ele_to_scroll = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")[-1]
    #     driver.execute_script("arguments[0].scrollIntoView();", ele_to_scroll)
    #     time.sleep(SCROLL_PAUSE_TIME)
    #     append_list_as_elements(prices, (price.text for price in
    #                                      driver.find_elements_by_xpath("//span[@class='cWr2cxa0k3zKePxbqpw3L']")))
    #     append_list_as_elements(prop_types, (prop_type.text.split('\n')[PROPERTY_TYPE_IDX] for prop_type in
    #                                          driver.find_elements_by_xpath("//div[@class='_1bluUEiq7lEDSV1yeF9mjl']")))
    #     append_list_as_elements(addresses, (address.text for address in
    #                                         driver.find_elements_by_xpath("//div[@property='address']")))
    #     append_list_as_elements(nums_rooms, (num_rooms.text.split()[NUM_OF_ROOMS_IDX] for num_rooms in
    #                                          driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
    #     append_list_as_elements(floors, (floor.text.split()[FLOOR_IDX] for floor in
    #                                      driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
    #     append_list_as_elements(sizes, (size.text.split()[SIZE_IDX] for size in
    #                                     driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
    #     append_list_as_elements(parking_spaces,
    #                             (parking.text.split()[PARKING_SPACES_IDX] if len(
    #                                 parking.text.split()) > PARKING_SPACES_IDX else 0 for parking in
    #                              driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
    #     new_len = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")
    #     if prev_len == new_len:
    #         break
    #     prev_len = new_len
    #     scroll += 1
    # for i in range(len(prices)):
    #     print(f"{i + 1}. Price: {prices[i]}, Type: {prop_types[i]}, Address: {addresses[i]}, "
    #           f"Nº Rooms: {nums_rooms[i]}, Floor: {floors[i]}, Size {sizes[i]}, Parking: {parking_spaces[i]}")
#     # Get scroll height
#     last_height = driver.execute_script("return document.body.scrollHeight")

#     while True:
#         # Scroll down to bottom
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#         # Wait to load page
#         time.sleep(SCROLL_PAUSE_TIME)

#         # Calculate new scroll height and compare with last scroll height
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
