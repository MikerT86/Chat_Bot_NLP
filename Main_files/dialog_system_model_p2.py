import json as js
import pandas as pd
import numpy as np
import os
import Levenshtein as lev
from sklearn.feature_extraction.text import CountVectorizer
import speech_recognition as sr

from classifier_functions import *
from extract_inform_functions import *
from nltk.tokenize import RegexpTokenizer

def create_environment(ontology_file, restaurants_file):

    with open(ontology_file) as json_data:
        ontology_data = js.load(json_data)

    #extracting ontology
    info_data = ontology_data["informable"]

    Ontology = dict({"food": np.array(info_data["food"]),
                    "areas": np.array(info_data["area"]),
                    "priceranges": np.array(info_data["pricerange"]),
                    "names": np.array(info_data["name"]),
                    "requests": np.array(ontology_data["requestable"])})

    #Making knowledge base for system                                        
    Knowledge_Base = dict({
        "preferences": {
            "foodtype": "",
            "area": "",
            "pricerange": "",
            "restaurantname": ""
        },
        "suggestions": pd.DataFrame(),
        "filled": False
    })

    DF_RESTAURANTS = pd.read_csv(restaurants_file) #put all variances of restaurants in dataframe 

    return Ontology, DF_RESTAURANTS, Knowledge_Base
  
class System():

    def __init__(self, current_state, ontology, model, restaurants, target, knowledge_base, features, vocabulary):
        
        self.current_state  = current_state
        self.ontology       = ontology
        self.model          = model
        self.restaurants    = restaurants
        self.target         = target
        self.knowledge_base = knowledge_base
        self.features       = features
        self.vocabulary     = vocabulary
        self.msg_array      = []

    recognizer = None

    def system_message(self):

        message = ""

        if self.current_state == "WELCOME":
            message = "SYSTEM: Hello , welcome to the Cambridge restaurant system? You can ask for restaurants by area , price range or food type . How may I help you?" 
        
        if self.current_state == "ASK_FOOD_TYPE":
            rest_amount = self.knowledge_base['suggestions'].shape[0]
            pricerange  = self.knowledge_base['preferences']['pricerange']
            area        = self.knowledge_base['preferences']['area']
            if pricerange != "" and area != "":
                message = "SYSTEM: There are {} restaurants in the {} price range and the {} part of town. What food type do you want?".format(rest_amount, pricerange, area)
            else:
                if pricerange != "":
                    message = "SYSTEM: There are {} restaurants in the {} price range. What food type do you want?".format(rest_amount, pricerange)
                else:
                    if area != "":
                        message = "SYSTEM: There are {} restaurants in the {} part of town. What food type do you want?".format(rest_amount, area)
                    else:
                        message = "SYSTEM: What food type do you want?"

        if self.current_state == "ASK_PRICE_RANGE":
            rest_amount = self.knowledge_base['suggestions'].shape[0]
            foodtype    = self.knowledge_base['preferences']['foodtype']
            area        = self.knowledge_base['preferences']['area']
            if foodtype != "" and area != "":
                message = "SYSTEM: There are {} restaurants of {} food type in the {} part of town. What price range would you like?".format(rest_amount, foodtype, area)
            else:
                if foodtype != "":
                    message = "SYSTEM: There are {} restaurants of {} food type. What price range would you like?".format(rest_amount, foodtype)
                else:
                    if area != "":
                        message = "SYSTEM: There are {} restaurants in the {} part of town. What food type do you want?".format(rest_amount, area)
                    else:
                        message = "SYSTEM: What price range would you like?"
        
        if self.current_state == "ASK_AREA":
            rest_amount = self.knowledge_base['suggestions'].shape[0]
            foodtype    = self.knowledge_base['preferences']['foodtype']
            pricerange  = self.knowledge_base['preferences']['pricerange']
            if foodtype != "" and pricerange != "":
                message = "SYSTEM: There are {} restaurants of {} food type and in the {} price range. What part of town do you have in mind?".format(rest_amount, foodtype, pricerange)
            else:
                if foodtype != "":
                    message = "SYSTEM: There are {} restaurants of {} food type. What part of town do you have in mind?".format(rest_amount, foodtype)
                else:
                    if pricerange != "":
                        message = "SYSTEM: There are {} restaurants in the {} price range. What part of town do you have in mind?".format(rest_amount, pricerange)
                    else:
                        message = "SYSTEM: What part of town do you have in mind?"
        
        if self.current_state == "SUGGEST":
            df_rest = self.knowledge_base['suggestions']
            message = "SYSTEM: The {} of {} food is a nice place in the {} of town and the prices are {}".format(df_rest['restaurantname'][0], df_rest['food'][0], df_rest["area"][0], df_rest["pricerange"][0])
        
        if self.current_state == "NO_REST":
            message = "SYSTEM: no restaurant to suggest, please change preferences"

        if self.current_state == "CODE":
            message = "SYSTEM: The postcode of restaurant is {}".format(self.knowledge_base['suggestions']['postcode'][0])
        
        if self.current_state == "PHONE":
            message = "SYSTEM: The phone number of restaurant is {}".format(self.knowledge_base['suggestions']['phone'][0])  
        
        if self.current_state == "ADDRESS":
            message = "SYSTEM: The address of restaurant is {}".format(self.knowledge_base['suggestions']['addr'][0]) 
        
        if self.current_state == "NAME":
            message = "SYSTEM: The name of restaurant is {}".format(self.knowledge_base['suggestions']['restaurantname'][0])
        
        if self.current_state == "AGAIN":
            message = "SYSTEM: Please, repeat again"
        
        if self.current_state == "DENIED":
            message = "SYSTEM: You not allowd to change preferences!"

        print(message.upper() if self.features['OUTPUT_CAPS'] else message)
        self.msg_array.append(message)

    def retrieve_restaurants(self):
    
        df_rest = self.restaurants.copy()

        if self.knowledge_base['preferences']['foodtype'] != "":
            df_rest = df_rest[df_rest['food'] == self.knowledge_base['preferences']['foodtype']]
        if self.knowledge_base['preferences']['pricerange'] != "":
            df_rest = df_rest[df_rest['pricerange'] == self.knowledge_base['preferences']['pricerange']]
        if self.knowledge_base['preferences']['area'] != "":
            df_rest = df_rest[df_rest['area'] == self.knowledge_base['preferences']['area']]
        
        df_rest.reset_index(inplace=True)
        self.knowledge_base['suggestions'] = df_rest

    def check_KB(self):

        if self.knowledge_base['preferences']['foodtype'] == "":
            return "ASK_FOOD_TYPE"
        else:        
            if self.knowledge_base['preferences']['pricerange'] == "":
                return "ASK_PRICE_RANGE"
            else:          
                if self.knowledge_base['preferences']['area'] == "":
                    return "ASK_AREA"   
                else:
                    self.knowledge_base['filled'] = True
                    return "SUGGEST"

    def extract_dialog_act(self, user_utterance):
        
        tokenizer = RegexpTokenizer('\w+')
        tokenized = tokenizer.tokenize(str(user_utterance))
    
        utterance = transform_utterance_levenshtein(tokenized, self.features['LEVENSHTEIN'])  
    
        count_vect = CountVectorizer(vocabulary = self.vocabulary, analyzer='word', min_df=0., max_df=1.)
        X = count_vect.fit_transform([utterance]).toarray()
        
        prediction = self.model.predict_classes(X)
        dialog_act = self.target[prediction[0]]

        return dialog_act    

    def exctract_request(self, user_utterance):
        
        tokenizer = RegexpTokenizer('\w+')
        tokenized = tokenizer.tokenize(str(user_utterance))
        
        matching_word = None
        for word in tokenized:
            for request_type in self.ontology["requests"]:
                if lev.distance(word, request_type) <= self.features['LEVENSHTEIN']:
                    matching_word = request_type
                    break

        if matching_word != None:
            if matching_word == "postcode":
                return "CODE"
            if matching_word == "phone":
                return "PHONE"   
            if matching_word == "addr":
                return "ADDRESS"
            if matching_word == "name":
                return "NAME"
        else:
            return "AGAIN"

    def get_user_utterance(self):

        user_etturance = input("USER: ").lower()
        self.msg_array.append(user_etturance)
        return user_etturance

    def put_state(self, new_state):

        self.current_state = new_state

    def get_state(self):
    
        return self.current_state

    def extract_users_preferences(self, user_utterance):
        
        tokenizer = RegexpTokenizer('\w+')
        tokenized = tokenizer.tokenize(str(user_utterance))
        
        utterance  = " ".join(tokenized) 
        df_suggest, df_rest = pd.DataFrame(), self.restaurants.copy()
    
        foodtype, pricerange, area = extract_preference_inform(utterance, self.features['LEVENSHTEIN'])

        if foodtype != None and foodtype not in self.knowledge_base['preferences']['foodtype']:
            
            if self.features['ASK_CONFIRMATION']:
                message = "SYSTEM: Do you mean {} type of food?".format(foodtype) 
                if self.__get_confirmation(message):
                    new_food_type = foodtype
                else:
                    new_food_type = self.knowledge_base['preferences']['foodtype']
            else:
                new_food_type = foodtype 
            
            if self.knowledge_base['preferences']['foodtype'] == "":
                self.knowledge_base['preferences']['foodtype'] = new_food_type
            else:
                if self.features['ALLOW_CHANGES']:
                    self.knowledge_base['preferences']['foodtype'] = new_food_type
                else:
                    self.put_state("DENIED")
                    self.system_message()
                    
        if pricerange != None  and pricerange not in self.knowledge_base['preferences']['pricerange']:

            if self.features['ASK_CONFIRMATION']: 
                message = "SYSTEM: Do you mean {} price range?".format(pricerange) 
                if self.__get_confirmation(message):
                    new_pricerange = pricerange
                else:
                    new_pricerange = self.knowledge_base['preferences']['pricerange']
            else:
                new_pricerange = pricerange 

            if self.knowledge_base['preferences']['pricerange'] == "":
                self.knowledge_base['preferences']['pricerange'] = new_pricerange
            else:
                if self.features['ALLOW_CHANGES']:
                    self.knowledge_base['preferences']['pricerange'] = new_pricerange
                else:
                    self.put_state("DENIED")
                    self.system_message()

        if area != None and area not in self.knowledge_base['preferences']['area']:

            if self.features['ASK_CONFIRMATION']:
                message = "SYSTEM: Do you mean {} area?".format(area)  
                if self.__get_confirmation(message):
                    new_area = area
                else:
                    new_area = self.knowledge_base['preferences']['area']
            else:
                new_area = area 

            if self.knowledge_base['preferences']['area'] == "":
                self.knowledge_base['preferences']['area'] = new_area
            else:
                if self.features['ALLOW_CHANGES']:
                    self.knowledge_base['preferences']['area'] = new_area
                else:
                    self.put_state("DENIED")
                    self.system_message()
    
    def __get_confirmation(self, message):

        print(message.upper() if self.features['OUTPUT_CAPS'] else message)
        self.msg_array.append(message)
        if self.features["USE_SPEECH_RECOGNOTION"]:
            user_utterance = self.speech_recognition()
        else:
            user_utterance  = self.get_user_utterance()

        dialog_act      = self.extract_dialog_act(user_utterance)

    
        return True if dialog_act == 'affirm' else False
    
    def clean_knowladge_base(self):
    
        self.knowledge_base = dict({
        "preferences": {
            "foodtype": "",
            "area": "",
            "pricerange": "",
            "restaurantname": ""
        },
        "suggestions": pd.DataFrame(),
        "filled": False
    })

    def speech_recognition(self):

        if self.recognizer is None:
            self.recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.recognizer.dynamic_energy_threshold = True

        input("\nPlease, press 'ENTER' to start speaking...")
        print("Listening....")

        with sr.Microphone() as source:
            audio = self.recognizer.listen(source, phrase_time_limit=5)

        try:
            print("Processing....")
            text = str(self.recognizer.recognize_google(audio, language="en-GB")).lower().strip()
            print("You said: ", text)
            self.msg_array.append(text)
            return text
        except Exception as e:
            print("Didn't catch what you said, please retry")
            self.speech_recognition()