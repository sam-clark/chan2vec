import collections
import sys
import argparse
import datetime

import numpy as np

import faiss 


def read_vec_fp(vec_fp, chan_info_fp, include_s=None):
    # Get chan_int to chan_id mappings
    chan_int_id_d = {}
    for lid, line in enumerate(open(chan_info_fp)):
        chan_id, chan_int_id, chan_name, chan_ds_subs, chan_tot_subs = line.strip("\n").split("\t")
        chan_int_id_d[int(chan_int_id)] = chan_id
    # Read in vectors 
    aid_chan_d = {}
    vec_l = []
    for lid, line in enumerate(open(vec_fp)):
        if lid < 2: continue
        tpl = line.strip("\n").split(" ")
        chan_int_id = int(tpl[0])
        chan_id = chan_int_id_d[chan_int_id]
        if include_s is not None and chan_id not in include_s: continue
        aid_chan_d[len(vec_l)] = chan_id
        # Normalize vector and change type
        vec = np.array([float(x) for x in tpl[1:-1]])
        vl = np.linalg.norm(vec)
        vec = (vec / vl).astype('float32')
        vec_l.append(vec)
    embed_m = np.stack(vec_l)
    return aid_chan_d, embed_m


def score_file_faiss(vec_fp, chan_info_fp, lab_fp, score_chan_fp, out_fp, num_neighbs=5, use_gpu=False,
                     multi_lab=False, output_sims=False, weight_neighbs=False, bin_prob=False,
                     multi_lab_prob=False, regression=False):
    assert not (multi_lab and bin_prob)
    res = None if not use_gpu else faiss.StandardGpuResources()
    # Read in labels
    if multi_lab:
        chan_lab_d = {}
        for l in open(lab_fp):
            if not multi_lab_prob:
                chan_id, lab = l.strip("\n").split("\t")
                if chan_id not in chan_lab_d:
                    chan_lab_d[chan_id] = set([])
                chan_lab_d[chan_id].add(lab)
            else:
                chan_id, lab, perc = l.strip("\n").split("\t")
                if chan_id not in chan_lab_d:
                    chan_lab_d[chan_id] = {}
                chan_lab_d[chan_id][lab] = float(perc)
    else:
        chan_lab_d = dict([l.strip("\n").split("\t") for l in open(lab_fp)])
    # Read in vectors for labels
    aid_chan_d_lab, embed_m_lab = read_vec_fp(vec_fp, chan_info_fp, include_s=set(chan_lab_d.keys()))
    # Read in vectors for queries
    score_chan_s = set([l.strip() for l in open(score_chan_fp)])
    aid_chan_d_q, embed_m_q = read_vec_fp(vec_fp, chan_info_fp, include_s=score_chan_s)
    # Create index
    d = embed_m_lab.shape[1]
    if use_gpu:
        index_flat = faiss.IndexFlatIP(d)
        gpu_index_flat = faiss.index_cpu_to_gpu(res, 0, index_flat)
        gpu_index_flat.add(embed_m_lab)
        D, I = gpu_index_flat.search(embed_m_q, num_neighbs+1)
    else:
        index = faiss.IndexFlatIP(d)
        index.add(embed_m_lab)
        D, I = index.search(embed_m_q, num_neighbs+1)
    of = open(out_fp, "w")
    for i in range(len(aid_chan_d_q)):
        chan_id = aid_chan_d_q[i]
        found = 0
        neighb_lab_d = collections.defaultdict(float)
        neighb_chan_id_l = []
        for aid_neighb, cos_sim in zip(I[i], D[i]):
            neighb_chan_id = aid_chan_d_lab[aid_neighb]
            if chan_id == neighb_chan_id: continue
            neighb_chan_id_l.append(neighb_chan_id + "|" + str(cos_sim))
            weight = 1
            if weight_neighbs:
                weight = (1 / np.exp(1 - cos_sim))
            if not multi_lab:
                lab = chan_lab_d[neighb_chan_id]
                if bin_prob:
                    neighb_lab_d["pos"] += weight*float(lab)
                    neighb_lab_d["tot"] += weight
                else:
                    neighb_lab_d[lab] += weight
            else:
                if not multi_lab_prob:
                    for lab in chan_lab_d[neighb_chan_id]:
                        neighb_lab_d[lab] += weight
                else:
                    for lab, perc in chan_lab_d[neighb_chan_id].items():
                        neighb_lab_d[lab] += weight*perc    
            found += 1
            if found == num_neighbs: break
        if len(neighb_lab_d) > 0:
            info_cols_l = []
            # Top sim labs
            if not multi_lab:
                if bin_prob:
                    prob = neighb_lab_d["pos"] / neighb_lab_d["tot"]
                    info_cols_l = [str(prob)]
                else:
                    if not regression:
                        max_lab, max_c = max(neighb_lab_d.items(), key=lambda x: x[1])
                        max_perc = max_c / sum(neighb_lab_d.values())
                        info_cols_l = [max_lab, "%.3f" % max_perc]
                    else:
                        # Take the weighted average for regression
                        weight_avg = sum([float(lab)*c for lab, c in neighb_lab_d.items()]) / sum(neighb_lab_d.values())
                        info_cols_l = ["%.3f" % weight_avg]
            else:
                all_sims_str = ",".join([lab + "|" + str(lab_c/found) for lab, lab_c in neighb_lab_d.items()])
                info_cols_l = [all_sims_str]
            # Top sim IDs (if specificied)
            if output_sims:
                neighb_chan_id_str = ",".join(neighb_chan_id_l)
                info_cols_l.append(neighb_chan_id_str)
            of.write("\t".join([chan_id] + info_cols_l) + "\n")
    of.close()

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--vec-fp')
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--label-fp')
    parser.add_argument('--score-chan-fp')
    parser.add_argument('--out-fp')
    parser.add_argument('--num-neighbs', type=int, default=5)
    parser.add_argument('--weight-neighbs', type=bool, default=False)
    parser.add_argument('--use-gpu', type=bool, default=False)
    parser.add_argument('--multi-lab', type=bool, default=False)
    parser.add_argument('--multi-lab-prob', type=bool, default=False)
    parser.add_argument('--regression', type=bool, default=False)
    parser.add_argument('--output-sims', type=bool, default=False)
    parser.add_argument('--bin-prob', type=bool, default=False)
    args=parser.parse_args()
    score_file_faiss(args.vec_fp, args.chan_info_fp, args.label_fp, args.score_chan_fp,
                     args.out_fp, num_neighbs=args.num_neighbs, use_gpu=args.use_gpu,
                     multi_lab=args.multi_lab, output_sims=args.output_sims,
                     weight_neighbs=args.weight_neighbs, bin_prob=args.bin_prob,
                     multi_lab_prob=args.multi_lab_prob, regression=args.regression)
