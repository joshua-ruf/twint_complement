# geocoder for TWINT

# run from the command line with the TWINT csv file as the argument
# make sure the df_states (file with North American state and province
# names) is included; and make sure the df_cities (file with large North American
# cities) is also included in your directory

from sys import argv
script, filename =  argv

import pandas as pd
import numpy as np
import inflection
import nltk as nltk
import re

data = pd.read_csv(filename, engine = 'python')

data['location']  = data['location'].apply(str)
# convert location data to text

def rm_punctuation(s):
	s = ' ' + re.sub(r'[^a-z]'," ", inflection.underscore(s)) + ' '
	return s
# makes underscores spaces, converts to lowercase, and leaves only characters

data['test'] = data.apply(lambda row: rm_punctuation(row['location']), axis=1)
# rid punctuation, CamelCase, and put spacing around words to ease searching

############################################
# In this section we label the tweet by location, separated by how the location was
# obtained (i.e. abb, dec, name)
############################################
df_states = pd.read_csv('df_states.csv')

data['test2'] = data.apply(lambda row: row['test'].upper(), axis=1)
data['test2'] = data['test2'].apply(nltk.word_tokenize)
# test2 is capitalized and tokenized, just use for state_abb search

def intersection(lst1):
    return set(lst1).intersection(set(df_states.state.tolist()))

data['state_abb'] = data['test2'].apply(intersection)

def state_dec_search(x):
	for i in range(len(df_states)):
		if df_states['state_dec'][i] != 'None':
			if df_states['state_dec'][i] in x:
				return df_states['state'][i]

data['state_dec'] = data['test'].apply(state_dec_search)

def state_name_search(x):
	for i in range(len(df_states)):
		if df_states['state_name'][i] in x:
			return df_states['state'][i]

data['state_name'] = data['test'].apply(state_name_search)

######################################################
# determines state/province from city mentions
######################################################
big =  pd.read_csv('df_cities.csv')

def city_finder(x):
	for i in range(len(big)):
		if big['city'][i] in x:
			return big['state_id'][i]

data['city_search'] = data['test'].apply(city_finder)

###############################
#Here is the geocoder!
###############################

def geocode(state_abb, state_dec, state_name, city_search):
	if len(state_abb)==0:
		if state_dec != None:
			return state_dec
		if state_dec == None:
			if state_name != None:
				return state_name
			if state_name == None:
				if city_search != None:
					return city_search
				if city_search == None:
					return None
	if len(state_abb)==1:
		return state_abb
	if len(state_abb)>1:
		return state_abb.intersection({state_dec, state_name, city_search})

data['geocode'] = data.apply(lambda row: geocode(row.state_abb,row.state_dec,row.state_name,row.city_search),axis=1)

data = data.dropna(subset = ['geocode'])
data = data.reset_index(drop = True)
# keep only data with locations

def set_to_string(set):
	set = [k for k in set] #converts set to list
	return ''.join(set) # converts list to string

data.geocode = data.apply(lambda row: set_to_string(row.geocode), axis=1)

data = data[data.geocode!='']
data = data.reset_index(drop = True)
#drops tweets without location information

data = data.drop(['test', 'test2', 'state_abb', 'state_dec', 'state_name', 'city_search'], axis=1)

# set = {k for k in set}
#converts list to set

text_file = open(filename+"tweet_count", "w")
text_file.write("Number of unique tweets with geocodes: %s\n" % len(data))
text_file.close()

data.to_csv(filename, sep=',', encoding = 'utf-8')
