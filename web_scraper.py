import time
from config import Configuration as Cfg
from config import Logger as Log
from selenium_scraper import SeleniumScraper
from utils import print_when_program_finishes


def main():
    Log.start_logging()
    Cfg.define_parser()
    Log.logger.info('main: CLI parser was successfull.')
    urls = [Cfg.URLS[key] for key in Cfg.LISTING_MAP[Cfg.args.property_listing_type]]
    if len(urls) == 0:
        Log.logger.error('main: No urls found to scrape.')
    for i, url in enumerate(urls):
        params = {"limit": Cfg.args.limit,
                  "to_print": Cfg.args.print,
                  "save": Cfg.args.save,
                  "verbose": Cfg.args.verbose,
                  "to_database": Cfg.args.database,
                  "listing_type": Cfg.LISTING_MAP[Cfg.args.property_listing_type][i]}
        time.sleep(Cfg.BETWEEN_URL_PAUSE)
        Log.logger.debug("main: Creating the scraper object")
        scraper = SeleniumScraper()
        Log.logger.debug(f"main: Scraping {url}")
        scraper.scrap_url(url, **params)
        Log.logger.debug("main: Closing driver")
        scraper.driver.close()
        Log.logger.debug("main: Quitting driver")
        scraper.driver.quit()
        Log.logger.info(f"main: Scrapped {url} successfully")

    print_when_program_finishes()


if __name__ == '__main__':
    main()
