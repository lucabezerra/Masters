import os
from collections import OrderedDict

import helpers

import MidiProcessor

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
                processor = MidiProcessor.MidiProcessor(
                    os.path.join(dirpath, name), runtime,
                    print_instruments_data=False, generate_image_files=True,
                    only_two_instruments=False, filter_by_timber=False)
                processor.process_tracks()
                if len(list(processor.beats)) == 0:
                    continue
                processor.setup_variables()
                processor.beats_by_instrument()
                means = processor.create_timelines()
                file_contents += processor.format_results_for_file_writing()

                for mean in means:
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
    tmp_dict = {}

    # populates the normalized means list
    for key, value in ordered_means['am'].items():
        am_overall_normed_means = []
        x = value
        if len(x) > 1:
            tmp_dict[key] = []
            for i in processor.normalize_array(x):
                am_overall_normed_means.append(i)
                all_normed_means.append(i)
                tmp_dict[key].append(i)

            # for individual means use this. for cumulative, use the one outside the for loop
            # import matplotlib.pyplot as plt
            # fig = plt.figure(figsize=(8, 3))
            # helpers.plot_data(am_overall_normed_means, key)

    # plotting the cumulative means
    helpers.plot_data(
        all_normed_means, None, 
        plot_title=f"Distribuicao de todas as {len(all_normed_means)} amostras")

    ordered_means_by_inst = OrderedDict()
    for k, v in tmp_dict.items():
        ordered_means_by_inst[k] = sorted(v)
    # helpers.plot_color_gradients(len(ordered_means_by_inst), ordered_means_by_inst, 'Greys')
    # helpers.write_to_file(runtime, file_contents)
    print(f"End: {helpers.get_time()}")


if __name__ == '__main__':
    run()

# TODO: Divide in bars, check time signature data