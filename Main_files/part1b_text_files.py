from classifier_functions import *

'''
part1b_text_files.py

This code will provide you with 3 new text files by just running the code
1 text file contains all the utterances with their associated dialogue acts
This file will be split up to a train and a test file where the percentage of splitting can be adjusted manually (in global_variables.py)
'''

#################################################################################### MAIN ####################################################################################

def main():
    """ Main program """

    conversation_directories = get_shuffled_conversation_directories_for(DATA_PATH)                             # Get conversations
    user_utterances_text_file = get_user_utterances_txt_file_from(conversation_directories)                     # Convert to utterances file
    train_file, test_file = split_conversation_in_train_test(user_utterances_text_file, PERCENTAGE_TRAIN_DATA)  # Split into train and test file
    
    return 0


if __name__ == "__main__":
    main()
