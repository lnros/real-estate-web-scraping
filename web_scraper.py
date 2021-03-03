from config import Configuration as cfg
from selenium_scraper import SeleniumScraper
from soup_scraper import SoupScraper
from utils import print_when_program_finishes


def main():
    cfg.define_parser()
    urls = [cfg.URLS[key] for key in cfg.LISTING_MAP[cfg.args.property_listing_type]]
    # if both soup and selenium are chosen, we use soup
    if cfg.args.soup:
        params = {"limit": cfg.args.limit,
                  "to_print": cfg.args.print,
                  "save": cfg.args.save,
                  "verbose": cfg.args.verbose}
        scraper = SoupScraper()
        for listing_type in cfg.LISTING_MAP[cfg.args.property_listing_type]:
            scraper.scrap(listing_type, **params)

    elif cfg.args.selenium:
        params = {"to_print": cfg.args.print,
                  "save": cfg.args.save,
                  "verbose": cfg.args.verbose}
        scraper = SeleniumScraper()
        for url in urls:
            scraper.scrap_url(url, **params)
            scraper.driver.close()
        scraper.driver.quit()

    print_when_program_finishes()


if __name__ == '__main__':
    main()
