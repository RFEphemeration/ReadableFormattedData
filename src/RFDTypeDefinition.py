# rfm todo unused, untested

import re

class NodeTypes():
	Bool = 'Bool'
	Int = 'Int'
	Float = 'Float'
	String = 'String'
	Array = 'Array'
	Object = 'Object'
	# RMF TODO: @Incomplete this should allow you to say min and max and allow either float or int, maybe more?
	MultiplePotential = 'MultiplePotential'

class Definition():
	def __init__(self, name, value, definition, example, children):
		self.name = name
		self.value = value
		self.definition = definition
		self.example = example
		self.children = children

	def MeetsDefinition(self, test_object):
		if (self.example is not None):
			for key, value in test_object:


class DataNode():
	def __init__(self, data_type, value, definition):
		self.data_type = data_type
		self.value = value
		self.definition = definition



	def Validate(self):
		example = self.definition.example

BasicTypes = [NodeTypes.Bool, NodeTypes.Int, NodeTypes.Float, NodeTypes.String]

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
			if Validate(test_node, potential_node):
				found = True
				break
		if not found:
			return False

def ValidateDefinitionOfArray(test_node, definition_node):
	#RMF TODO: @Incomplete
	return True

def GetTypesOfArrayValues(array):
	types_exist = {}
	types = []
	for node in array:
		if node.type not in types_exist:
			types_exist[node.type] = True
			types.append(node.type)
	return types

def IsArrayOfSingleType(array):
	if len(array) == 0:
		return True

	node_type = array[0]

	for node in array:
		if node.type != note_type:
			return False

	return node_type

def ArrayLengthAndTypeOrdersMatch(array1, array2):
	if len(array1) != len(array2):
		return False

	for node1, node2 in zip(array1, array2):
		if node1.type != node2.type:
			return False

	return True

def Validate(test_node, definition_node):
	if test_node.type != definition_node.type:
		return False
	if test_node.type in BasicTypes:
		if definition_node.defintion is None:
			# the base case
			return True
		else:
			return ValidateDefinitionOfBasicType(test_node.type, test_node.value, definition_node.definition)
	elif test_node.type == NodeTypes.Array:
		if definition_node.defintion is None:
			if ArrayLengthAndTypeOrdersMatch(test_node.value, definition_node.value):
				return True
			else:
				definition_array_type = IsArrayOfSingleType(definition_node.value)
				if (definition_array_type == False):
					return False
				elif (definition_array_type == True):
					# an empty array example just means type array
					return True
				else:
					test_array_type = IsArrayOfSingleType(test_node.value)
					return test_array_type == definition_array_type
		else:
			return ValidateDefinitionOfArray(test_node, definition_node)


	unvalidated_children = node.value.keys()

	if definition_node.value is not None:
		valid, unvalidated_children = PartialValidateByExample(node, definition_node.value, unvalidated_children)
		if not valid:
			return False

	if definition_node.definition is not None:
		valid, unvalidated_children = PartialValidateByDefinition(node, definition_node.definition, unvalidated_children)
		if not valid: return False

	if len(unvalidated_children > 0):
		return False

	return True

def PartialValidateByDefinition(node, definition, unvalidated_children):



def PartialValidateByExample(node, example, unvalidated_children):
	unvalidated_children = node.value.keys()
	valid = True

	for key, child_example in example.iteritems():
		if key not in node.value:
			valid = False

		child_node = node.value[key]
		if child_example.type != child_node.type:
			valid = False

		if child_node.type == NodeTypes.Object:
			if (Validate(child_node, child_example)):
				unvalidated_children.pop(key)
			else:
				valid = False
		elif child_node.type == NodeTypes.Array:
			# RMF TODO: @Incomplete array examples are not handled / well defined. what do we imply? that the types of the children are the same and the length is the same?
			valid = Validate(child_node, child_example)
		else:
			# in this case, the NodeType is a Bool, Int, Float, or String. which are all considered equivalent by 
			pass

	return valid, unvalidated_children


			(example_key, example_value) in zip(self.definition.example.items(), self.value.items()):