import numpy as np
import os, re
import pickle
#import gensim
import time
from wikipedia2vec import Wikipedia2Vec

fi = open('wn2wikidata3.txt', 'r')
counter = 0
counter_good = 0
counter_bad = 0
wiki2vec = Wikipedia2Vec.load('enwiki-20190420-50d.pkl')

for line in fi:
	ta = line.split()
	if ta[1].startswith('http://wordnet-rdf.princeton.edu/wn30'):
		pageid = ta[1][38:46]
		wikititle = ' '.join(ta[2:])
		counter += 1
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
					counter_good += 1
			else:
				counter_good += 1
		else:
			counter_good += 1
		
print(counter_good, counter_bad)
