import xml.etree.ElementTree as ET
import re, collections, pickle
import time
count = 0
count1 = 0
diff_id = 0
pages = 0

cur_title=""
cur_id=-1

maxsize, sumsize = 0, 0
maxlink, sumlink = 0, 0
maxset, sumset = 0, 0

rp = re.compile(r'[\[][\[](.*?)]]')
rp2 = re.compile(r'[\[][\[]')
rp3 = re.compile(r'\|')
rp4 = re.compile(r'#')
#a =rp.findall('[[1|100|101[[233[3]33|2[0]0]]3[[4]]5[[6|600]][[77[7]77]]]][[88[8]88|80]]')

start = time.time()

fo = open('title2id_new.pickle', 'rb')
title2id = pickle.load(fo)
fo.close()

'''
title2id = dict()
for key, value in title2id_old.items():
	title2id[key.lower()] = int(value)
'''
	
for event, elem in ET.iterparse('enwiki-20190101-pages-articles.xml', events=['end']):
	count1+=1
	if count1 % 10000 == 0:
		print('count1 =',count1, 'time elapsed =', time.time() - start)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title' and cur_title=="":
		cur_title = elem.text
		#print('title =',cur_title)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}id':
		count +=1
		if cur_id == -1:
			cur_id = int(elem.text)
			diff_id += 1
			#print('id =',cur_id)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text' and elem.text!=None:
		#print(len(elem.text))
		elem.text = elem.text.lower()
		sumsize += len(elem.text)
		maxsize = max(maxsize, len(elem.text))
		links = rp.findall(elem.text)
		if links != None:
			maxlink = max(maxlink, len(links))
			sumlink += len(links)
			
			word_count = dict()
			#print('id =', cur_id, 'links before =', len(links))
			#print(elem.text)
			for i in range(len(links)):
				tmp = rp4.split(rp3.split(rp2.split(links[i])[-1])[0])[0]
				tmp = tmp.replace('_', ' ')
				tmp = ' '.join(tmp.split())
				
				if tmp in title2id:
					if title2id[tmp] not in word_count:
						word_count[title2id[tmp]] = elem.text.count(tmp)
						#print('id =', cur_id, 'matched =', tmp, 'matches =', word_count[title2id[tmp]])
				#curset.add(rp3.split(rp2.split(links[i])[-1])[0])
				#print(links[i])
			maxset = max(maxset, len(word_count))
			sumset += len(word_count)
			
			#word_count = dict()
			#for x in curset:
			#	word_count[x] = elem.text.count(x)
			with open('./links2/'+str(cur_id), 'wb') as f:
				pickle.dump(word_count, f)
			#print(word_count)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
		cur_id=-1
		cur_title=""
		pages += 1
	elem.clear()
print('count1=',count1)
print('ids=',count)
print('different ids =', diff_id)
print('pages =', pages)
print('maxsize =', maxsize)
print('avgsize =', sumsize / pages)
print('maxlink =', maxlink, 'sumlink =', sumlink, 'avglink =', sumlink / pages)
print('maxset =', maxset, 'sumset =', sumset, 'avgset =', sumset / pages)

'''
f = open('result2_all', 'w')
print('count1=',count1, file=f)
print('ids=',count,file=f)
print('different ids =', diff_id, file=f)
print('pages =', pages, file=f)
print('maxsize =', maxsize, file=f)
print('avgsize =', sumsize / pages, file=f)
print('maxlink =', maxlink, 'sumlink =', sumlink, 'avglink =', sumlink / pages, file=f)
print('maxset =', maxset, 'sumset =', sumset, 'avgset =', sumset / pages, file=f)

'''
print("ok")
