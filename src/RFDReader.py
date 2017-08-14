import pprint
import json

def ReadNextChar(context):
	if (not context.remainder):
		context.next_char = None
		return
	context.next_char = context.remainder[0]
	#RMF TODO: @Speed check
	# context.remainder = context.remainder.replace(context.remainder[:1], '', 1)
	try:
		context.remainder = context.remainder[1:]
	except:
		context.remainder = ''
	return context.next_char

def StripLeadingWhitespace(context):
	context.remainder = context.remainder.lstrip(' \t')
	if (context.remainder and context.remainder[0] == '\n'):
		context.line_number += 1
	context.remainder = context.remainder.lstrip()

def PopContextType(context, context_type):
	if (len(context.type_stack) == 0):
		LogError("Context Type Stack is empty when we were trying to pop " + context_type)
	elif (context.type_stack[-1] != context_type):
		LogError("Context Type Stack tried to pop type " + context_type + " but the most recent type is " + context.type_stack[-1])
	else:
		#LogVerbose("Pop Context: " + context_type + " Location: " + MakePath(context.location_stack))
		context.type_stack.pop()

def PushContextType(context, context_type):
	#LogVerbose("Push Context: " + context_type + " Location: " + MakePath(context.location_stack))
	context.type_stack.append(context_type)

class Contexts():
	Unkown = 'Unkown'
	Value = 'Value'
	Object = 'Object'
	Array = 'Array'
	ParseValue = 'ParseValue'
	PropertyName = 'PropertyName'
	Definition = 'Definition'
	Macro = 'Macro'
	String = 'String'
	MultilineString = 'MultilineString'
	ParserSkip = 'ParserSkip'

def GetChildAtLocation(root, location):
	#LogVerbose ("Getting child at location: " + MakePath(location))
	child = root
	for step in location:
		child = child[step]
	return child

def SetChildAtLocation(root, location, value):
	#LogVerbose ("Setting child at location: " + MakePath(location) + " to value: " + str(value))
	child = root

	for step in location[:-1]:
		''' RMF TODO: @Debug child should already be there
		if not step in child:
			child[step] = {}
		'''
		child = child[step]
	child[location[-1]] = value

def LogError(error):
	print(error)

def LogVerbose(output):
	pprint.pprint(output)
	pass

def MakePath(array):
	path = ""
	if (len(array) == 0):
		return path
	for item in array[:-1]:
		path = path + str(item) + "."
	path = path + str(array[-1])
	return path

def PrintFunctionEnter(function_name, context):
	#LogVerbose(function_name + " at " + context.next_char + " on line " + str(context.line_number))
	pass

def GetInteger(v):
	try:
		return int(v)
	except:
		return None

def GetBoolean(v):
	v = v.strip().lower()
	if (v == "true"):
		return True
	if (v == "false"):
		return False
	return None

def ParseValue(property_value):
	ret_value = None

	if (ret_value == None):
		ret_value = GetInteger(property_value)
	
	if (ret_value == None):
		ret_value = GetBoolean(property_value)

	if (ret_value == None):
		ret_value = property_value.strip()

	return ret_value

def BeginValue(context):
	PrintFunctionEnter("BeginValue", context)
	if (context.type_stack[-1] == Contexts.Object):
		# do we need to append to the location stack for objects?
		# or should this be done in EndPropertyName
		pass
	elif (context.type_stack[-1] == Contexts.Array):
		current_array = GetChildAtLocation(context.loaded_object, context.location_stack)
		new_location = len(current_array)
		context.location_stack.append(new_location)
		current_array.append(None)
	PushContextType(context, Contexts.Value)

def EndValue(context):
	PrintFunctionEnter("EndValue", context)
	# RMF TODO : check if we're in an array or object and pop location accordingly
	PopContextType(context, Contexts.Value)
	context.location_stack.pop()

def BeginObject(context):
	PrintFunctionEnter("BeginObject", context)
	new_object = {}
	SetChildAtLocation(context.loaded_object, context.location_stack, new_object)
	PushContextType(context, Contexts.Object)
	StripLeadingWhitespace(context)

def DoNothing(context):
	pass

def EndObject(context):
	PrintFunctionEnter("EndObject", context)
	PopContextType(context, Contexts.Object)

def BeginPropertyName(context):
	PrintFunctionEnter("BeginPropertyName", context)
	PushContextType(context, Contexts.PropertyName)
	context.value_buffer = context.next_char

def IncrementPropertyName(context):
	context.value_buffer += context.next_char

def EndPropertyName(context):
	PrintFunctionEnter("EndPropertyName", context)
	PopContextType(context, Contexts.PropertyName)
	new_location = context.value_buffer.strip()
	context.value_buffer = ''
	context.location_stack.append(new_location)

def BeginParseValue(context):
	PrintFunctionEnter("BeginParseValue", context)
	PushContextType(context, Contexts.ParseValue)
	context.value_buffer = context.next_char

def StepParseValue(context):
	context.value_buffer += context.next_char

def EndParseValue(context):
	PrintFunctionEnter("EndParseValue", context)
	PopContextType(context, Contexts.ParseValue)
	parsed_value = ParseValue(context.value_buffer)
	SetChildAtLocation(context.loaded_object, context.location_stack, parsed_value)
	context.value_buffer = ''

def BeginArray(context):
	PrintFunctionEnter("BeginArray", context)
	PushContextType(context, Contexts.Array)
	new_array = []
	SetChildAtLocation(context.loaded_object, context.location_stack, new_array)
	StripLeadingWhitespace(context)
	context.value_buffer = ''

def EndArray(context):
	PrintFunctionEnter("EndArray", context)
	PopContextType(context, Contexts.Array)

class Context():
	loaded_object = {}
	type_stack = [Contexts.Object]
	location_stack = []
	value_buffer = ''
	value_object = None
	remainder = ''
	next_char = ''
	line_number = 1
	last_context = Contexts.Unkown

StepDelta = {
	Contexts.Object : {
		' ' : DoNothing,
		'\t': DoNothing,
		'}' : EndObject,
		'default' : BeginPropertyName
	},
	Contexts.Array : {
		' ' : DoNothing,
		'\t': DoNothing,
		']' : EndArray,
		'{' : lambda context: (BeginValue(context), BeginObject(context)),
		'[' : lambda context: (BeginValue(context), BeginArray(context)),
		'default' : lambda context: (BeginValue(context), BeginParseValue(context))
	},
	Contexts.PropertyName : {
		':' : lambda context: (EndPropertyName(context), BeginValue(context)),
		'default' : IncrementPropertyName
	},
	Contexts.Value : {
		' ' : DoNothing,
		'\t': DoNothing,
		'{' : BeginObject,
		'[' : BeginArray,
		'\n' : EndValue,
		',' : EndValue,
		'eof': EndValue,
		'}' : lambda context: (EndValue(context), EndObject(context)),
		']' : lambda context: (EndValue(context), EndArray(context)),
		'default': BeginParseValue
	},
	Contexts.ParseValue : {
		'\n' : lambda context: (EndParseValue(context), EndValue(context)),
		',' : lambda context: (EndParseValue(context), EndValue(context)),
		'eof': lambda context: (EndParseValue(context), EndValue(context)),
		'}' : lambda context: (EndParseValue(context), EndValue(context), EndObject(context)),
		']' : lambda context: (EndParseValue(context), EndValue(context), EndArray(context)),
		'default': StepParseValue
	}
}

def StepContext(context):
	next_char = ReadNextChar(context)
	context_type = context.type_stack[-1]
	
	if (context_type != context.last_context):
		#LogVerbose("Context: " + context_type)
		context.last_context = context_type
	#LogVerbose("Context: " + context_type + " Char : " + next_char + " Value Buffer: " + context.value_buffer)
	if (context_type in StepDelta):
		if (next_char in StepDelta[context_type]):
			StepDelta[context_type][next_char](context)
		elif ('default' in StepDelta[context_type]):
			StepDelta[context_type]['default'](context)
	if (next_char == '\n'):
		context.line_number = context.line_number + 1

def StepContextEOF(context):
	context_type = context.type_stack[-1]
	if (context_type != context.last_context):
		#LogVerbose("Context: " + context_type)
		context.last_context = context_type
	if (context_type in StepDelta):
		if ('eof' in StepDelta[context_type]):
			StepDelta[context_type]['eof'](context)

def LoadRFDFile(location):
	f = open (location, 'r')
	remainder = f.read()

	context = Context()
	context.remainder = remainder

	while (context.remainder):
		StepContext(context)
	StepContextEOF(context)
	if (len(context.location_stack) > 0):
		LogError("Location Stack isn't empty")
	if (len(context.type_stack) > 1):
		LogError("Context Stack hasn't returned to just object")
	return context.loaded_object

def main():
	loaded_object = LoadRFDFile('test_data.rfd')
	#pprint.pprint(loaded_object)
	print json.dumps(loaded_object, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
	main()
