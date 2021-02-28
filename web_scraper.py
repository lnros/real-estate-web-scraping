from config import Configuration
from selenium_scraper import SeleniumScraper
from utils import print_when_program_finishes


def main():
    Configuration.define_parser()
    urls = [Configuration.URLS[key] for key in Configuration.LISTING_MAP[Configuration.args.property_listing_type]]
    scraper = SeleniumScraper()
    params = {"to_print": Configuration.args.print,
              "save": Configuration.args.save,
              "verbose": Configuration.args.verbose}
    for url in urls:
        scraper.scrap_url(url, **params)
        scraper.driver.close()
    scraper.driver.quit()
    print_when_program_finishes()


if __name__ == '__main__':
    main()
