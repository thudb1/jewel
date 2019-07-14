import pickle,os
import MySQLdb

db = MySQLdb.connect("localhost", "lxx", "123456", "map_base")
cursor = db.cursor()

fo = open('wn2wikidata.txt', 'r')

fb2title = dict()
fb2wikidata = dict()

for lines in fo:
	sp = lines.split()
	cur_title = ' '.join(sp[2:]).lower()
	fb2title[sp[1][:-1]] = cur_title
	fb2wikidata[sp[1][:-1]] = sp[0]
	#print(sp[1], cur_title)
	
fo.close()

fo = open('title2id_new2.pickle', 'rb')
title2id = pickle.load(fo)
fo.close()

fo = open('id2id_new2.pickle', 'rb')
id2id = pickle.load(fo)
fo.close()

fo = open('entity2id_wn.txt', 'r')

outfile = open("wordnet_wiki.out", "w")
ff = open("fb_fuck_2", "w")
fg = open("fb_notitle_2", "w")

cnt = 0
count = 0

from_a, from_b = 0, 0
for line in fo:
	[a,b] = line.split()
	cnt += 1
	
	da, db = 0, 0

	if a in fb2title and fb2title[a] in title2id:
		#count += 1
		da = title2id[fb2title[a]]
		#print(a, title2id[fb2title[a]], file=outfile)
	if a in fb2wikidata:
		tmpline = 'select * from wbc_190101 where eu_aspect=\'T\' and eu_entity_id=\''+fb2wikidata[a].replace('\n','')+'\' order by eu_page_id asc'
		#print(tmpline)
		cursor.execute(tmpline)
		res = cursor.fetchone()
		if res != None and res[3] in id2id:
			#count += 1
			db = id2id[res[3]]
			#print(a, id2id[res[3]], file=outfile)
		else:
			tmpline = 'select * from wbc_190101 where eu_aspect=\'S\' and eu_entity_id=\''+fb2wikidata[a].replace('\n','')+'\' order by eu_page_id asc'
			#print(tmpline)
			cursor.execute(tmpline)
			res = cursor.fetchone()
			if res != None and res[3] in id2id:
				#count += 1
				db = id2id[res[3]]
		#print(a, file=outfile)
		#print(a, fb2title[a], fb2wikidata[a], file=fg)
	if da == 0 and db == 0:
		print(a, file=outfile)
	else:
		if da == 0 or not os.path.exists('./links2/'+str(da)):
			from_b += 1
			print(a, db, file=outfile)
		else:
			if db == 0 or not os.path.exists('./links2/'+str(db)):
				from_a += 1
				print(a, da, file=outfile)
			else:
				if da == db:
					print(a, da, file=outfile)
				else:
					fl = open('./links2/'+str(da), 'rb')
					lp = pickle.load(fl)
					fl.close()
				
					fr = open('./links2/'+str(db), 'rb')
					rp = pickle.load(fr)
					fr.close()
					
					if len(lp) > len(rp):
						from_a += 1
						print(a, da, file=outfile)
					else:
						from_b += 1
						print(a, db, file=outfile)
				
				

print('total count =', cnt, 'from_a =', from_a, 'from_b =', from_b)
