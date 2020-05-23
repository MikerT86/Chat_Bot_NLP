from os import listdir
from os.path import join, isdir
import json as js
import random
from general_helper_functions import *

'''
textfile_functions.py

This file contains all the text file helper functions.
'''


# __________________________________________PUBLIC FUNCTIONS__________________________________________ #

def create_text_file(conversation_directories):
    """ Create a text file if the user wants"""
    if not yes_or_no("Do you wish to create a .txt file with all conversations?"):
        return

    add_all_to_text_file(prompt_file_name(), conversation_directories)


def get_conversation_directories_for(path):
    """ Given the path, this function will retrieve all conversation directories from subdirectories and add them to
        a single list """

    all_directories = [join(path, o) for o in listdir(path)
                       if isdir(join(path, o))]
    directories_container = []

    for dir_path in all_directories:
        subdirectories = [join(dir_path, o) for o in listdir(dir_path)
                          if isdir(join(dir_path, o))]

        for subdirectory in subdirectories:
            directories_container.append(subdirectory)

    return directories_container

def get_shuffled_conversation_directories_for(path):
    """ Retrieve all conversation directories from subdirectories, add them to a single list and shuffle them """
    conversation_container = get_conversation_directories_for(path)
    random.shuffle(conversation_container)

    return conversation_container


def get_user_utterances_txt_file_from(conversation_directories):
    """ Get the utterances content and the associated dialogue acts and make a txt file with all the utterances """
    file_name = prompt_file_name()
    text_file = open(file_name, "a+")

    for conversation_directory in conversation_directories:
        data_user = open_user_conversation_in(conversation_directory)

        for i in range(len(data_user["turns"])):
            dialog_act_raw = data_user["turns"][i]["semantics"]["cam"]
            dialog_act_list = dialog_act_raw.split("|")

            for act in dialog_act_list:
                add_act_utterance_to_file(text_file, act, data_user, i)

    text_file.close()
    return text_file


def split_conversation_in_train_test(text_file, percentage_train):
    """ Provide a text file and a % for train data and split the file in two files """
    number_of_utterances = file_len(text_file.name)
    number_of_train_utterances = int(
        number_of_utterances * (percentage_train / 100))

    train_file_name = str(text_file.name).replace(".txt", "") + "_train.txt"
    test_file_name = str(text_file.name).replace(".txt", "") + "_test.txt"

    total_file = open(text_file.name, "r")
    train_file = open(train_file_name, "a+")
    test_file = open(test_file_name, "a+")

    for i, line in enumerate(total_file):
        if i < number_of_train_utterances:
            train_file.write(line)
        elif i >= number_of_train_utterances:
            test_file.write(line)

    total_file.close()
    train_file.close()
    test_file.close()

    return train_file, test_file

# __________________________________________PRIVATE FUNCTIONS__________________________________________ #

def add_all_to_text_file(file_name, conversation_directories):
    """ Add all conversations to text file """
    print("Creating text file...")

    for conversation_directory in conversation_directories:
        data_system, data_user = open_conversation_in(conversation_directory)
        add_to_text_file(file_name, data_system, data_user)


def add_to_text_file(file_name, data_system, data_user):
    """ Create and/or append a single conversation to text file """
    text_file = open(file_name, "a+")

    for i in range(len(data_system["turns"])):
        system_string = "System: {}\n".format(
            data_system["turns"][i]["output"]["transcript"])
        user_string = "User: {}\n".format(
            data_user["turns"][i]["transcription"])

        text_file.write(system_string)
        text_file.write(user_string)

    text_file.write("\n")
    text_file.close()


def add_act_utterance_to_file(text_file, dialog_act_raw, data_user, index):
    """ Make a string in the format dialogue act + utterance content and write it in a text file """
    dialog_act = dialog_act_raw.split("(")[0]
    user_transcription = (data_user["turns"][index]["transcription"])
    user_utterance_string = str(
        dialog_act + " " + user_transcription + "\n").lower()

    text_file.write(user_utterance_string)


def open_conversation_in(directory):
    """ Open the conversation JSON files and return """
    system_data = open_system_conversation_in(directory)
    user_data = open_user_conversation_in(directory)

    return system_data, user_data


def open_user_conversation_in(directory):
    """ Open the user conversation JSON file and return """
    user_file = directory + '/label.json'

    with open(user_file) as json_data:
        user_data = js.load(json_data)

    return user_data


def open_system_conversation_in(directory):
    """ Open the system conversation JSON file and return """
    system_file = directory + '/log.json'

    with open(system_file) as json_data:
        system_data = js.load(json_data)

    return system_data

def save_conversation(file_name, conversation_array):
    
    text_file = open(file_name, "a+")
    i = 0
    text_file.write("----------------------- \n")
    while i < len(conversation_array)-1:
        system_string = conversation_array[i]
        user_string = "USER: " + conversation_array[i+1]
        
        text_file.write(system_string)
        text_file.write("\n")
        text_file.write(user_string)
        text_file.write("\n")
        i = i + 2

    text_file.close()
