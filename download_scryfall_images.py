import requests #getting scryfall data
import os #making directories on my operating system
import shutil # deleting directories on my operating system
import sys 
import formatting

def check_status(response):
	"""Ensure that all requests to Scryfall are successful"""
	if response.status_code != 200:
		print(response.status_code + ": " + response)
		sys.exit(1)

def get_scryfall_data(set_code):
	"""Create a list containing information about each card in a certain Magic set"""
	# get set data and URIs from scryfall api
	response = requests.get("https://api.scryfall.com/sets/" + set_code)
	check_status(response)

	# get cards from scryfall api, using search URI
	response = requests.get(response.json()["search_uri"])
	check_status(response)

	cards = []
	while True:
		# add the text of each card on the current page to a list along with a URI for its artwork
		for card in response.json()["data"]:
			cards.append({"name":card["name"], "mana_cost":card["mana_cost"], "image_uri":card["image_uris"]["art_crop"], "type":card["type_line"], "rarity":card["rarity"], "text_box":card["oracle_text"], "watermark":card.get("watermark",""), "pt":(card.get("power", "") + "/" + card.get("toughness", "")), "artist":card["artist"]})
		# go to next page, or break
		if response.json()["has_more"] == True:
			response = requests.get(response.json()["next_page"])
			check_status(response)
		else:
			break
	# return the list of card names and artwork URIs
	return cards

def make_folders(image_folder_path, text_folder_path, cards):
	"""Uses json data from scryfall to create a folder of jpgs with card images and a folder of text files for keyboard_controller to read"""
	# delete folders if they already exist
	if image_folder_path and os.path.isdir(image_folder_path):
		shutil.rmtree(image_folder_path)
	if text_folder_path and os.path.isdir(text_folder_path):
		shutil.rmtree(text_folder_path)
	# create folders
	if image_folder_path:
		os.makedirs(image_folder_path)
		print("creating image folder at " + image_folder_path)
	if text_folder_path:
		os.makedirs(text_folder_path)
		print("creating text folder at " + text_folder_path)

	# for each card, get its image and text, then add them to the folders
	for card in cards:
		# certain characters are prohibited in filenames
		for special_char in (':','?','/','&','#','!','-'):
			card["name"] = card["name"].replace(special_char, '')
		if image_folder_path:
			add_to_image_folder(image_folder_path, card["name"], requests.get(card["image_uri"]))
		if text_folder_path:
			add_to_text_folder(text_folder_path, card["name"], card["mana_cost"], card["type"], card["rarity"], card["text_box"], card["watermark"], card["pt"], card["artist"])
	
def add_to_image_folder(folder_path, cardname, file):
	"""Add a jpg to the folder for images"""
	# multiple land cards can have the same name, but different artworks
	while os.path.exists(folder_path + cardname + ".jpg"):
		cardname = cardname + "1"
	
	# add the image to a file
	with open(folder_path + cardname + ".jpg", "xb") as f:
		f.write(file.content)

def add_to_text_folder(folder_path, cardname, mana_cost, type, rarity, text_box, watermark, pt, artist):
	"""Format the other card data, make a text file and add it to the folder for keyboard_controller"""
	# if card has been processed already, don't do it again
	if os.path.exists(folder_path + cardname + ".txt"):
		return
	
	# add the text to a file
	with open(folder_path + cardname + ".txt", "xb") as f:
		tab = "\n\ntab\n\n"

		s = ""
		s += tab # notes
		s += tab # tombstone
		s += tab + cardname
		s += tab + formatting.format_mana_cost(mana_cost)
		s += tab + formatting.format_art(cardname)
		s += tab * 2 # frame
		s += tab + formatting.format_type(type)
		s += tab + formatting.format_rarity(rarity)
		s += tab + formatting.format_text_box(text_box)
		s += tab + formatting.format_watermark(watermark)
		s += tab + formatting.format_pt(pt)
		s += tab # custom numbering
		s += tab # list indicator
		s += tab + artist
		s += tab # end
		f.write(s.encode("utf-8"))