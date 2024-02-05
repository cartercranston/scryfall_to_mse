from bs4 import BeautifulSoup
import requests
import datetime

cardlist_path = r"C:\Users\Carter\Documents\Gaming\Magic-Set-Editor\Sets\cardlists\Ravnica City of Guilds.txt"

def main():
	cardlist = get_cardlist(cardlist_path)
	for card in cardlist:
		request = format_request("ST", 3, True, datetime.datetime(year=2005,month=9,day=1), datetime.datetime(year=2007,month=9,day=1), card)
		response = requests.post(request)
		print(response.text)

def get_cardlist(cardlist_path):
	"""Returns a list containing the lines of a file."""
	names = []
	with open(cardlist_path) as f:
		s = f.read()
	for name in s.split("\n"):
		names.append(name.replace(" ","+"))
	return names

def format_request(format, level, sideboard, date_start, date_end, card):
	"""Creates a POST request for mtgtop8 to get info about a certain card's role in a certain format.
	
	Scraping requires a lot of hard code that doesn't make much sense without the server-side code for the website"""
	s = r"https://www.mtgtop8.com/search?current_page="
	s += r"&event_titre=&deck_titre=&player="
	s += r"&format="
	if format:
		s += format
	s += r"&archetype_sel%5BVI%5D=&archetype_sel%5BLE%5D=&archetype_sel%5BMO%5D=&archetype_sel%5BPI%5D=&archetype_sel%5BEX%5D=&archetype_sel%5BHI%5D=&archetype_sel%5BST%5D=&archetype_sel%5BBL%5D=&archetype_sel%5BPAU%5D=&archetype_sel%5BEDH%5D=&archetype_sel%5BHIGH%5D=&archetype_sel%5BEDHP%5D=&archetype_sel%5BCHL%5D=&archetype_sel%5BPEA%5D=&archetype_sel%5BEDHM%5D=&archetype_sel%5BALCH%5D=&archetype_sel%5BcEDH%5D=&archetype_sel%5BEXP%5D=&archetype_sel%5BPREM%5D="
	if level <= 4:
		s += r"&compet_check%5BP%5D=1"
	if level <= 3:
		s += r"&compet_check%5BM%5D=1"
	if level <= 2:
		s += r"&compet_check%5BC%5D=1"
	if level <= 1:
		s += r"&compet_check%5BR%5D=1"
	s += r"&MD_check=1"
	if sideboard:
		s += r"&SB_check=1"
	s += r"&cards="
	s += card + "%0D%0A"
	s += r"&date_start="
	if date_start:
		day = str(date_start.day) if date_start.day >= 10 else "0" + str(date_start.day)
		month = str(date_start.year) if date_start.month >= 10 else "0" + str(date_start.month)
		s += day + r"%2F" + month + r"%2F" + str(date_start.year)
	s += r"&date_end="
	if date_end:
		day = str(date_end.day) if date_end.day >= 10 else "0" + str(date_end.day)
		month = str(date_end.year) if date_end.month >= 10 else "0" + str(date_end.month)
		s += day + r"%2F" + month + r"%2F" + str(date_end.year)
	return s



if __name__ == "__main__":
	main()