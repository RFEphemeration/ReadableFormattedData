def AddStringDelimeter(context, arguments):
	for delimeter in arguments:
		context.potential_string_delimeters.append(delimeter)

def RemoveStringDelimeter(context, arguments):
	for delimeter in arguments:
		context.potential_string_delimeters.remove(delimeter)

def IncludeAll(context, arguments):
	f = open (arguments[0], 'r')
	remainder = f.read()
	context.remainder = remainder + '\n' + context.remainder

MacroFunctions = {
	'add_string_delimeter' : AddStringDelimeter,
	'remove_string_delimeter' : RemoveStringDelimeter,
	'include_all': IncludeAll,
}

def ExecuteMacro(context, command, arguments):
	if (command in MacroFunctions):
		MacroFunctions[command](context, arguments)