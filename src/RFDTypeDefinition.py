import re
import pprint
import pdb

from RFDUtilityFunctions import LogValidationCheck, LogError, GetInteger, GetBoolean, GetFloat, GetString, ParseValue

class RootTypes():
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

	'length',

	'one_of', # rmf todo: @incomplete will need more work to make this able to be nested

	'members',
	'name',
	'required',
	'delete_members' # from parent
}

RootTypeNameToPythonType = {
	RootTypes.Bool : (bool),
	RootTypes.Int : (int),
	RootTypes.Float : (float),
	RootTypes.String : (basestring),
	RootTypes.Array : (list),
	RootTypes.Object : (dict),
	RootTypes.Any : ()
}

BasicTypes = {
	RootTypes.Bool,
	RootTypes.Int,
	RootTypes.Float,
	RootTypes.String
}

BasicTypeParsers = {
	RootTypes.Bool : GetBoolean,
	RootTypes.Int : GetInteger,
	RootTypes.Float : GetFloat,
	RootTypes.String : GetString
}

class DefinitionNode():
	def __init__(self, definition):
		self.definition = definition


class DataNode():
	def __init__(self, data_type, value, definition):
		self.data_type = data_type
		self.value = value
		self.definition = definition

def ValitateTypeMatch(context, data, type_name_or_definition):

	validation_type = GetBasicType(type_name_or_definition)
	if (validation_type == RootTypes.String):
		type_name = type_name_or_definition

		if (type_name in RootTypeNameToPythonType):
			success = ValidateBuiltinTypeMatch(data, type_name)
			LogValidationCheck(data, type_name, success)
			return success

		else if (type_name in context.loaded_definitions):
			#rmf todo: @incomplete it's not just about whether it's a dict, but whether it is a definition, values should probably happen in a different loaded_ place
			if (not isinstance(context.loaded_definitions[type_name], dict)):
				LogError("Tried to validate against type that is data value")
				LogValidationCheck(data, type_name, success)
				return False

			definition = context.loaded_definitions[type_name]
			root_type = GetRootType(context, type_name)

		else:
			LogValidationCheck(data, type_name, success)
			return False

	else if (validation_type == RootTypes.Object):
		definition = type_name_or_definition
		root_type = GetRootType(data, definition)
	
	#rmf todo: this doesn't support extending either array or string, I think.
	if (root_type in BasicTypes):
		success = ValidateDefinitionOfBasicType(context, data, definition)
	else if (root_type == RootTypes.Array):
		success = ValidateDefinitionOfArrayType(context, data, definition)
	else:
		# rmf todo: @incomplete validate objects
		pass

	LogValidationCheck(data, type_name, success)
	return False

def Validate(context, data, type_name_or_definition):
	ValitateTypeMatch(context, data, type_name_or_definition)
	
def ValidateBuiltinTypeMatch(data, type_name):
	if (type_name == RootTypes.Any):
		return True
	else:
		return isinstance(data, RootTypeNameToPythonType[type_name])

def GetBasicType(data):
	for type_name in BasicTypes:
		if (ValidateBuiltinTypeMatch(data, type_name)):
			return type_name
	return None

def IsBasicType(data):
	return (GetBasicType(data) != None)

def ParseTypedBasicValue(string_buffer, type_name):
	parsed_value = BasicTypeParsers[type_name](string_buffer)
	if (parsed_value == None):
		LogError("Expected value " + string_buffer + " to be of type " + type_name)
		parsed_value = ParseValue(string_buffer)

	return parsed_value

def GetRootType(context, type_name_or_defintion):
	# rmf todo: @Incomplete this shouldn't use definition['type'], it should be based on explicit extension
	validation_type = GetBasicType(type_name_or_definition)
	if (validation_type == RootTypes.String):
		type_name = type_name_or_definition

	else if (validation_type == RootTypes.Object):
		type_definition = type_name_or_definition
		if ('type' in type_defintion):
			return type_definition['type']
		else if ('extends' in type_defition):
			type_name = type_defintion['extends']
		else:
			return RootTypes.Unspecified

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
		if ('type' in type_defintion):
			return type_definition['type']
		if ('extends' in type_defintion)
			type_name = type_defintion['extends']
		return RootTypes.Unspecified
		

def ValidateDefinitionOfBasicType(context, data, type_name_or_definition):
	if isinstance(definition, dict):
		definition = type_name_or_definition
	else:
		if type_name_or_definition in RootTypeNameToPythonType:
			return ValidateBuiltinTypeMatch(data, type_name_or_definition)
		if type_name_or_definition not in context.loaded_definitions:
			LogError("Unknown type name " + str(type_name_or_definition))
			return False
		definition = context.loaded_definitions[type_name_or_definition]

	if 'extends' in definition:
		#rmf todo: @incomplete allow extending multiple types
		if not definition['extends'] in context.loaded_definitions:
			return False
		if not ValidateTypeMatch(context, data, definition['extends']):
			return False

	if 'type' in definition:
		if definition['type'] in RootTypeNameToPythonType:
			if not ValidateBuiltinTypeMatch(data, definition['type']):
				return False
		else:
			return False
	if 'min' in definition:
		if data < definition['min']:
			return False
	if 'max' in definition:
		if data > definition['max']:
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

def ValidateDefinitionOfArrayType(context, data, definition):
	if 'length' in definition:
		length_value = definition['length']
		length_type = GetBasicType(length_value)
		if (length_type == RootTypes.Int):
			if (len(data) != length_value):
				return False
		else if (length_type == RootTypes.Object):
			if not ValidateDefinitionOfBasicType(context, len(data), definition['length']):
				return False
	if 'elements' in definition:
		elements_value = definition['elements']
		elements_type = GetBasicType(elements_value)
		if (elements_type == RootTypes.String):
			for element in data:
				if not Validate(context, element, elements_type):
					return False
		else if (elements_type == RootTypes.Object):
