#!/home/khassan/projects/webcrawler2/wc_virt_env/bin/python 
import sqlite3, os, pos_lemma, pdb

db = None

def createDB(nameDB):
	global db
	if os.path.isfile(nameDB):
		os.remove(nameDB)
	db = sqlite3.connect(nameDB)
	with db:
		cur = db.cursor()
		cur.execute("CREATE TABLE word(node_id INTEGER, article_id INTEGER, sent_id INTEGER, word_id INTEGER, word TEXT, pos TEXT, lemma TEXT, PRIMARY KEY(node_id, article_id, sent_id, word_id))")
		cur.execute("CREATE TABLE sent(node_id INTEGER, article_id INTEGER, sent_id INTEGER, sent VARCHAR, PRIMARY KEY(node_id, article_id, sent_id))")
		cur.execute("CREATE TABLE source(node_id, article_id INTEGER, source TEXT, PRIMARY KEY(node_id, article_id))")
		cur.execute("CREATE TABLE keyword(node_id, article_id INTEGER, keyword TEXT, PRIMARY KEY(node_id, article_id, keyword))")
		cur.execute("CREATE TABLE node(node_id INT, node_name TEXT, ancestor_node_id INT, PRIMARY KEY(node_id))")
		cur.execute("CREATE TABLE article(node_id INT, article_id INT, PRIMARY KEY(node_id, article_id))")
		cur.execute("CREATE TABLE descendant(node_id INT, descendant_node_id INT, PRIMARY KEY(node_id, descendant_node_id))")
		#Inser ROOT node to the 'node' tables as id 0
		cur.execute("INSERT INTO node(node_id, node_name) VALUES(?,?)", (0, 'ROOT'))
		#cur.execute("INSERT INTO article(node_id) VALUES(?)", (0))
		#cur.execute("INSERT INTO node(node_id) VALUES(?)", (0))

def insert_sentDB(node_id, article_id, sent_id, keyword, source, sent):
	global db
	word_id	= 0
	dictPL, words = pos_lemma.get_pos_lemma(sent)
	sent = ' '.join(words)
	#words	= sent.split()					#split sentence into tokens(words)
	with db:
		cur	= db.cursor()
		#insert sentence to the 'sent' table
		cur.execute("INSERT INTO sent(node_id, article_id, sent_id, sent) VALUES(?,?,?,?)", (node_id, article_id, sent_id, sent))
		#insert words of the sentence to the 'word' table
		for word in words:
			cur.execute("INSERT INTO word(node_id,article_id,sent_id,word_id,word,pos,lemma) VALUES(?,?,?,?,?,?,?)", (node_id, article_id, sent_id, word_id, word, dictPL[word][1], dictPL[word][0]))
			word_id+=1

def insert_nodeDB(node_id, node_name, ancestor_node_id):
	global db
	with db:
		cur	= db.cursor()
		#insert node ancestor 
		cur.execute("INSERT INTO node(node_id, node_name, ancestor_node_id) VALUES(?,?,?)", (node_id, node_name, ancestor_node_id))
		#insert to the ancestor node a descendant node
		cur.execute("INSERT INTO descendant(node_id, descendant_node_id) VALUES(?,?)", (ancestor_node_id, node_id))

def insert_articleDB(article_id, source, keyword , node_id):
	global db
	with db:
		cur	= db.cursor()
		#insert source of the article
		cur.execute("INSERT INTO source(node_id, article_id, source) VALUES(?,?,?)", (node_id, article_id, source))
		cur.execute("INSERT INTO keyword(node_id, article_id, keyword) VALUES(?,?,?)", (node_id, article_id, keyword))
		cur.execute("INSERT INTO article(node_id, article_id) VALUES(?,?)", (node_id, article_id))

def closeDB():
	global db
	if db:
		db.close()
