import os
from time import localtime, strftime
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np

import MidiProcessor

# coding=utf-8

__author__ = 'Luca'


class PlotGenerator():
    DIRPATH = "MIDIs"
    FILE_EXTENSION = ".MID"

    def __init__(self):
        self.file_contents = ""

    def get_time(self):
        return strftime("%Y_%m_%d___%H_%M_%S", localtime())

    def run(self):
        runtime = self.get_time()
        print "Begin: " + str(runtime)

        amount_of_means_by_num_insts = dict()
        amount_of_means_by_num_insts['am'] = dict()
        amount_of_means_by_num_insts['bm'] = dict()

        for (dirpath, dirnames, filenames) in os.walk(self.DIRPATH):
            for name in filenames:
                # remove the second condition on this IF to include drum samples
                if str(name).upper().find(self.FILE_EXTENSION) != -1:  # and dirpath.find("Drum_Loops") == -1:
                    self.processor = MidiProcessor.MidiProcessor(
                        os.path.join(dirpath + "\\" + name), name, runtime,
                        print_instruments_data=False, generate_image_files=True,
                        only_two_instruments=False, filter_by_timber=False)
                    self.processor.process_tracks()
                    self.processor.setup_variables()
                    self.processor.beats_by_instrument()
                    means = self.processor.create_timelines()
                    self.file_contents += self.processor.format_results_for_file_writing()

                    if means != "":
                        for i in range(len(means)):
                            # - means is a list with 2 ReturnData elements
                            # - amount_of_means_by_num_insts is a dict with 'am' and 'bm' keys
                            # - amount_of_means_by_num_insts['am'/'bm'] is a dict with the total #
                            #   of instruments as its value
                            # - amount_of_means_by_num_insts['am'/'bm'][6] is a dict with a list of
                            #   means from files with that amount of instruments, rounded to
                            #   4 digits

                            # >>> print amount_of_means_by_num_insts['am'][7]
                            # [1.0003, 1.0025, 1.0234]
                            if means[i].num_insts not in \
                                    amount_of_means_by_num_insts[means[i].mean_type]:
                                amount_of_means_by_num_insts[means[i].mean_type][means[i]
                                    .num_insts] = []

                            amount_of_means_by_num_insts[means[i].mean_type][means[i].num_insts]\
                                .append(round(means[i].mean_value, 4))

        # Python's dictionaries are unordered.
        ordered_means = OrderedDict(sorted(amount_of_means_by_num_insts.items()))
        all_normed_means = []
        tmp_dict = dict()

        # populates the normed means list
        for key, value in ordered_means['am'].iteritems():
            am_overall_normed_means = []
            x = value
            if len(x) > 1:
                tmp_dict[key] = []
                for i in self.processor.normalize_array(x):
                    am_overall_normed_means.append(i)
                    all_normed_means.append(i)
                    tmp_dict[key].append(i)

                # for individual means use this. for cumulative, use the one outside the for loop
                #fig = plt.figure(figsize=(8, 3))
                #self.plot_data(am_overall_normed_means, key)

        # plotting the cumulative means
        fig = plt.figure(figsize=(8, 3))
        self.plot_data(all_normed_means, None, plot_title="Distribuicao de Todas as Amostras (" +
                                                         str(len(all_normed_means)) + " amostras)")

        ordered_means_by_inst = OrderedDict()
        for k, v in tmp_dict.iteritems():
            print("Key: [" + str(k) + "] list: " + str(sorted(v)))
            ordered_means_by_inst[k] = sorted(v)
        #self.plot_color_gradients(len(ordered_means_by_inst), ordered_means_by_inst, 'Greys')

        #self.write_to_file(runtime, self.file_contents)
        print "End: " + str(self.get_time())

    def plot_color_gradients(self, nrows, lists, cmap_type):
        """
        Plots a list of gradients with the given lists' distribution.
        :param nrows: The number of entries (gradients) in the plot.
        :param lists: The lists of data for each entry (gradient)
        :param cmap_type: The colormap type (refer to
        http://matplotlib.org/examples/color/colormaps_reference.html for options)
        """
        # gets the axis of each entry (gradient)
        fig, axes = plt.subplots(nrows=nrows)
        fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99)
        axes[0].set_title("'Means by Instrument' Colormap", fontsize=14)

        # for each list of values contained in the 'lists' parameter
        for i, (key, values_list) in enumerate(lists.iteritems()):
            # generate the histogram values without plotting
            #   bins: the histogram's intervals
            #   vals: the values (y axis) for each interval
            vals, bins = np.histogram(values_list)
            # use values_list intead of vals below to get the distribution ordered by value
            # 1st param must be a np.ndarray with 2 symmetric lists of values (for this case)
            axes[i].imshow(np.concatenate((np.array([vals]), np.array([vals])),
                                          axis=0), aspect='auto', cmap=plt.get_cmap(cmap_type))
            pos = list(axes[i].get_position().bounds)
            x_text = pos[0] - 0.01
            y_text = pos[1] + pos[3] / 2.
            # sets the text next to each entry
            fig.text(x_text, y_text, str(key) + ' insts (' + str(len(values_list)) + ' samples)',
                     va='center', ha='right', fontsize=10)

        # Turn off *all* ticks & spines, not just the ones with colormaps.
        for ax in axes:
            ax.set_axis_off()

        plt.show()

    def plot_data(self, data_list, plot_id, plot_title=''):
        """
        Plots a histogram of the provided data.
        :param data_list: list of values to be plotted
        :param plot_id: in this case, the number of instruments that this plot corresponds to
        :param plot_title: a title, if the standard format one isnt suitable
        """
        # plotting the histogram
        n, bins, patches = plt.hist(data_list, alpha=0.3)
        x_axis = []
        # the points in the X axis are located exactly in the middle of each bin's interval
        for i in range(len(bins[:-1])):
            x_axis.append((bins[i] + bins[i + 1]) / 2)

        # plotting the standard deviation and the lines on top of the histogram
        error = np.std(data_list)
        plt.errorbar(x_axis, n, yerr=error, fmt='o')
        plt.plot(x_axis, n, linewidth=1, marker='4')

        if plot_title != '':
            plt.title(plot_title)
            plot_filename = ("Plots\\" +
                             plot_title.replace(' ', '_') + ".png")
        else:
            plt.title(str(plot_id) + (" instrumentos - Distribuicao dos EC's (" + str(len(data_list)) +
                      " amostras)"))
            plot_filename = ("Plots\\" + str(plot_id) + "_Insts_EC.png")

        plt.ylabel('# de ocorrencias (Desv. Pad.: ' + str(round(error, 2)) + ')')
        plt.xlabel("Valores Normalizados do Equilibrio de Coincidencias (EC)")
        plt.grid()
        plt.xlim(-1.0, 1.0)
        plt.savefig(plot_filename, bbox_inches='tight', dpi=200)

    def write_to_file(self, start_runtime, contents, write_mode='a'):
        """
        Writes contents to a file whose name is the provided runtime.
        :param start_runtime: the time the test started running
        :param contents: the contents to be written into the file
        :param write_mode: (optional) the write mode (default: append)
        """
        with open(start_runtime + ".txt", write_mode) as f:
            f.write("Filename\t\tMaxTrack\tNumInst\t\tTimeSig\t\tTPB\n")
            f.write(contents)

if __name__ == '__main__':
    plot_gen = PlotGenerator()
    plot_gen.run()

# TODO: Divide in bars, check time signature data