def return_row_before_print(row):
    return f"Price: {row['Price[NIS]']}, Type: {row['Property_type']}, City: {row['City']}, " \
           f"Address: {row['Address']}, Nº Rooms: {row['Rooms']}, Floor: {row['Floor']}, Size {row['Area[m^2]']}," \
           f" Parking: {row['Parking_spots']}"


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
        print(f'\nScraped total of {num_items} items\n')


def print_scroll_num(scroll_num, verbose=True):
    if verbose:
        print(f"Scroll nº {scroll_num}")


