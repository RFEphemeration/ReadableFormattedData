import pprint

ProtectedSymbols = {'{', '}', '[', ']', ',', '\n', ':', '.', '@'}

class Settings:
	LogError = True
	LogVerbose = False
	LogValidation = True

def LogError(error):
	if (not Settings.LogError):
		return
	print(error)

def LogVerbose(output):
	if (not Settings.LogVerbose):
		return
	pprint.pprint(output)

def LogValidationCheck(data, type_name, success):
	LogValidation("Validating data value: " + pprint.pformat(data)		
		+ " against type: " + type_name
		+ " > " + str(success))

def LogValidation(output):
	if (not Settings.LogValidation):
		return
	print(output)

def MakeObjectPath(array):
	path = ""
	if (len(array) == 0):
		return path
	for item in array[:-1]:
		path = path + str(item) + "."
	path = path + str(array[-1])
	return path

def SplitFilePath(path):
	file_path_and_name = path.rsplit('/', 1)
	file_path = ''
	file_name = ''
	if (len(file_path_and_name) > 1):
		file_path = file_path_and_name[0] + '/'
		file_name = file_path_and_name[1]
	else:
		file_name = file_path_and_name[0]
	return file_path, file_name

def MakeFilePath(array):
	return ('').join(array)

def GetInteger(v):
	try:
		return int(v)
	except:
		return None

def GetFloat(v):
	try:
		return float(v)
	except:
		return None

def GetBoolean(v):
	v = v.strip().lower()
	if (v == 'true' or v == 't'):
		return True
	if (v == 'false' or v == 'f'):
		return False
	return None

def GetString(v):
	return v.strip()

def ParseValue(string_buffer):
	ret_value = None

	functions = [GetInteger, GetFloat, GetBoolean, GetString]
	for func in functions:
		ret_value = func(string_buffer)
		if (ret_value != None):
			break

	return ret_value