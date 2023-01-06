
import os
import math
import numpy as np
import graph_tool as gt
import mpmath

from dpwnets import utils
from dpwnets import dp_mechanisms
from dpwnets import tools
from dpwnets import graphics

from metrics import (error_metrics, egocentric_metrics)

from graph.wgraph import WGraph

np.random.seed(1) 

class DPWeightedNets():

    def __init__(self, 
                    datasets_names, 
                    optins_methods, 
                    optins_perc, 
                    es, 
                    runs
                ):
        self.datasets_names = datasets_names  
        self.optins_methods = optins_methods
        self.optins_perc = optins_perc
        self.es = es
        self.runs = runs 

    def run(self):
        for dataset in self.datasets_names:
            utils.log_msg('*************** DATASET = ' + dataset + ' ***************')

            for optin_method in self.optins_methods: 
                for optin_perc in self.optins_perc:
                    url = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'data', dataset, '%s_%s_%s.graphml' % (dataset, optin_method, optin_perc )))
                    g = WGraph(url)

                    n = g.n()
                    optins = g.optins()
                    optouts = g.optouts()
                    non_optins_pos = g.vp.optin.fa == 0

                    mask_without_in_in = g.edges_without_in_in()
                    g_without_in_in = WGraph(G=gt.GraphView(g, efilt=mask_without_in_in), prune=True)

                    # mask_out_out = g.edges_out_out()
                    # g_out_out = WGraph(G=gt.GraphView(g, efilt=mask_out_out), prune=True)

                    len_all_edges_without_in_in = int( ( g.n() * (g.n()-1))/2 - (len(optins) * (len(optins)-1))/2 )

                    edges_w = g_without_in_in.edges_w()
                    num_total_edges = int(g_without_in_in.n()*(g_without_in_in.n()-1)/2)
                    all_edges_w = np.append(edges_w, [0] * (num_total_edges - len(edges_w)))

                    # all_edges_w = np.sort( np.random.choice(all_edges_w, 100, replace=False) )[::-1]

                    utils.log_msg('computing levels...')
                    levels_size = dp_mechanisms.get_levels_size(all_edges_w)

                    # picked_levels = []
                    # normalized_prob_masses = []
                    # graphic_pos = np.linspace(0, len(levels_size)-2, num=1000, dtype=int)

                    for e in self.es:
                        utils.log_msg('******* eps = ' + str(e) + ' *******')

                        utils.log_msg('computing probability mass...')
                        prob_mass = dp_mechanisms.compute_probability_mass(levels_size, e)

                        for r in range(self.runs):
                            utils.log_msg('....... RUN ' + str(r) + ' .......')   
                            
                            utils.log_msg('running exponential...')
                            picked_level, _ = dp_mechanisms.exponential_mechanism(prob_mass)

                            utils.log_msg('picked level: %s' % picked_level)

                            graph_positions_selected = np.random.choice(len_all_edges_without_in_in, size=picked_level, replace=True)
                            # counting_weights_pos = Counter(graph_positions_selected)
                            edges_pos, weights_to_sum = np.unique(graph_positions_selected, return_counts=True)
                            non_zero_edges_pos = edges_pos[edges_pos < len(edges_w)] # np.where(edges_pos < len(edges_w))[0]
                            signals = np.random.choice([-1, 1], size=len(non_zero_edges_pos))
                            weights_to_sum_non_zero_edges = weights_to_sum[non_zero_edges_pos] 
                            weights_to_sum_non_zero_edges_signal = weights_to_sum[non_zero_edges_pos] * signals
                            new_non_zero_edges_w = edges_w.copy()
                            new_non_zero_edges_w[non_zero_edges_pos] += weights_to_sum_non_zero_edges_signal
                            new_non_zero_edges_w_positive = tools.min_l2_norm_old(new_non_zero_edges_w, np.sum(new_non_zero_edges_w), min_value=0)
                            non_zero_edges = g_without_in_in.get_edges()
                            new_non_zero_edges = np.concatenate((non_zero_edges, np.array([new_non_zero_edges_w_positive]).T ), axis=1)

                            edges_g_prime = weights_to_sum[edges_pos >= len(edges_w)]
                            # edges_g_prime = weights_to_sum[zero_edges_pos]
                            num_edges_to_be_created = len(edges_g_prime)
                            utils.log_msg('creating random edges..')
                            created_edges = tools.sample_random_edges(n, num_edges_to_be_created, set(map(tuple, non_zero_edges)), non_optins_pos)
                            new_zero_edges = np.concatenate((created_edges, np.array([edges_g_prime]).T ), axis=1)

                            new_edges = np.append(new_non_zero_edges, new_zero_edges, axis=0)
                            new_g = tools.build_g_from_edges(g, new_edges)

                            utils.log_msg('saving graph...')
                            path_graph = "./data/%s/exp/%s_ins%s_e%s_r%s_exponential.graphml" % ( dataset , optin_method, optin_perc, e, r)     
                            new_g.save(path_graph)  

                    # path_graphic = "./data/%s/levels/prob_mass.png" % ( dataset )

                    # legends = [
                    #             '$\epsilon$=0.1',
                    #             '$\epsilon$=0.5',
                    #             '$\epsilon$=1.0'
                    #         ]

                    # # graphics.line_plot2( np.array(list(range(1, len(levels_size))))[graphic_pos], normalized_prob_masses,
                    # #                         xlabel='level', ylabel= 'prob. mass', ylog=True, # ylim=(min(normalized_prob_mass), None),
                    # #                         path=path_graphic, line_legends=legends, figsize=(10, 5))

                    # graphics.line_plot2( np.array(list(range(1, len(levels_size))))[graphic_pos], normalized_prob_masses,
                    #                         xlabel='level', ylabel= 'prob. mass', ylog=True, xlim=(0, 25000),
                    #                         path=path_graphic, line_legends=legends, figsize=(10, 5), colors = ['#000000', '#FF0000', '#0000FF'])

                    # print(picked_levels) 

if __name__ == "__main__":
    datasets_names = [
                          'high-school-contacts',
                        #   'reality-call2',
                        #   'enron',
                        #   'dblp'
                    ]

    optins_methods = ['affinity']
    optins_perc = [.0]

    es = [ 1 ]

    runs = 10

    exp = DPWeightedNets(datasets_names, optins_methods, optins_perc, es, runs)
    exp.run()