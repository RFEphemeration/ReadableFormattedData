import re
import pprint
import pdb

from RFDUtilityFunctions import LogValidationCheck, LogError, GetInteger, GetBoolean, GetFloat, GetString, ParseValue

class BuiltinValueTypes():
	Unspecified = 'Unspecified'
	Bool = 'Bool'
	Int = 'Int'
	Float = 'Float'
	String = 'String'
	Array = 'Array'
	Object = 'Object'
	Any = 'Any'

AllowedDefinitionMembers = {
	'type',
	'min',
	'max',
	'regex',
	'extends', # rmf todo: this is important, but requires partial validation
	'default_value',

	'one_of', # rmf todo: @incomplete will need more work to make this able to be nested

	'members',
	'name',
	'required',
	'delete_members' # from parent
}

BuiltinTypeNameToPythonType = {
	BuiltinValueTypes.Bool : (bool),
	BuiltinValueTypes.Int : (int),
	BuiltinValueTypes.Float : (float),
	BuiltinValueTypes.String : (basestring),
	BuiltinValueTypes.Array : (list),
	BuiltinValueTypes.Object : (dict),
	BuiltinValueTypes.Any : ()
}

BasicTypes = {
	BuiltinValueTypes.Bool,
	BuiltinValueTypes.Int,
	BuiltinValueTypes.Float,
	BuiltinValueTypes.String
}

BasicTypeParsers = {
	BuiltinValueTypes.Bool : GetBoolean,
	BuiltinValueTypes.Int : GetInteger,
	BuiltinValueTypes.Float : GetFloat,
	BuiltinValueTypes.String : GetString
}

class DefinitionNode():
	def __init__(self, definition):
		self.definition = definition


class DataNode():
	def __init__(self, data_type, value, definition):
		self.data_type = data_type
		self.value = value
		self.definition = definition

def Validate(context, data, type_name):
	success = False
	if (type_name in BuiltinTypeNameToPythonType):
		success = ValidateBuiltinTypeMatch(data, type_name)
		LogValidationCheck(data, type_name, success)
		return success

	elif (type_name in context.loaded_definitions):
		if (not isinstance(context.loaded_definitions[type_name], dict)):
			LogError("Tried to validate against type that is data value")
			LogValidationCheck(data, type_name, success)
			return success
		definition = context.loaded_definitions[type_name]
		basic_type_name = GetRootBasicType(context, type_name)
		if (basic_type_name != None):
			success = ValidateDefinitionOfBasicType(context, data, definition)
		else:
			# rmf todo: @incomplete validate objects and arrays
			pass

	LogValidationCheck(data, type_name, success)
	return success
	#type_data = context.loaded_definitions[]
	
def ValidateBuiltinTypeMatch(data, type_name):
	if (type_name == BuiltinValueTypes.Any):
		return True
	else:
		return isinstance(data, BuiltinTypeNameToPythonType[type_name])

def IsBasicType(data):
	for type_name in BasicTypes:
		if (ValidateBuiltinTypeMatch(data, type_name)):
			return True
	return False

def ParseTypedBasicValue(string_buffer, type_name):
	parsed_value = BasicTypeParsers[type_name](string_buffer)
	if (parsed_value == None):
		LogError("Expected value " + string_buffer + " to be of type " + type_name)
		parsed_value = ParseValue(string_buffer)

	return parsed_value

def GetRootBasicType(context, type_name):
	# rmf todo @Wrong this shouldn't use definition['type'], it should be based on explicit extension
	checked_types = set()
	while (type_name != None):
		if (type_name in BasicTypes):
			return type_name
		if (type_name in checked_types):
			return None # prevent circular references
		checked_types.add(type_name)
		if (type_name not in context.loaded_definitions):
			return None
		type_defintion = context.loaded_definitions[type_name]
		if ('type' not in type_defintion):
			return None
		type_name = type_defintion['type']
		

def ValidateDefinitionOfBasicType(context, data, definition):
	if 'type' in definition:
		if (definition['type'] in BuiltinTypeNameToPythonType):
			if not ValidateBuiltinTypeMatch(data, definition['type']):
				return False
		else:
			return False
	if 'min' in definition:
		if (data < definition['min']):
			return False
	if 'max' in definition:
		if (data > definition['max']):
			return False
	if 'regex' in definition:
		if not re.match(definition['regex']):
			return False
	if 'one_of' in definition:
		found = False
		for potential_node in definition['one_of']:
			# @RMF TODO: @Incomplete if the one of prevents extra members that are defined outside of one_of then this validation might fail when it should actually be valid
			if ValidateDefinitionOfBasicType(context, data, potential_node):
				found = True
				break
		if not found:
			return False

	return True