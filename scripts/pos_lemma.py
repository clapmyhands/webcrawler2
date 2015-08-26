#!/home/khassan/projects/webcrawler2/wc_virt_env/bin/python 
##input txt file, output python dictionary##
import nltk, re
from nltk.stem import WordNetLemmatizer

def get_pos_lemma(wordnet_txt):
	wordnet_lemmatizer = WordNetLemmatizer()
	#Make sure the decoding codec is unicode##
	wordnet_txt = wordnet_txt.decode('utf-8')
	#Tokenize
	tokens		= nltk.word_tokenize(wordnet_txt)
	#tokens		= wordnet_txt.split()
	#Generate POS
	pos			= nltk.pos_tag(tokens)
	#Organize the POS and lemma into a dictionary
	data_dict	= {}
	i=0
	for ele in tokens:
		data_dict[ele]=[]
		data_dict[ele].append(wordnet_lemmatizer.lemmatize(ele))
		data_dict[ele].append(pos[i][1])
		i=i+1

	return  data_dict, tokens
