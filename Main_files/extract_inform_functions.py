import json as js
import Levenshtein as lev
from operator import itemgetter
import random
from global_variables import *

pattern_dict = {
    "food": "food",
    "price": "priced",
    "area": "part",
}

with open(ONTOLOGY_FILE) as json_data:
    ontology = js.load(json_data)

def calculate_distance(utterance_split, keyword, max_distance=2):
    keyword_matches = []

    for word in utterance_split:
        actual_distance = lev.distance(word, keyword)
        if actual_distance <= max_distance:
            keyword_matches.append((word, actual_distance))

    if len(keyword_matches) > 0:
        smallest_distance_keyword = min(keyword_matches, key=itemgetter(1))
        return smallest_distance_keyword[0], smallest_distance_keyword[1]
    else:
        return None, None

def get_informable_before_keyword(utterance_list, keyword, keyword_type, max_distance=2):
    index = utterance_list.index(keyword)
    matching_list = []

    try:
        word_preceding_keyword = utterance_list[index - 1]
    except IndexError:
        return utterance_list, None

    for informable_type in ontology["informable"][keyword_type]:
        matching_word, matching_distance = calculate_distance(utterance_list, informable_type, max_distance)
        if matching_distance is not None:
            matching_list.append((informable_type, matching_distance))

    if len(matching_list) > 0:
        smallest_distance_informable_type = min(matching_list, key=itemgetter(1))
        utterance_list.remove(keyword)
        utterance_list.remove(word_preceding_keyword)
        return utterance_list, smallest_distance_informable_type[0]
    else:
        utterance_list.remove(keyword)
        return utterance_list, None

def compare_word_against_type(word, keyword_type, max_distance):
    matching_words = []
    for informable_type in ontology["informable"][keyword_type]:
        if lev.distance(word, informable_type) <= max_distance:
            matching_words.append(informable_type)

    if len(matching_words) > 0:
        return random.choice(matching_words)
    else:
        return None

def extract_preference_inform(tokenized_utterance, distance):
    utterance_list = tokenized_utterance.split(" ")

    food_set = False
    price_set = False
    area_set = False

    food_keyword, food_distance = calculate_distance(utterance_list, pattern_dict["food"])
    price_keyword, price_distance = calculate_distance(utterance_list, pattern_dict["price"])
    area_keyword, area_distance = calculate_distance(utterance_list, pattern_dict["area"])

    foodtype, pricerange, area = None, None, None

    if food_keyword is not None:
        updated_utterance_list, food_type = get_informable_before_keyword(utterance_list, food_keyword, "food", distance)
        utterance_list = updated_utterance_list
        if food_type is not None:
            #insert KB["food"] with food_type
            food_set = True
            foodtype = food_type

    if pattern_dict["price"] in utterance_list:
        updated_utterance_list, price_type = get_informable_before_keyword(utterance_list, price_keyword, "pricerange", distance)
        utterance_list = updated_utterance_list
        if price_type is not None:
            #insert KB["price"] with price_type
            price_set = True
            pricerange = price_type

    if pattern_dict["area"] in utterance_list:
        updated_utterance_list, area_type = get_informable_before_keyword(utterance_list, area_keyword, "area", distance)
        utterance_list = updated_utterance_list
        if area_type is not None:
            #insert KB["area"] with area_type
            area_set = True
            area = area_type

    for word in utterance_list:
        matching_food = compare_word_against_type(word, "food", distance)
        if (matching_food is not None) and (food_set == False):
            #insert KB["food"] with food_type
            foodtype = matching_food

        matching_price = compare_word_against_type(word, "pricerange", distance)
        if (matching_price is not None) and (price_set == False):
            # insert KB["food"] with food_type
            pricerange = matching_price

        matching_area = compare_word_against_type(word, "area", distance)
        if (matching_area is not None) and (area_set == False):
            # insert KB["food"] with food_type
            area = matching_area

    return foodtype, pricerange, area

def transform_utterance_levenshtein(tokenized_utterance, distance):
    
    new_list = []

    for word in tokenized_utterance:
        matching_food = compare_word_against_type(word, "food", distance)
        if (matching_food is not None):
            #insert KB["food"] with food_type
            word = matching_food

        matching_price = compare_word_against_type(word, "pricerange", distance)
        if (matching_price is not None):
            # insert KB["food"] with food_type
            word = matching_price

        matching_area = compare_word_against_type(word, "area", distance)
        if (matching_area is not None):
            # insert KB["food"] with food_type
            word = matching_area

        new_list.append(word)

    new_utterance = " ".join(new_list)

    return new_utterance

#extract_preference_inform("I would like to eat some portugese food")
