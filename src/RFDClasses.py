from RFDUtilityFunctions import LogError, LogVerbose, MakeObjectPath, SplitFilePath

class Contexts():
	Unkown = 'Unkown'
	Value = 'Value'
	Object = 'Object'
	Array = 'Array'
	String = 'String'
	ParseValue = 'ParseValue'
	PropertyName = 'PropertyName'
	NewDefinitionName = 'NewDefinitionName'
	ValueType = 'ValueType'

	StringName = 'StringName' # for properties, definitions, and base values

	Macro = 'Macro'

	All = 'All'

	BaseName = 'BaseName'
	BaseValue = 'BaseValue'
	

	MultilineString = 'MultilineString'
	ParserSkip = 'ParserSkip'

class FileStackLocation():
	def __init__(self, file_location, file_name, file_contents):
		self.file_location = file_location
		self.file_name = file_name
		self.remaining_text = file_contents
		self.line_number

	def ReadNextChar(self):
		if (not self.remaining_text):
			return None
		next_char = self.remaining_text[0]
		try:
			self.remaining_text = self.remaining_text[1:]
		except:
			self.remaining_text = ''
		return next_char

class ObjectStackLocation():
	def __init__(self, context_type, object_location, file_location):
		self.context_type = context_type
		self.object_location = object_location
		self.children = {}

class Context():
	def __init__(self, path, contents):
		self.loaded_object = {}
		self.loaded_definitions = {}
		self.context_stack = [Contexts.Object]
		self.shelved_location_stack = []
		self.location_stack = []
		self.type_stack = []
		self.file_stack = []
		self.file_stack_pop_char_number = []
		self.value_buffer = ''
		self.value_object = None
		self.remainder = contents
		self.next_char = ''
		self.line_number = 1
		self.char_number = 0
		self.last_context = Contexts.Unkown
		self.active_string_delimeter = ''
		self.string_escaped = False
		self.potential_string_delimeters = ['"', "'"]
		file_path, file_name = SplitFilePath(path)
		self.PushFilePath(file_path, len(contents))
		self.in_definition = False

	def PopContextType(self, context_type):
		if (len(self.context_stack) == 0):
			LogError("Context Type Stack is empty when we were trying to pop " + context_type)
		elif (self.context_stack[-1] != context_type):
			LogError("Context Type Stack tried to pop type " + context_type + " but the most recent type is " + self.context_stack[-1])
		else:
			self.PrintFunctionEnter("Pop " + context_type)
			self.context_stack.pop()

	def PushContextType(self, context_type):
		self.PrintFunctionEnter("Push " + context_type)
		self.context_stack.append(context_type)

	def PopFilePath(self):
		self.file_stack.pop()
		self.file_stack_pop_char_number.pop()

	def PushFilePath(self, location, length):
		self.file_stack.append(location)
		self.file_stack_pop_char_number[:] = (n + length for n in self.file_stack_pop_char_number)
		self.file_stack_pop_char_number.append(self.char_number + length)

	def ReadNextChar(self):
		self.prev_char = self.next_char
		if (not self.file_stack):
			self.next_char = None
			return
		#self.next_char = self.file_stack[-1].ReadNextChar()
		self.next_char = self.remainder[0]
		if (self.next_char == None):
			self.next_char = '\n'

		self.char_number += 1
		if (len(self.file_stack_pop_char_number) > 0
			and self.char_number >= self.file_stack_pop_char_number[-1]):
			self.PopFilePath()
		try:
			self.remainder = self.remainder[1:]
		except:
			self.remainder = ''
		if (self.next_char == '\n'):
			self.line_number += 1

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
		LogVerbose ("Getting child at location: " + MakeObjectPath(self.location_stack))
		child = self.loaded_object
		if (self.in_definition):
			child = self.loaded_definitions

		for step in self.location_stack:
			child = child[step]
		return child

	def SetChildAtLocation(self, value):
		LogVerbose ("Setting child at location: " + MakeObjectPath(self.location_stack) + " to value: " + str(value))

		child = self.loaded_object
		if (self.in_definition):
			child = self.loaded_definitions

		if (len(self.location_stack) == 0):
			child = value
			return

		for step in self.location_stack[:-1]:
			child = child[step]
		child[self.location_stack[-1]] = value