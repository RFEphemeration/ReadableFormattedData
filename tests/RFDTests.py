import json
import sys
sys.path.append('../src')

from RFDReader import ParseRFDFile

def main():
	loaded_object = ParseRFDFile('../examples/test_definitions.rfd')
	print "Loading and printing ../examples/test_defintions.rfd"
	print json.dumps(loaded_object, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
	main()