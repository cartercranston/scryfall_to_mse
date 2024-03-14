from bs4 import BeautifulSoup
import requests
import datetime

cardlist_path = r""
create_path = r""

def main():
	cardlist = get_cardlist(cardlist_path)
	decks = {}
	max_decks_for_one_card = 0

	for card in cardlist[:5]:
		decks_with_card = []
		request_obj = format_request(card, format="ST", level=3, date_start=datetime.datetime(year=2005,month=9,day=1), date_end=datetime.datetime(year=2007,month=9,day=1))
		response = requests.get(r"https://www.mtgtop8.com/search", params=request_obj)
		soup = BeautifulSoup(response.content, 'html.parser')
		while (soup):
			decks_with_card.extend(get_decks(soup))
			soup = next_page(soup, request_obj)
		if decks_with_card != []:
			decks[card] = decks_with_card

			# update the maximum number of decks that any one card appears in
			if len(decks_with_card) > max_decks_for_one_card:
				max_decks_for_one_card = len(decks_with_card)

	create_sql_db_from_decks(decks, create_path, "ravnica_standard", max_decks_for_one_card)

def get_cardlist(cardlist_path):
	"""Returns a list containing the lines of a file."""
	names = []
	with open(cardlist_path) as f:
		s = f.read()
	for name in s.split("\n"):
		names.append(name.replace(" ","+"))
	return names

def format_request(card, format="", level=1, sideboard=True, date_start=False, date_end=False):
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
	request_obj["archetype_sel%BVI%5D"] = ""
	request_obj["archetype_sel%BLE%5D"] = ""
	request_obj["archetype_sel%BMO%5D"] = ""
	request_obj["archetype_sel%BPI%5D"] = ""
	request_obj["archetype_sel%BEX%5D"] = ""
	request_obj["archetype_sel%BHI%5D"] = ""
	request_obj["archetype_sel%BST%5D"] = ""
	request_obj["archetype_sel%BBL%5D"] = ""
	request_obj["archetype_sel%BPAU%5D"] = ""
	request_obj["archetype_sel%BEDH%5D"] = ""
	request_obj["archetype_sel%BHIGH%5D"] = ""
	request_obj["archetype_sel%BEDHP%5D"] = ""
	request_obj["archetype_sel%BCHL%5D"] = ""
	request_obj["archetype_sel%BPEA%5D"] = ""
	request_obj["archetype_sel%BEDHM%5D"] = ""
	request_obj["archetype_sel%BALCH%5D"] = ""
	request_obj["archetype_sel%BcEDH%5D"] = ""
	request_obj["archetype_sel%BEXP%5D"] = ""
	request_obj["archetype_sel%BPREM%5D"] = ""

	# include all decks whose level is greater than or equal to level
	if level <= 4:
		request_obj["compet_check%5BP%5D"] = 1
	if level <= 3:
		request_obj["compet_check%5BM%5D"] = 1
	if level <= 2:
		request_obj["compet_check%5BC%5D"] = 1
	if level <= 1:
		request_obj["compet_check%5BR%5D"] = 1

	# always look for the card in mainboards, and may also look in sideboards
	request_obj["MD_check"] = 1
	if sideboard:
		request_obj["SB_check"] = 1

	# we are looking for a particular card
	request_obj["cards"] = card
	request_obj["date_start"] = ""

	# date is formatted dd/mm/yyyy, with the slashes being encoded as %2F
	if date_start:
		day = str(date_start.day) if date_start.day >= 10 else "0" + str(date_start.day)
		month = str(date_start.year) if date_start.month >= 10 else "0" + str(date_start.month)
		request_obj["date_start"] = day + r"%2F" + month + r"%2F" + str(date_start.year)
	request_obj["date_end"] = ""
	if date_end:
		day = str(date_end.day) if date_end.day >= 10 else "0" + str(date_end.day)
		month = str(date_end.year) if date_end.month >= 10 else "0" + str(date_end.month)
		request_obj["date_end"] = day + r"%2F" + month + r"%2F" + str(date_end.year)

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
			deck.append("Competitive")
		elif len(images) == 2:
			deck.append("Major")
		elif len(images) == 1 and images[0]["src"] == "/graph/star.png":
			deck.append("Regular")
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
	"""Clicks on the 'Next' button and returs the resulting page as a BeautifulSoup, or False if there are no more pages."""
	nav_bar_items = soup.find_all(class_="Nav_norm")

	# if there is only one page, return False
	if nav_bar_items == []:
		return False
	
	# if on the last page, return False
	if soup.find_all(class_="Nav_PN_no") != []:
		return False
	
	# otherwise, find the button for the current page and increase its number by 1
	page_num = soup.find(class_="Nav_cur").string
	page_num = str(int(page_num) + 1)
	request["current_page"] = page_num
	return BeautifulSoup(requests.post(request).content, 'html.parser')

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
rank_achieved integer NOT NULL,
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
	print(unique_decks)
	list_unique_decks = list(unique_decks.values())
	print(list_unique_decks)
	for deck in list_unique_decks:
		# start an insertion statement for the deck table with the deck's id
		deck_table_row_creation += "INSERT into decks VALUES (\n'" + str(deck[7][6:]) + "'"
		
		# add columns to the insertion statement in the correct order
		for column in (0,1,4,6):
			deck_table_row_creation += ", '" + str(deck[column]).replace("'", "") + "'"
		# add the last column, with slashes replaced by dashes to fit SQL design sensibilities
		deck_table_row_creation += ", '" + str(deck[5]).replace("/","-") + "'\n);\n\n"
	
	# write the complete query to a .sql file
	with open (path, "w") as f:
		f.write(header + deck_table_row_creation + card_table_row_creation)

if __name__ == "__main__":
	main()