import os
from selenium import webdriver
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

SCROLL_PAUSE_TIME = 1

for url in urls.values():
    driver.get(url)
    prices = [price.text for price in driver.find_elements_by_xpath("//span[@class='cWr2cxa0k3zKePxbqpw3L']")]
    prop_types = [prop_type.text.split('\n')[1] for prop_type in driver.find_elements_by_xpath("//div[@class='_1bluUEiq7lEDSV1yeF9mjl']")]
    addresses = [address.text for address in driver.find_elements_by_xpath("//div[@property='address']")]
    nums_rooms = [num_rooms.text.split()[0] for num_rooms in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")]
    floors = [floor.text.split()[1] for floor in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")]
    sizes = [size.text.split()[2] for size in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")]
    parking_spaces = [parking.text.split()[3] if len(parking.text.split()) > 3 else 0 for parking in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']")]

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
