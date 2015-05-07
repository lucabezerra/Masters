# coding=utf-8

__author__ = 'Luca'

import MidiProcessor

if __name__ == '__main__':
	processor = MidiProcessor.MidiProcessor('C:\\Users\\Luca\\Downloads\\MIDIs\\Brazilian\\FREVO.MID')
	processor.processTracks()
	processor.setup_variables()
	processor.beatsByInstrument()
	processor.createTimelines()
