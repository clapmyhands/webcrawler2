#!/home/khassan/projects/webcrawler2/wc_virt_env/bin/python
# -*- coding:utf-8 -*-
'''
In boilerpipe/extract/__init__.py
1. Change user-agent to: - "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
2. Change getHTML() function to "return self.data"
'''
from __future__ import print_function
from guess_language import guessLanguage
from boilerpipe.extract import Extractor
import pdb, os, sys, re, lxml.html, json, urllib, argparse
import normalize, db, time
import xml.etree.ElementTree as ET
from xml_handler import *
from num2words import num2words

#inputs
#num				- number of links per page to display  (default: 10)
#lang				- language (default: en)
#sortby				- sort link by relevance or date (default: relevance)
#sourceList.json	- source query pattern
#keyword.list		- list of keywords
#normalize			- true or false
if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--inputFile", help="input file containg keywords (one keyword per line)", required=True)
	parser.add_argument("-f","--sourceFile", help="input file containg source list (json file)", required=True)
	parser.add_argument("-o","--outputDir", help="output folder for saving search results", required=True)
	parser.add_argument("-a","--abbrFile", help="input file containg abbreviation/acronym list (json file)", required=False)
	parser.add_argument("-r","--result", help="number of results to generate in search, defalut value '10'", default='10')
	parser.add_argument("-s","--sortby", help="sort the links by 'date', default value 'relevance'", choices=['date','relevance'], default='')
	parser.add_argument("-l","--lang", help="set text language, default value 'english'", choices=['en','fr','es'], default='en')
	parser.add_argument("-n","--norm", help="activate normalization", action="store_true", default=False)
	args = parser.parse_args()

	if not os.path.isfile(args.sourceFile) or not os.path.isfile(args.inputFile):
		print('***Input file or source file does not exist! Exiting... (in main.py)')
		exit()

	if not os.path.isdir(args.outputDir):
		os.mkdir(args.outputDir)

	if args.norm:
		print('Normalization is activated')
	else:
		print('Normalization is deactivated')

	#Create new otput directory, delete it if exists
	#os.system('rm -r '+str(args.outputDir))
	#os.mkdir(args.outputDir)
	
	#Create output file (XML format)
	#pdb.set_trace()
	#prettifyXML(args.outputDir+"/output_file.xml")
	#exit()
	doc_id = int(createXMLFile(args.outputDir+"/output_file.xml")) + 1
	#Read source (seed) list
	temp_reader		= open(args.sourceFile,'r')
	source_list		= json.load(temp_reader)
	temp_reader.close()

	#Read list of keywords
	temp_reader		= open(args.inputFile,'r') 
	keyword_list	= temp_reader.read().splitlines()
	temp_reader.close()
	log_writer		= open('logfile.txt','a')

	#All text will be saved automatically in database and in output directory text file 'text.tmp'
	#Create database container, db.createDB(DB name), DSC = domain specific corpus
	#db.createDB("DSC2.db")
	#node_id		= 0	
	#article_id	= -1 
	#sent_id		= -1 

	for keyword in keyword_list:
		log_writer.write('searching articles on: '+ keyword+'\n')
		for source in source_list:
			pattern	= str(source['Pattern']).split()
			query	= ""
			xpath	= ""
			#build URL query
			for obj in pattern:
				if obj =='xpath':
					XPATH = source[obj]
				elif obj =='url': 
					query += source[obj+'_def']
				elif obj =='keyword':
					query += source[obj]
					query += '\"'+keyword.replace(' ','+')+'\"'
				elif obj =='num' and args.result !="":
					query += source[obj]
					query += args.result
				elif obj =='lang' and args.lang !="":
					query += source[obj]
					query += args.lang
				#elif obj =='sortby' and args.sortby !="":
				#	query += source[obj]
				#	query += args.sortby 
				else:
					query += source[obj]
					query += source[obj+'_def']
			#retrieve HTML page of the URL source
			try:
				extractor		= Extractor(extractor='ArticleExtractor', url=query)
				extracted_html	= extractor.getHTML()
			except:
				e = sys.exc_info()[0]
				print("\n***ERROR (in main.py, extractor 1): "+str(e))
				# sleep for 4 seconds before trying crawling agian, otherwise you will be identified and blocked
				time.sleep(4)
				continue

			#retrieve URLs from the HTML page
			doc	= lxml.html.document_fromstring(extracted_html)
			urlList = list()
			for url in doc.xpath(XPATH):
				url_tmp = str(url.attrib.get('href'))
				if not 'http' in url_tmp:
					url_tmp = source['url']+url_tmp
				urlList.append(url_tmp)

			#retrieve texts from the URLs
			for url in urlList:
				try:
					extractor		= Extractor(extractor='ArticleExtractor', url=url)	
					extracted_text	= extractor.getText()

					#skip text if size is less than threshold
					if len(extracted_text)<500:
						print("\n***SIZE IS TOO SMALL, TEXT IS EXCLUDED!!! (in main.py, extractor)\n")
						# sleep for 4 seconds before trying crawling agian, otherwise you will be identified and blocked
						time.sleep(4)
						continue

					#skip text if the language is not same as requested
					lang_tmp = guessLanguage(extracted_text).encode('utf-8')
					if lang_tmp != args.lang:
						print("\n***WRONG LANGUAGE!!! (in main.py, guessLanguage)")
						# sleep for 4 seconds before trying crawling agian, otherwise you will be identified and blocked
						time.sleep(4)
						continue
				except:
					#if 'request timeout' happens go to the next URL
					e = sys.exc_info()[0]
					print("\n***ERROR (in main.py, extractor 2): "+str(e))
					# sleep for 4 seconds before trying crawling agian, otherwise you will be identified and blocked
					time.sleep(4)
					continue
				#article_id += 1
				#db.insert_articleDB(article_id, url, keyword.replace('+',' '), node_id)
				#pdb.set_trace()
				if not checkDuplicate(args.outputDir+"/output_file.xml", keyword, url):
					writeXMLFile(args.outputDir+"/output_file.xml", doc_id, keyword, url, extracted_text)
					doc_id += 1
log_writer.close()
#********************************************************************************************************
#*********************** TEXT NORMALIZATION AND SENTENCE SEGMENTATION ***********************************
'''	
					#print(extracted_text.encode('utf-8'))
					#Text normaliztion
					extracted_text = normalize.cleanText(extracted_text, args.abbrFile)
					#print(extracted_text.encode('utf-8'))
					#Sentence segmentation and saving data to the db, in one sentence per line manner
					extracted_text = extracted_text.splitlines()
					temp_sent	=''
					prev_line	='period'
					sent_id		= -1
					for cur_line in extracted_text:
						if prev_line != 'period':
							new_line = temp_sent+' '+cur_line
						else:
							new_line = cur_line
						line = new_line.split('.')
						for sent in line:
							if sent == '':
								prev_line='period'
							elif line.index(sent)==(len(line)-1):
								if extracted_text.index(cur_line)==(len(extracted_text)-1):
									sent = re.sub('\s+',' ',sent).strip()
									#temp_writer.write(sent.encode('utf-8')+'\n')
									sent_id+=1
									db.insert_sentDB(node_id, article_id, sent_id, keyword, url, sent.encode('utf-8'))
								else:
									temp_sent = sent
									prev_line='NOT'
							elif len(sent) > 40:
								sent = re.sub('\s+',' ',sent).strip()
								#temp_writer.write(sent.encode('utf-8')+'\n')
								sent_id+=1
								db.insert_sentDB(node_id, article_id, sent_id, keyword, url, sent.encode('utf-8'))
							else:
								prev_line='period'
'''
	#db.closeDB()
#pdb.set_trace()
prettifyXML(args.outputDir+"/output_file.xml")
exit()
'''
#TEXT NORMALIZATION
				#1. expand abbreviations and acronyms
				for abbr in abbr_list:
					extracted_text = extracted_text.replace(abbr,abbr_list[abbr])
			
				#2. remove garbage symbols
				extracted_text	= re.sub('(\[.*\]|\(.*\)|\{.*\}|<.*>)','',extracted_text)												#removes all words in brackets
				extracted_text	= re.sub('(\++|,+|-+|\*+|:+|/+|>+|<+|=+|\^+|%+|\$+|#+|@+|\|+|~+|_+|`+|\'+|\"+)',' ',extracted_text)		#removes symbols 
				extracted_text	= re.sub(' +',' ',extracted_text)																		#removes multiple spaces

				#3. num to words conversion
				for word in extracted_text.encode('utf-8').split():
					if str(word).replace('.','',1).isdigit():
						extracted_text = extracted_text.replace(str(word), num2words(float(word)),1)'''
