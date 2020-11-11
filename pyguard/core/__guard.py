import warnings
from inspect import getfullargspec
from functools import wraps
from pyguard.errors import ArgumentIncongruityWarning, InvalidArgumentError
from pyguard.core.allinstance import allinstance

class Guard:
	def __init__(self, *types, **kwtypes):
		"""
		See '__validate_constructor' for examples of valid and invalid inputs. 
		"""
		self._types = types
		self._kwtypes = kwtypes
		self.__validate_constructor()

	def __call__(self, func):
		"""
		'__call__' is implemented to allow the Guard decoration of methods and 
		is therefore called when the decorated method is called.
		"""
		self.func = func
		@wraps(func)
		def decor(*args, **kwargs):
			func_params = getfullargspec(func).args
			passed_args = {k:v for k,v in zip(func_params, args)}
			scanned_args = self.__scanargs(passed_args)
			self.__validate(scanned_args, passed_args)
			type_count = len(self._types) + len(self._kwtypes)
			if type_count != len(func_params):
				warnings.warn(ArgumentIncongruityWarning(func, type_count, len(func_params)), stacklevel=2)

			return func(*args, **kwargs)
		return decor

	def __validate_constructor(self):
		"""
		'__validate_constructor' is implemented to validate the passed *types 
		and **kwtypes of the Guard class.

		Parameters
		----------
		*types   : type, (type,)
		**kwtypes: type, (type,)


		Examples
		--------
		
		Parameters 'a', 'b', and 'c' must be of type 'int', 'int', and 'int', 
		respectively.

		>>> @guard(int, int, int)
		>>> def foo(a, b, c):

		>>> foo(1, 2, 3)



		A tuple filled with elements of type 'type' passed signifies multiple 
		valid types for one parameter. In this case, parameter 'c' can either 
		be of type 'int' or 'float.'

		>>> @guard(int, int, (int, float))
		>>> def foo(a, b, c):

		>>> foo(1, 2, 3)
		>>> foo(1, 2, 3.14159)
	
	

		Types passed via keyword is also accepted, given that the keyword 
		matches the name of a parameter that exists in the method's signature.

		>>> @guard(a=int, b=int, c=int)
		>>> def foo(a, b, c):

		>>> foo(1, 2, 3)
		


		Similarly to the last example, a combination of both positional and 
		keyworded arguments are able to be passed into the Guard constructor 
		and will also support out-of-order type-enforcement. In this example, 
		'a=str' enforces that the method's parameter 'a' must be of type 'str', 
		even though it was specified as a keyword argument that follows 
		multiple positional arguments. Both 'b' and 'c' will then be enforced 
		to be of type 'int.'

		>>> @guard(int, int, a=str):
		>>> def foo(a, b, c):

		>>> foo('Hello World!', 1, 2)



		Only types and tuples of types may be passed to the constructor.	
		When called, this method will raise an exception: "ValueError: guard 
		constructor not properly called!"

		>>> @guard(int, int, 'foo')
		>>> def foo(a, b, c):

		>>> foo(1, 2, 3)



		A warning will be raised when the number of types passed to the Guard 
		constructor is larger than the number of parameters in the method's 
		signature. When the method is called, this warning is raised: 
		"ArgumentIncongruityWarning: Enforcing 4 types while only 3 arguments 
		exist."

		>>> guard(int, int, int, str)
		>>> def foo(a, b, c):

		>>> foo(1, 2, 3)



		Similarly to the last example, a warning will be raised when the number 
		of parameters in the method's signature is larger than the number of 
		types passed to the Guard constructor. When the method is called, this 
		warning is raised: "ArgumentIncongruityWarning: Enforcing only 3 types 
		while 4 arguments exist. Defined method, 'foo,' may produce unexpected 
		results."

		>>> guard(int, int, int)
		>>> def foo(a, b, c, d):

		>>> foo(1, 2, 3, 4)
		"""
		all_types = list(self._types) + list(self._kwtypes.values())
		
		for enforced_type in all_types:
			if not isinstance(enforced_type, (type, tuple)):
				raise(ValueError(f"guard constructor not properly called!"))
			elif isinstance(enforced_type, tuple):
				if not allinstance(enforced_type, type) or len(enforced_type) == 0:
					raise(ValueError(f"guard constructor not properly called!"))

	def __validate(self, scanned_args, passed_args):
		"""
		'__validate' is implemented to validate the types of the parameters 
		passed to the method against the enforced types passed to the Guard 
		constructor. 
		
		Examples
		--------

		If the types of the parameters passed to the method do not match their 
		enforced type, an exception is raised: "InvalidArgumentError: 'foo' 
		expects parameter "c" to be of type "int" but found "str""

		>>> @guard(int, int, int)
		>>> def foo(a, b, c):

		>>> foo(1, 2, 'Hello World!')
		"""
		for param, enforced_type in scanned_args.items():
			if enforced_type is not None:
				# because 'bool' is a subclass of 'int,' it won't fail if 'True' or 'False' is passed while 'int' is enforced
				if isinstance(passed_args[param], bool):
					if isinstance(enforced_type, tuple):
						if bool not in enforced_type:
							raise(InvalidArgumentError(self.func, param, enforced_type, type(passed_args[param]).__name__))
					elif enforced_type != bool:
							raise(InvalidArgumentError(self.func, param, enforced_type, type(passed_args[param]).__name__))

				if not isinstance(passed_args[param], enforced_type):
					raise(InvalidArgumentError(self.func, param, enforced_type, type(passed_args[param]).__name__))


	def __scanargs(self, passed_args):
		"""
		'__scanargs' is implemented for format the arguments and parameters in 
		a way that allows other methods to use the data easily and efficiently. 
		A dictionary will is returned with the method's parameters as the keys 
		and the enforced type on each of those parameters as the value.
		"""
		specified_kw = passed_args.keys() & self._kwtypes.keys()
		scanned_args = {k:None for k in passed_args}
		for k in specified_kw:
			if k in passed_args:
				scanned_args[k] = self._kwtypes[k]
		idx = 0
		for k in scanned_args.keys():
			if idx > len(self._types)-1:
				break
			if scanned_args[k] is None:
				scanned_args[k] = self._types[idx]
				idx += 1

		return scanned_args