# coding=utf-8

__author__ = 'Luca'

import math
from collections import OrderedDict
import mido
from mido import midifiles
import PercussionDevicesEnum


class MidiProcessor(object):
    '''
        Class that performs the whole MIDI processing.
    '''

    def __init__(self, midi_file_path, filename, runtime, print_instruments_data=False,
                 generate_image_files=False, only_two_instruments=False, filter_by_timber=False):
        self.mid = mido.midifiles.MidiFile(midi_file_path)
        self.filename = filename
        self.runtime = runtime
        self.ticks_per_beat = self.mid.ticks_per_beat
        # self.mid.print_tracks()
        self.beats = {}
        self.instruments = {}
        self.ordered_beats = {}
        self.numerator = self.denominator = 4
        self.tempo, self.absolute_time_counter, self.max_track_length, \
        self.bar_size, self.bar_counter, self.bpm = 0, 0, 0, 0, 0, 0
        self.print_instruments_data = print_instruments_data
        self.generate_image_files = generate_image_files
        self.only_two_instruments = only_two_instruments
        self.filter_by_timber = filter_by_timber
        self.percussion_devices = PercussionDevicesEnum.PercussionDevices()

    def process_tracks(self):
        for i, track in enumerate(self.mid.tracks):
            self.absolute_time_counter = 0
            for j, message in enumerate(track):
                # not only note_on messages have times greater than zero
                self.absolute_time_counter += message.time
                if message.type == 'note_on':
                    if message.velocity > 0 and message.channel == 9:
                        # The same absolute time might have beats from
                        # multiple instruments. Therefore, a list is required.
                        if self.absolute_time_counter not in self.beats:
                            self.beats[self.absolute_time_counter] = []
                            self.beats[self.absolute_time_counter].append(message)
                        else:
                            has_note = False
                            # Check if there are no other messages from the same instrument at that
                            # same time before inserting
                            for entry in self.beats[self.absolute_time_counter]:
                                if entry.note == message.note:
                                    has_note = True
                            if not has_note:
                                self.beats[self.absolute_time_counter].append(message)
                elif message.type == 'set_tempo':
                    self.tempo = message.tempo
                    self.bpm = (1000000 / self.tempo) * 60
                elif message.type == 'time_signature':
                    self.numerator = message.numerator
                    self.denominator = message.denominator
                elif message.type == 'text':
                    pass
            if self.absolute_time_counter > self.max_track_length:
                self.max_track_length = self.absolute_time_counter

    def setup_variables(self):
        # Python's dictionaries are unordered.
        self.ordered_beats = OrderedDict(sorted(self.beats.items()))

    def beats_by_instrument(self):
        for abs_beat_time, instruments_list in self.ordered_beats.iteritems():
            for single_instrument in instruments_list:
                instrument_name = str(single_instrument.note)
                if instrument_name not in self.instruments:
                    self.instruments[instrument_name] = []
                self.instruments[instrument_name].append(abs_beat_time)

    def count_instruments_by_beat(self):
        inst_sum = 0
        binary_sum = 0
        max_instruments_at_once = 1
        min_instruments_at_once = len(self.instruments)
        means = []

        if len(self.instruments) < 2:
            print "LESS THAN 2 INSTRUMENTS:", self.mid.filename

        # gets the list of instruments that played at each beat
        for beat, inst_list in self.ordered_beats.iteritems():
            # checks and sets the max and min instruments found
            if len(inst_list) > max_instruments_at_once: max_instruments_at_once = len(inst_list)
            if len(inst_list) < min_instruments_at_once: min_instruments_at_once = len(inst_list)

            if len(inst_list) >= 2:
                binary_sum += 1

            # checks whether it should filter the coincidences by timber or not
            if not self.filter_by_timber:
                inst_sum += len(inst_list)
            else:
                inst_sum += self.percussion_devices.get_timber_group(inst_list)

        # The Arithmetic Mean (sum of instruments from all beats divided by the amount of beats)
        arith_mean = float(inst_sum) / float(len(self.ordered_beats))

        return_data = ReturnData()
        return_data.mean_type = 'am'
        return_data.num_insts = len(self.instruments)
        return_data.mean_value = arith_mean

        means.append(return_data)

        # The Binary Mean (anything above 1 instrument counts as only 2 instruments)
        bin_mean = min_instruments_at_once + (float(binary_sum) / float(len(self.ordered_beats)))

        return_data = ReturnData()
        return_data.mean_type = 'bm'
        return_data.num_insts = len(self.instruments)
        return_data.mean_value = bin_mean

        means.append(return_data)

        return means

    def print_instrument_name(self, inst_id):
        if int(inst_id) >= 33 and int(inst_id) <= 81:
            print self.percussion_devices.PercussionDevicesDict[int(inst_id)]
        else:
            print inst_id

    def get_tubs_placement(self, attack_time):
        return int(math.ceil(float(attack_time) / (float(self.ticks_per_beat) / 12.0)))

    def create_timelines(self):
        # "instruments" é um dicionário onde, para cada elemento, a chave é o nome do instrumento,
        # e o valor é uma lista de inteiros, onde cada elemento representa o tempo, em ticks, onde
        # aconteceu um ataque de nota. Para transformar na notação TUBS, é preciso preencher as
        # diferenças de tempo entre cada ataque com espaços vazios (ou pontos, na notação textual).
        if self.print_instruments_data:
            print "\nINSTRUMENTOS:"
        for instrument_id, beats_ticks in self.instruments.iteritems():
            if self.print_instruments_data and len():
                self.print_instrument_name(instrument_id)
            prev_tick = 0
            tubs = ""
            # Deve-se preencher espaços vazios apenas nos timeslots que não sejam utilizados por batidas. Por exemplo,
            # se temos batidas nos tempos 4 e 7 do sistema TUBS, devemos preencher com [7 - (4+1)] = 2 batidas, pois os
            # tempos 4 e 7 já estão reservados, sobrando os tempos 5 e 6 para preencher com espaços vazios.
            for tick in beats_ticks:
                tubs_tick = self.get_tubs_placement(tick)
                tubs_prev_tick = self.get_tubs_placement(prev_tick)

                for _ in range(tubs_prev_tick + 1, tubs_tick):
                    tubs += "."

                if tubs_prev_tick == tubs_tick and tick > 0:
                    pass
                else:
                    tubs += "X"

                if tick == 0:
                    prev_tick = tick + 1
                else:
                    prev_tick = tick

            # Preenchendo os últimos slots do TUBS, caso a última batida não tenha sido
            # no último tempo da música.
            if self.get_tubs_placement(prev_tick) < self.get_tubs_placement(self.max_track_length):
                for t in range(self.get_tubs_placement(prev_tick) + 1,
                               self.get_tubs_placement(self.max_track_length) + 1):
                    tubs += "."

            if self.print_instruments_data:
                print tubs + "\t" + str(self.get_tubs_placement(prev_tick)) + "-" + \
                      str(self.get_tubs_placement(self.max_track_length)),
                print "[Length: " + str(len(tubs)) + "]"

        if self.generate_image_files:
            return self.count_instruments_by_beat()

        return ""


    def format_results_for_file_writing(self):
        return self.filename + "\t\t" + str(self.max_track_length) + "\t\t" + \
               str(len(self.instruments)) + "\t\t" + str(self.numerator) + "/" + \
               str(self.denominator) + "\t\t" + str(self.ticks_per_beat) + "\n"


    def normalize_array(self, original_array):
        return_array = []
        max_value = max(original_array)
        min_value = min(original_array)
        normalized_max = 1.0
        normalized_min = -1.0
        normalized_range = normalized_max - normalized_min

        # to avoid a ZeroDivisionError below, we deal with this special case
        if max_value == min_value:
            return [normalized_min for _ in range(len(original_array))]

        # lambda function for transposing the original values to the normalized ones through a
        # linear function calculation
        # y = ax + b -> normalized_value = (a * original_value) + b
        a = -normalized_range / float(min_value - max_value)
        b = normalized_max - (a * max_value)
        converter = lambda x: (a * x) + b

        for item in original_array:
            return_array.append(converter(item))

        return return_array


class ReturnData(object):
    mean_type = ""
    num_insts = 0
    mean_value = 0.0


if __name__ == '__main__':
    from time import localtime, strftime
    import argparse

    parser = argparse.ArgumentParser(description='Running the processor module by itself.')
    parser.add_argument('-file', '-f', type=str, help='the file path')

    args = parser.parse_args()
    print "Begin: " + str(strftime("%Y_%m_%d___%H_%M_%S", localtime()))
    processor = MidiProcessor(args.file, args.file.split('\\')[-1],
                              strftime("%Y_%m_%d___%H_%M_%S", localtime()),
                              print_instruments_data=True, generate_image_files=True,
                              only_two_instruments=False, filter_by_timber=False)
    processor.process_tracks()
    processor.setup_variables()
    processor.beats_by_instrument()
    means = processor.create_timelines()
    processor.format_results_for_file_writing()
    print "End: " + str(strftime("%Y_%m_%d___%H_%M_%S", localtime()))