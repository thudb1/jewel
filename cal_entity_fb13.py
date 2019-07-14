import numpy as np
import os, re
import pickle
#import gensim
import time
import random
from wikipedia2vec import Wikipedia2Vec

#files = os.listdir('./rel')

vec_count = 50
'''
fkk = open('id2title.pickle', 'rb')
id2title = pickle.load(fkk)
'''

'''
fkk = open('id2id.pickle', 'rb')
id2id = pickle.load(fkk)
'''

wiki2vec = Wikipedia2Vec.load('enwiki-20190420-50d-disambi.pkl')

#model = gensim.models.Word2Vec.load("gensim_100_model")
#print(type(model))

counter,count_valid = 0,0
	
#all_array = np.zeros(vec_count)

fg = open('bad_fb', 'w')
mmap = dict()

beg = time.time()

pre_emb = np.load('ent_embeddings_50.npy')
res = np.zeros(vec_count)

good = 0
fb = open('entity2id-fb13.txt', 'r')
for line in fb:
	ta = line.split()
	counter += 1
	cur = np.zeros(vec_count)
	
	if len(ta) == 2:
		pageid = ta[0].replace('_', ' ')
		try:
			tmp = wiki2vec.get_entity_vector(pageid)
		except KeyError:
			take2 = pageid.capitalize()
			try:
				tmp = wiki2vec.get_entity_vector(take2)
			except KeyError:
				take3 = ' '.join([s.capitalize() for s in pageid.split()])
				try:
					tmp = wiki2vec.get_entity_vector(take3)
				except KeyError:
					res = np.row_stack((res, pre_emb[random.randint(0, pre_emb.shape[0]-1)]))
				else:
					good += 1
					res = np.row_stack((res, tmp))
			else:
				good += 1
				res = np.row_stack((res, tmp))
		else:
			good += 1
			res = np.row_stack((res, tmp))
		'''
		if not os.path.exists('./rel/'+pageid):
			#print('fuck', pageid)
			all_array = np.row_stack((all_array, cur))
			continue
		fl = open('./rel/'+pageid, 'rb')
		cur_word_count = pickle.load(fl)
		fl.close()
		count_valid += 1
		
		#print(cur_word_count)
		sum_value = 0.0
		for word, value in cur_word_count.items():
			try:
				tmp = wiki2vec.get_entity_vector(id2title[str(word)])
			except KeyError:
				#all_array = np.row_stack((all_array, cur))
				continue
			else:
				sum_value += value
				cur += tmp * value
		if sum_value > 1e-8:
			cur /= sum_value
		'''
		'''
		if pageid in id2title:
			try:
				tmp = wiki2vec.get_entity_vector(id2title[pageid])
			except KeyError:
				continue
			else:
				pre_emb[counter-1] = tmp
				count_valid += 1
				#cur = tmp
		'''
	#print(id2title[pageid], cur)
	#all_array = np.row_stack((all_array, cur))
	#all_array = np.inert(all_array, 0, values = cur, axis=0)
	if counter % 500 == 0:
		#break
		print('counter =', counter, 'time =', time.time() - beg)
		
#print(all_array)

#print('after deletion')
#all_array = np.delete(all_array, 0, axis = 0)

print('valid =', good)
np.save('ent_50_fb13', res)
checkok = np.load('ent_50_fb13.npy')

print(checkok.shape)
'''
for i in range(checkok.shape[0]):
	print(checkok[i][0])
'''
#print(checkok[0].shape)
#print(checkok[0])
#print(all_array)
