# coding=utf-8

__author__ = 'Luca'

import MidiProcessor
from os import walk

if __name__ == '__main__':
	dirs = []
	files = []
	for (dirpath, dirnames, filenames) in walk("C:\\Users\\Luca\\PycharmProjects\\Testing"):
		if dirpath.find("MIDI") != -1:
			print dirpath
		if dirnames.find("MIDI") != -1:
			dirs.extend(dirnames)
		if filenames.find(".MID") != -1 or filenames.find(".mid") != -1:
			files.extend(filenames)

	print len(files)
	for single_file in files:
		print single_file


	# processor = MidiProcessor.MidiProcessor('C:\\Users\\Luca\\Downloads\\MIDIs\\Brazilian\\AFOXE.MID')
	# processor.processTracks()
	# processor.setup_variables()
	# processor.beatsByInstrument()
	# processor.createTimelines()
