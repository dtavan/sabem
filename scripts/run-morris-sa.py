"""

"""

import sys
import os
import argparse
from builtins import input

import pandas as pd
import matplotlib.pyplot as plt

from pybps import BPSProject

from SALib.sample import morris as ms
from SALib.analyze import morris as ma
from SALib.plotting import morris as mp
from SALib.util import read_param_file
from SALib.plotting.morris import horizontal_bar_plot, covariance_plot


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run Morris Sensitivity Analysis, by default on all model outputs.')

    parser.add_argument('model_dir', help='path to folder containing model')
    parser.add_argument('param_file', help='name of parameter range file')
    parser.add_argument('-Y', dest='model_output', help='name of model output to be analyzed')
    parser.add_argument('-o', dest='out_attr', help='attribute of model output: Total, Max or Both (default: Both)', default='Both')
    parser.add_argument('-n', dest='r', default=10, type=int, help='Number of elementary effects or trajectories (default: 10)')
    parser.add_argument('-l', dest='p', default=6, type=int, help='Number of levels in the OAT sampling (default: 6)')
    parser.add_argument('-g', dest='delta', default=2, type=int, help='Grid jump size in the OAT sampling (default: 2)')
    parser.add_argument('-c', dest='ncore', default='max', help='Number of local cores to use for parallel simulations (default: max)')

    args = parser.parse_args()

    model_dir = os.path.abspath(args.model_dir)
    param_file = os.path.join(model_dir, args.param_file)
    model_output = args.model_output
    out_attr = args.out_attr
    r = args.r # Number of elementary effects or trajectories; Typical values: between 5 and 10
    p = args.p # Number of levels in the OAT sampling; Typical value: 4 or 6
    delta = args.delta # "grid jump" (minimum jump from one level to the other); Typical value: 1 or 2
    ncore = args.ncore
	
    # Load parameter range file
    problem = read_param_file(os.path.join(model_dir, param_file))

    # Morris OAT sampling
    param_values = ms.sample(problem, N=r, num_levels=p, grid_jump=delta, optimal_trajectories=None)

    # Save samples
    samples = pd.DataFrame(param_values, columns=problem['names'])
    samples.to_csv(os.path.join(model_dir, "Parameter_Samples.csv"), index=False)

    # Prompt user for confirmation before launching simulations
    print('The script will launch {} simulation jobs, which can take a significant time to run. Do you want to continue? (y/n)'.format(samples.shape[0]))
    cont = input()
    cont = cont[:1].lower()
    if cont not in ['y','n']:
        print('Error: expected y or n')
        sys.exit(1)
    if cont != 'y':
        print('Exiting program...')
        sys.exit(1)

    # Create new instance of BPSProject class to hold all of the info
    # about simulation project
    batch = BPSProject(model_dir)

    # Add simulation jobs to BPSProject instance
    batch.add_jobs()

    # Run simulation jobs
    batch.run(ncore)

    # Extracting results
    #batch.jobs2df()
    #batch.runsum2df()
    batch.results2df()
	
    # Evaluate all model output attributes if no attribute was specified
    if out_attr == 'Both':
        out_attr_list = ['Total', 'Maximum Value']
    elif out_attr == 'Max':
        out_attr_list = ['Maximum Value']
    else:
        out_attr_list = ['Total']
	
	# Perform analysis for each attribute in list
    for o_attr in out_attr_list:
        results = batch.results_df[batch.results_df.Month == o_attr].drop('Month', axis=1).set_index('JobID')

        # Evaluate all model outputs if no model output was specified
        if model_output is not None:
            model_output_list = [model_output]
        else:
            model_output_list = list(results.columns)

        # Perform Morris Analysis on each model output in list
        for m_out in model_output_list:
            # Specify which column of the output file to analyze (zero-indexed)
            Si = ma.analyze(problem, param_values, results[m_out], conf_level=0.95,
                            print_to_console=False,
                            num_levels=p, grid_jump=delta, num_resamples=1000)
            # Returns a dictionary with keys 'mu', 'mu_star', 'sigma', and 'mu_star_conf'
            # e.g. Si['mu_star'] contains the mu* value for each parameter, in the
            # same order as the parameter file

            # Plot results and save to file
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,6))
            horizontal_bar_plot(ax1, Si,{}, sortby='mu_star', unit=r"kWh/year")
            covariance_plot(ax2, Si, {}, unit=r"kWh/year")
            plt.suptitle('Results of Morris Analysis on {} {}'.format(m_out, 'Max' if 'Max' in o_attr else o_attr))
            plt.subplots_adjust(left=0.15)
            plt.savefig(os.path.join(model_dir, 'morris_plot_{}_{}.png'.format(m_out, 'Max' if 'Max' in o_attr else o_attr)), dpi=300)
