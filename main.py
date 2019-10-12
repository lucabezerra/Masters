import os
from collections import OrderedDict

import helpers
from midi_processor import MidiProcessor

# coding=utf-8

__author__ = 'Luca'


DIRPATH = "MIDIs"
FILE_EXTENSION = ".MID"


def run():
    file_contents = ""
    runtime = helpers.get_time()
    print(f"Begin: {runtime}")

    # am - arithmetic mean
    # bm - binary mean
    num_means_by_num_insts = {'am': {}, 'bm': {}}
    
    for (dirpath, _, filenames) in os.walk(DIRPATH):
        for name in filenames:
            # remove the second condition on this IF to include drum samples
            if name.upper().find(FILE_EXTENSION) != -1:  # and dirpath.find("Drum_Loops") == -1:
                processor = MidiProcessor(os.path.join(dirpath, name), runtime)
                processor.process_tracks()
                if len(list(processor.beats)) == 0:
                    continue
                processor.setup_variables()
                processor.beats_by_instrument()         
                # processor.create_timelines()  # if you want to print the TUBS timelines   
                # file_contents += processor.format_results_for_file_writing()

                for mean in processor.count_instruments_by_beat():
                    print(":::: mean:", mean)
                    # - means is a list with 2 ReturnData elements
                    # - num_means_by_num_insts is a dict with 'am' and 'bm' keys
                    # - num_means_by_num_insts['am'/'bm'] is a dict with the total number
                    #   of instruments as its value
                    # - num_means_by_num_insts['am'][6] is a dict with a list of means from
                    #   files with that amount of instruments, rounded to 4 digits

                    # >>> print num_means_by_num_insts['am'][7]
                    # [1.0003, 1.0025, 1.0234]
                    type_ = mean.mean_type
                    num_insts = mean.num_insts
                    value = mean.mean_value
                    if num_insts not in num_means_by_num_insts[type_]:
                        num_means_by_num_insts[type_][num_insts] = []
                    
                    num_means_by_num_insts[type_][num_insts].append(round(value, 4))

    ordered_means = OrderedDict(sorted(num_means_by_num_insts.items()))
    all_normed_means = []

    # populates the normalized means list
    for means_array in ordered_means['am'].values():
        for mean in helpers.normalize_array(means_array):                
            all_normed_means.append(mean)

    # plotting the cumulative means
    helpers.plot_data(
        all_normed_means, None, 
        plot_title=f"Distribuicao de todas as {len(all_normed_means)} amostras")

    # for individual means use this. for cumulative, use the one outside the for loop
    # helpers.plot_individual_means(ordered_means)

    # for an overview of the information of the samples database, use the code below
    # helpers.write_to_file(runtime, file_contents)
    print(f"End: {helpers.get_time()}")


if __name__ == '__main__':
    run()

# TODO: Divide in bars, check time signature data