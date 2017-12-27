import pprint
from RFDClasses import Contexts, Context
from RFDUtilityFunctions import LogError, LogVerbose, ParseValue
from RFDMacros import ExecuteMacro
from RFDTypeDefinition import Validate, BuiltinValueTypes

def AddCharToBuffer(context):
	context.value_buffer += context.next_char

def DoNothing(context):
	pass

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
		if (not context.in_definition):
			context.type_stack.append(BuiltinValueTypes.Any)
		#rmf todo: @incomplete allowing types inside of array
	context.PushContextType(Contexts.Value)

def EndValue(context):
	context.PrintFunctionEnter("EndValue")
	context.PopContextType(Contexts.Value)
	if (not context.in_definition
		and context.type_stack[-1] != BuiltinValueTypes.Any
		and len(context.type_stack) > 0):
		Validate(context, context.GetChildAtLocation(), context.type_stack[-1])

	context.location_stack.pop()
	if (len(context.location_stack) == 0 and context.in_definition):
		context.location_stack = context.shelved_location_stack[:]
		context.shelved_location_stack = []
		context.in_definition = False

def BeginValueType(context):
	context.PrintFunctionEnter("BeginValueType")
	context.PushContextType(Contexts.ValueType)
	context.value_buffer = ''

def EndValueType(context):
	context.PrintFunctionEnter("EndValueType")
	context.PopContextType(Contexts.ValueType)
	new_type = context.value_buffer.strip()
	#rmf todo: @incorrect, if a string name is used, it will still strip it
	# post string name seems to be a useful state
	context.value_buffer = ''
	context.type_stack[-1] = new_type

def BeginObject(context):
	context.PrintFunctionEnter("BeginObject")
	new_object = {}
	context.SetChildAtLocation(new_object)
	context.PushContextType(Contexts.Object)

def EndObject(context):
	context.PrintFunctionEnter("EndObject")
	context.PopContextType(Contexts.Object)

def BeginBaseName(context):
	context.PrintFunctionEnter("BeginBaseName")
	context.PushContextType(Contexts.BaseName)
	context.value_buffer = ''

def EndBaseName(context):
	context.PrintFunctionEnter("EndBaseName")
	context.PopContextType(Contexts.BaseName)
	new_base_name = context.value_buffer.strip()
	context.value_buffer = ''
	context.location_stack.append(new_location)

def BeginNewDefinitionName(context):
	context.PrintFunctionEnter("BeginNewDefinitionName")
	context.PushContextType(Contexts.NewDefinitionName)
	context.value_buffer = ''
	context.in_definition = True

def StepNewDefinitionName(context):
	context.value_buffer += context.next_char

def EndNewDefinitionName(context):
	context.PrintFunctionEnter("EndNewDefinitionName")
	context.PopContextType(Contexts.NewDefinitionName)
	new_definition_name = context.value_buffer.strip()
	context.value_buffer = ''
	context.loaded_definitions[new_definition_name] = None
	context.shelved_location_stack = context.location_stack[:]
	context.location_stack = [new_definition_name]
	context.in_definition = True

def BeginPropertyName(context):
	context.PrintFunctionEnter("BeginPropertyName")
	context.PushContextType(Contexts.PropertyName)
	context.value_buffer = context.next_char

def EndPropertyName(context):
	context.PrintFunctionEnter("EndPropertyName")
	context.PopContextType(Contexts.PropertyName)
	new_location = context.value_buffer.strip()
	context.value_buffer = ''
	# rmf todo: where to put this?
	context.location_stack.append(new_location)
	if (not context.in_definition):
		context.type_stack.append(BuiltinValueTypes.Any)

def BeginStringName(context):
	context.PrintFunctionEnter("BeginStringName")
	context.PushContextType(Contexts.StringName)
	context.value_buffer = ''
	context.active_string_delimeter = context.next_char

def PotentialBeginStringName(fallback):
	def InnerPotentialBeginStringName(context):
		if (context.value_buffer == ''):
			return BeginStringName(context)
		else:
			return fallback(context)
	return InnerPotentialBeginStringName

def EndStringName(context):
	context.PrintFunctionEnter("EndStringName")
	context.PopContextType(Contexts.StringName)

def BeginParseValue(context):
	context.PrintFunctionEnter("BeginParseValue")
	context.PushContextType(Contexts.ParseValue)
	context.value_buffer = context.next_char

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
		'default': AddCharToBuffer
	},
	Contexts.Object : {
		' ' : DoNothing,
		'\t': DoNothing,
		'\n': DoNothing,
		'}' : EndObject,
		'#' : BeginMacro,
		'@' : BeginNewDefinitionName,
		'potential_string_delimeter' : [BeginPropertyName, BeginStringName],
		'default' : BeginPropertyName
	},
	Contexts.Array : {
		' ' : DoNothing,
		'\t': DoNothing,
		'\n': DoNothing,
		']' : EndArray,
		'{' : [BeginValue, BeginObject],
		'[' : [BeginValue, BeginArray],
		'potential_string_delimeter' : [BeginValue, BeginString],
		'default' : [BeginValue, BeginParseValue]
	},
	Contexts.NewDefinitionName : {
		':' : [EndNewDefinitionName, BeginValue],
		'potential_string_delimeter' : PotentialBeginStringName(AddCharToBuffer),
		'default': AddCharToBuffer
	},
	Contexts.PropertyName : {
		':' : [EndPropertyName, BeginValue],
		'potential_string_delimeter' : PotentialBeginStringName(AddCharToBuffer),
		'default' : AddCharToBuffer
	},
	Contexts.StringName : {
		'active_string_delimeter': EndStringName,
		# RMF TODO: @Awkward you can end a string name and continue in parse mode before hitting ':'
		'default' : AddCharToBuffer
	},
	Contexts.String : {
		'active_string_delimeter': EndString,
		'default' : StepString
	},
	Contexts.Value : {
		' ' : DoNothing,
		'\t': DoNothing,
		'@' : BeginValueType,
		'{' : BeginObject,
		'[' : BeginArray,
		'\n' : EndValue,
		',' : EndValue,
		'eof': EndValue,
		'}' : [EndValue, EndObject],
		']' : [EndValue, EndArray],
		'potential_string_delimeter': BeginString,
		'default': BeginParseValue
	},
	Contexts.ValueType : {
		'potential_string_delimeter' : PotentialBeginStringName(AddCharToBuffer),
		' ' : EndValueType,
		'\t' : EndValueType,
		'\n' : [EndValueType, EndValue],
		',' : [EndValueType, EndValue],
		'eof': [EndValueType, EndValue],
		'default': AddCharToBuffer
	},
	Contexts.ParseValue : {
		'\n' : [EndParseValue, EndValue],
		',' : [EndParseValue, EndValue],
		'eof': [EndParseValue, EndValue],
		'}' : [EndParseValue, EndValue, EndObject],
		']' : [EndParseValue, EndValue, EndArray],
		'default': AddCharToBuffer
	}
}

def CallStepDelta(context, context_type, step_key):
		if (isinstance(StepDelta[context_type][step_key], (list, tuple))):
			for step_function in StepDelta[context_type][step_key]:
				step_function(context)
		else:
			StepDelta[context_type][step_key](context)

def StepContext(context):
	next_char = context.ReadNextChar()
	context_type = context.context_stack[-1]
	
	if (context_type != context.last_context):
		#LogVerbose("Context: " + context_type)
		context.last_context = context_type
	#LogVerbose("Context: " + context_type + " Char : " + next_char + " Value Buffer: " + context.value_buffer)
	if (next_char in StepDelta[Contexts.All]):
		CallStepDelta(context, Contexts.All, next_char)
	elif (context_type in StepDelta):
		if (next_char in StepDelta[context_type]):
			CallStepDelta(context, context_type, next_char)
		elif ('active_string_delimeter' in StepDelta[context_type] and next_char == context.active_string_delimeter):
			CallStepDelta(context, context_type, 'active_string_delimeter')
		elif ('potential_string_delimeter' in StepDelta[context_type] and next_char in context.potential_string_delimeters):
			CallStepDelta(context, context_type, 'potential_string_delimeter')
		elif ('default' in StepDelta[context_type]):
			CallStepDelta(context, context_type, 'default')


def StepContextEOF(context):
	context_type = context.context_stack[-1]
	if (context_type != context.last_context):
		#LogVerbose("Context: " + context_type)
		context.last_context = context_type
	if (context_type in StepDelta):
		if ('eof' in StepDelta[context_type]):
			CallStepDelta(context, context_type, 'eof')

def ParseRFDString(path, contents):
	context = Context(path, contents)
	while (context.remainder):
		StepContext(context)
	StepContextEOF(context)
	if (len(context.location_stack) > 0):
		LogError("Location Stack isn't empty")
	if (len(context.context_stack) != 1):
		LogError("Context Stack hasn't returned to just object")
	return context.loaded_object, context.loaded_definitions

def ParseRFDFile(location):
	f = open (location, 'r')
	remainder = f.read()

	return ParseRFDString(location, remainder)