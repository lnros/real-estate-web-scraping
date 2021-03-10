import time
from config import Configuration as Cfg
from selenium_scraper import SeleniumScraper
from utils import print_when_program_finishes


def main():
    Cfg.define_parser()
    urls = [Cfg.URLS[key] for key in Cfg.LISTING_MAP[Cfg.args.property_listing_type]]
    for i, url in enumerate(urls):
        params = {"limit": Cfg.args.limit,
                  "to_print": Cfg.args.print,
                  "save": Cfg.args.save,
                  "verbose": Cfg.args.verbose,
                  "to_database": Cfg.args.database,
                  "listing_type": Cfg.LISTING_MAP[Cfg.args.property_listing_type][i]}
        time.sleep(Cfg.BETWEEN_URL_PAUSE)
        scraper = SeleniumScraper()
        scraper.scrap_url(url, **params)
        scraper.driver.close()
        scraper.driver.quit()

    print_when_program_finishes()


if __name__ == '__main__':
    main()
