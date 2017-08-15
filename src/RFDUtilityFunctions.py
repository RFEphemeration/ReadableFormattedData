def LogError(error):
	print(error)

def LogVerbose(output):
	pprint.pprint(output)
	pass

def MakePath(array):
	path = ""
	if (len(array) == 0):
		return path
	for item in array[:-1]:
		path = path + str(item) + "."
	path = path + str(array[-1])
	return path

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
	if (v == "true"):
		return True
	if (v == "false"):
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