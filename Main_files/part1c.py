from classifier_functions import *
from dialog_system_model import *
from sklearn.externals import joblib
from global_variables import *
import os

def features_handling():
    
    #Default features setting
    features = dict({
        "OUTPUT_CAPS":      False,      #OUTPUT IN ALL CAPS OR NOT
        "LEVENSHTEIN":       0,          #Levenshtein edit distance for preference extraction
        "ASK_CONFIRMATION": False,      #Ask confirmation for each preference or not
        "ALLOW_CHANGES":    True,       #Allow users to change their preferences or not
        "LIMIT_DIALOGS":    0           #Limit the dialog to a certain number of utterances
    })

    #Asking user to set each of features
    for key in features:
        if key == 'OUTPUT_CAPS':
            answer = str(input("Make output in all caps? [y/n]: ")).lower().strip()
            features['OUTPUT_CAPS'] = True if answer == 'y' else False 
            
        if key == 'LEVENSHTEIN':
            answer = int(input("Levenshtein distance: "))
            features['LEVENSHTEIN'] = answer

        if key == 'ASK_CONFIRMATION':
            answer = input("Always ask confirmation of entered preference? [y/n]: ").lower().strip()
            features['ASK_CONFIRMATION'] = True if answer == 'y' else False
        
        if key == 'ALLOW_CHANGES':
            answer = input("Allow to change preferences? [y/n]: ").lower().strip()
            features['ALLOW_CHANGES'] = True if answer == 'y' else False

        if key == 'LIMIT_DIALOGS':
            answer = int(input("Dialog limit [0 - No limit]: "))
            features['LIMIT_DIALOGS'] = answer

    return features

#"""<State Transition funcrion>"""    
def state_transition(system, dialogs_counter=0):

    print("--------------------------------------")
    system.system_message()
    
    #checking feature of dialog limits, if it's ON sent message with amount of dialogs left
    if system.features['LIMIT_DIALOGS'] != 0:
        print("Dialogs left: {}".format(system.features['LIMIT_DIALOGS'] - dialogs_counter))

        #if user out of dialog acts, checking is the dialog finish (found restaurant) then finish
        #if system still have options and KB not filled system restarts, otherwise finish dialog
        if system.features['LIMIT_DIALOGS'] == dialogs_counter:
            if system.knowledge_base['filled'] == False and system.knowledge_base['suggestions'].shape[0] > 1:
                system.clean_knowladge_base()
                system.put_state("WELCOME")
                system.system_message()
            else:
                print("SYSTEM: Sorry, no dialog acts left! [Dialog Limit: {}]".format(system.features['LIMIT_DIALOGS']))
                return 0

    #getting uer utterance and retviev dialog act
    user_utterance  = system.get_user_utterance()
    dialog_act      = system.extract_dialog_act(user_utterance)
    
    #Analysing dialog acts
    if dialog_act == 'inform' or dialog_act == 'reqalts':

        system.extract_users_preferences(user_utterance)
        system.retrieve_restaurants() #getting restaurants according preferences
        
        current_state = system.check_KB() #checking fillnes of KB and choose new state for system
        
        #system checking enough to suggest or not (like in diagram)
        if system.knowledge_base['filled']:
            if system.knowledge_base['suggestions'].shape[0] == 0:
                    system.put_state("NO_REST")                  
            else:
                system.put_state("SUGGEST")
        else:
            if system.knowledge_base['suggestions'].shape[0] == 0:
                system.put_state("NO_REST")
            else:
                if system.knowledge_base['suggestions'].shape[0] == 1:    
                    system.put_state("SUGGEST")
                else:
                    system.put_state(current_state)

    if dialog_act == "hello":

        system.put_state("WELCOME")

    if dialog_act == "request" and system.get_state() == "SUGGEST":
    
        request = system.exctract_request(user_utterance)
        system.put_state(request)

    if dialog_act == 'reqmore' and system.get_state() == "SUGGEST":

            if system.knowledge_base['suggestions'].shape[0] > 1:
                system.knowledge_base['suggestions'].drop([0], inplace=True)
                system.knowledge_base['suggestions'].reset_index(inplace=True)
                system.put_state("SUGGEST") 
            else:
                system.put_state("NO_REST")

    if dialog_act == 'null':

        system.put_state("AGAIN")

    if dialog_act == 'restart':
    
        system.clean_knowladge_base()
        system.put_state("WELCOME")

    if dialog_act == 'bye' or dialog_act == 'thankyou':
        
        return 0

    dialogs_counter = dialogs_counter + 1

    state_transition(system, dialogs_counter)

def main():

    #creating intology, DataFrame of restaurantsm and dictionary of knowledge base            
    ontology, df_restaurants, knowledge_base = create_environment(ONTOLOGY_FILE, RESTAURANTS_FILE)

    #Put your model from file .pkl or use the ML classifier (DT_model)
    if os.path.exists('NN_model.pkl'):
        predict_model   = joblib.load('NN_model.pkl')
        try:
            file = open("vocabulary.txt")
            vocabulary = file.read().replace('\n', ' ').split()
        except IOError:
            print("Vocabulary file not found")
            return 0
    else:
        # Train the neural network and test with the test data
        # Get conversations, convert to utterances file, split into train and test file
        conversation_directories = get_shuffled_conversation_directories_for(DATA_PATH)
        user_utterances_text_file = get_user_utterances_txt_file_from(conversation_directories)
        train_file, test_file = split_conversation_in_train_test(user_utterances_text_file, 85)
        # Count unique words in train file,
        vocabulary = create_list_unique_words(train_file.name)
        with open('vocabulary.txt', 'w') as file:
            for item in vocabulary:
                file.write("%s\n" % item)

        train_data  = create_data_matrix(vocabulary, train_file.name)
        test_data   = create_data_matrix(vocabulary, test_file.name)

        train_labels, lb_classes        = create_labels_matrix(train_file.name)
        test_labels, label_binarizer    = create_labels_matrix(test_file.name, lb_classes)
        
        predict_model = neural_network(train_data, train_labels, vocabulary, test_data, test_labels)
        #Save the model into file
        joblib.dump(predict_model, './NN_model.pkl') 

    print("\033c") 
    print("//Setting Features-------------------------------------")
    features    = features_handling()
    new_system  = System("WELCOME", ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary)
    
    #start of wroking system 
    state_transition(new_system)

if __name__ == '__main__':
    main()