import sys
import os # for making filepaths
from download_scryfall_images import get_scryfall_data, make_folders
from keyboard_controller import connect_dir_to_keyboard

def main():
	if len(sys.argv) >= 5:
		set_code = sys.argv[1]
		set_name = sys.argv[2]
		path = sys.argv[3]
		mode = sys.argv[4]
		image_folder_path = os.path.join(path, "images", set_name, "") if (mode == "images" or mode == "all images") else ""
		text_folder_path = os.path.join(path, "text", set_name, "") if (mode == "text" or mode == "all text" or mode == "images" or mode == "all images") else ""
		keyboard_path = os.path.join(path, "text", set_name, "") if (mode == "keyboard") else ""
		cardlist_path = os.path.join(path, "cardlists", set_name + ".txt") if (mode == "text" or mode == "all text" or mode == "images" or mode == "all images") else ""
	else:
		print("""    Not enough arguments given. The desired format is as follows:
      python run_scripts.py <three-letter set code> <set name> <path to folder> <mode>
		
    <mode> can be "text", "all text", "images", "all images", or "keyboard" """)
		sys.exit(1)
		
	# scryfall only needs to be bothered if we're getting new data
	if  mode == "text" or mode == "images":
		make_folders(image_folder_path, text_folder_path, cardlist_path, get_scryfall_data(set_code, False))
	elif mode == "all text" or mode == "all images":
		make_folders(image_folder_path, text_folder_path, cardlist_path, get_scryfall_data(set_code, True))

	# hijacking the keyboard needs to be specifically asked for
	elif mode == "keyboard":
		print(keyboard_path)
		connect_dir_to_keyboard(keyboard_path)


if __name__ == "__main__":
	main()