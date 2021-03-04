from dateutil import parser


def return_row_before_print(row):
    # selenium
    try:
        return f"Price: {row['Price[NIS]']}, Type: {row['Property_type']}, City: {row['City_name']}, " \
               f"Address: {row['Street_name']}, {row['House_number']}, Nº Rooms: {row['Rooms']}, Floor: {row['Floor']}, Size {row['Area[m^2]']}," \
               f" Parking underground: {row['Parking_spots_underground']}, Parking above ground: {'Parking_spots_aboveground'}"
    except KeyError:
        # soup
        return f"Price: {row['Price[NIS]']}, Type: {row['Property_type']}, City: {row['City']}, " \
               f"Address: {row['Address']}, Nº Rooms: {row['Rooms']}, Floor: {row['Floor']}, Size {row['Area[m^2]']}," \
               f" Parking: {row['Parking_spots']}"


def create_df_row(property_dict):
    """
    Given a dictionary with property information, transform it into a dictionary to be used as a dataframe row
    """
    try:
        df_row = {'Date': [parser.parse(property_dict['created_at']).date()],
                  'City_name': [property_dict['address']['en']['city_name']],
                  'Street_name': [property_dict['address']['en']['street_name']],
                  'House_number': [property_dict['address']['en']['house_number']],
                  'Bathrooms': [property_dict['additional_info']['bathrooms']],
                  'Rooms': [property_dict['additional_info']['rooms']],
                  'Floor': [property_dict['additional_info']['floor']['on_the']],
                  'Area[m^2]': [property_dict['additional_info']['area']['base']],
                  'Parking_spots_aboveground': [
                      property_dict['additional_info'].get('parking', {}).get('aboveground')],
                  'Parking_spots_underground': [
                      property_dict['additional_info'].get('parking', {}).get('underground')],
                  'Price[NIS]': [property_dict['price']],
                  'Property_type': [property_dict['property_type']]
                  }
        return df_row
    except KeyError:
        # TODO Take care of new project in buy
        pass


def print_when_program_finishes():
    print('\nDone!\n')


def print_access(url, verbose=True):
    if verbose:
        print(f'\nAccessing {url}\n')


def print_scrolling(url, verbose=True):
    if verbose:
        print(f"\nScrolling down {url}\n")


def print_scraping(url, verbose=True):
    if verbose:
        print(f"\nScraping {url}\n")


def print_row(df, to_print=True):
    if to_print:
        for index, row in df.iterrows():
            print(return_row_before_print(row))


def print_total_items(df, verbose=True):
    if verbose:
        num_items = len(df)
        print(f'\nScraped total of {num_items} items')


def print_scroll_num(scroll_num, verbose=True):
    if verbose:
        print(f"Scroll nº {scroll_num}")


def print_getting_url_for_regions(verbose=True):
    if verbose:
        print("Getting url for each region...")


def print_getting_regional_data(verbose=True):
    if verbose:
        print("Getting regional data...")


def print_transform_df(verbose=True):
    if verbose:
        print("Transforming the data to dataframe...")
