class ArgumentIncongruityWarning(Warning):
	"""
	Warning raised when number of type arguments do not match 
	the function's number of parameters. This could mean both 
	overconstraining and underconstraining the method's parameters.
	"""
	def __init__(self, funcname, typecount, argcount):
		if typecount > argcount:
			self.msg = (
			f"Enforcing {typecount} {'type' if typecount == 1 else 'types'} "
			f"while only {argcount} {'argument exists' if argcount == 1 else 'arguments exist'}. "
			)
		elif typecount < argcount:
			self.msg = (
			f"Enforcing only {typecount} {'type' if typecount == 1 else 'types'} "
			f"while {argcount} {'argument exists' if argcount == 1 else 'arguments exist'}. "
			f"Defined method, {funcname}(), may produce unexpected results."
			)

	def __str__(self):
		return self.msg

class InvalidArgumentError(TypeError):
	def __init__(self, parameter, enforcedarg, givenarg):
		self.error = (
			f"{givenarg} was enforced on parameter '{parameter}' but found {givenarg}"
		)

	def __str__(self):
		return self.error


"""
str was enforced on parameter 'b' but found str
"""