import sys
import os # for making filepaths
from download_scryfall_images import get_scryfall_data, make_folders
from keyboard_controller import connect_dir_to_keyboard

def main():
	if len(sys.argv) >= 5:
		set_code = sys.argv[1]
		set_name = sys.argv[2]
		mode = sys.argv[3]
		path = sys.argv[4]
		image_folder_path = os.path.join(path, "images", set_name, "") if (mode == "images" or mode == "create") else ""
		text_folder_path = os.path.join(path, "text", set_name, "") if (mode == "text" or mode == "create") else ""
	else:
		print("""Not enough arguments given. The desired format is as follows:
		python run_scripts.py <three-letter set code> <set name> <mode> (<path to folder>)
		
		<mode> can be "create", "images", "text" or "keyboard" """)
		sys.exit(1)
		
	# scryfall only needs to be bothered if we're getting new data
	if mode == "images" or mode == "text" or mode == "create":
		make_folders(image_folder_path, text_folder_path, get_scryfall_data(set_code))

	# hijacking the keyboard needs to be specifically asked for
	if mode == "keyboard":
		connect_dir_to_keyboard(text_folder_path)


if __name__ == "__main__":
	main()