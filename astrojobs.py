"""
astrojobs: Get latest astronomy job and rumor news in your command line

Project website: https://github.com/pmocz/astrojobs

The MIT License (MIT)
Copyright (c) 2021 Philip Mocz (pmocz)
http://opensource.org/licenses/MIT
"""
from __future__ import absolute_import, print_function

import difflib
import os
from shutil import copyfile
import sys
from argparse import ArgumentParser
from packaging import version

import bs4 as bs
import requests
import urllib.request
from wasabi import color


__version__ = "0.0.5"
dir_path = os.path.dirname(os.path.realpath(__file__))



def printDiff(file1, file2):
	text1 = open(file1).readlines()
	text2 = open(file2).readlines()
	diff = difflib.ndiff(text1, text2)
	for l in diff:
		if (l[0] == "+"):
			print(color(l[2:], fg="green"))
		elif (l[0] == "-"):
			print(color(l[2:], fg="red"))
		




def check_aas_updates(jobType):
	### List New Job Openings from AAS Job Register
	print(color("WARNING: The AAS Job Register (https://jobregister.aas.org) is currently protected by Cloudflare and cannot be scraped by this tool.", fg="yellow"))
	print(color("Please visit the website directly to check for updates.", fg="yellow"))
	print('=======================================================\n')
	return





def check_rumormill_updates(jobType):
	### List New Rumors from the Rumor Mill
	if(jobType == 'faculty'):
		jobTypeId = 'Rumor+Mill+Faculty-Staff'
	elif(jobType == 'postdoc'):
		jobTypeId = 'Rumor+Mill'
	
	# req = urllib.request.Request('https://www.astrobetter.com/wiki/'+jobTypeId, headers={'User-Agent': 'Mozilla/5.0'})
	# source = urllib.request.urlopen(req).read()
	source = requests.get('https://www.astrobetter.com/wiki/'+jobTypeId, headers={'User-Agent': 'Mozilla/5.0'}).text
	
	soup = bs.BeautifulSoup(source,'html.parser')
	
	jobs = soup.find_all('td')
	
	jobfile = dir_path + '/sav_' + jobType + '_rumor.txt'
	jobfile_old = dir_path + '/sav_' + jobType + '_rumor_old.txt'
	
	if not os.path.exists(jobfile_old):
		open(jobfile_old,"w+").close()
	
	### save new rumors ###
	f = open(jobfile,"w+")
	cc = 0
	
	# The table now has 4 columns: Empty, Job Title, Empty, Deadline
	# We want to extract Job Title (index 1) and Deadline (index 3)
	
	num_columns = 4
	num_rows = len(jobs) // num_columns
	
	for i in range(num_rows):
		# Extract Job Title (2nd column, index 1)
		job_idx = i * num_columns + 1
		if job_idx >= len(jobs): break
		
		job_cell = jobs[job_idx]
		
		# Extract Deadline (4th column, index 3)
		deadline_idx = i * num_columns + 3
		if deadline_idx >= len(jobs): break
		
		deadline_cell = jobs[deadline_idx]
		
		# Process Job Title
		line = str(job_cell)
		line = line.replace('<td>','')
		line = line.replace('</td>','')
		line = line.replace('<a href=','')
		line = line.replace('</a>','')
		line = line.replace('>ad','')
		line = line.replace('<a class=','')
		line = line.replace('<p>','')
		line = line.replace('</p>','')
		line = line.replace('<br/>','')
		line = line.replace('<span>','')
		line = line.replace('</span>','')
		line = line.replace('\n','   ')
		
		# Process Deadline
		deadline = str(deadline_cell)
		deadline = deadline.replace('<td>','')
		deadline = deadline.replace('</td>','')
		deadline = deadline.replace('<p>','')
		deadline = deadline.replace('</p>','')
		deadline = deadline.replace('<br/>','')
		deadline = deadline.replace('<span>','')
		deadline = deadline.replace('</span>','')
		deadline = deadline.replace('\n','   ')
		
		full_line = line + "   ||  " + deadline + "\n"
		f.write(full_line)
	
	f.close()
	
	print('=======================================================')
	print('NEW ' + jobType + ' rumors')
	print('=======================================================')
	
	# Print differences
	#os.system('colordiff ' + jobfile_old + ' ' + jobfile)
	printDiff(jobfile_old,jobfile)
	
	# save jobs as oldjobs
	copyfile(jobfile, jobfile_old)
	
	print(jobType + ' rumor mill check complete!\n')




### Main
def main():
	
	parser = ArgumentParser()
	parser.add_argument(
		"-f",
		"--faculty",
		action="store_true",
		help="show updates for faculty jobs/rumors",
	)
	parser.add_argument(
		"-p",
		"--postdoc",
		action="store_true",
		help="show updates for postdoc jobs/rumors",
	)
	parser.add_argument(
		"--version",
		action="version",
		version="%(prog)s {version}".format(version=__version__),
	)
	args = parser.parse_args()
	
	if len(sys.argv)==1:
		print('=======================================================')
		print('astrojobs: get astro job/rumor updates in terminal since last check')
		print('=======================================================\n')
		parser.print_help()
	
	
	# show postdoc updates
	if args.postdoc:
		check_aas_updates("postdoc")
		check_rumormill_updates("postdoc")
		
		
	# show faculty updates
	if args.faculty:
		check_aas_updates("faculty")
		check_rumormill_updates("faculty")
	

	# check version
	try:
		latest_version = version.parse(
			requests.get(
				"https://pypi.python.org/pypi/astrojobs/json", timeout=0.1,
			).json()["info"]["version"]
		)
	except (requests.RequestException, KeyError, ValueError):
		pass
	else:
		if latest_version > version.parse(__version__):
			msg = "A newer version of astrojobs (v{}) is now available!\n".format(
				latest_version
			)
			msg += "Please consider updating it by running:\n\n"
			msg += "pip install astrojobs=={}".format(latest_version)
			print(_headerize(msg))



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(_headerize("Abort! astrojobs interupted by a keyboard signal!"))
