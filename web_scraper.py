import time
from config import Configuration as Cfg
from config import Logger as Log
from selenium_scraper import SeleniumScraper
from utils import print_when_program_finishes


def main():
    """
    This program scrapes real estate information from 'https://www.onmap.co.il/en' and it can:
    - Print it to the user
    - Save it to csv
    - Save into a database
    A Google Chrome webpage will open and close for every different url it scrapes within the website.
    There are at most 4 different pages for it to scrape: buy, rent, commercial, new homes
    If the user chooses to fetch more information, beware that this is a lengthy process that
    takes around one second per property scraped.
    """
    Log.start_logging()
    Cfg.define_parser()
    Log.logger.info(Log.main_cli)
    urls = [Cfg.URLS[key] for key in Cfg.LISTING_MAP[Cfg.args.property_listing_type]]
    if len(urls) == 0:
        Log.logger.error(Log.main_no_url)
    for i, url in enumerate(urls):
        params = {Cfg.LIMIT_KEY: Cfg.args.limit,
                  Cfg.PRINT_KEY: Cfg.args.print,
                  Cfg.SAVE_KEY: Cfg.args.save,
                  Cfg.VERBOSE_KEY: Cfg.args.verbose,
                  Cfg.DB_KEY: Cfg.args.database,
                  Cfg.FETCH_KEY: Cfg.args.fetch,
                  Cfg.LISTING_TYPE_KEY: Cfg.LISTING_MAP[Cfg.args.property_listing_type][i]}
        time.sleep(Cfg.BETWEEN_URL_PAUSE)
        Log.logger.debug(Log.main_scrape_obj)
        scraper = SeleniumScraper()
        Log.logger.debug(Log.main_scraping(url))
        scraper.scrap_url(url, **params)
        Log.logger.debug(Log.main_closing_driver)
        scraper.driver.close()
        Log.logger.debug(Log.main_quit_drive)
        scraper.driver.quit()
        Log.logger.info(Log.main_scraped_success(url))

    print_when_program_finishes()


if __name__ == '__main__':
    main()
