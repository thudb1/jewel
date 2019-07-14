#coding:utf-8
import keras_config
import numpy as np
import tensorflow as tf
import os
import time
import datetime
import ctypes
import argparse

ll = ctypes.cdll.LoadLibrary   
lib = ll("./init.so")
test_lib = ll("./test.so")

#rate = 0.1 nbatches=100 traintimes=1000 margin=100

class Config(object):

	def __init__(self, flag, args):
		print("executed")
		lib.setInPath(args.path)
		test_lib.setInPath(args.path)
		lib.setBernFlag(0)
		self.learning_rate = float(args.alpha)
		self.testFlag = flag
		self.loadFromData = flag
		self.L1_flag = True
		self.hidden_size = int(args.dimension)
		self.nbatches = int(args.nbatches)
		self.entity = 0
		self.relation = 0
		self.trainTimes = int(args.times)
		self.margin = float(args.margin)
		self.init_str = args.method

class TransEModel(object):

	def __init__(self, config, init_str = None):

		entity_total = config.entity
		relation_total = config.relation
		batch_size = config.batch_size
		size = config.hidden_size
		margin = config.margin
		
		#self.ent_b4_embedding = np.load('w2v_allarray.npy')

		self.pos_h = tf.placeholder(tf.int32, [None])
		self.pos_t = tf.placeholder(tf.int32, [None])
		self.pos_r = tf.placeholder(tf.int32, [None])

		self.neg_h = tf.placeholder(tf.int32, [None])
		self.neg_t = tf.placeholder(tf.int32, [None])
		self.neg_r = tf.placeholder(tf.int32, [None])

		with tf.name_scope("embedding"):
		
			# select embeddings 
			
			if init_str == 'orig':
				self.ent_embeddings = tf.get_variable(name = "ent_embedding", shape = [entity_total, size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
			elif init_str != 'thres06':
				self.ent_embeddings = tf.get_variable(name = "ent_embedding", initializer = tf.constant(np.load('ent_50_v2_dic.npy')))
			else:
				self.ent_embeddings = tf.get_variable(name = "ent_embedding", initializer = tf.constant(np.load('ent_100_thres06.npy')))
			#self.ent_embeddings = tf.get_variable(name = "ent_embedding", shape = [entity_total, size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
			'''
			if config.testFlag:
				self.ent_embeddings = tf.get_variable(name = "ent_embedding", shape = [entity_total, size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
			else:
				self.ini = tf.constant(np.load('w2v_allarray.npy'), dtype=tf.dtypes.float32)
				self.ent_embeddings = tf.get_variable(name = "ent_embedding", initializer = self.ini)
			'''
			if init_str == 'entrel':
				self.rel_embeddings = tf.get_variable(name = "rel_embedding", initializer = tf.constant(np.load('./rel_upd_50.npy'), dtype=tf.float32))
			else:
				self.rel_embeddings = tf.get_variable(name = "rel_embedding", shape = [relation_total, size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
			pos_h_e = tf.nn.embedding_lookup(self.ent_embeddings, self.pos_h)
			pos_t_e = tf.nn.embedding_lookup(self.ent_embeddings, self.pos_t)
			pos_r_e = tf.nn.embedding_lookup(self.rel_embeddings, self.pos_r)
			neg_h_e = tf.nn.embedding_lookup(self.ent_embeddings, self.neg_h)
			neg_t_e = tf.nn.embedding_lookup(self.ent_embeddings, self.neg_t)
			neg_r_e = tf.nn.embedding_lookup(self.rel_embeddings, self.neg_r)

		if config.L1_flag:
			pos = tf.reduce_sum(abs(pos_h_e + pos_r_e - pos_t_e), 1, keep_dims = True)
			neg = tf.reduce_sum(abs(neg_h_e + neg_r_e - neg_t_e), 1, keep_dims = True)
			self.predict = pos
		else:
			pos = tf.reduce_sum((pos_h_e + pos_r_e - pos_t_e) ** 2, 1, keep_dims = True)
			neg = tf.reduce_sum((neg_h_e + neg_r_e - neg_t_e) ** 2, 1, keep_dims = True)
			self.predict = pos

		with tf.name_scope("output"):
			self.loss = tf.reduce_sum(tf.maximum(pos - neg + margin, 0))


def deal(flag, args):
	config = Config(flag, args)
	if (config.testFlag):
		test_lib.init()
		config.relation = test_lib.getRelationTotal()
		config.entity = test_lib.getEntityTotal()
		config.batch = test_lib.getEntityTotal()
		config.batch_size = config.batch
	else:
		lib.init()
		config.relation = lib.getRelationTotal()
		config.entity = lib.getEntityTotal()
		config.batch_size = lib.getTripleTotal() // config.nbatches
	
	with tf.Graph().as_default():
		sess = tf.Session()
		with sess.as_default():
			initializer = tf.contrib.layers.xavier_initializer(uniform = False)
			with tf.variable_scope("model", reuse=None, initializer = initializer):
				trainModel = TransEModel(config = config, init_str = args.method)

			global_step = tf.Variable(0, name="global_step", trainable=False)
			optimizer = tf.train.GradientDescentOptimizer(config.learning_rate)
			grads_and_vars = optimizer.compute_gradients(trainModel.loss)
			train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)
			saver = tf.train.Saver()
			sess.run(tf.initialize_all_variables())
			if (config.loadFromData):
				saver.restore(sess, './model'+args.method+'.vec')

			def train_step(pos_h_batch, pos_t_batch, pos_r_batch, neg_h_batch, neg_t_batch, neg_r_batch):
				feed_dict = {
					trainModel.pos_h: pos_h_batch,
					trainModel.pos_t: pos_t_batch,
					trainModel.pos_r: pos_r_batch,
					trainModel.neg_h: neg_h_batch,
					trainModel.neg_t: neg_t_batch,
					trainModel.neg_r: neg_r_batch
				}
				_, step, loss = sess.run(
					[train_op, global_step, trainModel.loss], feed_dict)
				return loss

			def test_step(pos_h_batch, pos_t_batch, pos_r_batch):
				feed_dict = {
					trainModel.pos_h: pos_h_batch,
					trainModel.pos_t: pos_t_batch,
					trainModel.pos_r: pos_r_batch,
				}
				step, predict = sess.run(
					[global_step, trainModel.predict], feed_dict)
				return predict

			ph = np.zeros(config.batch_size, dtype = np.int32)
			pt = np.zeros(config.batch_size, dtype = np.int32)
			pr = np.zeros(config.batch_size, dtype = np.int32)
			nh = np.zeros(config.batch_size, dtype = np.int32)
			nt = np.zeros(config.batch_size, dtype = np.int32)
			nr = np.zeros(config.batch_size, dtype = np.int32)

			ph_addr = ph.__array_interface__['data'][0]
			pt_addr = pt.__array_interface__['data'][0]
			pr_addr = pr.__array_interface__['data'][0]
			nh_addr = nh.__array_interface__['data'][0]
			nt_addr = nt.__array_interface__['data'][0]
			nr_addr = nr.__array_interface__['data'][0]

			lib.getBatch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
			test_lib.getHeadBatch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
			test_lib.getTailBatch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
			test_lib.testHead.argtypes = [ctypes.c_void_p]
			test_lib.testTail.argtypes = [ctypes.c_void_p]

			if not config.testFlag:
				for times in range(config.trainTimes):
					res = 0.0
					for batch in range(config.nbatches):
						lib.getBatch(ph_addr, pt_addr, pr_addr, nh_addr, nt_addr, nr_addr, config.batch_size)
						res += train_step(ph, pt, pr, nh, nt, nr)
						current_step = tf.train.global_step(sess, global_step)
					print(times)
					print(res)
				saver.save(sess, './model'+args.method+'.vec')
				np.save('transE_fb_50_'+args.method+'_ent', trainModel.ent_embeddings.eval())
				np.save('transE_fb_50_'+args.method+'_rel', trainModel.rel_embeddings.eval())
			else:
				total = test_lib.getTestTotal()
				for times in range(total):
					test_lib.getHeadBatch(ph_addr, pt_addr, pr_addr)
					res = test_step(ph, pt, pr)
					test_lib.testHead(res.__array_interface__['data'][0])

					test_lib.getTailBatch(ph_addr, pt_addr, pr_addr)
					res = test_step(ph, pt, pr)
					test_lib.testTail(res.__array_interface__['data'][0])
					'''
					print(times)
					if (times % 50 == 0):
						test_lib.test()
					'''
				test_lib.test()
				
def main(_):
	# possible arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--path', '-p', default='./data/FB15K/')
	parser.add_argument('--method', '-m', default='emb')
	parser.add_argument('--alpha', '-a', default='0.001')
	parser.add_argument('--times', '-t', default='1000')
	parser.add_argument('--dimension', '-d', default='50')
	parser.add_argument('--opt_method', '-o', default='SGD')
	parser.add_argument('--lmbda', '-l', default='0.0001')
	parser.add_argument('--margin', '-g', default='1.0')
	parser.add_argument('--nbatches', '-n', default='100')
	args = parser.parse_args()
	deal(False, args)
	deal(True, args)

if __name__ == "__main__":
	tf.app.run()
