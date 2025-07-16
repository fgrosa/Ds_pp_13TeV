'''
python script to create yaml files with set of cuts for cut-variation studies
'''

import os
import copy
import yaml
import argparse
from itertools import product

def make_cuts_ml(config):
    var_key = config['var_key']
    var_tag = config['var_tag']
    step_variation = config['step_variation']
    num_step_pos = config['num_step_pos']
    num_step_pos_half_step = config['num_step_pos_half_step']
    num_step_neg = config['num_step_neg']
    num_step_neg_half_step = config['num_step_neg_half_step']
    edge_to_vary = config['edge_to_vary']

    in_dir = config['in_dir']
    cut_file_central = config['cut_file_central']
    out_dir = config['out_dir']
    out_file_tag = config['out_file_tag']

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with open(os.path.join(in_dir, cut_file_central), 'r') as cut_file_yml:
        cutset = yaml.load(cut_file_yml, yaml.FullLoader)

    neg_steps = [-i for i in range(1, num_step_neg + 1)]
    neg_steps += [-num_step_neg - i / 2 for i in range(1, num_step_neg_half_step + 1)]
    neg_steps = neg_steps[::-1]
    pos_steps = list(range(0, num_step_pos + 1))
    pos_steps += [num_step_pos + i / 2 for i in range(1, num_step_pos_half_step + 1)]
    steps = neg_steps + pos_steps

    n_combinations = len(var_key)

    for prod_steps in product(steps, repeat=n_combinations):
        print(prod_steps)
        cutset_mod = copy.deepcopy(cutset)
        file_tag = ""
        for i, step in enumerate(prod_steps):
            modified_list = []
            cuts = cutset_mod[var_key[i]]
            for min_val, max_val, pt_min in zip(cuts['min'], cuts['max'], cutset_mod['pt']['min']):
                delta = step * step_variation[i][f'{pt_min:.1f}']
                if edge_to_vary[i] == 'min':
                    new_value = min_val + delta
                    if new_value < 0. or new_value >= max_val:
                        print("Warning: cut is negative or min value is greater than max value")
                        new_value = min_val
                else:
                    new_value = max_val + delta
                    if new_value > 1. or new_value <= min_val:
                        print("Warning: cut is greater than 1 or max value is less than min value")
                        new_value = max_val
                modified_list.append(new_value)
            cuts[edge_to_vary[i]] = modified_list

            step_name = 'pos' if step >= 0 else 'neg'
            step_idx = pos_steps.index(step) if step >= 0 else neg_steps.index(step)
            name = f'_{var_tag[i]}_{step_name}{str(int(step_idx)).zfill(2)}'
            file_tag += name

        cut_file_mod = f'{out_file_tag}{file_tag}.yml'
        with open(os.path.join(out_dir, cut_file_mod), 'w') as outfile_mod:
            yaml.dump(cutset_mod, outfile_mod, default_flow_style=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate cut-variation YAML files.')
    parser.add_argument('--config', '-c', type=str, required=True, help='Path to YAML configuration file')
    args = parser.parse_args()

    with open(args.config, 'r') as stream:
        config = yaml.safe_load(stream)

    make_cuts_ml(config)
