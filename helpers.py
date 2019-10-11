import os
from time import localtime, strftime
import matplotlib.pyplot as plt
import numpy as np



def get_time():
        return strftime("%Y_%m_%d___%H_%M_%S", localtime())


def plot_color_gradients(nrows, lists, cmap_type):
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
    for i, (key, values_list) in enumerate(lists.items()):
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
        fig.text(x_text, y_text, f'{key} insts ({len(values_list)} samples)',
                  va='center', ha='right', fontsize=10)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axes:
        ax.set_axis_off()

    plt.show()


def plot_data(data_list, plot_id, plot_title=''):
    """
    Plots a histogram of the provided data.
    :param data_list: list of values to be plotted
    :param plot_id: in this case, the number of instruments that this plot corresponds to
    :param plot_title: a title, if the standard format one isnt suitable
    """
    fig = plt.figure(figsize=(8, 3))
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
    
    os.mkdir('Plots') if not os.path.exists('Plots') else None

    if plot_title != '':
        plt.title(plot_title)
        plot_filename = (f"Plots/{plot_title.replace(' ', '_')}.png")
    else:
        plt.title(f"{plot_id} instrumentos - Distribuicao dos EC's ({len(data_list)} amostras)")
        plot_filename = (f"Plots/{plot_id}_Insts_EC.png")

    plt.ylabel(f'# de ocorrencias (Desv. Pad.: {round(error, 2)})')
    plt.xlabel("Valores Normalizados do Equilibrio de Coincidencias (EC)")
    plt.grid()
    plt.xlim(-1.0, 1.0)
    plt.savefig(plot_filename, bbox_inches='tight', dpi=200)


def write_to_file(start_runtime, contents, write_mode='a'):
    """
    Writes contents to a file whose name is the provided runtime.
    :param start_runtime: the time the test started running
    :param contents: the contents to be written into the file
    :param write_mode: (optional) the write mode (default: append)
    """
    with open(f"{start_runtime}.txt", write_mode) as f:
        f.write("Filename\t\tMaxTrack\tNumInst\t\tTimeSig\t\tTPB\n")
        f.write(contents)


def get_timber_group(self, inst_list):

    HighTimberInstruments = {}
    MediumTimberInstruments = {}
    LowTimberInstruments = {}

    if inst_list in HighTimberInstruments:
        return "high"
    elif inst_list in MediumTimberInstruments:
        return "medium"
    elif inst_list in LowTimberInstruments:
        return "low"
    else:
        return "none"