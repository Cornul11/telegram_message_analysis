from bs4 import BeautifulSoup
import sys

def read_file(file_name):
	with open(file_name, 'r', encoding='utf-8') as fi:
		text_to_analyze = fi.read()
	return text_to_analyze

def get_file_name():
	if len(sys.argv) < 2:
		print("Usage filename")
		sys.exit()
	return ' '.join(sys.argv[1:])

def main():
	file_name_with_extension = get_file_name()
	text_to_analyze = BeautifulSoup(open(file_name_with_extension), "lxml")
	prettyHTML = text_to_analyze.prettify()
	f = open('latest_pretty.html', "w+")
	f.write(prettyHTML)
	f.close()

main()
