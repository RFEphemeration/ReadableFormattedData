import pprint
from RFDClasses import Contexts, Context
from RFDUtilityFunctions import LogError, LogVerbose, ParseValue
from RFDMacros import ExecuteMacro

def BeginMacro(context):
	context.PushContextType(Contexts.Macro)
	context.value_buffer = ''

def EndMacro(context):
	context.PopContextType(Contexts.Macro)
	command = context.value_buffer.split()
	arguments = []
	if (len(command) > 1):
		arguments = command[1:]
	command = command[0]
	valid_command = ExecuteMacro(context, command, arguments)
	if (not valid_command):
		# RMF TODO: @Incomplete this should probably be a parse value?
		# do we want to enable this relatively ambiguous syntax?
		pass

def StepMacro(context):
	context.value_buffer += context.next_char

def BeginValue(context):
	context.PrintFunctionEnter("BeginValue")
	if (context.context_stack[-1] == Contexts.Object):
		# do we need to append to the location stack for objects?
		# or should this be done in EndPropertyName
		pass
	elif (context.context_stack[-1] == Contexts.Array):
		current_array = context.GetChildAtLocation()
		new_location = len(current_array)
		context.location_stack.append(new_location)
		current_array.append(None)
	context.PushContextType(Contexts.Value)

def EndValue(context):
	context.PrintFunctionEnter("EndValue")
	# RMF TODO : check if we're in an array or object and pop location accordingly
	context.PopContextType(Contexts.Value)
	context.location_stack.pop()

def BeginObject(context):
	context.PrintFunctionEnter("BeginObject")
	new_object = {}
	context.SetChildAtLocation(new_object)
	context.PushContextType(Contexts.Object)

def DoNothing(context):
	pass

def EndObject(context):
	context.PrintFunctionEnter("EndObject")
	context.PopContextType(Contexts.Object)

def BeginBaseName(context):
	context.PrintFunctionEnter("BeginBaseName")
	context.PushContextType(Contexts.BaseName)
	context.value_buffer = ''

def StepBaseName(context):
	context.value_buffer += context.next_char

def EndBaseName(context):
	context.PrintFunctionEnter("EndBaseName")
	context.PopContextType(Contexts.BaseName)
	new_base_name = context.value_buffer.strip()
	context.value_buffer = ''
	context.location_stack.append(new_location)

def BeginPropertyName(context):
	context.PrintFunctionEnter("BeginPropertyName")
	context.PushContextType(Contexts.PropertyName)
	context.value_buffer = context.next_char

def StepPropertyName(context):
	context.value_buffer += context.next_char

def EndPropertyName(context):
	context.PrintFunctionEnter("EndPropertyName")
	context.PopContextType(Contexts.PropertyName)
	new_location = context.value_buffer.strip()
	context.value_buffer = ''
	# rmf todo: where to put this?
	context.location_stack.append(new_location)

def BeginPropertyStringName(context):
	context.PrintFunctionEnter("BeginPropertyStringName")
	context.PushContextType(Contexts.PropertyStringName)
	context.value_buffer = ''
	context.active_string_delimeter = context.next_char

def StepPropertyStringName(context):
	context.value_buffer += context.next_char

def EndPropertyStringName(context):
	context.PrintFunctionEnter("EndPropertyStringName")
	context.PopContextType(Contexts.PropertyStringName)

def BeginParseValue(context):
	context.PrintFunctionEnter("BeginParseValue")
	context.PushContextType(Contexts.ParseValue)
	context.value_buffer = context.next_char

def StepParseValue(context):
	context.value_buffer += context.next_char

def EndParseValue(context):
	context.PrintFunctionEnter("EndParseValue")
	context.PopContextType(Contexts.ParseValue)
	parsed_value = ParseValue(context.value_buffer)
	context.SetChildAtLocation(parsed_value)
	context.value_buffer = ''

def BeginString(context):
	context.PrintFunctionEnter("BeginString")
	context.PushContextType(Contexts.String)
	context.value_buffer = ''
	context.active_string_delimeter = context.next_char

def StepString(context):
	context.value_buffer += context.next_char
	# RMF TODO: @Decision, do we want to have escaped strings? I think they're stupid and I don't really ever need to use them
	if (context.next_char == '\\'):
		context.string_escaped = not context.string_escaped
	else:
		context.string_escaped = False

def EndString(context):
	context.PrintFunctionEnter("EndString")
	context.PopContextType(Contexts.String)
	context.SetChildAtLocation(context.value_buffer)

def BeginArray(context):
	context.PrintFunctionEnter("BeginArray")
	context.PushContextType(Contexts.Array)
	new_array = []
	context.SetChildAtLocation(new_array)
	context.value_buffer = ''

def EndArray(context):
	context.PrintFunctionEnter("EndArray")
	context.PopContextType(Contexts.Array)

StepDelta = {
	Contexts.All: {
		'\r': DoNothing
	},
	Contexts.Macro: {
		'\n': EndMacro,
		'eof': EndMacro,
		'default': StepMacro
	},
	Contexts.Object : {
		' ' : DoNothing,
		'\t': DoNothing,
		'\n': DoNothing,
		'}' : EndObject,
		'#' : BeginMacro,
		'potential_string_delimeter' : lambda context: (BeginPropertyName(context), BeginPropertyStringName(context)),
		'default' : BeginPropertyName
	},
	Contexts.Array : {
		' ' : DoNothing,
		'\t': DoNothing,
		'\n': DoNothing,
		']' : EndArray,
		'{' : lambda context: (BeginValue(context), BeginObject(context)),
		'[' : lambda context: (BeginValue(context), BeginArray(context)),
		'potential_string_delimeter' : lambda context: (BeginValue(context), BeginString(context)),
		'default' : lambda context: (BeginValue(context), BeginParseValue(context))
	},
	Contexts.PropertyName : {
		':' : lambda context: (EndPropertyName(context), BeginValue(context)),
		'default' : StepPropertyName
	},
	Contexts.PropertyStringName : {
		'active_string_delimeter': EndPropertyStringName,
		# RMF TODO: @Awkward you can end a string name and continue in parse mode before hitting ':'
		'default' : StepPropertyStringName
	},
	Contexts.String : {
		'active_string_delimeter': EndString,
		'default' : StepString
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
		'potential_string_delimeter': BeginString,
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
	next_char = context.ReadNextChar()
	context_type = context.context_stack[-1]
	
	if (context_type != context.last_context):
		#LogVerbose("Context: " + context_type)
		context.last_context = context_type
	#LogVerbose("Context: " + context_type + " Char : " + next_char + " Value Buffer: " + context.value_buffer)
	if (next_char in StepDelta[Contexts.All]):
		StepDelta[Contexts.All][next_char](context)
	elif (context_type in StepDelta):
		if (next_char in StepDelta[context_type]):
			StepDelta[context_type][next_char](context)
		elif ('active_string_delimeter' in StepDelta[context_type] and next_char == context.active_string_delimeter):
			StepDelta[context_type]['active_string_delimeter'](context)
		elif ('potential_string_delimeter' in StepDelta[context_type] and next_char in context.potential_string_delimeters):
			StepDelta[context_type]['potential_string_delimeter'](context)
		elif ('default' in StepDelta[context_type]):
			StepDelta[context_type]['default'](context)

def StepContextEOF(context):
	context_type = context.context_stack[-1]
	if (context_type != context.last_context):
		#LogVerbose("Context: " + context_type)
		context.last_context = context_type
	if (context_type in StepDelta):
		if ('eof' in StepDelta[context_type]):
			StepDelta[context_type]['eof'](context)

def ParseRFDString(path, contents):
	context = Context(path, contents)
	while (context.remainder):
		StepContext(context)
	StepContextEOF(context)
	if (len(context.location_stack) > 0):
		LogError("Location Stack isn't empty")
	if (len(context.context_stack) != 1):
		LogError("Context Stack hasn't returned to just object")
	return context.loaded_object

def ParseRFDFile(location):
	f = open (location, 'r')
	remainder = f.read()

	return ParseRFDString(location, remainder)