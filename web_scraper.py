import time
from config import Configuration as Cfg
from selenium_scraper import SeleniumScraper
from soup_scraper import SoupScraper
from utils import print_when_program_finishes


def main():
    Cfg.define_parser()
    urls = [Cfg.URLS[key] for key in Cfg.LISTING_MAP[Cfg.args.property_listing_type]]
    # if both soup and selenium are chosen, we use soup
    if Cfg.args.scraper_type == 'soup':
        params = {"limit": Cfg.args.limit,
                  "to_print": Cfg.args.print,
                  "save": Cfg.args.save,
                  "verbose": Cfg.args.verbose}
        scraper = SoupScraper()
        for listing_type in Cfg.LISTING_MAP[Cfg.args.property_listing_type]:
            scraper.scrap(listing_type, **params)

    elif Cfg.args.scraper_type == 'selenium':
        params = {"to_print": Cfg.args.print,
                  "save": Cfg.args.save,
                  "verbose": Cfg.args.verbose}
        for url in urls:
            time.sleep(3)
            scraper = SeleniumScraper()
            scraper.scrap_url(url, **params)
            scraper.driver.close()
            scraper.driver.quit()

    print_when_program_finishes()


if __name__ == '__main__':
    main()
