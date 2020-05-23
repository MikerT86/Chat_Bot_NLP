DATA_PATH = "../../dstc2_merge/data/"
ONTOLOGY_FILE = '../Data_files/ontology_dstc2.json'
RESTAURANTS_FILE = '../Data_files/restaurantinfo.csv'
MODEL_NN  = '../Data_files/NN_model.pkl'
VOCABULARY = '../Data_files/vocabulary.txt'

TARGET_NAMES = ['ack', 'affirm', 'bye', 'confirm', 'deny', 'hello', 'inform', 'negate', 'null', 'repeat',
               'reqalts', 'reqmore', 'request', 'restart', 'thankyou']

PERCENTAGE_TRAIN_DATA = 85     # Variable for splitting up the data into a train and test file