from os.path import exists

'''
general_helper_functions.py

This file contains all the general helper functions.
'''


# __________________________________________PUBLIC FUNCTIONS__________________________________________ #

def yes_or_no(question):
    """ Prompt a yes/no question to the user and return boolean """
    reply = str(input(question + " (y/n): ")).lower().strip()
    if reply == 'y':
        return True
    if reply == 'n':
        return False
    else:
        return yes_or_no("Please enter")


def prompt_file_name():
    """ Prompt user for a file name with some error checking """
    file_name = input("Please enter a name for the text file:  ")

    if file_name == "":
        return prompt_file_name()
    path = "{}.txt".format(file_name)

    if not exists(path):
        return path
    else:
        print("Error: file with this name already exists or invalid name")
        return prompt_file_name()


def file_len(fname):
    """ Count the number of lines in a .txt file """
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
