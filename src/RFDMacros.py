from RFDUtilityFunctions import ProtectedSymbols, MakeFilePath, SplitFilePath

def AddStringDelimeter(context, arguments):
	for delimeter in arguments:
		context.potential_string_delimeters.append(delimeter)

def RemoveStringDelimeter(context, arguments):
	for delimeter in arguments:
		if (not delimeter in ProtectedSymbols):
			context.potential_string_delimeters.remove(delimeter)

def IncludeAll(context, arguments):
	file_path, file_name = SplitFilePath(arguments[0])
	full_path = MakeFilePath(context.file_stack) + file_path
	f = open (full_path + file_name, 'r')
	remainder = f.read()
	context.remainder = remainder + '\n' + context.remainder
	file_length = len(remainder) + 1
	context.PushFilePath(file_path, file_length)

MacroFunctions = {
	'add_string_delimeter' : AddStringDelimeter,
	'remove_string_delimeter' : RemoveStringDelimeter,
	'include_all': IncludeAll,
}

def ExecuteMacro(context, command, arguments):
	if (command in MacroFunctions):
		MacroFunctions[command](context, arguments)