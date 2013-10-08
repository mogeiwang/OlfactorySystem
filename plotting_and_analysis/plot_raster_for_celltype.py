import os, sys, inspect
# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../")))
print 'cmd_subfolder', cmd_subfolder
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import simulation_parameters
import MergeSpikefiles
import SetOfCurvesPlotter
import numpy as np
import pylab

def plot_raster_for_celltype(cell_type, show=True):
    print 'Loading Spikes from:', params['%s_spikes_merged_fn_base' % cell_type]

    fn = params['%s_spiketimes_merged_fn_base' % (cell_type)] + str(pn) + '.dat'
    if (os.path.exists(fn) == False):
        Merger = MergeSpikefiles.MergeSpikefiles(params)
        Merger.merge_spiketimes_files(params['%s_spiketimes_fn_base' % (cell_type)], params['%s_spiketimes_merged_fn_base' % (cell_type)], pn)

    print 'Loading ', fn
    data = np.loadtxt(fn)
    assert (data.size > 0), 'ERROR file %s has 0 size\nIf there was a problem when merging them, delete the empty one and rerun' % (fn)

    from FigureCreator import plot_params
    pylab.rcParams.update(plot_params)
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    pylab.subplots_adjust(left=.2)

    ax.plot(data[:,0], data[:,1], 'o', markersize=2, color='k')
    ax.set_xlim((0, params['t_sim']))
    ax.set_title('%s spikes' % cell_type.upper())
    ax.set_xlabel('Time [ms]')
    ax.set_ylabel('Cell GID')

    output_fn = params['figure_folder'] + '/' + 'rasterplot_%s_%d.png' % (cell_type, pn)
    print 'Saving figure to', output_fn
    pylab.savefig(output_fn, dpi=(200))




if __name__ == '__main__':
    info_txt = \
    """
    Usage:
        python plot_response_curve.py [FOLDER] [CELLTYPE] 
        or
        python plot_response_curve.py [FOLDER] [CELLTYPE] [PATTERN_NUMBER]
    """
    assert (len(sys.argv) > 2), 'ERROR: folder and cell_type not given\n' + info_txt
    folder = sys.argv[1]
    cell_type = sys.argv[2]
    try:
        pn = int(sys.argv[3])
    except:
        print 'WARNING: Using the default pattern number 0'
        pn = 0

    params_fn = os.path.abspath(folder) + '/Parameters/simulation_parameters.json'
    param_tool = simulation_parameters.parameter_storage(params_fn=params_fn)
    params = param_tool.params

    if cell_type == 'all':
#        cell_types = params['cell_types']
        cell_types = ['mit', 'pg', 'gran']
    else:
        cell_types = [cell_type]

    for cell_type in cell_types:
        print 'Plotting raster for:', cell_type
        plot_raster_for_celltype(cell_type)

    pylab.show()
