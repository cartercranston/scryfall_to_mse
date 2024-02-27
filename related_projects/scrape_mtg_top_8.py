from bs4 import BeautifulSoup
import requests
import datetime

cardlist_path = r""
output_path = r""

def main():
	cardlist = get_cardlist(cardlist_path)
	decks = {}

	for card in cardlist:
		decks_with_card = []
		request_obj = format_request(card, "ST", 3, True, datetime.datetime(year=2005,month=9,day=1), datetime.datetime(year=2007,month=9,day=1))
		response = requests.get(r"https://www.mtgtop8.com/search", params=request_obj)
		soup = BeautifulSoup(response.content, 'html.parser')
		while (soup):
			decks_with_card.extend(get_decks(soup))
			soup = next_page(soup, request_obj)
		if decks_with_card != []:
			decks[card] = decks_with_card

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
	
	Scraping requires a lot of hard code that doesn't make much sense without the server-side code for the website."""
	request_obj = {}
	request_obj["current_page"] = ""
	request_obj["event_titre"] = ""
	request_obj["deck_titre"] = ""
	request_obj["player"] = ""
	request_obj["format"] = format
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
	if level <= 4:
		request_obj["compet_check%5BP%5D"] = 1
	if level <= 3:
		request_obj["compet_check%5BM%5D"] = 1
	if level <= 2:
		request_obj["compet_check%5BC%5D"] = 1
	if level <= 1:
		request_obj["compet_check%5BR%5D"] = 1
	request_obj["MD_check"] = 1
	if sideboard:
		request_obj["SB_check"] = 1
	request_obj["cards"] = card
	request_obj["date_start"] = ""
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
	"""Returns a list where each element consists of information about a deck."""
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
		elif images[0]["src"] == "/graph/star.png":
			deck.append("Regular")
		elif images[0]["src"] == "/graph/bigstar.png":
			deck.append("Professional")
		else:
			print("issue with images:\n" + str(images))
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

if __name__ == "__main__":
	main()