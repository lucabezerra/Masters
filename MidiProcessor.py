# coding=utf-8

__author__ = 'Luca'

import mido
from mido import midifiles
from collections import OrderedDict
import math
import PercussionDevicesEnum
from time import gmtime, strftime, localtime

# mid = None
# fileName = ""
# beats = {}
# instruments = {}
# orderedBeats = {}
# numerator = denominator = 4
# tempo = absoluteTimeCounter = ticksPerBeat = maxTrackLength = barSize = barCounter = 0

class MidiProcessor(object):
	def __init__(self, midi_file_path, file_name, runtime):
		self.mid = mido.midifiles.MidiFile(midi_file_path)
		self.fileName = file_name
		self.runtime = runtime
		self.ticksPerBeat = self.mid.ticks_per_beat
		#self.mid.print_tracks()
		####
		self.beats = {}
		self.instruments = {}
		self.orderedBeats = {}
		self.numerator = self.denominator = 4
		self.tempo = self.absoluteTimeCounter = self.maxTrackLength = self.barSize = self.barCounter = 0

	def processTracks(self):
		for i, track in enumerate(self.mid.tracks):
			self.absoluteTimeCounter = 0
			for j, message in enumerate(track):
				self.absoluteTimeCounter += message.time  # not only note_on messages have times greater than zero
				if message.type == 'note_on':
					if message.velocity > 0:
						# The same absolute time might have beats from
						# multiple instruments. Therefore, a list is required.
						if self.absoluteTimeCounter not in self.beats:
							self.beats[self.absoluteTimeCounter] = []
							self.beats[self.absoluteTimeCounter].append(message)
						else:
							hasNote = False
							# Check if there are no other messages from the same instrument at that same time before inserting
							for entry in self.beats[self.absoluteTimeCounter]:
								if entry.note == message.note:
									hasNote = True
							if not hasNote:
								self.beats[self.absoluteTimeCounter].append(message)
				elif message.type == 'set_tempo':
					tempo = message.tempo
					bpm = (1000000 / tempo) * 60
				elif message.type == 'time_signature':
					numerator = message.numerator
					denominator = message.denominator
				elif message.type == 'text':
					pass
			if self.absoluteTimeCounter > self.maxTrackLength:
				self.maxTrackLength = self.absoluteTimeCounter

	def setup_variables(self):
		self.orderedBeats = OrderedDict(sorted(self.beats.items()))  # Python's dictionaries are not ordered.
		#self.barSize = getTubsPlacement(self.ticksPerBeat) * self.denominator
		#self.barCounter = 0
		#print "TS: " + str(self.numerator) + "/" + str(self.denominator) + "(" + str(self.barSize) + ")"
		#print "T: " + str(self.tempo) + " | BPM: " + str(self.bpm) + " | TPB: " + str(self.ticksPerBeat)

	def beatsByInstrument(self):
		for absBeatTime, instrumentsList in self.orderedBeats.iteritems():
			for singleInstrument in instrumentsList:
				instrumentName = str(singleInstrument.note)
				if instrumentName not in self.instruments:
					self.instruments[instrumentName] = []
				self.instruments[instrumentName].append(absBeatTime)

	def printInstrumentName(self, instID):
		if int(instID) >= 33 and int(instID) <= 81:
			print PercussionDevicesEnum.PercussionDevices.PercussionDevicesDict[int(instID)]
		else:
			print instID

	def getTubsPlacement(self, attackTime):
		return int(math.ceil(float(attackTime) / (float(self.ticksPerBeat) / 12.0)))
		#return attackTime

	# "instruments" é um dicionário onde, para cada elemento, a chave é o nome do instrumento,
	# e o valor é uma lista de inteiros, onde cada elemento representa o tempo, em ticks, onde
	# aconteceu um ataque de nota. Para transformar na notação TUBS, é preciso preencher as
	# diferenças de tempo entre cada ataque com espaços vazios (ou pontos, na notação textual).
	def createTimelines(self):
		#print "\nINSTRUMENTOS:"
		for instrumentID, beatsTicks in self.instruments.iteritems():
			#self.printInstrumentName(instrumentID)
			prevTick = 0
			tubs = ""
			prevDiff = 0
			# Deve-se preencher espaços vazios apenas nos timeslots que não sejam utilizados por batidas. Por exemplo,
			# se temos batidas nos tempos 4 e 7 do sistema TUBS, devemos preencher com [7 - (4+1)] = 2 batidas, pois os
			# tempos 4 e 7 já estão reservados, sobrando os tempos 5 e 6 para preencher com espaços vazios.
			for tick in beatsTicks:
				tubsTick = self.getTubsPlacement(tick)
				tubsPrevTick = self.getTubsPlacement(prevTick)
				# if tubsTick > (barSize * (barCounter + 1)):
				#	 tubs += "|"
				#	 barCounter += 1

				for _ in range(tubsPrevTick + 1, tubsTick):
					tubs += "."

				diff = len(tubs) + 1 - self.getTubsPlacement(tick)
				#if not tubsPrevTick == tubsTick and not len(tubs) + 1 == self.getTubsPlacement(tick) and not diff == prevDiff and tick > 0:
				if tubsPrevTick == tubsTick and tick > 0:
					#print "HERE \/! Diff: " + str(diff)
					prevDiff = diff
					#tubs += "|"
					#tubs += "X"
				else:
					tubs += "X"

				#if instrumentID == '42':
				#	print "Len: " + str(len(tubs)) + " | Pos (Tick): " + str(self.getTubsPlacement(tick))

				if tick == 0:
					prevTick = tick + 1
				else:
					prevTick = tick

			# Preenchendo os últimos slots do TUBS, caso a última batida não tenha sido no último tempo da música. Aqui
			#  não é necessário o lembrete de cima, com relação à subtração de 1 do valor, porque o valor de
			# maxTrackLength é o último slot a ser preenchido, não a próxima batida.
			if self.getTubsPlacement(prevTick) < self.getTubsPlacement(self.maxTrackLength):
				for t in range(self.getTubsPlacement(prevTick) + 1, self.getTubsPlacement(self.maxTrackLength) + 1):
					tubs += "."

			#print tubs + "\t" + str(self.getTubsPlacement(prevTick)) + "-" + str(self.getTubsPlacement(self.maxTrackLength)),
			#print "[Length: " + str(len(tubs)) + "]"

			if len(tubs) != self.getTubsPlacement(self.maxTrackLength):
				print "**************** Problem on timeline length: " + self.mid.filename + " -->",
				str(self.printInstrumentName(instrumentID))
			elif len(self.instruments) < 2:
				print "**************** Less than 2 instruments: " + self.mid.filename + " -->" +\
				str(len(self.instruments))


	def writeResultsToFile(self):
		line = self.fileName + "\t\t" + str(self.maxTrackLength) + "\t\t" + str(len(self.instruments)) + \
		       "\t\t" + str(self.numerator) + "/" + str(self.denominator) + "\t\t" + str(self.ticksPerBeat) + "\n"

		with open(self.runtime + ".txt", 'a') as f:
			f.write(line)

