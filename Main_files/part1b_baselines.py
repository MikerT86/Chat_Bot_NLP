from global_variables import DATA_PATH
from classifier_functions import *

'''
part1b_baselines.py

With this code you can test the two baselines 
It can classify an utterance that is entered in the terminal
It will also provide the accuracy of the two baselines
Unfortunately to use different baselines one has to comment out other functions in the main
'''

#################################################################################### MAIN ####################################################################################

def main():
    """ Main program """

    # Make new train and test data .txt files (uncomment if you want to use this instead of the variable names on the top of this file)
    conversation_directories = get_shuffled_conversation_directories_for(DATA_PATH)
    user_utterances_text_file = get_user_utterances_txt_file_from(conversation_directories)
    train_file, test_file = split_conversation_in_train_test(user_utterances_text_file, 85)

    # Baseline 1:
    print("\n \n  USING/TESTING BASELINE 1 RIGHT NOW \n \n")
    print("The accuracy of baseline 1 for training data is: ", classify_by_keyword_accuracy(train_file.name)) # Calculate the accuracy on the training data
    print("The accuracy of baseline 1 for test data is: ", classify_by_keyword_accuracy(test_file.name))      # Calculate the accuracy on the test data
    user_utt = str(input("Please enter an utterance to classify with baseline 1: "))                          # Enter an utterance to classify
    print(classify_by_keyword(user_utt))                                                                      # Return list of possible dialogue acts

    # Baseline 2:
    print("\n \n  USING/TESTING BASELINE 2 RIGHT NOW \n \n")
    randomly_classify_train_distribution = randomly_classify_with_distribution_file(train_file.name)    # Make distribution of trainig data
    randomly_classify_test_distribution = randomly_classify_with_distribution_file(test_file.name)      # Make distribution of test data
    print("The accuracy of baseline 2 for training data is: ",
          randomly_classify_accuracy(train_file.name, randomly_classify_train_distribution))            # Calculate the accuracy on the training data
    print("The accuracy of baseline 2 for test data is: ",                                              # Calculate the accuracy on the test data
          randomly_classify_accuracy(test_file.name, randomly_classify_test_distribution))
    print(randomly_classify_with_distribution(randomly_classify_train_distribution))                    # Enter an utterance to classify

    return 0


if __name__ == "__main__":
    main()
