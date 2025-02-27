import os
import numpy as np

from dpwnets import (utils, graphics)
from metrics import (error_metrics, egocentric_metrics)

from graph.wgraph import WGraph

class ResultsDPWeightedNets():

    def __init__(self, 
                    datasets_names, 
                    optins_methods, 
                    optins_perc, 
                    e, 
                    ks, 
                    error_met, 
                    ego_metrics,
                    num_sample_nodes,
                    threshold,
                    runs
                ):
        self.datasets_names = datasets_names  
        self.optins_methods = optins_methods
        self.optins_perc = optins_perc
        self.e = e
        self.ks = ks
        self.error_met = error_met
        self.ego_metrics = ego_metrics
        self.num_sample_nodes = num_sample_nodes
        self.threshold = threshold
        self.runs = runs 

    def run(self):
        
        for dataset in self.datasets_names:
            utils.log_msg('*************** DATASET = ' + dataset + ' ***************')
            for optin_method in self.optins_methods: 
                for optin_perc in self.optins_perc:
                    url = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'data', dataset, '%s_%s_%s.graphml' % (dataset, optin_method, optin_perc )))
                    g = WGraph(url)

                    ego_metrics_true = {}

                    errors_1 = {} # approach 1
                    errors_2 = {} # approach 2
                    errors_3 = {} # approach 3

                    for ego_metric in self.ego_metrics:
                        # ego_metrics_true[ego_metric] = egocentric_metrics.calculate(g, ego_metric )
                        errors_1[ego_metric] = {}
                        errors_2[ego_metric] = {}
                        errors_3[ego_metric] = {}

                        for error_metr in self.error_met: 
                            errors_1[ego_metric][error_metr] = []
                            errors_2[ego_metric][error_metr] = []
                            errors_3[ego_metric][error_metr] = []

                            # for k in self.ks: 
                            #     errors_1[ego_metric][error_metr][k] = []
                            #     errors_2[ego_metric][error_metr][k] = []

                    utils.log_msg('*************** e = ' + str(e) + ' ***************')
                    
                    errors_list_1 = {} # approach 1
                    errors_list_2 = {} # approach 2
                    errors_list_3 = {} # approach 3

                    for ego_metric in self.ego_metrics:
                        errors_list_1[ego_metric] = {}
                        errors_list_2[ego_metric] = {}
                        errors_list_3[ego_metric] = {}

                        for error_metr in self.error_met: 
                            errors_list_1[ego_metric][error_metr] = {}
                            errors_list_2[ego_metric][error_metr] = {}
                            errors_list_3[ego_metric][error_metr] = {}

                            for k in self.ks: 
                                errors_list_1[ego_metric][error_metr][k] = []
                                errors_list_2[ego_metric][error_metr][k] = []
                                errors_list_3[ego_metric][error_metr][k] = []
                                   
                    for r in range(self.runs):  
                        utils.log_msg('===== run ' + str(r) + ' =====')

                        path_g1 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'data', dataset, 'exp', 'graph_perturbed_%s_ins%s_e%s_r%s_global_final.graphml' % ( optin_method, optin_perc, e, r )))
                        g1 = WGraph(path_g1)

                        path_g2 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'data', dataset, 'exp', 'graph_perturbed_%s_ins%s_e%s_r%s_local_final.graphml' % ( optin_method, optin_perc, e, r )))
                        g2 = WGraph(path_g2)

                        path_g3 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'data', dataset, 'exp', 'graph_perturbed_%s_ins%s_e%s_r%s_baseline_final.graphml' % ( optin_method, optin_perc, e, r )))
                        g3 = WGraph(path_g3)

                        for ego_metr in self.ego_metrics:
                            # ego_metric_pred_1 = egocentric_metrics.calculate(g1, ego_metr)
                            # ego_metric_pred_2 = egocentric_metrics.calculate(g2, ego_metr)
                            # ego_metric_pred_3 = egocentric_metrics.calculate(g3, ego_metr)
                        
                            graph_list = np.array([
                                                    g, 
                                                    g1, 
                                                    g2, 
                                                    g3
                                                ])
                            max_k = max(self.ks)

                            all_paths = egocentric_metrics.strong_shortest_paths_random(graph_list, max_k, self.num_sample_nodes, self.threshold)
                            ego_metrics_true[ego_metr] = all_paths[0]
                            ego_metric_pred_1 = all_paths[1] 
                            ego_metric_pred_2 = all_paths[2]
                            ego_metric_pred_3 = all_paths[3]

                            for k in self.ks:

                                for error_metr in self.error_met: 
                                    if error_metr == 'jaccard_shortest_paths_random':
                                        error_1 = error_metrics.jaccard_shortest_paths_random( ego_metrics_true[ego_metr], ego_metric_pred_1, k, self.num_sample_nodes)                   
                                        errors_list_1[ego_metr][error_metr][k].append(error_1)
                                        # utils.log_msg('g1 global %s %s = %s' % ( error_metr, ego_metr, error_1 ) )

                                        error_2 = error_metrics.jaccard_shortest_paths_random( ego_metrics_true[ego_metr], ego_metric_pred_2, k, self.num_sample_nodes)                   
                                        errors_list_2[ego_metr][error_metr][k].append(error_2)
                                        # utils.log_msg('g2 global ds %s %s = %s' % ( error_metr, ego_metr, error_2 ) )

                                        error_3 = error_metrics.jaccard_shortest_paths_random( ego_metrics_true[ego_metr], ego_metric_pred_3, k, self.num_sample_nodes)                   
                                        errors_list_3[ego_metr][error_metr][k].append(error_3)
                                        # # utils.log_msg('g3 local %s %s = %s' % ( error_metr, ego_metr, error_3 ) )

                                    else: 
                                        error_1 = error_metrics.mre_shortest_paths_random( ego_metrics_true[ego_metr], ego_metric_pred_1, k, self.num_sample_nodes)                   
                                        errors_list_1[ego_metr][error_metr][k].append(error_1)
                                        # utils.log_msg('g1 global %s %s = %s' % ( error_metr, ego_metr, error_1 ) )

                                        error_2 = error_metrics.mre_shortest_paths_random( ego_metrics_true[ego_metr], ego_metric_pred_2, k, self.num_sample_nodes)                   
                                        errors_list_2[ego_metr][error_metr][k].append(error_2)
                                        # utils.log_msg('g2 global ds %s %s = %s' % ( error_metr, ego_metr, error_2 ) )

                                        error_3 = error_metrics.mre_shortest_paths_random( ego_metrics_true[ego_metr], ego_metric_pred_3, k, self.num_sample_nodes)                   
                                        errors_list_3[ego_metr][error_metr][k].append(error_3)
                                        # # utils.log_msg('g3 local %s %s = %s' % ( error_metr, ego_metr, error_3 ) )


                    for ego_metr in self.ego_metrics:
                        for error_metr in self.error_met:
                            for k in self.ks:
                                ego_metric_mean_1 = np.mean( errors_list_1[ego_metr][error_metr][k])
                                errors_1[ego_metr][error_metr].append(ego_metric_mean_1)

                                ego_metric_mean_2 = np.mean( errors_list_2[ego_metr][error_metr][k] )
                                errors_2[ego_metr][error_metr].append(ego_metric_mean_2)  

                                ego_metric_mean_3 = np.mean( errors_list_3[ego_metr][error_metr][k] ) 
                                errors_3[ego_metr][error_metr].append(ego_metric_mean_3) 

                    legends = [
                                'global', 
                                'local',
                                'high-pass-filter '
                            ] 
                    
                    for ego_metr in self.ego_metrics:
                        for error_metr in self.error_met: 

                            y = []
                            y.append(errors_1[ego_metr][error_metr])
                            y.append(errors_2[ego_metr][error_metr])
                            y.append(errors_3[ego_metr][error_metr])
                            # y.append(errors_3[ego_metr][error_metr])
                            path_result = "./data/%s/results/result_%s_%s_%s_%s_e%s_t%s.png" % ( dataset, optin_method, optin_perc, ego_metr, error_metr, e, self.threshold) 
                            graphics.line_plot2(np.array(self.ks), np.array(y), xlabel='k', ylabel= error_metr, ylog=False, line_legends=legends, path=path_result)                                
                            # path_result2 = "./data/%s/results/logscale_result_%s_%s_%s_%s.png" % ( dataset, optin_method, optin_perc, ego_metr, error_metr) 
                            # graphics.line_plot2(np.array(self.ks), np.array(y), xlabel='$\epsilon$', ylabel= error_metr, ylog=True, line_legends=legends, path=path_result2)                                


if __name__ == "__main__":
    datasets_names = [
                          'copenhagen-interaction',
                          'high-school-contacts',
                        #   'reality-call',
                        #   'contacts-dublin',
                        #   'digg-reply', 
                        #   'enron',
                        #   'wiki-talk', 
                        #  'dblp'
                      ]

    optins_methods = ['affinity']
    optins_perc = [.0]

    ks = [ 5, 10, 20, 50, 100 ]
    e = 1

    # PRECISION AND RECALL

    error_met = [
                    'jaccard_shortest_paths_random',
                    'mre_shortest_paths_random'
                ]

    ego_metrics = [ 
                       'strong_shortest_paths_random'  
                    ]

    runs = 4
    num_sample_nodes = 10  # number of random nodes selected 

    threshold = 5
    
    exp = ResultsDPWeightedNets(datasets_names, optins_methods, optins_perc, e, ks, error_met, ego_metrics, num_sample_nodes, threshold, runs)
    exp.run()