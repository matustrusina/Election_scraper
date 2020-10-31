import Scraper_module


def main():

    print('''
This script scrapes election data from a site 
and puts them into a csv file. 
    ''')

    county_url = Scraper_module.get_url()

    print('Your data is being downloaded. This may take a while...')

    city_data = Scraper_module.bs4_scrape1(county_url)
    names_list = Scraper_module.get_city_names(city_data)
    partial_urls = Scraper_module.get_city_url(city_data)
    number_list = Scraper_module.get_city_number(city_data)

    Scraper_module.city_parse(partial_urls)
    Scraper_module.file_creator()


if __name__ == '__main__':
    main()
