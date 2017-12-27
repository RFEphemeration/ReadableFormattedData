import re
import pprint

class BuiltinValueTypes():
	Bool = 'Bool'
	Int = 'Int'
	Float = 'Float'
	String = 'String'
	Array = 'Array'
	Object = 'Object'
	Any = 'Any'
	# RMF TODO: @Incomplete this should allow you to say min and max and allow either float or int, maybe more?
	MultiplePotential = 'MultiplePotential'


class DefinitionNode():
	def __init__(self, definition):
		self.definition = definition


class DataNode():
	def __init__(self, data_type, value, definition):
		self.data_type = data_type
		self.value = value
		self.definition = definition

def Validate(context, data, type_name):
	pprint.pprint("Validating data of type: " + type_name)
	pprint.pprint(data)

def ValidateDefinitionOfBasicType(test_node, definition_node):
	value = test_node.value
	definition = definition_node.definition
	if definition['min']:
		if (value < definition["min"]):
			return False
	if definition['max']:
		if (value > definition["max"]):
			return False
	if definition['regex']:
		if not re.match(definition['regex']):
			return False
	if definition['one_of']:
		found = False
		for potential_node in definition['one_of']:
			# @RMF TODO: @Incomplete if the one of prevents extra members that are defined outside of one_of then this validation might fail when it should actually be valid
			if Validate(test_node, potential_node):
				found = True
				break
		if not found:
			return False