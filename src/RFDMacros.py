def AddStringDelimeter(context, arguments):
	for delimeter in arguments:
		context.potential_string_delimeters.append(delimeter)

def RemoveStringDelimeter(context, arguments):
	for delimeter in arguments:
		context.potential_string_delimeters.remove(delimeter)

MacroFunctions = {
	'add_string_delimeter' : AddStringDelimeter,
	'remove_string_delimeter' : RemoveStringDelimeter
}

def ExecuteMacro(context, command, arguments):
	if (command in MacroFunctions):
		MacroFunctions[command](context, arguments)