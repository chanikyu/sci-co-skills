"""runners.py — metabolomics raw-processing runners (mzML/.CDF -> feature table). External tools run
inside the `scico-metabolomics` conda env via `conda run`.

UNVERIFIED in-session (needs real mzML + tool installs). Standard commands; the caller picks ppm /
peak-width from the data. GC-MS deconvolution has no production Python -> wraps eRah (R) / MS-DIAL.
"""
import os
import glob
import datetime
import subprocess
import pandas as pd

ENV = "scico-metabolomics"


def _tee(cmd, logf, shell=False):
    with open(logf, "a") as fh:
        fh.write(f"[{datetime.datetime.now():%H:%M:%S}] $ {cmd if shell else ' '.join(cmd)}\n")
    p = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
    with open(logf, "a") as fh:
        fh.write(p.stdout + p.stderr + f"[exit {p.returncode}]\n")
    if p.returncode != 0:
        raise RuntimeError(f"command failed (see {logf}): {cmd}")


def _cr(*args):
    return ["conda", "run", "-n", ENV, *args]


def msconvert(raw_dir, out_dir, log):
    """Vendor .raw/.d/.wiff -> centroided mzML (ProteoWizard). Skip if inputs are already mzML."""
    os.makedirs(out_dir, exist_ok=True)
    _tee(_cr("bash", "-c",
             f"msconvert {raw_dir}/* --mzML --filter 'peakPicking vendor msLevel=1-' -o {out_dir}"), log)
    return out_dir


def asari_lc(mzml_dir, out_dir, mode, log):
    """LC-MS feature detection + alignment + grouping (asari, pure Python). mode = pos | neg."""
    _tee(_cr("asari", "process", "--mode", mode, "--input", mzml_dir, "--output", out_dir), log)
    hit = glob.glob(os.path.join(out_dir, "**", "*eature*able*.tsv"), recursive=True)
    if not hit:
        raise RuntimeError(f"asari produced no feature table under {out_dir}")
    return hit[0]


def xcms_lc(mzml_dir, out_dir, ppm, peakwidth, log):
    """LC-MS via XCMS + CAMERA (r-xcms) — publication-grade. Runs an Rscript that writes feature_table.csv."""
    os.makedirs(out_dir, exist_ok=True)
    r = os.path.join(out_dir, "_xcms.R")
    with open(r, "w") as fh:
        fh.write(
            "library(xcms)\n"
            f"fs <- list.files('{mzml_dir}', pattern='mzML$', full.names=TRUE)\n"
            "d <- readMSData(fs, mode='onDisk')\n"
            f"d <- findChromPeaks(d, CentWaveParam(ppm={ppm}, peakwidth=c({peakwidth[0]},{peakwidth[1]})))\n"
            "d <- adjustRtime(d, ObiwarpParam())\n"
            "d <- groupChromPeaks(d, PeakDensityParam(sampleGroups=rep(1, length(fs))))\n"
            "d <- fillChromPeaks(d)\n"
            f"write.csv(featureValues(d, value='into'), file='{out_dir}/feature_table.csv')\n")
    _tee(_cr("Rscript", r), log)
    return os.path.join(out_dir, "feature_table.csv")


def erah_gc(cdf_dir, out_dir, log):
    """GC-MS deconvolution + alignment (eRah, R). No production-grade Python deconvolution exists."""
    os.makedirs(out_dir, exist_ok=True)
    r = os.path.join(out_dir, "_erah.R")
    with open(r, "w") as fh:
        fh.write(
            "library(erah)\n"
            f"ex <- newExp(instrumental=createInstrumentalTable(list.files('{cdf_dir}', full.names=TRUE)))\n"
            "ex <- deconvolveComp(ex, setDecPar(min.peak.width=1))\n"
            "ex <- alignComp(ex, alParameters=setAlPar(min.spectra.cor=0.9))\n"
            f"write.csv(alignList(ex), file='{out_dir}/feature_table.csv')\n")
    _tee(_cr("Rscript", r), log)
    return os.path.join(out_dir, "feature_table.csv")


def detect_features(input_dir, out_dir, platform="lc", engine="asari", mode="pos",
                    ppm=10, peakwidth=(5, 30), log=None):
    """Dispatch raw -> feature table by platform/engine. Returns the feature-table path."""
    os.makedirs(out_dir, exist_ok=True)
    log = log or os.path.join(out_dir, "detect.log")
    if platform == "gc":
        return erah_gc(input_dir, out_dir, log)
    if engine == "xcms":
        return xcms_lc(input_dir, out_dir, ppm, peakwidth, log)
    return asari_lc(input_dir, out_dir, mode, log)
