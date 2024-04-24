import re

class Formatting:
	def __init__(self, cardname, mana_cost, type, rarity, text_box, flavour_text, watermark, pt, artist):
		self.cardname = cardname
		self.mana_cost = mana_cost
		self.type = type
		self.rarity = rarity
		self.text_box = text_box
		self.flavour_text = flavour_text
		self.watermark = watermark
		self.pt=pt
		self.artist = artist

	def __str__(self):
		tab = "\n\ntab\n\n"

		s = ""
		s += tab # notes
		s += tab # tombstone
		s += tab + self.cardname
		s += tab + self.format_mana_cost()
		s += tab + self.format_art()
		s += tab * 2 # frame
		s += tab + self.format_type()
		s += tab + self.format_rarity()
		s += tab + self.format_text_box()
		s += tab + self.format_watermark()
		s += tab + self.format_pt()
		s += tab # custom numbering
		s += tab # list indicator
		s += tab + self.artist
		s += tab # end
		return s

	def format_mana_cost(self):
		generic = ""
		s = ""
		appendix = ""

		# remove curly braces and split string
		symbols = self.mana_cost.replace("{", "").split("}")
		for symbol in symbols:
			if symbol.isdigit() and symbol != "0":
				generic = "V" * int(symbol)
			elif symbol == "X":
				appendix += symbol
			else:
				s += symbol
		return s + generic + appendix
	
	def mana_value(self):
		mv = 0
		symbols = self.mana_cost.replace("{", "").split("}")
		for symbol in symbols:
			if symbol.isdigit():
				mv += int(symbol)
			# hybrid symbols
			elif "/" in symbol:
				if "2" in symbol:
					mv += 2
				else:
					mv += 1
			elif symbol == "X":
				pass
			else:
				mv += 1
		return mv

	def format_art(self):
		return "\n\n".join(["", "make_image;", self.cardname + ".jpg", "down", "", "enter", "", "enter", ""])

	def format_type(self):
		# MSE doesn't like emdashes, and doesn't need spaces before or after hyphens
		type = self.type.replace(r" — ", r"-").replace("−", r"-")
		# I will generally want to change the typeline of Legendary permanents
		if "Legendary" in type:
			type = type.replace("Legendary ", "")
			if "Creature" in type:
				type = type + " Legend"
		# I will generally want cheap artifacts and artifacts that sacrifice themselves to be Baubles
		if self.mana_value() < 3 or ("Sacrifice " + self.cardname) in self.text_box:
			type = type.replace("Artifact", "Bauble")

		# Instant is no longer a card type
		if "Instant" in type:
			type = type.replace("Instant", "Sorcery")

		return type

	def format_rarity(self):
		return "\n\n".join(["", "down", "", self.rarity[0], "", "enter", ""])

	def format_text_box(self):
		s = ""

		# add legend rule
		if "Legendary" in self.type:
			s += "Unique\n"
		
		# add keyword to instants
		if "Instant" in self.type:
			s += "Instant\n"

		# format generic mana symbols and remove braces from other mana symbols
		in_mana_symbol = False
		in_compound_symbol = False
		generic = ""
		for char in self.text_box:
			if char == "{":
				in_mana_symbol = True
			elif in_mana_symbol and char == "}":
				in_mana_symbol = False
				in_compound_symbol = True
			elif in_mana_symbol and char.isdigit() and char != "0":
				generic += "V" * int(char)
			elif in_mana_symbol:
				s += char
			elif in_compound_symbol:
				# if a } isn't immediately followed by a {, the compound mana symbol ends
				in_compound_symbol = False
				s += generic
				generic = ""
				s += char
			else:
				s += char

		# remove reminder text that's not on its own line
		s = re.sub(r"(?<!\n)\(.*\)", "", s)

		# MSE doesn't like emdashes
		s = re.sub(r"[—−]", r"-", s)

		# add delay for equip costs
		s = re.sub(r"(?<=Equip )", r"\n\n\n\n", s)

		# add flavour text
		if self.flavour_text:
			s = "\n\n".join([s, "down", "", "down", "", "down", "", "down", self.flavour_text])

		return s

	def format_watermark(self):
		if self.cardname == "Plains":
			commands = (["down", "right"])
		elif self.cardname == "Island":
			commands = (["down", "right", "down"])
		elif self.cardname == "Swamp":
			commands = (["down", "right", "down", "down"])
		elif self.cardname == "Mountain":
			commands = (["down", "right", "down", "down", "down"])
		elif self.cardname == "Forest":
			commands = (["down", "right", "down", "down", "down", "down"])
		else:
			match self.watermark:
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
		commands.insert(0, "down")
		commands.append("enter")
		return "".join(["\n\n" + command + "\n\n" for command in commands])
			
	def format_pt(self):
		if self.pt == "/":
			return ""
		else:
			power, toughness = self.pt.split("/")
			if power.isdigit() and int(power) > 1:
				# multiply power by 1.5
				power = power + "x1.5"
			if toughness.isdigit() and int(toughness) > 1:
				# multiply toughness by 1.5
				toughness = toughness + "x1.5"
			
			return "/".join([power, toughness])