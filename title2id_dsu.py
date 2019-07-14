#mod again
import xml.etree.ElementTree as ET
import re, collections, pickle
import time

id2id = dict()

def findset(x):
	if x not in id2id or x == id2id[x]:
		return x
	id2id[x] = findset(id2id[x])
	return id2id[x]
	
rp = re.compile(r'[\[][\[](.*?)]]')
rp2 = re.compile(r'[\[][\[]')
rp3 = re.compile(r'\|')
rp4 = re.compile(r'#')

#print(rp4.split('abcd efgfd#12345#666 566')[0])

start = time.time()

count1=0
count_redirect = 0

'''
fo = open('title2id.pickle', 'rb')
title2id_old = pickle.load(fo)
fo.close()

# transfer to lower case
title2id_lower = dict()
for key, value in title2id_old.items():
	title2id_lower[key.lower()] = value

print(len(title2id_lower))
'''

print('start')
title2id = dict()
cur_title=""
cur_id=-1
diff_id=0
for event, elem in ET.iterparse('enwiki-20190101-pages-articles.xml', events=['end']):
	count1+=1
	if count1 % 100000 == 0:
		print('count1 =',count1, 'redirects =', count_redirect, 'time elapsed =', time.time() - start)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title' and cur_title=="":
		cur_title = elem.text.lower()
		#print('title =',cur_title)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}id':
		#count +=1
		if cur_id == -1:
			cur_id = int(elem.text)
			diff_id += 1
			#print('id =',cur_id)
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text' and elem.text!=None:
		#print(cur_id)
		#cur_id_int = int(cur_id)
		#print('title =', cur_title)
		#print('cur_id =', cur_id)
		#print(elem.text)
		if elem.text.startswith('#REDIRECT [['):
			count_redirect += 1
			tmp = rp4.split(rp3.split(rp2.split(rp.findall(elem.text)[0])[-1])[0])[0]
			#print(tmp)
			tmp = tmp.replace('_', ' ').lower()
			tmp = ' '.join(tmp.split())
			
			if tmp.startswith(':'):
				tmp = tmp[1:]
				
			if cur_title in title2id:
				id2id[cur_id] = title2id[cur_title]
			else:
				if tmp in title2id:
					id2id[cur_id] = title2id[cur_title] = title2id[tmp]
				else:
					id2id[cur_id] = title2id[cur_title] = cur_id
			#print('tmp =', tmp)
			'''
			if tmp not in title2id_lower:
				#print('error id =', cur_id, 'split to', tmp, 'original text =')
				#print(elem.text)
				id2id[cur_id] = title2id[cur_title] = cur_id
			else:
				old_id = int(title2id_lower[tmp])
				#print('old id =', old_id)
				id2id[cur_id] = title2id[cur_title] = findset(old_id)
			'''
				
		else:
			id2id[cur_id] = title2id[cur_title] = cur_id
		#print(cur_title, cur_id, id2id[cur_id], type(id2id[cur_id]), type(title2id[cur_title]))
		'''
		#print(len(elem.text))
		sumsize += len(elem.text)
		maxsize = max(maxsize, len(elem.text))
		links = rp.findall(elem.text)
		if links != None:
			maxlink = max(maxlink, len(links))
			sumlink += len(links)
			
			curset = set()
			for i in range(len(links)):
				curset.add(rp3.split(rp2.split(links[i])[-1])[0])
				#print(links[i])
			maxset = max(maxset, len(curset))
			sumset += len(curset)
			
			word_count = dict()
			for x in curset:
				word_count[x] = elem.text.count(x)
			with open('./links/'+cur_id, 'wb') as f:
				pickle.dump(word_count, f)
			#print(word_count)
		'''
	
	if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
		cur_id=-1
		cur_title=""
		#pages += 1
	elem.clear()
	


with open('id2id_after_dsu.pickle', 'wb') as f:
	pickle.dump(id2id, f)
	
with open('title2id_pre_dsu_2.pickle', 'wb') as f:
	pickle.dump(title2id, f)


print('redirects =', count_redirect)
print(len(id2id))
for key in id2id:
	id2id[key] = findset(key)
	
print(len(title2id))
for key in title2id:
	#print(key, title2id[key])
	title2id[key] = findset(title2id[key])
	
with open('id2id_new2.pickle', 'wb') as f:
	pickle.dump(id2id, f)
	
with open('title2id_new2.pickle', 'wb') as f:
	pickle.dump(title2id, f)
