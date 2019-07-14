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

wiki2vec = Wikipedia2Vec.load('enwiki-20190420-50d.pkl')

#model = gensim.models.Word2Vec.load("gensim_100_model")
#print(type(model))

counter,count_valid = 0,0
	
#all_array = np.zeros(vec_count)

mmap = dict()

beg = time.time()

pre_emb = np.load('ent_embeddings_50.npy')
# fillin by random

fo = open('entity2id_wn.txt', 'r')
counter = 0

id2row = dict()
row2id = []
for line in fo:
	 ta = line.split()
	 id2row[ta[0]] = counter
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

count_filled = 0

def success(pageid, title, vec, mark=-1):
	global count_filled
	if pageid in id2row:
		ent_emb[id2row[pageid]] = vec
		marked[id2row[pageid]] = mark
		count_filled += 1
		
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
			
print('count filled =', count_filled)
def process_entity(filename):
	print('filename =', filename)
	print(ent_emb.shape)
	fo = open(filename, 'r')
	
	good_count = 0
	for line in fo:
		ta = line.split()
		if ta[0] in id2row and marked[id2row[ta[0]]] == 0:
			#good_count += 1
			#marked[id2row[ta[0]]] = 1
			available = int(ta[3], 16)
			for i in range(available):
				word = ta[4+i*2]
				try:
					tmp = wiki2vec.get_entity_vector(word)
				except KeyError:
					take2 = word.capitalize()
					try:
						tmp = wiki2vec.get_entity_vector(take2)
					except KeyError:
						if '_' in word:
							take3 = word.replace('_', ' ')
							try:
								tmp = wiki2vec.get_entity_vector(take3)
							except KeyError:
								take4 = take3.capitalize()
								try:
									tmp = wiki2vec.get_entity_vector(take4)
								except KeyError:
									take5 = ' '.join([s.capitalize() for s in take3.split()])
									try:
										tmp = wiki2vec.get_entity_vector(take5)
									except KeyError:
										pass
									else:
										success(ta[0], take5, tmp, 1)
										break
								else:
									success(ta[0], take4, tmp, 1)
									break
							else:
								success(ta[0], take3, tmp, 1)
								break
					else:
						success(ta[0], take2, tmp, 1)
						break
				else:
					success(ta[0], word, tmp, 1)
					break
	print('goods =', good_count)
	fo.close()
	
def process_word(filename):
	print('filename =', filename)
	fo = open(filename, 'r')
	for line in fo:
		ta = line.split()
		if ta[0] in id2row and marked[id2row[ta[0]]] == 0:
			available = int(ta[3], 16)
			for i in range(available):
				word = ta[4+i*2]
				try:
					tmp = wiki2vec.get_word_vector(word)
				except KeyError:
					pass
				else:
					success(ta[0], word, tmp, 2)
					break
							
process_entity('./WordNet-3.0/dict/data.noun')
process_entity('./WordNet-3.0/dict/data.verb')
process_entity('./WordNet-3.0/dict/data.adj')
process_entity('./WordNet-3.0/dict/data.adv')

np.save('ent_50_wn', ent_emb)


process_word('./WordNet-3.0/dict/data.noun')
process_word('./WordNet-3.0/dict/data.verb')
process_word('./WordNet-3.0/dict/data.adj')
process_word('./WordNet-3.0/dict/data.adv')

print('count_after', counter)
fb = open('bad_bad_id', 'w')
for i in range(counter):
	if marked[i] == 0:
		print(row2id[i], file=fb)
		
fb.close()

np.save('ent_50_wn_word', ent_emb)
np.save('marked', marked)
