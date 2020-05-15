#!/bin/python3

""""
    Written on: 2020-02-10 to 2020-05-15
    Written by: Lightmoll
    
    This script runs through an git folder before publishing
	to catch and report potentially sensitve information

    USAGE:
		run file with python3 ghs.py
		or 			  ./ghs.py

		To parse the current directory use .
		To update sensitve word list change the 'sensitve_words' array
"""

from pathlib import Path
import argparse
import errno
import glob  # .gitignore uses glob notation
import os
import re

try:
	import stringcolor as stc
	NO_COLORS = False
except Exception:
	print("Install string-color with 'pip install string-color' for a colored output")
	NO_COLORS = True

#read from local file
sensitive_words = [ ]
sensitive_words_file = os.path.join(Path.home(), ".config/github-sanatise/sensitive_words.txt")

#check if folder exits, else create them
if not os.path.exists(os.path.dirname(sensitive_words_file)):
    try:
        os.makedirs(os.path.dirname(sensitive_words_file))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

#try to open sensitve files file, if not there, create it
try:
	with open(sensitive_words_file, "r", encoding="utf-8") as file:
		for line in file.readlines():
			sensitive_words.append(line.rstrip())

except FileNotFoundError:
	print("Please setup your sensitive words list\nEnter each word (sentence) on a new line. Type 'END' to continue with program\n")
	word = input("+| ")
	while word != "END":
		with open(sensitive_words_file, "a+", encoding="utf-8") as file:
			file.write(f"{word}\n")

		sensitive_words.append(word)
		word = input("+| ")
	
	print(f"Setup complete. You can edit the wordlist here:\n{sensitive_words_file}\n")


COMMON_FILE_TYPES = ["c", "h", "cpp", "hpp", "hh", "cs", "csx", "java", "class", "m", "py",
					 "lua", "rb", "r", "pl", "vbp", "swift", "fs", "f", "js", "json", "ts", "css",
                     "less", "sass", "txt", "php", "htm", "html","xhtml", "xml","yml", "md", 
                     "markdown", "ahk", "as", "config", "sh", "bat", "ps1"]

#basic struct for errors
error_list_struct = {
	"error_level": 2,
	"type":"Error_type",
	"desc":"description",
	"line": 4,
	"file_path":"/src/file.py",
	}

regex_list_sens_words = []

def time_wrapper(in_func): #for debugging

	def catch_time(*args, **fargs):
		import time
		st_time = time.time()
		in_func(*args, **fargs)
		print(f"Elapsed time: {time.time()-st_time}")

	return catch_time


## VARIUOS INDIVIDUAL CHECK FUNCTIONS
def _find_sensitve_word_verbose(in_line):
	for word in sensitive_words:
		if in_line.lower().find(word) >= 0:
			return in_line
	return False

#only necessary for non-verbose!
def gen_regex_list():
	global regex_list_sens_words
	for word in sensitive_words:
		word = word.strip()
		regex_list_sens_words.append(re.compile(r"(?:^|[^a-z])" + word + r"(?:[^a-z]|$)", re.IGNORECASE))

def _find_sensitve_word(in_line):
	global regex_list_sens_words
	for regex in regex_list_sens_words:
		regex_search_result = regex.match(in_line)
		if regex_search_result != None:
				first_part = in_line[:regex_search_result.pos]
				word = stc.bold(in_line[regex_search_result.pos:regex_search_result.endpos])
				last_part = in_line[regex_search_result.endpos:]
				return f"{first_part}{word}{last_part}"
		return False

e_mail_reg = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
def _find_e_mail(in_line):
	if e_mail_reg.search(in_line) == None:
		return False
	return in_line

def _find_strange_file_extensions(file_name):
	return False

def sanatize_file(file_path, verbose):
	error_list = []

	with open(file_path) as file:
		for i, line in enumerate(file.readlines()):
			if _find_e_mail(line):
				error_list.append({
					"error_level": 2,
					"type":"E-Mail",
					"line": i +1,
					"desc": _find_e_mail(line), #might save to var
					"file_path":file_path,
					})
			if (not verbose and _find_sensitve_word(line)):
				error_list.append({
					"error_level": 4,
					"type":"Blacklisted Word",
					"line": i +1,
					"desc": _find_sensitve_word(line), #might save to var
					"file_path":file_path,
					})
			elif (verbose and _find_sensitve_word_verbose(line)):
				error_list.append({
					"error_level": 4,
					"type":"Blacklisted Word",
					"line": i +1,
					"desc": _find_sensitve_word_verbose(line), #might save to var
					"file_path":file_path,
					})
	return error_list

#TODO Very ugly, needs refactoring if possible
def list_valid_files_in_folder(folder_path, scan_git=False, all_file_types=False):
	files = []

	#catch if input is multiple files/paths
	if type(folder_path) is list:
		for path in folder_path:
			files.extend(
				list_valid_files_in_folder(path, scan_git=scan_git, all_file_types=all_file_types)
				)
		return files

	#filer files, which can not be opened or read as text
	def file_filter_strict(file): #TODO Change name
		if os.access(file, os.R_OK):
			try:
				open(file, encoding="utf-8").read()
				return True
			except Exception:
				pass
		return False

	def file_filter_lazy(file): #TODO Change name
		extension = file.split(".")[-1].lower()
		if extension in COMMON_FILE_TYPES:
			return file_filter_strict(file)
		return False

	if all_file_types:
		file_filter = file_filter_strict
	else:
		file_filter = file_filter_lazy


	#collect all files
	git_ignore_rules = []
	if os.path.isfile(folder_path):
		files.append(folder_path)
	elif os.path.isdir(folder_path):
		for (dirpath, dirnames, filenames) in os.walk(folder_path):
			for dirname in dirnames:
				if dirname == ".git": #catch .git folders
					pass
					git_ignore_rules.append(("/",os.path.join(dirpath, dirname)))
			for file in filenames:
				if file == ".gitignore": #catch .gitignore rules
					with open(os.path.join(dirpath, file), encoding="utf-8") as git_file:
						file_lines = git_file.readlines() #read all lines from file
						file_lines = list(filter(lambda x: x!="\n", file_lines)) #remove all empty lines
						git_ignore_rules.extend([(dirpath, f.rstrip()) for f in file_lines]) #strip \n and add current path
				files.append(os.path.join(dirpath, file))

	if not scan_git:
		#handle .gitignore rules, TODO only 80% covered (! support missing)
		ignored_files = []
		for path, rule in git_ignore_rules:
			glob_pattern = os.path.join(path, rule)
			if glob_pattern[-1] == "/": #add gitquirk to globpattern
				glob_pattern += "**"
			elif glob_pattern[-4:] == ".git": #add .git quirk to globpattern
				glob_pattern += "/**"
			ignored_files.extend(glob.glob(glob_pattern, recursive=True))

		files = [f for f in files if f not in ignored_files]
		#end handle .gitignore rules

	files = list(filter(file_filter, files))
	return files

def report_errors(error_list):
	if NO_COLORS:
		if len(error_list) == 0:
			print("There are no Sensitive Parts in your Code")
		for error in error_list:
			print(f"{error['type']} at line {error['line']} in file\n{error['file_path']}\n")
			print(f" {error['line']}| {error['desc'].lstrip()} \n")
	else: #if machine supports colors
		if len(error_list) == 0:
			print(stc.cs("There are no Sensitive Parts in your Code", "green"))
		for error in error_list:
			print(stc.cs(error["type"], "maroon"), end=" ")
			print(f"found at line {error['line']} in")
			print(stc.cs( "\t"+ error['file_path'], "lightgrey6"))
			print(f"\t{stc.cs(error['line'], 'lightgrey6')}| {error['desc'].lstrip()}")


def filter_duplicates(error_list): #TODO Might not work perfectly, but good enough
	for elm in error_list:
		for elm2 in error_list:
			if elm is not elm2:
				if (elm["line"] == elm2["line"]) and (elm["file_path"] == elm2["file_path"]):
					error_list.remove(elm)
					break
	return error_list

#@time_wrapper #uncomment to print timing information
def main(cwd, **flags):

	def sort_by_err_lvl(elem):
		return elem["error_level"]

	files_to_scan = list_valid_files_in_folder(cwd, scan_git=flags["scan_git"], all_file_types=flags["all_file_types"])
	error_list = []
	if not flags["verbose"]:
		pass #put here line below	
	gen_regex_list() #is called here, so it is only called once

	for file in files_to_scan:
		error_list.extend(sanatize_file(file, flags["verbose"]))

	if flags["sort"]:
		error_list.sort(key=sort_by_err_lvl)
	filter_duplicates(error_list)
	report_errors(error_list)


def profile():
	import cProfile
	cProfile.run("main('/home/HOMEDIR/Documents/Programming/', verbose=False, sort=True, scan_git=False, all_file_types=True)")

if __name__ == '__main__':
	global debug_state
	parser = argparse.ArgumentParser(description="code privacy sanitizer, it automatically ignores all .git and in .gitignore specified folders")
	parser.add_argument("folderPath", nargs="+", help="enter a folder or file of your source code")
	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument("-v", "--verbose-output", action="store_true", help="shows more, possible faulty results")
	parser.add_argument("-s", "--sort", action="store_true", help="sort occurrences by importance")
	parser.add_argument("-a", "--all", action="store_true", help="scan all files regardless of their file extension")
	parser.add_argument("--scan-git", action="store_true", help="scan the entire folder structure regardless of any .gitignore and .git")
	args = parser.parse_args()
	main(args.folderPath, verbose=args.verbose_output, sort=args.sort, scan_git=args.scan_git, all_file_types=args.all)
	#profile() # uncomment to profile script
