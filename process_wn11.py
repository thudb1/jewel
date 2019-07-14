import numpy as np
import os, re
import pickle
#import gensim
import time, random
from wikipedia2vec import Wikipedia2Vec

vec_count = 50
#fkk = open('id2title.pickle', 'rb')
#id2title = pickle.load(fkk)

'''
fkk = open('id2id.pickle', 'rb')
id2id = pickle.load(fkk)
'''

wiki2vec = Wikipedia2Vec.load('enwiki-20190420-50d-disambi.pkl')

#model = gensim.models.Word2Vec.load("gensim_100_model")
#print(type(model))

counter,count_valid = 0,0
	
#all_array = np.zeros(vec_count)

mmap = dict()

beg = time.time()

pre_emb = np.load('ent_embeddings_50.npy')
# fillin by random

fo = open('entity2id_wn11.txt', 'r')
counter = 0

#id2row = dict()
row2id = []
for line in fo:
	 ta = line.split()
	 #id2row[ta[0]] = counter
	 counter += 1
	 row2id.append(ta[0])
	 
'''
while pre_emb.shape[0] < counter:
	pre_emb = np.row_stack((pre_emb, pre_emb[random.randint(0, pre_emb.shape[0]-1)]))
'''

ent_emb = np.zeros((counter, vec_count))
for i in range(counter):
	ent_emb[i] = pre_emb[random.randint(0, pre_emb.shape[0]-1)]
	
marked = np.zeros(counter, dtype=np.int)

print('counter =', counter)

count_filled = 0

'''
def success(pageid, title, vec, mark=-1):
	global count_filled
	if pageid in id2row:
		ent_emb[id2row[pageid]] = vec
		marked[id2row[pageid]] = mark
		count_filled += 1
'''
		
'''
fi = open('wn2wikidata3.txt', 'r')
counter_good, counter_bad = 0,0
for line in fi:
	ta = line.split()
	if ta[1].startswith('http://wordnet-rdf.princeton.edu/wn30'):
		pageid = ta[1][38:46]
		wikititle = ' '.join(ta[2:])
		try:
			tmp = wiki2vec.get_entity_vector(wikititle)
		except KeyError:
			take2 = wikititle.capitalize()
			try:
				tmp = wiki2vec.get_entity_vector(take2)
			except KeyError:
				take3 = ' '.join([s.capitalize() for s in wikititle.split()])
				try:
					tmp = wiki2vec.get_entity_vector(take3)
				except KeyError:
					print(pageid, take3)
					counter_bad += 1
				else:
					success(pageid, take3, tmp)
					counter_good += 1
			else:
				success(pageid, take2, tmp)
				counter_good += 1
		else:
			success(pageid, wikititle, tmp)
			counter_good += 1
'''
			
#print('count filled =', count_filled)
def process_entity():
	'''
	print('filename =', filename)
	print(ent_emb.shape)
	fo = open(filename, 'r')
	'''
	#good_count = 0
	global count_filled
	for i in range(counter):
		word = (row2id[i].replace('_', ' ')[:-1]).strip()
		#print(word)
		try:
			tmp = wiki2vec.get_entity_vector(word)
		except KeyError:
			take2 = word.capitalize()
			try:
				tmp = wiki2vec.get_entity_vector(take2)
			except KeyError:
				try:
					tmp = wiki2vec.get_entity_vector(' '.join([s.capitalize() for s in word.split()]))
				except KeyError:
					pass
				else:
					count_filled += 1
					marked[i] = 1
					ent_emb[i] = tmp
			else:
				count_filled += 1
				marked[i] = 1
				ent_emb[i] = tmp
				#success(ta[0], take2, tmp, 1)
				#break
		else:
			count_filled += 1
			marked[i] = 1
			ent_emb[i] = tmp
			#success(ta[0], word, tmp, 1)
			#break
	
def process_word():
	#print('filename =', filename)
	#fo = open(filename, 'r')
	global count_filled
	for i in range(counter):
		if marked[i] == 0:
			word = (row2id[i].replace('_', ' ')[:-1]).strip()
			try:
				tmp = wiki2vec.get_word_vector(word)
			except KeyError:
				pass
			else:
				count_filled += 1
				marked[i] = -1
				ent_emb[i] = tmp

process_entity()
print('count entity =', count_filled)

process_word()

print(count_filled)
np.save('ent_50_wn11', ent_emb)
