import ast, json, pickle, time
from socket import *
from select import epoll, EPOLLIN, EPOLLHUP
from threading import Thread, enumerate as tnumerate
from os import getcwd
from os.path import abspath, isfile
from shutil import copy2

socks = {}
datas = {}
requests = {}
dictbase = {}
flags = {'request_id' : 0}
stash = {}

class autodict(dict):
	def __init__(self, *args, **kwargs):
		super(autodict, self).__init__(*args, **kwargs)

	def __getitem__(self, key):
		if not key in self:
			self[key] = autodict()

		val = dict.__getitem__(self, key)
		return val

	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)

	def __getstate__(self):
		# For pickle.dump
		state = dict.copy(self)
		return state

	def __setstate__(self, state):
		# For pickle.load
		dict.update(self, state)

	def dump(self, *args, **kwargs):
		copy = {}
		for key, val in self.items():
			if type(key) == bytes and b'*' in key: continue
			elif type(key) == str and '*' in key: continue
			elif type(val) == dict or type(val) == autodict:
				val = val.dump()
				copy[key] = val
			else:
				copy[key] = val
		return copy

class dictabase(dict, Thread):
	def __init__(self, dict_name=None, master=True, log=False, *args, **kwargs):
		self.dict_name = dict_name
		self.master = master
		self.lock = False
		self.log = log
		#self.last_trace = []
		if dict_name and master:
			Thread.__init__(self)
			self.sock = socket()
			self.mainFid = self.sock.fileno()
			dictbase[dict_name] = self
			self.polly = epoll()
			self.polly.register(self.mainFid, EPOLLIN)
			self.sock.connect(('127.0.0.1', 1337))
			self.sock.send(bytes(f'{flags["request_id"]}:1:{dict_name}', 'UTF-8')+b'\x00')
			flags["request_id"] += 1

		super(dictabase, self).__init__(*args, **kwargs)

		if dict_name and master:
			self.start()

	def __getitem__(self, key):
		#dictbase[self.dict_name].last_trace.append(key)
		if not key in self:
			if self.master:
				self.sock.send(bytes(f'{flags["request_id"]}:0:{key}', 'UTF-8')+b'\x00')
			else:
				dictbase[self.dict_name].sock.send(bytes(f'{flags["request_id"]}:0:{key}', 'UTF-8')+b'\x00')

			print(flags["request_id"])
			time.sleep(1)
			print(requests)
			while flags["request_id"] not in requests:
				pass

			while len(requests[flags["request_id"]]['data']) < requests[flags["request_id"]]['length']:
				print('Waiting for data')
				#print('Waiting for data on request: {}'.format(flags["request_id"]))
				#print(flags["request_id"] not in requests)
				#print(flags)
				#if flags["request_id"] in requests:
				#	print(len(requests[flags["request_id"]]['data']) < requests[flags["request_id"]]['length'])
				#	print(len(requests[flags["request_id"]]['data']), requests[flags["request_id"]]['length'])

			if dictbase[self.dict_name].log:
				print(f'Creating key: {key}')
			dictbase[self.dict_name].lock = True
			print(pickle.loads(requests[flags["request_id"]]['data']))
			self[key] = dictabase(dict_name=self.dict_name, master=False, **pickle.loads(requests[flags["request_id"]]['data']))
			dictbase[self.dict_name].lock = False

			flags["request_id"] += 1 

		val = dict.__getitem__(self, key)
		return val

	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)
		if not dictbase[self.dict_name].lock:
			if dictbase[self.dict_name].log:
				print('Set {}:'.format(key), dictbase[self.dict_name])
			dictbase[self.dict_name].sock.send(bytes(f'{flags["request_id"]}:1:{dictbase[self.dict_name]}', 'UTF-8')+b'\x00')
			flags["request_id"] += 1

	def __eq__(self, other):
		return self is other
	def __hash__(self):
		return hash(id(self))

	def dump(self, *args, **kwargs):
		copy = {}
		for key, val in self.items():
			if type(key) == bytes and b'*' in key: continue
			elif type(key) == str and '*' in key: continue
			elif type(val) == dict or type(val) == dictabase:
				val = val.dump()
				copy[key] = val
			else:
				copy[key] = val
		return copy

	def run(self):
		mt = None
		for t in tnumerate():
			if t.name == 'MainThread':
				mt = t
				break

		while mt and mt.isAlive():
			for fid, eid in self.polly.poll(0.025):
				if fid == self.mainFid and eid == EPOLLIN:
					data = self.sock.recv(8192)

					if data == b'' or b':' not in data:
						self.sock.shutdown(SHUT_RDWR)
					else:
						#data = data.decode('UTF-8')
						request_id, length, data = data.split(b':', 2)
						#request_id, data = data.split(':', 1)
						length = int(length)
						request_id = int(request_id)
						#data = pickle.loads(data)
						if not request_id in requests: requests[request_id] = {'length' : length, 'data' : b''}
						requests[request_id]['data'] += data
						if len(requests[request_id]['data']) >= requests[request_id]['length']:
							#if dictbase[self.dict_name].log:
							print('Server sent data: {} [{}]'.format(data, request_id))

				elif eid == 17:
					if dictbase[self.dict_name].log:
						print('{} has disconnected'.format('Server'))
					self.polly.unregister(fid)
					self.sock.close()

def server():
	## TODO: Testdata below!
	stash = autodict()
	stash['players']['Torxed']['url'] = 'https://github.com/Torxed/dictabase'

	## ----

	#state = abspath(f'{getcwd()}/state_dictabase.pickle')
	#try:
	#	if isfile(state):
	#		with open(state, 'rb') as fh:
	#			stash = pickle.load(fh)
	#except:
	#	print('Failed to load stash, starting from fresh setup.')

	sock = socket()
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.bind(('', 1337))
	sock.listen(4)
	mainFid = sock.fileno()
	polly = epoll()
	polly.register(mainFid, EPOLLIN)

	while 1:
		run = {}
		for fid, eid in polly.poll(0.025):
			run[fid] = True
			if fid == mainFid:
				ns, na = sock.accept()
				polly.register(ns.fileno(), EPOLLIN|EPOLLHUP)
				print('{} has connected'.format(na))
				socks[ns.fileno()] = {'sock' : ns, 'addr' : na}
			elif fid in socks and eid == EPOLLIN:
				if not fid in datas: datas[fid] = {'last' : 0, 'data' : b'', 'instanced' : None, 'pos' : None}
				
				data = socks[fid]['sock'].recv(8192)
				datas[fid]['data'] += data

				if data == b'':
					socks[fid]['sock'].shutdown(SHUT_RDWR)
				else:
					print('{} sent data: {}'.format(socks[fid]['addr'], data))

			elif fid in socks and eid == 17:
				print('{} has disconnected'.format(socks[fid]['addr']))
				polly.unregister(fid)
				socks[fid]['sock'].close()
				del(socks[fid])
				del(datas[fid])

		for fid in datas:
			if fid in run: continue

			if len(datas[fid]['data']):
				print('Parsing data: {}'.format(datas[fid]['data']))
				for block in datas[fid]['data'].split(b'\x00'):
					if len(block) <= 0: continue

					block = block.decode('UTF-8')
					request_id, mode, block = block.split(':', 2)
					mode = int(mode)

					if not datas[fid]['instanced']:
						datas[fid]['instanced'] = block
						datas[fid]['pos'] = stash[datas[fid]['instanced']]
						one_level = autodict()
						for key in datas[fid]['pos'].keys():
							one_level[key] = autodict()

						payload = pickle.dumps(one_level)
						length = len(payload)
						response = f'{request_id}:{length}'
						print('Sending: {}:<pickle data>'.format(response))
						print(json.dumps(one_level, indent=4, sort_keys=True))
						socks[fid]['sock'].send(bytes(response+':', 'UTF-8')+payload)

					elif mode == 0:
						print('Mode 0', block)
						if not block in datas[fid]['pos']: datas[fid]['pos'][block] = autodict()

						datas[fid]['pos'] = datas[fid]['pos'][block]
						payload = pickle.dumps(datas[fid]['pos'])
						length = len(payload)
						response = f'{request_id}:{length}'
						print('Sending: {}:<pickle data>'.format(response))
						socks[fid]['sock'].send(bytes(response+':', 'UTF-8')+payload)

					elif mode == 1:
						print('Updating stash[{}]: {}'.format(datas[fid]['instanced'], stash[datas[fid]['instanced']]))
						d = ast.literal_eval(block)
						stash[datas[fid]['instanced']] = d

						#if isfile(state):
						#	copy2(state, f'{state}.bkp')
						#
						#with open(state, 'wb') as fh:
						#	pickle.dump(stash, fh)

						print(stash)

				datas[fid]['data'] = b''

if __name__ == '__main__':
	server()