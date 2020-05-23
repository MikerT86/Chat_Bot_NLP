from textfile_functions import *

'''
printing_functions.py

This file contains all the printing helper functions.
'''


# __________________________________________PUBLIC FUNCTIONS__________________________________________ #

def print_all_conversations(conversation_directories):
    """ Print the one whole conversation on the screen.
        Print the next when the user presses the Enter key, until no more conversations left """
    for conversation_directory in conversation_directories:
        data_system, data_user = open_conversation_in(conversation_directory)

        _print_conversation(data_system, data_user)
        input("Press Enter to continue... \n")


# __________________________________________PRIVATE FUNCTIONS__________________________________________ #

def _print_conversation(data_system, data_user):
    """ Print the current conversation to the console """
    for i in range(len(data_system["turns"])):
        print("System: ", data_system["turns"][i]["output"]["transcript"])
        print("User: ", data_user["turns"][i]["transcription"])
