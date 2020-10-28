import pickle
import hashlib
import os
import time

def UniqIdentifer(buflen=20):
	return hashlib.sha512(bytes(str(time.time()), 'UTF-8') + os.urandom(buflen)).hexdigest()

class Value():
	def __init__(self, *args, **kwargs):
		self._pointer = None

	@property
	def pointer(self):
		return self._pointer
	
	@pointer.setter
	def pointer(self, value):
		self._pointer = value

class Str(str, Value):
	def __init__(self, *args, **kwargs):
		str.__init__(*args, **kwargs)
		Value.__init__(self, *args, **kwargs)

class Int(int, Value):
	def __init__(self, *args, **kwargs):
		str.__init__(*args, **kwargs)
		Value.__init__(self, *args, **kwargs)

class Dictabase(dict):
	def __init__(self, *args, **kwargs):
		struct = None
		if len(args) and type(args[0]) in (dict, Dictabase):
			struct, *args = args

		super(Dictabase, self).__init__(*args, **kwargs)
		self._identifiers = {}
		self._pointer = None
		self._position = 0

		if struct:
			self.__init__build(struct)

	def __enter__(self, save_buf_pos=False):
		return self

	def __exit__(self, *args, **kwargs):
		return True

	def __getitem__(self, key):
		if not (value := dict.get(self, key, None)):
			value = Dictabase()
			value._identifiers = self._identifiers

		return value

	def __setitem__(self, key, val):
		print(f'Setting "{key}": ({type(val)}) {val}')
		_id_ = UniqIdentifer()

		if type(val) != Dictabase:
			value_map = {
				str : Str,
				int : Int,
				dict : Dictabase
			}

			val = value_map[type(val)](val)
			if type(val) is Dictabase:
				val._identifiers = self._identifiers
		else:
			print(f'Modding {val} identifiers to {self}')
			val._identifiers = self._identifiers

		val.pointer = _id_
		self._identifiers[_id_] = val
		dict.__setitem__(self, key, val)

	def __contains__(self, key):
		if key in self:
			return True

	@property
	def pointer(self):
		return self._pointer
	
	@pointer.setter
	def pointer(self, value):
		self._pointer = value
		return True

	def id(self, _id_):
		print(self._identifiers)
		if _id_ in self._identifiers:
			return self._identifiers[_id_]

	def __init__build(self, d):
		for key, val in d.items():
			if type(val) is dict:
				val = Dictabase(val)
				val._identifiers = self._identifiers

			self[key] = val

if __name__ == '__main__':
	x = Dictabase({
		'First level' : {
			'Second level' : {
				'Third value #1' : 1,
				'Third value #2' : 2
			}
		}
	})

	import json
	print(json.dumps(x, indent=4))

	first_level_pointer = x['First level']['Second level'].pointer
	print(first_level_pointer)
	print(x.id(first_level_pointer))