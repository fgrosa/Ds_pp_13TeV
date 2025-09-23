"""
Script to perform D0 signal extraction as a function of BDT
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from flarefly.data_handler import DataHandler
from flarefly.fitter import F2MassFitter
import ROOT


def perform_fit(file_name, histo_name, fitter_name, sgn_funcs, bkg_funcs,
                mass_min, mass_max):
    """
    Method for fit
    """
    labels_signal_pdf = [r"$\mathrm{D_{s}}^{+}$", r"$\mathrm{D}^{+}$"]
    labels_bkg_pdf = ["Comb. bkg."]

    data_hdl = DataHandler(file_name, histoname=histo_name, limits=[mass_min, mass_max])

    fitter = F2MassFitter(data_hdl,
                          name_signal_pdf=sgn_funcs,
                          name_background_pdf=bkg_funcs,
                          name=fitter_name, tol=0.1,
                          label_signal_pdf=labels_signal_pdf,
                          label_bkg_pdf=labels_bkg_pdf)
    fitter.set_particle_mass(0, pdg_id=431, limits=[1.95, 1.98])
    fitter.set_particle_mass(1, pdg_id=411, limits=[1.85, 1.88])
    fitter.set_signal_initpar(0, "sigma", 0.005, limits=[0.0001, 0.06])
    fitter.set_signal_initpar(1, "sigma", 0.005, limits=[0.0001, 0.06])
    fitter.set_signal_initpar(0, "frac", 0.1, limits=[0., 0.5])
    fitter.set_signal_initpar(1, "frac", 0.1, limits=[0., 0.5])
    fitter.set_background_initpar(0, "c0", 0.4)
    fitter.set_background_initpar(0, "c1", -0.2)
    fitter.set_background_initpar(0, "c2", -0.01)
    fitter.set_background_initpar(0, "c3", 0.01)
    fitter.set_background_initpar(0, "lam", -1.)

    fitter.mass_zfit()

    return fitter

# main function to perform fits
def optimise_signif(infile_name, force_project, project_only, bdt_min, bdt_max, bdt_step,
                    pt_min, pt_max, cent_min, cent_max, outputdir):
    """
    Method for fitting
    """

    infile_name_histos = os.path.join(
        outputdir, f"hist_mass_pt{pt_min:.0f}_{pt_max:.0f}_cent{cent_min:.0f}_{cent_max:.0f}.root")
    if force_project or not os.path.isfile(infile_name_histos):
        project(infile_name, bdt_min, bdt_max, bdt_step, pt_min, pt_max, cent_min, cent_max, outputdir)
    else:
        print("WARNING: using already available projection")

    if project_only:
        sys.exit()

    cuts_to_test = np.arange(bdt_min, bdt_max + bdt_step, bdt_step)
    ncuts = len(cuts_to_test)

    # we first fit the high significance cases
    outfile_name = os.path.join(
        outputdir, f"significance_scan_d0_{pt_min:.0f}_{pt_max:.0f}_cent{cent_min:.0f}_{cent_max:.0f}.root")
    outfile = ROOT.TFile(outfile_name, "recreate")
    outfile.Close()

    part_names = ["ds", "dplus"]
    part_colors = [ROOT.kRed+1, ROOT.kAzure+4]
    rawyields = [[], []]
    sigmas = [[], []]
    means = [[], []]
    significances = [[], []]
    sobs = [[], []]

    max_rawy, max_signif, max_soverb = 0., 0., 0.
    for icut, cut in enumerate(cuts_to_test):
        fitter_data = perform_fit(infile_name_histos,
                                  f"hist_mass_bdt{cut:.3f}",
                                  f"ds_bdt{cut:.3f}",
                                  ["gaussian", "gaussian"],
                                  ["chebpol2"],
                                  1.75,
                                  2.15)

        if fitter_data.get_fit_result.converged:
            for isig in range(2):
                rawyield = fitter_data.get_raw_yield(isig)
                max_rawy = max(max_rawy, rawyield[0])
                sigma = fitter_data.get_signal_parameter(isig, "sigma")
                mean = fitter_data.get_mass(isig)
                significance = fitter_data.get_significance(isig, nsigma=3)
                max_signif = max(max_signif, significance[0])
                soverb = fitter_data.get_signal_over_background(isig, nsigma=3)
                max_soverb = max(max_soverb, soverb[0])
                rawyields[isig].append(rawyield)
                sigmas[isig].append(sigma)
                means[isig].append(mean)
                significances[isig].append(significance)
                sobs[isig].append(soverb)

            fitter_data.dump_to_root(outfile_name,
                                     option="update",
                                     suffix=f"_bdt{cut:.3f}")

            xaxis = r"$M(\mathrm{KK\pi})$ (GeV/$c^{2}$)"
            fig, _ = fitter_data.plot_mass_fit(style="ATLAS", figsize=(8, 8), axis_title=xaxis)
            figres = fitter_data.plot_raw_residuals(figsize=(8, 8), style="ATLAS", axis_title=xaxis)

            fig.savefig(
                os.path.join(outputdir, f"massfit_pt{pt_min:.0f}_{pt_max:.0f}_bdt{cut:.3f}.pdf")
            )
            figres.savefig(
                os.path.join(outputdir, f"massfitres_pt{pt_min:.0f}_{pt_max:.0f}_bdt{cut:.3f}.pdf")
            )

    cuts = cuts_to_test
    xlim = (bdt_min - 0.5*bdt_step, bdt_max + 0.5*bdt_step)

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    for ax in axes:
        ax.set_xlim(xlim)

    labels = [r"$\mathrm{D_s^+}$", r"$\mathrm{D^+}$"]
    colors = ["red", "C0"]

    # Raw yield
    for isig in range(2):
        axes[0].errorbar(cuts, [p[0] for p in rawyields[isig]],
                        yerr=[p[1] for p in rawyields[isig]],
                        fmt="o-", color=colors[isig], label=labels[isig])
    axes[0].set_ylabel("Raw yield")
    axes[0].set_xlabel("BDT bkg <")
    axes[0].xaxis.set_label_coords(0.8, -0.1)
    axes[0].legend()

    # Sigma
    for isig in range(2):
        axes[1].errorbar(cuts, [p[0] for p in sigmas[isig]],
                        yerr=[p[1] for p in sigmas[isig]],
                        fmt="o-", color=colors[isig])
    axes[1].set_ylabel(r"$\sigma$ (GeV/$c^2$)")
    axes[1].set_xlabel("BDT bkg <")
    axes[1].xaxis.set_label_coords(0.8, -0.1)

    # Mean
    for isig in range(2):
        axes[2].errorbar(cuts, [p[0] for p in means[isig]],
                        yerr=[p[1] for p in means[isig]],
                        fmt="o-", color=colors[isig])
    axes[2].set_ylabel(r"$\mu$ (GeV/$c^2$)")
    axes[2].set_xlabel("BDT bkg <")
    axes[2].xaxis.set_label_coords(0.8, -0.1)

    # Significance
    for isig in range(2):
        axes[3].errorbar(cuts, [p[0] for p in significances[isig]],
                        yerr=[p[1] for p in significances[isig]],
                        fmt="o-", color=colors[isig])
    axes[3].set_ylabel("Significance (3σ)")
    axes[3].set_xlabel("BDT bkg <")
    axes[3].xaxis.set_label_coords(0.8, -0.1)

    # S/B
    for isig in range(2):
        axes[4].errorbar(cuts, [p[0] for p in sobs[isig]],
                        yerr=[p[1] for p in sobs[isig]],
                        fmt="o-", color=colors[isig])
    axes[4].set_ylabel("S/B (3σ)")
    axes[4].set_xlabel("BDT bkg <")
    axes[4].xaxis.set_label_coords(0.8, -0.1)

    # Legend
    axes[5].axis("off")

    # Invisible lines for the legend
    line1 = axes[5].plot([], [], 'o-', color=colors[0], label=labels[0])[0]
    line2 = axes[5].plot([], [], 'o-', color=colors[1], label=labels[1])[0]

    textstr = rf"${pt_min:.0f} < p_\mathrm{{T}} < {pt_max:.0f}~\mathrm{{GeV/}}c$" f"\nCentrality: {cent_min:.0f}-{cent_max:.0f} %"
    axes[5].text(0.5, 0.9, textstr, transform=axes[5].transAxes, fontsize=20,
                 verticalalignment='top', horizontalalignment='center')
    axes[5].legend(handles=[line1, line2], loc="center", fontsize=24)

    plt.tight_layout()
    plt.savefig(os.path.join(outputdir, f"significance_scan_pt{pt_min:.0f}_{pt_max:.0f}_cent{cent_min:.0f}_{cent_max:.0f}.pdf"))
    plt.close()


# function to project the sparse
def project(infile_name, bdt_min, bdt_max, bdt_step, pt_min, pt_max, cent_min, cent_max, outputdir):
    """
    Method for sparse projection
    """

    infile = ROOT.TFile.Open(infile_name)
    sparse = infile.Get("hf-task-ds/Data/hSparseMass")
    infile.Close()

    outfile = ROOT.TFile(
        os.path.join(outputdir, f"hist_mass_pt{pt_min:.0f}_{pt_max:.0f}_cent{cent_min:.0f}_{cent_max:.0f}.root"), "recreate")
    pt_bin_min = sparse.GetAxis(1).FindBin(pt_min*1.001)
    pt_bin_max = sparse.GetAxis(1).FindBin(pt_max*0.999)
    cent_bin_min = sparse.GetAxis(2).FindBin(cent_min*1.001)
    cent_bin_max = sparse.GetAxis(2).FindBin(cent_max*0.999)
    sparse.GetAxis(1).SetRange(pt_bin_min, pt_bin_max)
    sparse.GetAxis(2).SetRange(cent_bin_min, cent_bin_max)
    histos_pt = []
    for icut, cut in enumerate(np.arange(bdt_min, bdt_max+bdt_step, bdt_step)):
        bdt_bkg_bin_max = sparse.GetAxis(3).FindBin(cut*0.999)
        sparse.GetAxis(3).SetRange(1, bdt_bkg_bin_max)
        histos_pt.append(sparse.Projection(0))
        histos_pt[icut].SetName(f"hist_mass_bdt{cut:.3f}")
        outfile.cd()
        histos_pt[icut].Write()
    outfile.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("--infile", "-i", metavar="text",
                        default="AnalysisResults.root", help="input file")
    parser.add_argument("--force_project", "-f", action="store_true",
                        default=False, help="force projection of THnSparse")
    parser.add_argument("--project_only", "-p", action="store_true",
                        default=False, help="do projection only, no fit")
    parser.add_argument("--bdt_min", "-mi", type=float,
                        default=0.002, help="minimum BDT cut to test")
    parser.add_argument("--bdt_max", "-ma", type=float,
                        default=0.02, help="maximum BDT cut to test")
    parser.add_argument("--bdt_step", "-s", type=float,
                        default=0.002, help="step between one BDT cut and another")
    parser.add_argument("--pt_min", "-ptmi", type=float,
                        default=0., help="minimum pT bin")
    parser.add_argument("--pt_max", "-ptma", type=float,
                        default=1., help="maximum pT bin")
    parser.add_argument("--cent_min", "-cmi", type=float,
                        default=0., help="minimum centrality bin")
    parser.add_argument("--cent_max", "-cma", type=float,
                        default=1., help="maximum centrality bin")
    parser.add_argument("--output_dir", "-o", metavar="text",
                        default=".", help="output directory")
    args = parser.parse_args()

    optimise_signif(args.infile, args.force_project, args.project_only,
                    args.bdt_min, args.bdt_max, args.bdt_step,
                    args.pt_min, args.pt_max, args.cent_min, args.cent_max,
                    args.output_dir)
