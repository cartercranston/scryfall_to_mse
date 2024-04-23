import os, codecs, csv

PATH = os.path.join("BRO statistics", "")
FILENAMES = os.listdir(PATH)
EXPECTED_COLUMNS = ("Name","Color","Rarity","# Seen","ALSA","# Picked","ATA","# GP",r"% GP","GP WR","# OH","OH WR","# GD","GD WR","# GIH","GIH WR","# GNS","GNS WR","IWD")
CONST_COLUMNS = ("Name","Color","Rarity")
DRAFT_COLUMNS = ("#Picked","ATA",r"Played %")
DRAFT_COLUMN_MODIFIERS = ("", "Trad. ", "Top ")
INGAME_COLUMNS = ("GP WR","IWD","OHI")
INGAME_COLUMN_MODIFIERS = ("", "Trad. ", "Top ", "Early ", "White ", "Blue ", "Black ", "Red ", "Green ")
CONST_FILENAME = "default_card_ratings.csv"
DRAFT_FILENAMES = ("default_card_ratings.csv","traditional_draft_card_ratings.csv","top_user_card_ratings.csv")
INGAME_FILENAMES = ("default_card_ratings.csv","traditional_draft_card_ratings.csv","top_user_card_ratings.csv","first_2_weeks_card_ratings.csv")
FILENAME_COLOURS = ("w","u","b","r","g","wu","wb","wr","wg","ub","ur","ug","br","bg","rg","wub","wur","wug","wbr","wbg","wrg","ubr","ubg","urg","brg")
WANTED_COLUMNS = []
for column in CONST_COLUMNS:
	WANTED_COLUMNS.append(column)
for column in DRAFT_COLUMNS:
	for modifier in DRAFT_COLUMN_MODIFIERS:
		WANTED_COLUMNS.append(modifier + column)
for column in INGAME_COLUMNS:
	for modifier in INGAME_COLUMN_MODIFIERS:
		WANTED_COLUMNS.append(modifier + column)

CSV_NAME = 0
CSV_COLOUR = 1
CSV_RARITY = 2
CSV_NUMPICKED = 5
CSV_ATA = 6
CSV_NUMGP = 7
CSV_PERCENTGP = 8
CSV_GPWR = 9
CSV_NUMOH = 10
CSV_OHWR = 11
CSV_NUMGIH = 14
CSV_GIHWR = 15
CSV_NUMGNS = 16
CSV_GNSWR = 17
CSV_IWD = 18

COLOUR_GP_INDEX = 0
COLOUR_OH_INDEX = 1
COLOUR_GIH_INDEX = 2
COLOUR_GNS_INDEX = 3

# method written by SKG, https://www.stefangordon.com/remove-bom-mark-from-text-files-in-python/
def remove_bom_inplace(path):
	"""Removes BOM mark, if it exists, from a file and rewrites it in-place"""
	buffer_size = 4096
	bom_length = len(codecs.BOM_UTF8)

	with open(path, "r+b") as fp:
		chunk = fp.read(buffer_size)
		if chunk.startswith(codecs.BOM_UTF8):
			i = 0
			chunk = chunk[bom_length:]
			while chunk:
				fp.seek(i)
				fp.write(chunk)
				i += len(chunk)
				fp.seek(bom_length, os.SEEK_CUR)
				chunk = fp.read(buffer_size)
			fp.seek(-bom_length, os.SEEK_CUR)
			fp.truncate()


def assert_filename(filename):
	"""Ensures that there is a file with the given name in the folder of csv files."""
	if filename not in FILENAMES:
		print("missing file " + filename)
		exit()

def write_grid_to_file(header, grid):
	"""Convert the header, then the grid, into a list of comma-separated values. Write the result into a file."""
	s = ""
	for row in header:
		for column in row[:-1]:
			s += str(column) + ","
		s += str(row[-1]) + "\n"
	for row in grid:
		for column in row[:-1]:
			s += str(column) + ","
		s += str(row[-1]) + "\n"
	with open("condensed_BRO_statistics.csv", "w") as f:
		f.write(s)

def extract(double_string):
	"""Removes quotation marks from a string, converts it to a float if it's a number, then returns it"""
	s = double_string.replace("\"","").rstrip()

	# return empty strings as-is
	if s == "":
		return ""
	# return percentages as floating point numbers
	if s[-1] == "%":
		try:
			return float(s.rstrip("%"))/100
		except(TypeError,ValueError):
			pass
	if s[-2:] == "pp":
		try:
			return float(s.rstrip("pp"))/100
		except(TypeError,ValueError):
			pass
	# return decimals and integers as floating-point numbers
	try:
		return float(s)
	# return other strings as-is, but without commas so that they don't show up in the final csv file
	except(TypeError,ValueError):
		return s.replace(",","")

def ratio(x, y):
	"""Return x divided by y, if possible"""
	if y == 0 or y == "" or x == "":
		return ""
	else:
		return x / y

def ratio_difference(x1, y1, x2, y2):
	"""Return the difference x1/y1 - x2/y2, if possible"""
	if y1 == 0 or y1 == "" or y2 == 0 or y2 == "" or x1 == "" or x2 == "":
		return ""
	else:
		return (x1 / y1) - (x2 / y2)

def add_to_cell(array_3d, x, y, z, val):
	"""Adds val to the x,y,zth element of array_3d, even if it was previously an empty string"""
	if isinstance(val, float):
		if array_3d[x][y][z] == "" and isinstance(val, float):
			array_3d[x][y][z] = val
		elif isinstance(val, float):
			array_3d[x][y][z] += val

def add_to_header(header, is_weighted, i, val):
	column = WANTED_COLUMNS[i]
	if "Main" in column or "WR" in column or "%" in column:
		header[2 if is_weighted else 1][i] = str(round(val * 100, 1)) + "%"
	elif "IWD" in column or "OHI" in column:
		header[2 if is_weighted else 1][i] = str(round(val * 100, 1)) + "pp"
	else:
		header[2 if is_weighted else 1][i] = str(round(val, 1))

def main():
	# determine the width and height of the input grids
	# -------------------------------------------------
	num_cards = 0
	#remove_bom_inplace(os.path.join(PATH, FILENAMES[0]))
	with open(os.path.join(PATH, FILENAMES[0]), "rt") as f:
		reader = csv.reader(f)
		# check that the columns in at least one file are correct, and count the number of rows
		columns = [extract(s) for s in next(reader)]
		if tuple(columns) != EXPECTED_COLUMNS:
			print("Incorrect columns:\n" + str(columns))
			exit()
		# count the number of rows, not including the first row
		for line in reader:
			num_cards += 1

	# create an empty output grid with a different width and height
	# -------------------------------------------------------------
	# the first three rows belong to the header
	grid_header = tuple([[""] * len(WANTED_COLUMNS) for _ in range(3)])
	for i in range(len(WANTED_COLUMNS)):
		grid_header[0][i] = WANTED_COLUMNS[i]
	grid_header[1][0] = "Mean" # Average value among unique cards in set
	grid_header[2][0] = "Average" # Average value among actual cards in packs
	# each other row corresponds to a card in the set
	grid = tuple([[""] * len(WANTED_COLUMNS) for _ in range(num_cards)])

	# initialize variables for grid header
	# ------------------------------------
	non_averaged_columns = len(CONST_COLUMNS) + (len(DRAFT_COLUMN_MODIFIERS) if "#Picked" in DRAFT_COLUMNS else 0) # the number of columns for which averaging doesn't make sense
	
	header_totals_unweighted = [0] * (len(WANTED_COLUMNS) - non_averaged_columns) # each element is the numerator of a 'Mean'
	header_totals_weighted = [0] * (len(WANTED_COLUMNS) - non_averaged_columns) # each element is the numerator of an 'Average'
	header_unweighted_denominators = [0] * (len(WANTED_COLUMNS) - non_averaged_columns) # each element is the denominator of a 'Mean'
	header_weighted_denominators = [0] * (len(WANTED_COLUMNS) - non_averaged_columns) # each element is the denominator of an 'Average'
	
	default_numpicked = [0] * num_cards # used to calculate the weighting on the White, Blue, Black, Red, and Green averages

	# add const statistics to grid
	# ----------------------------
	filename = CONST_FILENAME
	assert_filename(filename)
	with open(os.path.join(PATH, filename), "r") as f:
		reader = csv.reader(f)
		next(reader) # skip the first row, which doesn't correspond to a card
		for card_i in range(num_cards):
			l = next(reader)
			grid[card_i][name_index()] = extract(l[CSV_NAME]) # Name
			grid[card_i][colour_index()] = extract(l[CSV_COLOUR]) # Colour
			grid[card_i][rarity_index()] = extract(l[CSV_RARITY]) # Rarity

	# add draft statistics to grid
	# ----------------------------
	for mod_i in range(len(DRAFT_FILENAMES)):
		filename = DRAFT_FILENAMES[mod_i]
		assert_filename(filename)
		with open(os.path.join(PATH,filename),"r") as f:
			reader = csv.reader(f)
			next(reader) # skip the first row, which doesn't correspond to a card
			for card_i in range(num_cards):
				l = next(reader)

				# Number Picked
				numpicked = extract(l[CSV_NUMPICKED])
				if isinstance(numpicked, float):
					# store value for average calculations
					if mod_i == 0:
						default_numpicked[card_i] = numpicked
					# add to grid
					grid[card_i][numpicked_index(mod_i)] = numpicked
				else:
					# If Number Picked is missing, there's a problem
					print("missing # Picked when card is " + card_i + ", i is " + i)
					exit()

				# ATA
				ata = extract(l[CSV_ATA])
				if isinstance(ata, float):
					# store value for average calculations
					header_totals_unweighted[mod_i] += ata
					header_totals_weighted[mod_i] += ata * numpicked
					header_unweighted_denominators[ata_index(mod_i) - non_averaged_columns] += 1
					header_weighted_denominators[ata_index(mod_i) - non_averaged_columns] += numpicked
					# add to grid
					grid[card_i][ata_index(mod_i)] = str(round(ata, 2))

				# Main %
				mainboard_ratio = extract(l[CSV_PERCENTGP])
				if isinstance(mainboard_ratio, float):
					# store value for average calculations
					header_totals_unweighted[mod_i + 1 * len(DRAFT_COLUMN_MODIFIERS)] += mainboard_ratio
					header_totals_weighted[mod_i + 1 * len(DRAFT_COLUMN_MODIFIERS)] += mainboard_ratio * numpicked
					header_unweighted_denominators[mainboard_percent_index(mod_i) - non_averaged_columns] += 1
					header_weighted_denominators[mainboard_percent_index(mod_i) - non_averaged_columns] += numpicked
					# add to grid as percentage
					grid[card_i][mainboard_percent_index(mod_i)] = str(round(mainboard_ratio * 100)) + "%"

	# add ingame statistics to grid
	# -----------------------------
	for mod_i in range(len(INGAME_FILENAMES)):
		filename = INGAME_FILENAMES[mod_i]
		assert_filename(filename)
		with open(os.path.join(PATH,filename),"r") as f:
			reader = csv.reader(f)
			next(reader) # skip the first row, which doesn't correspond to a card
			for card_i in range(num_cards):
				l = next(reader)
				numpicked = extract(l[CSV_NUMPICKED])

				# GP WR
				gpwr = extract(l[CSV_GPWR])
				if isinstance(gpwr, float):
					# store value for average calculations
					header_totals_unweighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)] += gpwr
					header_totals_weighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)] += gpwr * numpicked
					header_unweighted_denominators[gpwr_index(mod_i) - non_averaged_columns] += 1
					header_weighted_denominators[gpwr_index(mod_i) - non_averaged_columns] += numpicked
					# add to grid as percentage
					grid[card_i][gpwr_index(mod_i)] = str(round(gpwr * 100)) + "%"
				
				# IWD
				iwd = extract(l[CSV_IWD])
				if isinstance(iwd, float):
					# store value for average calculations
					header_totals_unweighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS) + 1 * len(INGAME_COLUMN_MODIFIERS)] += iwd
					header_totals_weighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS) + 1 * len(INGAME_COLUMN_MODIFIERS)] += iwd * numpicked
					header_unweighted_denominators[iwd_index(mod_i) - non_averaged_columns] += 1
					header_weighted_denominators[iwd_index(mod_i) - non_averaged_columns] += numpicked
					# add to grid as percentage-point-diff
					grid[card_i][iwd_index(mod_i)] = str(round(iwd * 100)) + "pp"
				
				# OHI
				ohwr = extract(l[CSV_OHWR])
				gihwr = extract(l[CSV_GIHWR])
				if isinstance(ohwr, float) and isinstance(gihwr, float):
					ohi = ohwr - gihwr # OHI is the improvement from GIH WR to OH WR
					# store value for average calculations
					header_totals_unweighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS) + 2 * len(INGAME_COLUMN_MODIFIERS)] += ohi
					header_totals_weighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)  + 2 * len(INGAME_COLUMN_MODIFIERS)] += ohi * numpicked
					header_unweighted_denominators[ohi_index(mod_i) - non_averaged_columns] += 1
					header_weighted_denominators[ohi_index(mod_i) - non_averaged_columns] += numpicked
					# add to grid as percentage-point-diff
					grid[card_i][ohi_index(mod_i)] = str(round(ohi * 100)) + "pp"

	# add ingame statistics for specific colours to grid
	# --------------------------------------------------
	games_played_vals = tuple([tuple([[""] * num_cards for i in range(5)]) for i in range(4)])
	games_won_vals = tuple([tuple([[""] * num_cards for i in range(5)]) for i in range(4)])
	for colours in FILENAME_COLOURS:
		filename = colours + "_card_ratings.csv"
		assert_filename(filename)
		with open(os.path.join(PATH,filename),"r") as f:
			reader = csv.reader(f)
			next(reader) # skip the first row, which doesn't correspond to a card
			for card_i in range(num_cards):
				l = next(reader)

				# Assess a card's GP WR in a certain deck
				numgp = extract(l[CSV_NUMGP])
				gpwr = extract(l[CSV_GPWR])
				if isinstance(numgp, float) and isinstance(gpwr, float):
					numgpwins = numgp * gpwr
				else:
					numgp = ""
					numgpwins = ""

				# Assess a card's OH WR in a certain deck
				numoh = extract(l[CSV_NUMOH])
				ohwr = extract(l[CSV_OHWR])
				if isinstance(numoh, float) and isinstance(ohwr, float):
					numohwins = numoh * ohwr
				else:
					numoh = ""
					numohwins = ""
				
				# Assess a card's GIH WR in a certain deck
				numgih = extract(l[CSV_NUMGIH])
				gihwr = extract(l[CSV_GIHWR])
				if isinstance(numgih, float) and isinstance(gihwr, float):
					numgihwins = numgih * gihwr
				else:
					numgih = ""
					numgihwins = ""

				# Assess a card's GNS WR in a certain deck
				numgns = extract(l[CSV_NUMGNS])
				gnswr = extract(l[CSV_GNSWR])
				if isinstance(numgns, float) and isinstance(gnswr, float):
					numgnswins = numgns * gnswr
				else:
					numgns = ""
					numgnswins = ""

				for colour, colour_i in (("w",0),("u",1),("b",2),("r",3),("g",4)):
					if colour in colours:
						add_to_cell(games_played_vals, COLOUR_GP_INDEX, colour_i, card_i, val=numgp)
						add_to_cell(games_won_vals, COLOUR_GP_INDEX, colour_i, card_i, val=numgpwins)
						add_to_cell(games_played_vals, COLOUR_OH_INDEX, colour_i, card_i, val=numoh)
						add_to_cell(games_won_vals, COLOUR_OH_INDEX, colour_i, card_i, val=numohwins)
						add_to_cell(games_played_vals, COLOUR_GIH_INDEX, colour_i, card_i, val=numgih)
						add_to_cell(games_won_vals, COLOUR_GIH_INDEX, colour_i, card_i, val=numgihwins)
						add_to_cell(games_played_vals, COLOUR_GNS_INDEX, colour_i, card_i, val=numgns)
						add_to_cell(games_won_vals, COLOUR_GNS_INDEX, colour_i, card_i, val=numgnswins)
					
	for colour_i in range(5):
		mod_i = colour_i + len(INGAME_COLUMN_MODIFIERS) - 5
		for card_i in range(num_cards):
			# Assess a card's GP WR in all decks with a certain colour
			gpwr = ratio(games_won_vals[COLOUR_GP_INDEX][colour_i][card_i], games_played_vals[COLOUR_GP_INDEX][colour_i][card_i])
			
			# Assess a card's GIH WR and GNS WR in all decks with a certain colour
			iwd = ratio_difference(games_won_vals[COLOUR_GIH_INDEX][colour_i][card_i], games_played_vals[COLOUR_GIH_INDEX][colour_i][card_i], games_won_vals[COLOUR_GNS_INDEX][colour_i][card_i], games_played_vals[COLOUR_GNS_INDEX][colour_i][card_i])
			
			# Assess a card's OH WR and GIH WR in all decks with a certain colour
			ohi = ratio_difference(games_won_vals[COLOUR_OH_INDEX][colour_i][card_i], games_played_vals[COLOUR_OH_INDEX][colour_i][card_i], games_won_vals[COLOUR_GIH_INDEX][colour_i][card_i], games_played_vals[COLOUR_GIH_INDEX][colour_i][card_i])
			
			# Add card data for header
			if isinstance(gpwr, float):
				# store value for average calculations
				header_totals_unweighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)] += gpwr
				header_totals_weighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)] += gpwr * default_numpicked[card_i]
				header_unweighted_denominators[gpwr_index(mod_i) - non_averaged_columns] += 1
				header_weighted_denominators[gpwr_index(mod_i) - non_averaged_columns] += default_numpicked[card_i]
				# add to grid as percentage
				grid[card_i][gpwr_index(mod_i)] = str(round(gpwr * 100)) + "%"
			if isinstance(iwd, float):
				# store value for average calculations
				header_totals_unweighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS) + 1 * len(INGAME_COLUMN_MODIFIERS)] += iwd
				header_totals_weighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)  + 1 * len(INGAME_COLUMN_MODIFIERS)] += iwd * default_numpicked[card_i]
				header_unweighted_denominators[iwd_index(mod_i) - non_averaged_columns] += 1
				header_weighted_denominators[iwd_index(mod_i) - non_averaged_columns] += default_numpicked[card_i]
				# add to grid as percentage-point-diff
				grid[card_i][iwd_index(mod_i)] = str(round(iwd * 100)) + "pp"
			if isinstance(ohi, float):
				# store value for average calculations
				header_totals_unweighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS) + 2 * len(INGAME_COLUMN_MODIFIERS)] += ohi
				header_totals_weighted[mod_i + 2 * len(DRAFT_COLUMN_MODIFIERS)  + 2 * len(INGAME_COLUMN_MODIFIERS)] += ohi * default_numpicked[card_i]
				header_unweighted_denominators[ohi_index(mod_i) - non_averaged_columns] += 1
				header_weighted_denominators[ohi_index(mod_i) - non_averaged_columns] += default_numpicked[card_i]
				# add to grid as percentage-point-diff
				grid[card_i][ohi_index(mod_i)] = str(round(ohi * 100)) + "pp"

	# Populate grid header
	# --------------------
	# print(header_totals_unweighted[3])
	# print(header_unweighted_denominators[3])
	# print(header_totals_weighted[3])
	# print(header_weighted_denominators[3])
	for i in range(non_averaged_columns, len(WANTED_COLUMNS)):
		add_to_header(grid_header, False, i, ratio(header_totals_unweighted[i - non_averaged_columns], header_unweighted_denominators[i - non_averaged_columns]))
		add_to_header(grid_header, True, i, ratio(header_totals_weighted[i - non_averaged_columns], header_weighted_denominators[i - non_averaged_columns]))

	# Finally, export the grid
	# ------------------------
	write_grid_to_file(grid_header, grid)

def name_index():
	return 0
def colour_index():
	return 1
def rarity_index():
	return 2
def numpicked_index(offset):
	return len(CONST_COLUMNS) + offset
def ata_index(offset):
	return len(CONST_COLUMNS) + len(DRAFT_COLUMN_MODIFIERS) * 1 + offset
def mainboard_percent_index(offset):
	return len(CONST_COLUMNS) + len(DRAFT_COLUMN_MODIFIERS) * 2 + offset
def gpwr_index(offset):
	return len(CONST_COLUMNS) + len(DRAFT_COLUMN_MODIFIERS) * len(DRAFT_COLUMNS) + offset
def iwd_index(offset):
	return len(CONST_COLUMNS) + len(DRAFT_COLUMN_MODIFIERS) * len(DRAFT_COLUMNS) + len(INGAME_COLUMN_MODIFIERS) * 1 + offset
def ohi_index(offset):
	return len(CONST_COLUMNS) + len(DRAFT_COLUMN_MODIFIERS) * len(DRAFT_COLUMNS) + len(INGAME_COLUMN_MODIFIERS) * 2 + offset

if __name__ == "__main__":
	main()