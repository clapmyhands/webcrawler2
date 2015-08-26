#!/home/khassan/projects/webcrawler2/wc_virt_env/bin/python
# -*- coding:utf-8 -*-
"""
"""
import re, os, json, pdb
from num2words import num2words

def cleanText(text, acronymFile):
	#Load dictionary of acronyms and abbrs
	if not os.path.isfile(acronymFile):
		print('***Acronym/abbreviation file does not exist! Acronyms and abbrs will not be expanded! (In normalize.py)***')
	else:
		temp_reader	= open(acronymFile,'r')
		abbr_list	= json.load(temp_reader)
		temp_reader.close()
		#Expand abbreviations and acronyms
		tokenList	= text.split()
		for token in tokenList:
			if token.lower() in abbr_list:
				tokenList[tokenList.index(token)] = abbr_list[token.lower()]
		text	= ' '.join(tokenList)
	#Convert text into lowercase
	text	= text.lower()
	#protect not identified (not in our list) abbrs and acronynms, by replacing periods with underscore, A.B.C.D.E.F.=>A_B_C_D_E_F_
	text	= re.sub('([a-z])\.([a-z])','\g<1>_\g<2>',text)
	text	= re.sub('_([a-z])\.','_\g<1>_',text)
	text	= re.sub('_([a-z])\.','_\g<1>_',text)
	#Remove phrases enclosed in the brackers, eg: (word1 word 2), <word3 word4> and etc.
	text	= re.sub('(\[.*?\]|\(.*?\)|\{.*?\}|<.*?>)','',text)
	text	= re.sub(' +',' ',text)		#remove multiple spaces
	#Seperate floating numbers by 'point', eg: 1.4=> 1 point 4, .5  => 0 point 5
	text	= re.sub('(\d)\.(\d)','\g<1> point \g<2>',text)
	#text	= re.sub('( +)\.(\d)',' 0 point \g<2>',text)
	#Join thousands, eg: 1,000,000=>1000000
	text	= re.sub('(\d),(\d)','\g<1>\g<2>',text)
	#Put space between decimal and non decimal, eg: 50% => 50 %, 4am => 4 am, 100$ => 100 $, #5 => # 5
	text	= re.sub('(\d)(\D)','\g<1> \g<2>',text)
	text	= re.sub('(\D)(\d)','\g<1> \g<2>',text)
	text	= re.sub(' +',' ',text)		#remove multiple spaces
	#Replace symbols, eg: 2 $=>2 dollars,1 $=>1 dollar, 5 %=>5 percents and etc.
	text	= re.sub('\$','dollars', text)
	#text	= re.sub('','euros', text)
	#text	= re.sub('','pounds', text)
	#text	= re.sub('','yuans', text)
	text	= re.sub('%','percents', text)
	text	= re.sub('&','and', text)
	#Math equations, eg: 4 + 5 = 9, 4 plus 5 equals 9
	text	= re.sub('(\d) \+ (\d)','\g<1> plus \g<2>', text)
	text	= re.sub('(\d) - (\d)','\g<1> minus \g<2>', text)
	text	= re.sub('(\d) \* (\d)','\g<1> product \g<2>', text)
	text	= re.sub('(\d) / (\d)','\g<1> over \g<2>', text)
	text	= re.sub('(\d) = (\d)','\g<1> equals \g<2>', text)
	text	= re.sub('(\d) > (\d)','\g<1> more than \g<2>', text)
	text	= re.sub('(\d) < (\d)','\g<1> less than \g<2>', text)
	#text	= re.sub('(\d) >= (\d)','\g<1> more or equal to \g<2>', text)
	#text	= re.sub('(\d) <= (\d)','\g<1> less or equal to \g<2>', text)
	text	= re.sub(' +',' ',text)		#remove multiple spaces
	#Replaces other symbols with whitespace
	text	= re.sub('(\++|,+|-+|\*+|:+|/+|>+|<+|=+|\^+|%+|\$+|#+|@+|\|+|~+|`+|\'+|\"+)',' ',text)
	text	= re.sub(' +',' ',text)		#remove multiple spaces
	#num to words conversion
	for word in text.split():
		if str(word.encode('utf-8')).isdigit():
			text = text.replace(word, num2words(float(word)),1)
	#Replace the rest symbols with the period, in order to split sentences by period later.
	text	= re.sub('(!+|\?+|;+|:+)','.', text)
	return text
