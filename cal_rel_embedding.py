import numpy as np
import os,re
import pickle
import time
from wikipedia2vec import Wikipedia2Vec

ent_embedding = np.load('w2v_50.npy')

fb = open('train2id.txt', 'r')

#print(ent_embedding.shape)
#print(ent_embedding.shape[0])

rel_count = 1345
dim = 50

head_map, tail_map, intersect_map = {}, {}, {}
for i in range(rel_count):
	head_map[i] = set()
	tail_map[i] = set()
	intersect_map[i] = {}
	
counter = 0

map_pageid = np.zeros(ent_embedding.shape[0], dtype=np.int)
fc = open('wiki_entity_aftermod.out', 'r')

for line in fc:
	ta = line.split()
	if len(ta) == 2:
		map_pageid[counter] = int(ta[1])
	counter += 1	

#print(map_pageid.shape, map_pageid[0])
#print(map_pageid)

counter = 0
window = 50

start = time.time()
for line in fb:
	ta = line.split()
	#head_map[int(ta[2])].add(int(ta[0]))
	#tail_map[int(ta[2])].add(int(ta[1]))
	counter += 1
	
	if counter % 1000 == 0:
		print('counter =', counter, 'time elapsed =', time.time() - start)
		
	#print(ta[0], map_pageid[int(ta[0])], ta[1], map_pageid[int(ta[1])])
	if map_pageid[int(ta[0])] == 0 or map_pageid[int(ta[1])] == 0:
		continue
		
	fl = open('./links2/'+str(map_pageid[int(ta[0])]), 'rb')
	h_wc = pickle.load(fl)
	fl.close()
	
	fl = open('./links2/'+str(map_pageid[int(ta[1])]), 'rb')
	t_wc = pickle.load(fl)
	fl.close()
	
	#print(map_pageid[int(ta[0])], '=', len(h_wc), map_pageid[int(ta[1])], '=', len(t_wc))
	#print(len(h_wc), h_wc)
	#print(len(t_wc), t_wc)
	
	#hs, ts = set(), set()
	combine_set = set()
	
	hs = sorted(h_wc.items(), key = lambda item:item[1], reverse=True)
	#ts = sorted(t_wc.items(), key = lambda item:item[1], reverse=True)
	
	for i in range(min(len(hs), window)):
		if hs[i][0] in t_wc:
			if hs[i][0] in intersect_map[int(ta[2])]:
				intersect_map[int(ta[2])][hs[i][0]] += hs[i][1] * t_wc[hs[i][0]]
			else:
				intersect_map[int(ta[2])][hs[i][0]] = hs[i][1] * t_wc[hs[i][0]]
		
	'''	
	for i in range(min(len(ts), window)):
		if (ts[i][0] in h_wc) and (ts[i][0] not in interse):
			insersect_map[int(ta[2])].add(ts[i][0])
	'''
	
fg = open('rel_intersect', 'w')		
for i in range(rel_count):
	print(len(intersect_map[i]), file=fg)
fg.close()

#r_emb = np.zeros((rel_count, dim))
r_emb = np.load('rel_embeddings_50.npy')
wiki2vec = Wikipedia2Vec.load('enwiki-20190420-50d-disambi.pkl')

fg = open('id2title.pickle', 'rb')
i2t = pickle.load(fg)

for i in range(rel_count):
	cur_cnt = 0
	cur_vec = np.zeros(dim)
	for word, value in intersect_map[i].items():
		try:
			tmp = wiki2vec.get_entity_vector(i2t[str(word)])
		except KeyError:
			continue
		else:
			cur_cnt += value
			cur_vec += tmp * value
	if cur_cnt > 1e-8:
		r_emb[i] = cur_vec / cur_cnt
		
np.save('rel_upd_50_dict', r_emb)
checkok = np.load('rel_upd_50_dict.npy')
print(checkok.shape)
