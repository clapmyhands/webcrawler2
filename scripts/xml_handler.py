import xml.etree.ElementTree as ET
import os
from lxml import etree
from xml.dom.minidom import parse, parseString

'''
Creates the XML file
'''
def createXMLFile(fileName):
	try:
		if not os.path.isfile(fileName):
			tree	= ET.ElementTree()
			root	= ET.Element('database')
			tree._setroot(root)
			tree.write(fileName, xml_declaration=True, encoding='utf-8', method="xml")
			return '0'
		else:
			xPath	= ".//doc[last()]"
			tree	= ET.parse(fileName)
			root	= tree.getroot()
			lastElement = root.find(xPath)
			return lastElement.attrib['doc_id']
	except:
		print "Failed to open file."

'''
Write to the XML file
'''
def writeXMLFile(fileName, doc_id, keyword, URL, text):
	try:
		tree	= ET.parse(fileName)
		root	= tree.getroot()
		child	= ET.SubElement(root,"doc",{'doc_id':str(doc_id), 'keyword':keyword, 'URL':URL})
		child.text = text
		tree.write(fileName, xml_declaration=True, encoding='utf-8', method="xml")
	except:
		print "Failed to write into the file."

'''
Check for existing articles, otherwise create it.
'''
def checkDuplicate(fileName, keyword, URL):
	try:
		tree	= ET.parse(fileName)
		root	= tree.getroot()
		xPath	= ".//doc[@keyword=\'"+keyword+"\'"+"]"
		for elementNode in root.findall(xPath):
			if elementNode.attrib['URL'] == URL:
				print "Dupilcate detected"
				return True
		return False 
	except:
		return False

'''
Reparse the XML document to make it more readable.
'''   
def prettifyXML(fileName):
	try:
		parserFormat	= etree.XMLParser(remove_blank_text=True)
		tree			= ET.parse(fileName, parserFormat)
		root			= tree.getroot()
		rough_string	= ET.tostring(root, encoding = "utf-8", method = "xml")
		reparsed		= parseString(rough_string)
		f				= open(fileName , 'w')
		f.write(reparsed.toprettyxml(indent="\t").encode('utf-8'))
		f.close()
	except:
		print "Prettify failed"
