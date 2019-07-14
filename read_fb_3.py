#coding:utf8
import bz2
import json
import time

def readFromBz2(file):
	tmp = str(file.readline(), encoding='utf-8')
	content = tmp.replace('\n', '')
	#content = str(file.readline()).replace('\n', '')
	if (content == "]"):
		return False, []
	if (content[-1] == ","):
		content = content[0:-1]
	content = json.loads(content)
	return True, content

def operateList(file, lists):
	global ss
	if 'claims' in lists:
		for i in lists['claims']:
			for j in lists['claims'][i]:
				if ('type' in j) and (j['type'] == 'statement') and ('mainsnak' in j):
					if ('property' in j['mainsnak']) and (j['mainsnak']['property'] == 'P2888'):
						ss += 1
						title = lists['labels']['en']['value']
						if ('sitelinks' in lists) and ('enwiki' in lists['sitelinks']):
							title = lists['sitelinks']['enwiki']['title']
						file.write(lists['id'] + ' ' + j['mainsnak']['datavalue']['value'] + ' ' + title + '\n')
					'''
					con = j['mainsnak']
					if ('datavalue' in con) and (con['datatype'] == u'wikibase-item'):
						file.write(lists['id'] + "\t" +  con['property'] + "\t" +  'Q' + (str)(con['datavalue']['value']['numeric-id']) + "\n")
						ss += 1
					if ('datavalue' in con) and (con['datatype'] == u'wikibase-property'):
						file.write(lists['id'] + "\t" +  con['property'] + "\t" +  'P' + (str)(con['datavalue']['value']['numeric-id']) + "\n")
						ss += 1
					'''

ss = 0
file = bz2.BZ2File("latest-all-2019.json.bz2", "r")
#file = open('latest10.json', 'r')
fout = open("wn2wikidata3.txt", "w")
log = open("log.txt", "w")
content = file.readline()
flag = True
lists = []
tot = 0

start = time.time()
while (flag):
	flag, lists = readFromBz2(file)
	if not flag:
		break
	tot = tot + 1
	try:
		operateList(fout, lists)
		if (tot % 10000 == 0):
			print(tot, ss, 'time =', time.time() - start)
			#print (time.time() - start)
	except Exception:
		print(lists['id'])
		log.write(lists['id'] + "\n")
log.close()
fout.close()
file.close()
