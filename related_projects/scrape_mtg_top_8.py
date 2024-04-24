from bs4 import BeautifulSoup
import requests
import datetime
import time

NAME = "ravnica_standard"
FORMAT = "ST" #ST, MO, PAU, LE, PI?
DATE_START = ""
DATE_END = ""

CARDLIST_PATH = r""
CREATE_PATH = r""

def main():
    cardlist = get_cardlist(CARDLIST_PATH)
    decks_by_card = {}
    max_decks_for_one_card = 0

    for card in cardlist:
        decks_with_card = get_all_decks(card)
        if decks_with_card != []:
            # add decks to full dict
            decks_by_card[card] = decks_with_card
            # update the maximum number of decks that any one card appears in
            if len(decks_with_card) > max_decks_for_one_card:
                print(len(decks_with_card))
                max_decks_for_one_card = len(decks_with_card)

    create_sql_db_from_decks(decks_by_card, CREATE_PATH, NAME, max_decks_for_one_card)

def get_cardlist(cardlist_path):
    """Returns a list containing the lines of a file."""
    s = ""
    with open(cardlist_path) as f:
        s = f.read()
    return s.split("\n")

def get_all_decks(card):
    """
    Uses the process_request and get_decks functions to get either
		60 Professional decks,
		55 Professional/Major decks,
		or 50 Professional/Major/Competitive decks
    containing the card, which are returned as a list.
    """
    # if the card has seen no play at all, return an empty list
    initial_request = format_request(card, min_level=2, format=FORMAT, date_start=DATE_START, date_end=DATE_END)
    initial_soup = process_request(initial_request)
    initial_decks = get_decks(initial_soup)
    if len(initial_decks) == 0:
        return []

    # otherwise, find the card's best decks
    decks_with_card = []

    # get up to 60 Professional decks
    request = format_request(card, min_level=4, format=FORMAT, date_start=DATE_START, date_end=DATE_END)
    soup = process_request(request), card
    while soup:
        decks_with_card.extend(get_decks(soup))
        if len(decks_with_card) < 60:
            soup = next_page(soup, request)
    # if subsequent steps will add nothing, store the decks and skip to the next card
    if len(decks_with_card) >= 50:
        return decks_with_card[:60]

    # get up to 50 Major decks
    request = format_request(card, min_level=3, max_level=3, format=FORMAT, date_start=DATE_START, date_end=DATE_END)
    soup = process_request(request)
    while soup:
        decks_with_card.extend(get_decks(soup))
        if len(decks_with_card) < 50:
            soup = next_page(soup, request)
    # if subsequent steps will add nothing, store the decks and skip to the next card
    if len(decks_with_card) >= 40:
        return decks_with_card[:50]

    # get up to 40 Competitive decks
    request = format_request(card, min_level=2, max_level=2, format=FORMAT, date_start=DATE_START, date_end=DATE_END)
    soup = process_request(request)
    while soup:
        decks_with_card.extend(get_decks(soup))
        if len(decks_with_card) < 40:
            soup = next_page(soup, request)
    return decks_with_card[:40]

def process_request(request_obj):
    """Sends the request periodically, until a response is given, then returns the response as a BeautifulSoup"""
    while(True):
        time.sleep(1.5)
        try:
            response = requests.get(r"https://www.mtgtop8.com/search", params=request_obj)
            if response.status_code != 200:
                print(response.status_code)
            break
        except:
            time.sleep(6.5)
            continue
    return assert_soup(BeautifulSoup(response.content, 'html.parser'), request_obj)

def assert_soup(soup, request_obj):
    """Ensures that soup has no error messages"""
    if soup.font:
        print("card name error:")
        print(request_obj["cards"])
        return None
    else:
        return soup

def format_request(card, format="", min_level=1, sideboard=True, date_start=False, date_end=False):
    """Creates a POST request for mtgtop8 to get info about a certain card's role in a certain format.
    It is a json object.
    
    Scraping requires a lot of hard coded lines that doesn't make much sense without the server-side code for the website."""
    request_obj = {}
    request_obj["current_page"] = ""
    request_obj["event_titre"] = "" # sic
    request_obj["deck_titre"] = "" # sic
    request_obj["player"] = ""
    request_obj["format"] = format

    # I haven't found a need for these yet, but it doesn't hurt to include them
    # request_obj["archetype_sel[VI]"] = ""
    # request_obj["archetype_sel[LE]"] = ""
    # request_obj["archetype_sel[MO]"] = ""
    # request_obj["archetype_sel[PI]"] = ""
    # request_obj["archetype_sel[EX]"] = ""
    # request_obj["archetype_sel[HI]"] = ""
    # request_obj["archetype_sel[ST]"] = ""
    # request_obj["archetype_sel[BL]"] = ""
    # request_obj["archetype_sel[PAU]"] = ""
    # request_obj["archetype_sel[EDH]"] = ""
    # request_obj["archetype_sel[HIGH]"] = ""
    # request_obj["archetype_sel[EDHP]"] = ""
    # request_obj["archetype_sel[CHL]"] = ""
    # request_obj["archetype_sel[PEA]"] = ""
    # request_obj["archetype_sel[EDHM]"] = ""
    # request_obj["archetype_sel[ALCH]"] = ""
    # request_obj["archetype_sel[cEDH]"] = ""
    # request_obj["archetype_sel[EXP]"] = ""
    # request_obj["archetype_sel[PREM]"] = ""

    # include all decks whose level is greater than or equal to min_level
    if min_level <= 4:
        request_obj["compet_check[P]"] = 1
    if min_level <= 3:
        request_obj["compet_check[M]"] = 1
    if min_level <= 2:
        request_obj["compet_check[C]"] = 1
    if min_level <= 1:
        request_obj["compet_check[R]"] = 1

    # always look for the card in mainboards, and may also look in sideboards
    request_obj["MD_check"] = 1
    if sideboard:
        request_obj["SB_check"] = 1

    # we are looking for a particular card
    request_obj["cards"] = card
    request_obj["date_start"] = ""

    # date is formatted dd/mm/yyyy
    if date_start:
        day = str(date_start.day) if date_start.day >= 10 else "0" + str(date_start.day)
        month = str(date_start.month) if date_start.month >= 10 else "0" + str(date_start.month)
        request_obj["date_start"] = day + "/" + month + "/" + str(date_start.year)
    request_obj["date_end"] = ""
    if date_end:
        day = str(date_end.day) if date_end.day >= 10 else "0" + str(date_end.day)
        month = str(date_end.month) if date_end.month >= 10 else "0" + str(date_end.month)
        request_obj["date_end"] = day + "/" + month + "/" + str(date_end.year)

    return request_obj

def get_decks(soup):
    """Returns a list where each element is the information about one deck."""
    decks = []
    decklist_table = soup.find("form", {"name":"compare_decks"})
    for row in decklist_table.find_all(class_="hover_tr"):
        deck = []
        columns = row.find_all("td")
        # read links from Deck, Player and Event columns
        for column in (1,2,4):
            deck.append(columns[column].a.string)
        # read plaintext from Format, Rank and Date columns
        for column in (3,6,7):
            deck.append(columns[column].string)
        # count the number of stars in Level column
        images = columns[5].find_all("img")
        if len(images) == 3:
            deck.append("Major")
        elif len(images) == 2:
            deck.append("Competitive")
        elif len(images) == 1 and images[0]["src"] == "/graph/star.png":
            deck.append("Regular")
            print("Regular at ", end="")
            print(row)
        elif len(images) == 1 and images[0]["src"] == "/graph/bigstar.png":
            deck.append("Professional")
        else:
            deck.append("No Level")
            print("No Level for tournament \"" + columns[4].a.string + "\"")
            continue # to skip events with no level
        # get deck link from Deck column
        deck.append(columns[1].a["href"])

        decks.append(deck)
    return decks

def next_page(soup, request):
    """Clicks on the 'Next' button of an mtgtop8 page and returns the result as a BeautifulSoup, or False if there are no more pages."""
    nav_bar_items = soup.find_all("div", class_="Nav_norm")

    # if there is only one page, return False
    if nav_bar_items == []:
        return False
    
    # if on the last page, return False
    if soup.find(class_="Nav_PN_no") and soup.find(class_="Nav_PN_no").string == "Next":
        return False
    
    # otherwise, find the button for the current page and increase its number by 1
    page_num = soup.find(class_="Nav_cur").string
    page_num = str(int(page_num) + 1)
    request["current_page"] = page_num
    return process_partial_request(request)

def create_sql_db_from_decks(decks, path, database_name, max_num_decks_for_one_card):
    """ Creates an SQL query which will create a relational database of cards and decks.
        Each card corresponds to a row of a cards table, each deck corresponds to a row of a decks table, 
        and each row of the cards table has the foreign keys of one or more rows of the decks table.
    """

    # the SQL query is not constructed from start to finish, but each of three sections of the query is.
    # those sections are the creation of the database and tables, the insertion of cards into one table,
    # and the insertion of decks into the other table
    header = ""
    deck_table_row_creation = ""
    card_table_row_creation = ""

    unique_decks = {}

    # Header Code
    # -----------
    # create the database
    header += "DROP DATABASE IF EXISTS " + database_name + ";\n"
    header += "CREATE DATABASE " + database_name + ";\n"
    header += "USE " + database_name + ";\n\n"
    
    # create the tables
    header += """CREATE TABLE decks (
deck_id varchar(255) NOT NULL,
deck_name varchar(255) NOT NULL,
player varchar(255) NOT NULL,
rank_achieved varchar(255) NOT NULL,
competition_level varchar(255) NOT NULL,
event_date date,
PRIMARY KEY(deck_id)
);

CREATE TABLE cards (
card_id int NOT NULL AUTO_INCREMENT,
card_name varchar(255) NOT NULL,
"""
    # the number of columns in the cards table depends on how many foreign keys it needs.
    # it needs just enough foreign keys for the card with the most decks to see all of those decks.
    for i in range(1, max_num_decks_for_one_card + 1):
        header += "deck_id" + str(i) + " varchar(255),\n"
    header += "PRIMARY KEY(card_id),\n"
    for i in range(1, max_num_decks_for_one_card):
        header += "FOREIGN KEY(deck_id" + str(i) + ") REFERENCES decks(deck_id),\n"
    header += "FOREIGN KEY(deck_id" + str(max_num_decks_for_one_card) + ") REFERENCES decks(deck_id)\n);\n\n"

    # Code to Insert Rows in Cards Table
    # ---------------------------------
    for card,decks_with_card in decks.items():
        # start an insertion statement for the card table
        card_table_row_creation += "INSERT into cards (card_name"
        # state how many columns the row will have
        for i in range(1, len(decks_with_card) + 1):
            card_table_row_creation += ", deck_id" + str(i)
        # specify that the first column of the row is the card's name
        # apostrophes and pluses are removed because apostrophes break the query and pluses are unnecessary
        card_table_row_creation += ") VALUES (\n'" + str(card).replace("'", "").replace("+", " ") + "'" 
        
        for deck in decks_with_card:
            # if this deck has yet to be seen, save it so it can be inserted into the decks table
            unique_decks[deck[-1][6:]] = deck
             
            # add the deck as a column of the insertion statement
            card_table_row_creation += ", '" + str(deck[-1][6:]) + "'"
        # finish the insertion statement
        card_table_row_creation += "\n);\n\n"

    # Code to Insert Rows in Decks Table
    # ---------------------------------
    # all but the last deck are separated by columns in the insertion statement for the card table
    list_unique_decks = list(unique_decks.values())
    for deck in list_unique_decks:
        # start an insertion statement for the deck table with the deck's id
        deck_table_row_creation += "INSERT into decks VALUES (\n'" + str(deck[7][6:]) + "'"
        
        # add columns to the insertion statement in the correct order
        for column in (0,1,4,6):
            deck_table_row_creation += ", '" + str(deck[column]).replace("'", "") + "'"
        # add the last column, with slashes replaced by dashes to fit SQL design sensibilities
        try:
            (d, m, y) = str(deck[5]).split("/")
            deck_table_row_creation += ", '" + y + "-" + m + "-" + d + "'\n);\n\n"
        except:
            print(deck[5])
            pass
    
    # write the complete query to a .sql file
    with open (path, "wb") as f:
        f.write((header + deck_table_row_creation + card_table_row_creation).encode("utf-8"))

if __name__ == "__main__":
    main()