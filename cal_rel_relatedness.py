import xml.etree.ElementTree as ET
import re, collections, pickle
import time, os
import numpy as np
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
#a =rp.findall('[[1|100|101[[233[3]33|2[0]0]]3[[4]]5[[6|600]][[77[7]77]]]][[88[8]88|80]]')

start = time.time()

'''
fo = open('id2title_1000.pickle', 'rb')
id2title = pickle.load(fo)
fo.close()
'''

'''
fo = open('title2id.pickle', 'rb')
title2id = pickle.load(fo)
fo.close()
'''

W = np.log(19000000)
print('W =', W)

counter = 0

#files = os.listdir('./links2')

#for pageid, title in id2title.items():

count = 0
count_good = 0
fb = open('wiki_entity_aftermod.out', 'r')

#all_array = np.zeros(vec_count)
for line in fb:
	ta = line.split()
	count += 1
	if len(ta) == 2:
		pageid = ta[1]
		if not os.path.exists('./links2/'+pageid):
			print('fuck', pageid)
		
		fl = open('./links2/'+pageid, 'rb')
		cur_word_count = pickle.load(fl)
		fl.close()
		
		counter += 1
		if counter % 10 == 0:
			print('counter =', counter, 'time elapsed =', time.time() - start)
		#print(pageid)
		#print(len(cur_word_count), type(cur_word_count))
		#print(cur_word_count)
		#for words, freq in cur_word_count.items():
		#	print(words, freq)
	
		cur_rel = dict()
		sum_weight = 0.0
		#print('id =', pageid, 'len =', len(cur_word_count))
		for word, freq in cur_word_count.items():
			# calc joint
			fr = open('./links2/'+str(word), 'rb')
			cur_word_count2 = pickle.load(fr)
			fr.close()
		
			if len(cur_word_count2) == 0:
				continue
			#print('link =', word, 'len =', len(cur_word_count2), 'minsize =', np.log(min(len(cur_word_count), len(cur_word_count2))))
			
			and_size = 0
			if len(cur_word_count) < len(cur_word_count2):
				for word2 in cur_word_count:
					if word2 in cur_word_count2:
						and_size += 1
			else:
				for word2 in cur_word_count2:
					if word2 in cur_word_count:
						and_size += 1
			#print('andsize =', and_size)
			if and_size == 0:
				continue
			tmp = 1.0 - (np.log(max(len(cur_word_count), len(cur_word_count2))) - np.log(and_size)) / (W - np.log(min(len(cur_word_count), len(cur_word_count2))))
			#print('tmp =', tmp)
			sum_weight += tmp
			cur_rel[word] = tmp
		if sum_weight < 1e-9:
			continue
		#print('sum_wegight =', sum_weight)
		for word in cur_rel:
			cur_rel[word] /= sum_weight
		with open('./rel2/'+pageid, 'wb') as f:
			pickle.dump(cur_rel, f)
		

'''
print(type(id2title))
print(id2title)

print(type(title2id))
print(title2id)
for pageid, title in id2title.items():
	print(pageid, title)
for title, pageid in title2id.items():
	print(title, pageid)
	
for pageid, title in id2title.items():
	print(type(pageid), type(title))
'''
