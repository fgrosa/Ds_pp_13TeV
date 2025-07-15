'''
python standalone script to apply trained models to data using the hipe4ml package
run: python MLApplication.py cfgFileNameML.yml
Use the same config file as that used in the classification
'''
import os
import sys
import argparse
import yaml
import numpy as np

from hipe4ml.model_handler import ModelHandler
from hipe4ml.tree_handler import TreeHandler

def swap_prongs(df):
    df['fNSigTpcTofKaExpKa0'] = df.apply(
        lambda row: row['fNSigTpcTofKa2'] if row['fIsCandidateSwapped'] else row['fNSigTpcTofKa0'],
        axis=1
    )
    df['fNSigTpcTofPiExpPi2'] = df.apply(
        lambda row: row['fNSigTpcTofPi0'] if row['fIsCandidateSwapped'] else row['fNSigTpcTofPi2'],
        axis=1
    )
    df['fNSigTofKaExpKa0'] = df.apply(
        lambda row: row['fNSigTofKa2'] if row['fIsCandidateSwapped'] else row['fNSigTofKa0'],
        axis=1
    )
    df['fNSigTofPiExpPi2'] = df.apply(
        lambda row: row['fNSigTofPi0'] if row['fIsCandidateSwapped'] else row['fNSigTofPi2'],
        axis=1
    )
    df['fNSigTpcKaExpKa0'] = df.apply(
        lambda row: row['fNSigTpcKa2'] if row['fIsCandidateSwapped'] else row['fNSigTpcKa0'],
        axis=1
    )
    df['fNSigTpcPiExpPi2'] = df.apply(
        lambda row: row['fNSigTpcPi0'] if row['fIsCandidateSwapped'] else row['fNSigTpcPi2'],
        axis=1
    )

def swap_prongs_others(df):
    df['fImpactParameter0Exp0'] = df.apply(
        lambda row: row['fImpactParameter2'] if row['fIsCandidateSwapped'] else row['fImpactParameter0'],
        axis=1
    )
    df['fImpactParameter2Exp2'] = df.apply(
        lambda row: row['fImpactParameter0'] if row['fIsCandidateSwapped'] else row['fImpactParameter2'],
        axis=1
    )

def main(): #pylint: disable=too-many-statements, too-many-branches
    # read config file
    parser = argparse.ArgumentParser(description='Arguments to pass')
    parser.add_argument('cfgFileName', metavar='text', default='cfgFileNameML.yml', help='config file name for ml')
    args = parser.parse_args()

    print('Loading analysis configuration: ...', end='\r')
    with open(args.cfgFileName, 'r') as ymlCfgFile:
        inputCfg = yaml.load(ymlCfgFile, yaml.FullLoader)
    print('Loading analysis configuration: Done!')

    PtBins = [[a, b] for a, b in zip(inputCfg['pt_ranges']['min'], inputCfg['pt_ranges']['max'])]
    OutputLabels = [inputCfg['output']['out_labels']['Bkg'],
                    inputCfg['output']['out_labels']['Prompt']]
    if inputCfg['output']['out_labels']['FD'] is not None:
        OutputLabels.append(inputCfg['output']['out_labels']['FD'])
    ColumnsToSave = inputCfg['appl']['column_to_save_list']
    ModelList = inputCfg['ml']['saved_models']
    ModelHandls = []
    for iBin in range(len(PtBins)):
        ModelPath = ModelList[iBin]
        if not isinstance(ModelPath, str):
            print('\033[91mERROR: path to model not correctly defined!\033[0m')
            sys.exit()
        ModelPath = os.path.expanduser(ModelPath)
        print(f'Loaded saved model: {ModelPath}')
        ModelHandl = ModelHandler()
        ModelHandl.load_model_handler(ModelPath)
        ModelHandls.append(ModelHandl)

    for inputFile, outName in zip(inputCfg['standalone_appl']['inputs'], inputCfg['standalone_appl']['output_names']):
        print(f'Loading and preparing data file {inputFile}: ...', end='\r')
        DataHandler = TreeHandler(inputFile)
        if inputCfg["data_prep"]["filt_bkg_mass"]:
                DataHandler = DataHandler.get_subset(inputCfg['data_prep']['filt_bkg_mass'], frac=1.,
                                            rndm_state=inputCfg['data_prep']['seed_split'])
        if inputCfg["data_prep"]["test_fraction"]:
                DataHandler = DataHandler.get_subset(frac=inputCfg["data_prep"]["test_fraction"],
                                            rndm_state=inputCfg['data_prep']['seed_split'])

        print(DataHandler.get_n_cand())
        DataHandler.slice_data_frame('fPt', PtBins, True)
        print(f'Loading and preparing data files {inputFile}: Done!')

        print('Applying ML model to dataframes: ...', end='\r')
        for iBin, PtBin in enumerate(PtBins):
            OutPutDirPt = os.path.join(os.path.expanduser(inputCfg['standalone_appl']['output_dir']),
                                       f'pt{PtBin[0]}_{PtBin[1]}')
            if os.path.isdir(OutPutDirPt):
                print((f'\033[93mWARNING: Output directory \'{OutPutDirPt}\' already exists,'
                       ' overwrites possibly ongoing!\033[0m'))
            else:
                os.makedirs(OutPutDirPt)
            DataDfPtSel = DataHandler.get_slice(iBin)
            swap_prongs(DataDfPtSel)
            #swap_prongs_others(DataDfPtSel)
            yPred = ModelHandls[iBin].predict(DataDfPtSel, inputCfg['ml']['raw_output'])
            ColumnsToSaveFinal = ColumnsToSave
            if not isinstance(ColumnsToSaveFinal, list):
                print('\033[91mERROR: column_to_save_list must be defined!\033[0m')
                sys.exit()
            if 'inv_mass' not in ColumnsToSaveFinal:
                print('\033[93mWARNING: inv_mass is not going to be saved in the output dataframe!\033[0m')
            if 'pt_cand' not in ColumnsToSaveFinal:
                print('\033[93mWARNING: pt_cand is not going to be saved in the output dataframe!\033[0m')
            if 'pt_B' in ColumnsToSaveFinal and 'pt_B' not in DataDfPtSel.columns:
                ColumnsToSaveFinal.remove('pt_B') # only in MC
            DataDfPtSel = DataDfPtSel.loc[:, ColumnsToSaveFinal]
            if ModelHandls[iBin].get_n_classes() < 3:
                DataDfPtSel['ML_output'] = yPred
            else:
                for Pred, Lab in enumerate(OutputLabels):
                    DataDfPtSel[f'ML_output_{Lab}'] = yPred[:, Pred]
            DataDfPtSel.to_parquet(f'{OutPutDirPt}/{outName}_pT_{PtBin[0]}_{PtBin[1]}_ModelApplied.parquet.gzip')
            del DataDfPtSel
        print('Applying ML model to dataframes: Done!')

main()
