# Web scraping OnMap
https://github.com/lnros/real-estate-web-scraping

This web scraper get the data from properties for sale and rent from  the Israeli [OnMap](https://www.onmap.co.il/en/)  website.

The website has four main data sources: buy, rent, new homes and commercial data.


#### Buy:
Properties for sale

#### Rent:
Properties for rent

#### Commercial:
Commercial properties for rent

#### New homes:
Properties that are on planning or construction phase


## Two web scraper versions

With both versions it is possible to either print the results to the screen or to save them in csv files.

### The slow (but 100% scraping)
This version accesses each webpage we want to scrap information from and, with
[Selenium](https://www.selenium.dev/selenium/docs/api/py/index.html#).

New homes not implemented yet.

Web scraper script name: web_scraper_selenium.py

Usage: web_scraper_selenium.py [-h] [--print] [--save] [--verbose]
                               {buy,rent,commercial,new_homes,all}

positional arguments: <br>
&nbsp;&nbsp;&nbsp;&nbsp;   {buy,rent,commercial,new_homes,all}
                       choose which type of properties you would like to scrape

optional arguments:<br>
&nbsp;&nbsp;&nbsp;&nbsp;   -h, --help            show this help message and exit<br>
&nbsp;&nbsp;&nbsp;&nbsp;   --print, -p           print the results to the screen<br>
&nbsp;&nbsp;&nbsp;&nbsp;   --save, -s            save the scraped information into a csv file in the
                        same directory<br>
&nbsp;&nbsp;&nbsp;&nbsp;   --verbose, -v         prints messages during the scraper execution<br>

##### Known issues:
When scraping properties for sale (in buy), there are new homes as well inside. There is less information about them, which causes an asymmetry and potential mismatch in the information scraped.
### The fast and efficient (but less scraping)
This version accesses directly the website database server and collects the information stored in JSON format.
Uses [requests](https://requests.readthedocs.io) and 
[BeautifulSoup](https://readthedocs.org/projects/beautiful-soup-4/)
mostly to get the job done. This version only scraps buy and rent properties.

Web scraper script name: on_map_web_scaper.py

How to use it: run it from the command line.

Usage: on_map_web_scraper.py [-h] [--limit n] [--todir path] {buy,rent,all}

positional arguments: <br>
 &nbsp;&nbsp;&nbsp;&nbsp; {buy,rent,all}   'buy' or 'rent' or 'all'

optional arguments: <br>
 &nbsp;&nbsp;&nbsp;&nbsp;   -h, --help       show this help message and exit <br>
  &nbsp;&nbsp;&nbsp;&nbsp;  --limit n, -l n  limit to n number of properties per region <br>
  &nbsp;&nbsp;&nbsp;&nbsp;  --todir path     save the scraped information into a csv file in the given
directory <br>


#### Authors
@lnros - Leonardo Rosenberg <br>
@Shahar9772 - Shahar Shoshany