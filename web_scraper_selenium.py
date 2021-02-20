import os
import time

from selenium import webdriver
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# silent web_driver log
os.environ['WDM_LOG_LEVEL'] = '0'

opts = webdriver.ChromeOptions()
opts.headless = True
driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)

URL = 'https://www.onmap.co.il/en'
urls = {'buy': URL + '/homes/buy',
        'rent': URL + '/homes/rent'}
# html arranged differently
# 'commercial': URL + '/commercial/rent/',
# 'new homes': URL + '/projects/'}

PROPERTY_TYPE_IDX = 1
NUM_OF_ROOMS_IDX = 0
FLOOR_IDX = 1
SIZE_IDX = 2
PARKING_SPACES_IDX = 3
SCROLL_PAUSE_TIME = 2


def append_list_as_elements(original_list, to_append):
    for elem in to_append:
        original_list.append(elem)


for url in tqdm(urls.values()):
    driver.get(url)
    prev_len = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")
    prices = []
    prop_types = []
    addresses = []
    nums_rooms = []
    floors = []
    sizes = []
    parking_spaces = []
    scroll = 1
    while True:
        print(scroll)
        ele_to_scroll = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")[-1]
        driver.execute_script("arguments[0].scrollIntoView();", ele_to_scroll)
        time.sleep(SCROLL_PAUSE_TIME)
        append_list_as_elements(prices, (price.text for price in
                                         driver.find_elements_by_xpath("//span[@class='cWr2cxa0k3zKePxbqpw3L']")))
        append_list_as_elements(prop_types, (prop_type.text.split('\n')[PROPERTY_TYPE_IDX] for prop_type in
                                             driver.find_elements_by_xpath("//div[@class='_1bluUEiq7lEDSV1yeF9mjl']")))
        append_list_as_elements(addresses, (address.text for address in
                                            driver.find_elements_by_xpath("//div[@property='address']")))
        append_list_as_elements(nums_rooms, (num_rooms.text.split()[NUM_OF_ROOMS_IDX] for num_rooms in
                                             driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
        append_list_as_elements(floors, (floor.text.split()[FLOOR_IDX] for floor in
                                         driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
        append_list_as_elements(sizes, (size.text.split()[SIZE_IDX] for size in
                                        driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
        append_list_as_elements(parking_spaces,
                                (parking.text.split()[PARKING_SPACES_IDX] if len(
                                    parking.text.split()) > PARKING_SPACES_IDX else 0 for parking in
                                 driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")))
        new_len = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")
        if prev_len == new_len:
            break
        prev_len = new_len
        scroll += 1
    for i in range(len(prices)):
        print(f"{i + 1}. Price: {prices[i]}, Type: {prop_types[i]}, Address: {addresses[i]}, "
              f"Nº Rooms: {nums_rooms[i]}, Floor: {floors[i]}, Size {sizes[i]}, Parking: {parking_spaces[i]}")
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
