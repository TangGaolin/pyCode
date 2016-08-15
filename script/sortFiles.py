#!/usr/bin/env python
__author__ = 'tanggaolin'

import os
import shutil

def getFile(file_path):

	file_list = os.listdir(file_path)

	files = []

	for item in file_list:
		file = file_path + '/' +  item
		if os.path.isfile(file):
			print item
			files.append(item)

	return files
			


if __name__ == "__main__":

	file_path = '/Users/tanggaolin/Downloads'
	files = getFile(file_path)
	os.chdir(file_path)

	for file in files:
		ext = os.path.splitext(file)[1].strip('.')
		if ext is not '':
			if ext == 'docx':
				ext = 'doc'
			if ext == 'xlsx':
				ext = 'xls'
			if os.path.isdir(ext) is False:
				os.mkdir(ext)
				print 'mkdir : ' + ext 
			shutil.move(file,ext + '/' + file);
			print 'move : ' + file 
