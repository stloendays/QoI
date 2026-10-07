"""Numbers quoted in the text for NC Fig. 4 (KCN), derived from data/kcn_law.{json,npz}.

    D:/Tools/pur_bridge_env/Scripts/python.exe kcn_stats.py   -> KCN_STATS.json
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, "data", "kcn_law.json")))
Z = np.load(os.path.join(HERE, "data", "kcn_law.npz"))
g = J["cert"]["1e-06"]
edges = Z["bin_edges"]
qc = 0.5 * (edges[1:] + edges[:-1])
modes = Z["modes"]
amp = np.sqrt(Z["ref_power"] / np.maximum(modes, 1)) / J["ptp"]
law_step = g["law"]["alpha_rel"] * qc ** 2
cross = float(qc[np.argmax((amp < law_step) & (modes > 0))])      # first bin whose rms amplitude is below the step
out = {"tau": 1e-6, "cr": {k: v["cr"] for k, v in g.items()}, "bytes": {k: v["bytes"] for k, v in g.items()},
       "law_over_uniform": g["law"]["cr"] / g["uniform"]["cr"], "trunc_q_cut": g["trunc"]["q_cut"],
       "q_rms_amplitude_below_law_step": cross}
dens = {}
for k in ("law", "uniform", "trunc", "zfp", "sz3", "sperr"):
    w = Z["werr_" + k]
    d = (w / np.maximum(modes, 1)) / (w.sum() / modes.sum())
    dens[k] = {"lowest_bin": float(d[0]), "max_over_populated_q<=0.25": float(d[qc <= 0.25].max()),
               "min_over_populated_q<=0.25": float(d[qc <= 0.25].min())}
out["hartree_error_per_mode_relative_to_mean"] = dens
sb = Z["shell_bytes_law"]
out["law_bytes_fraction_q<=0.3125"] = float(sb[:10].sum() / sb.sum())
out["law_bytes_percent_q<=0.3125"] = round(100 * out["law_bytes_fraction_q<=0.3125"], 2)
json.dump(out, open(os.path.join(HERE, "KCN_STATS.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
