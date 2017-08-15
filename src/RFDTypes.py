from RFDUtilityFunctions import LogError, LogVerbose, MakePath

class Contexts():
	Unkown = 'Unkown'
	Value = 'Value'
	Object = 'Object'
	Array = 'Array'
	String = 'String'
	ParseValue = 'ParseValue'
	PropertyName = 'PropertyName'
	Definition = 'Definition'
	Macro = 'Macro'
	MultilineString = 'MultilineString'
	ParserSkip = 'ParserSkip'
	All = 'All'

class Context():
	def __init__(self):
		self.loaded_object = {}
		self.type_stack = [Contexts.Object]
		self.location_stack = []
		self.value_buffer = ''
		self.value_object = None
		self.remainder = ''
		self.next_char = ''
		self.line_number = 1
		self.last_context = Contexts.Unkown
		self.active_string_delimeter = ''
		self.string_escaped = False
		self.potential_string_delimeters = ['"', '\'']

	def PopContextType(self, context_type):
		if (len(self.type_stack) == 0):
			LogError("Context Type Stack is empty when we were trying to pop " + context_type)
		elif (self.type_stack[-1] != context_type):
			LogError("Context Type Stack tried to pop type " + context_type + " but the most recent type is " + self.type_stack[-1])
		else:
			self.PrintFunctionEnter("Pop " + context_type)
			self.type_stack.pop()

	def PushContextType(self, context_type):
		self.PrintFunctionEnter("Push " + context_type)
		self.type_stack.append(context_type)

	def ReadNextChar(self):
		if (not self.remainder):
			self.next_char = None
			return
		self.prev_char = self.next_char
		self.next_char = self.remainder[0]
		try:
			self.remainder = self.remainder[1:]
		except:
			self.remainder = ''
		if (self.next_char == '\n'):
			self.line_number = self.line_number + 1
		return self.next_char

	def StripLeadingWhitespace(self):
		self.remainder = self.remainder.lstrip(' \t')
		if (self.remainder and self.remainder[0] == '\n'):
			self.line_number += 1
		self.remainder = self.remainder.lstrip()

	def PrintFunctionEnter(self, function_name):
		#LogVerbose(function_name + ": at " + self.next_char + " on line " + str(self.line_number))
		pass

	def GetChildAtLocation(self):
		#LogVerbose ("Getting child at location: " + MakePath(location))
		child = self.loaded_object
		for step in self.location_stack:
			child = child[step]
		return child

	def SetChildAtLocation(self, value):
		#LogVerbose ("Setting child at location: " + MakePath(location) + " to value: " + str(value))
		child = self.loaded_object
		if (len(self.location_stack) == 0):
			child = value
			return

		for step in self.location_stack[:-1]:
			child = child[step]
		child[self.location_stack[-1]] = value