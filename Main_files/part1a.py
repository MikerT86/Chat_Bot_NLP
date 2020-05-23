from global_variables import DATA_PATH
from printing_functions import print_all_conversations
from textfile_functions import create_text_file, get_conversation_directories_for

''' 
part1a.py

With this code you will able to print the dialogues one by one
First the system will ask you is you want to make a text file where all the dialogues will be saved, you can answer with y/n
After that you press enter to show the next dialogue in the terminal 
'''

def main():
    conversation_directories = get_conversation_directories_for(DATA_PATH)  # Get the conversations
    create_text_file(conversation_directories)                              # Create a file will all the conversations
    print_all_conversations(conversation_directories)                       # Print the conversations in the terminal

    return 0

if __name__ == "__main__":
    main()
