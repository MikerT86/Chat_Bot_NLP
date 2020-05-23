from classifier_functions import *
from dialog_system_model_p2 import *
from sklearn.externals import joblib
from global_variables import *
from textfile_functions import *
import os

def features_handling():
    
    #Default features setting
    features = dict({
        "OUTPUT_CAPS":      False,      #OUTPUT IN ALL CAPS OR NOT
        "LEVENSHTEIN":       1,          #Levenshtein edit distance for preference extraction
        "ASK_CONFIRMATION": True,      #Ask confirmation for each preference or not
        "ALLOW_CHANGES":    True,       #Allow users to change their preferences or not
        "LIMIT_DIALOGS":    0,
        "USE_SPEECH_RECOGNOTION":    False           #Limit the dialog to a certain number of utterances
    })

    return features

#"""<State Transition funcrion>"""    
def state_transition(system, dialogs_counter=0):

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
    if system.features["USE_SPEECH_RECOGNOTION"]:
        user_utterance = system.speech_recognition()
    else:
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

def conversation(system_type, file_name, use_speech, use_confirmation, ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary):
    
    features['USE_SPEECH_RECOGNOTION']  = use_speech
    features['ASK_CONFIRMATION']        = use_confirmation
    
    path = "{}_system_{}.txt".format(file_name, system_type)

    text_file = open(path, "a+")
    text_file.write("Conversation with sytem {} \n".format(system_type))
    text_file.close()
    print("Conversation with sytem {} \n".format(system_type))
    dialogs = 0
    while dialogs < 4:
        print("\033c")
        new_system  = System("WELCOME", ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary)
        new_system.clean_knowladge_base()
        state_transition(new_system)
        save_conversation(path, new_system.msg_array)
        dialogs = dialogs + 1    

def main():

    #creating intology, DataFrame of restaurantsm and dictionary of knowledge base            
    ontology, df_restaurants, knowledge_base = create_environment(ONTOLOGY_FILE, RESTAURANTS_FILE)

    #Put your model from file .pkl or use the ML classifier (DT_model)
    if os.path.exists(MODEL_NN):
        predict_model   = joblib.load(MODEL_NN)
        try:
            file = open(VOCABULARY)
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
        with open(VOCABULARY, 'w') as file:
            for item in vocabulary:
                file.write("%s\n" % item)

        train_data  = create_data_matrix(vocabulary, train_file.name)
        test_data   = create_data_matrix(vocabulary, test_file.name)

        train_labels, lb_classes        = create_labels_matrix(train_file.name)
        test_labels, label_binarizer    = create_labels_matrix(test_file.name, lb_classes)
        
        predict_model = neural_network(train_data, train_labels, vocabulary, test_data, test_labels)
        #Save the model into file
        joblib.dump(predict_model, MODEL_NN) 

    print("\033c") 
    #print("//Setting Features-------------------------------------")
    features    = features_handling()
    file_name = input("Please enter a name for the text file:  ")
    if file_name == "":

        return prompt_file_name()
    
    system_type = str(input("Which system starts first? [a - explicit confirmation, b - implicit confirmation only]: ")).lower()
    if system_type == 'a':

        conversation('A', file_name, True, True, ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary)
        input("Press 'ENTER' when you ready to start next system...")
        conversation('B', file_name, True, False, ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary)
        
    else:

        conversation('B', file_name, True, False, ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary)
        input("Press 'ENTER' when you ready to start next system...")
        conversation('A', file_name, True, True, ontology, predict_model, df_restaurants, TARGET_NAMES, knowledge_base, features, vocabulary)
        
if __name__ == '__main__':
    main()