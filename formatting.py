import re

def format_mana_cost(mana_cost):
	generic = ""
	s = ""
	appendix = ""

	# remove curly braces and split string
	symbols = mana_cost.replace("{", "").split("}")
	for symbol in symbols:
		if symbol.isdigit() and symbol != "0":
			generic = "V" * int(symbol)
		elif symbol == "X":
			appendix += symbol
		else:
			s += symbol
	return s + generic + appendix

def format_art(art_name):
	return "\n\n".join(["", "make_image;", art_name, "down", "", "enter", "", "enter", ""])

def format_type(type):
	type = type.replace(r" — ", "-") # MSE doesn't like emdashes, and doesn't need spaces before or after hyphens
	return type

def format_rarity(rarity):
	return "\n\n".join(["", "down", "", rarity[0], "", "enter", ""])

def format_text_box(text_box, flavour_text):
	s = ""

	# format generic mana symbols and remove braces from other mana symbols
	tokens = text_box.split("{")
	for token in tokens:
		split = token.split("}")
		if len(split) == 1:
			s += split[0]
			continue
		elif len(split) == 2:
			if split[0].isdigit() and split[0] != "0":
				s += "V" * int(split[0])
			else:
				s += split[0]
			s += split[1]
		else:
			print("token longer than expected in format_text_box, where text box is:\n" + text_box)

	# remove reminder text that's not on its own line
	s = re.sub(r"(?<!\n)\(.*\)", "", s)

	# add flavour text
	if flavour_text:
		s = "\n\n".join([s, "down", "", "down", "", "down", "", "down", flavour_text])

	return s

def format_watermark(watermark):
	match watermark:
		case "Azorius":
			commands = (["down", "down", "down", "right"])
		case "Dimir":
			commands = ["down", "down", "down", "right", "down"]
		case "Rakdos":
			commands = ["down", "down", "down", "right", "down", "down"]
		case "Gruul":
			commands = ["down", "down", "down", "right", "down", "down", "down"]
		case "Selesnya":
			commands = ["down", "down", "down",  "right", "down", "down", "down", "down"]
		case "Orzhov":
			commands = ["down", "down", "down", "right", "down", "down", "down", "down", "down"]
		case "Izzet":
			commands = ["down", "down", "down", "right", "down", "down", "down", "down", "down", "down"]
		case "Golgari":
			commands = ["down", "down", "down", "right", "down", "down", "down", "down", "down", "down", "down"]
		case "Boros":
			commands = ["down", "down", "down", "right", "down", "down", "down", "down", "down", "down", "down", "down"]
		case "Simic":
			commands = ["down", "down", "down", "right", "down", "down", "down", "down", "down", "down", "down", "down", "down"]
		case "Mirrodin":
			commands = ["down", "down", "down", "down", "right"]
		case "Phyrexia":
			commands = ["down", "down", "down", "down", "right", "down"]
		case "Abzan":
			commands = ["down", "down", "down", "down", "down", "right"]
		case "Jeskai":
			commands = ["down", "down", "down", "down", "down", "right", "down"]
		case "Sultai":
			commands = ["down", "down", "down", "down", "down", "right", "down", "down"]
		case "Mardu":
			commands = ["down", "down", "down", "down", "down", "right", "down", "down", "down"]
		case "Temur":
			commands = ["down", "down", "down", "down", "down", "right", "down", "down", "down", "down"]
		case "Dromoka":
			commands = ["down", "down", "down", "down", "down", "down", "right"]
		case "Ojutai":
			commands = ["down", "down", "down", "down", "down", "down", "right", "down"]
		case "Silumgar":
			commands = ["down", "down", "down", "down", "down", "down", "right", "down", "down"]
		case "Kolaghan":
			commands = ["down", "down", "down", "down", "down", "down", "right", "down", "down", "down"]
		case "Atarka":
			commands = ["down", "down", "down", "down", "down", "down", "right", "down", "down", "down", "down"]
		case _:
			return ""
	commands.insert("down", 0)
	commands.append("enter")
	return ''.join(["\n\n" + command + "\n\n" for command in commands])
		
def format_pt(pt):
	if pt == "/":
		return ""
	else:
		power, toughness = pt.split("/")
		if power.isdigit() and int(power) > 1:
			# multiply power by 1.5
			power = power + "x1.5"
		if toughness.isdigit() and int(toughness) > 1:
			# multiply toughness by 1.5
			toughness = toughness + "x1.5"
		
		return "/".join([power, toughness])