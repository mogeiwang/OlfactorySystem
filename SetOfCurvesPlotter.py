import numpy as np
import pylab
from FigureCreator import plot_params


class SetOfCurvesPlotter(object):

    def __init__(self, params):
        self.params = params


    def plot_set_of_curves(self, output_fn=None, cell_type='orn'):

        self.cell_type = cell_type
        if cell_type == 'orn':
            n_per_group = self.params['rel_orn_mit']
            shared_param_idx = 3
            x_idx = 2
        else:
            n_per_group = 1
            shared_param_idx = 4
            x_idx = 3

        self.gid_idx = 0 # index in parameter file which contains the cell gids

        x_data, y_data = self.get_xy_data(shared_param_idx, x_idx)
        y_avg, y_std = self.get_average_group_curve(x_data, y_data, n_per_group)

        colorlist = ["#0000FF", "#006600", "#FF0000", "#00FFFF", "#CC00FF", "#FFFF00", "#000000", \
                "#00FF00", "#663300", "#FF3399", "#66CCCC", "#FFCC99", "#FFFFCC"]
        
        pylab.rcParams.update(plot_params)
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        color_group_idx = 0
        n_cells = len(x_data)
        lw = 1
        for i_ in xrange(n_cells):
            if cell_type == 'orn':
                color_group_idx = i_ / n_per_group
                color = colorlist[color_group_idx % len(colorlist)]
                ax.plot(x_data[i_], y_data[i_], label='%d' % color_group_idx, c=color, lw=lw)
            else:
                ax.plot(x_data[i_], y_data[i_], label='%d' % i_, lw=lw)
            ax.set_xscale('log')

        for group in xrange(len(y_avg)):
            color = colorlist[group % len(colorlist)]
            ax.errorbar(x_data[0], y_avg[group], yerr=y_std[group], c=color, lw=4)

        ax.set_title('%s response curves' % cell_type.upper())
        ax.set_xlabel('Concentration [a.u.]')
        ax.set_ylabel('Output rate [Hz]')
        ax.set_ylim((0, ax.get_ylim()[1]))

        if output_fn != None:
            pylab.savefig(output_fn)
        else:
            pylab.show()
        return x_data, y_data


    def get_average_group_curve(self, x_data, y_data, n_per_group):
        """
        A group is a set of ORNs projecting to the same MIT cell.
        Keyword arguments:
        x_data, y_data  --  the response curves of single ORNs in lists, obtained from get_xy_data
        n_per_group -- (int) should be params['rel_orn_mit']
        """

        n_total = len(y_data)
        n_groups = n_total / n_per_group
        x_dim = x_data[0].size
        y_avg = np.zeros((x_dim, n_groups))
        y_std = np.zeros((x_dim, n_groups))

        for group_idx in xrange(n_groups):
            i0 = group_idx * n_per_group
            i1 = (group_idx + 1) * n_per_group
            for x_idx in xrange(x_dim):
                y_avg[x_idx, group_idx] = y_data[i0:i1, x_idx].mean()
                y_std[x_idx, group_idx] = y_data[i0:i1, x_idx].std()
#                print 'debug', i0, i1
#                print 'debug, group_idx, x_idx, y_avg, y_std', group_idx, x_idx, y_data[i0:i1, x_idx]

        y_std = y_std.transpose()
        y_avg = y_avg.transpose()
        print 'y avg std', len(y_std)
        return y_avg, y_std





    def get_xy_data(self, shared_param_idx, x_idx):

        pattern_nr = 0

        param_fn = self.params['%s_params_fn_base' % (self.cell_type)] + '%d.dat' % pattern_nr
        print 'Loading cell parameters from:', param_fn
        cell_params = np.loadtxt(param_fn, skiprows=1)

        nspike_fn = self.params['%s_spikes_merged_fn_base' % self.cell_type] + '%d.dat' % pattern_nr
        print 'Loading nspike data from:', nspike_fn
        self.nspikes = np.loadtxt(nspike_fn)


        # get GIDs that have a certain parameter in common
        group_params = np.unique(cell_params[:, shared_param_idx])
        n_groups = group_params.size
        # the data to be plotted
        x_data = [[] for i in xrange(n_groups)]
        y_data = [[] for i in xrange(n_groups)]

        for i_, val in enumerate(group_params):
            group_idx = np.array(cell_params[:, shared_param_idx] == val).nonzero()[0]
            x_values_for_group = cell_params[group_idx, x_idx]
            gids = cell_params[group_idx, self.gid_idx]
            for j_, gid in enumerate(gids):
                f_out = self.get_nspikes(gid) / (self.params['t_sim'] / 1000.)
                y_data[i_].append(f_out)
                x_data[i_].append(x_values_for_group[j_])

        x_data = np.array(x_data)
        y_data = np.array(y_data)
        return x_data, y_data
        


    def get_nspikes(self, gid):
        """
        Assuming that GIDs are stored in column 0 in self.nspikes the number of spikes fired by cell gid is returned.
        """
        try:
            idx = self.nspikes[:, 0] == gid
            return self.nspikes[idx, 1][0]
        except:
            return 0

        
