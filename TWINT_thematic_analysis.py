# thematic analysis for TWINT

# run this program from the command line with the csv file from TWINT as the argument

# edit the 'themes_and_words.xlxs' file to include your themes and search-words,
# 	column 1 is the theme; column two is the search word

# this code returns a binary variable for each theme that take the value 1
# if at least one of the words in that theme appear in each Tweet

from sys import argv
script, TWINT_file = argv

import pandas as pd
import numpy as np
import inflection
import re

data = pd.read_csv(TWINT_file, engine = 'python')

data['tweet2']  = data['tweet'].apply(str)
data['tweet2'] = data.apply(lambda row: re.sub(r'[^a-z0-9]'," ", inflection.underscore(row['tweet2'])), axis=1)

words = pd.read_excel('themes_and_words.xlxs')
words['word'] = words['word'].apply(str)

themes = words['theme'].unique().tolist()

def function(list1,list2):
	if len([x for x in list1 if x in list2])>=1:
		return 1
	else:
		return 0

for i in range(len(themes)):
	data[themes[i]] = data.apply(lambda row: function(words[words.theme==themes[i]].word.tolist(), row['tweet2']), axis=1)
	# creates a dummy variable using the word_finder function above

data = data.drop(['tweet2'], axis=1)

data.to_csv(TWINT_file, sep=',', encoding = 'utf-8')
