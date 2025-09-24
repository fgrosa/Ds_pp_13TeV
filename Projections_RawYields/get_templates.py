import argparse
import os
import pandas as pd
import ROOT


def make_templates(infile_name, out_file):
    
    with ROOT.TFile.Open(infile_name) as infile:
        hist_templ = []

        for key in infile.GetListOfKeys():
            if "h_mass" in key.GetName():
                hist_name = key.GetName()
                hist = infile.Get(hist_name)
                hist.SetDirectory(0)
                hist_templ.append(hist.Clone(hist_name.replace("hMass", "hDplusTemplate")))
                hist_templ[-1].SetDirectory(0)
                hist_templ[-1].Smooth(1000)

    output = ROOT.TFile(out_file, "recreate")
    for hist in hist_templ:
        hist.Write()
    output.Close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get D+ mass templates from MC")
    parser.add_argument("input", type=str, help="Input ROOT file with histograms")
    parser.add_argument("output", type=str, help="Output ROOT file to save templates")
    args = parser.parse_args()

    make_templates(args.input, args.output)