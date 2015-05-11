# coding=utf-8

__author__ = 'Luca'

import MidiProcessor
from time import localtime, strftime
import os

windows_url = "C:\\Users\\Luca\\PycharmProjects\\Testing\\MIDIs"
linux_url = ""

if __name__ == '__main__':
	runtime = strftime("%Y_%m_%d___%H_%M_%S", localtime())
	with open(runtime + ".txt", 'a') as f:
			f.write("Filename\t\tMaxTrack\tNumInst\t\tTimeSig\t\tTPB\n")

	for (dirpath, dirnames, filenames) in os.walk(windows_url):
		for name in filenames:
			#print "File: " + name
			processor = MidiProcessor.MidiProcessor(os.path.join(dirpath + "\\" + name), name, runtime)
			processor.processTracks()
			processor.setup_variables()
			processor.beatsByInstrument()
			processor.createTimelines()
			processor.writeResultsToFile()

	# TODO: Divide in bars, check time signature data, do coincidences algorithm