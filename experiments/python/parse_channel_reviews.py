import argparse
import collections

import numpy as np
import pandas as pd

def parse_chan_revs(chan_rev_fp, filt_reviewers, pol_class_fp, soft_tag_fp, pol_lean_fp,
                    pol_class_override_fp, override_soft_tags, override_reviewers,
                    relevance_thresh=0.5):
    # Pol class overrides..
    pol_class_override_d = {}
    if pol_class_override_fp is not None:
        for line in open(pol_class_override_fp):
            chan_id, lab = line.strip("\n").split("\t")
            pol_class_override_d[chan_id] = int(float(lab))
    # Override tags ...
    ov_soft_tag_s = set(override_soft_tags.split(","))
    ov_st_revs_s = set(override_reviewers.split(","))
    # Filter out some reviwers (specifically model based ones)
    filt_reviewers_s = set(filt_reviewers.split(","))
    # Read in review data
    chan_rev_df = pd.read_csv(chan_rev_fp)
    chan_rel_d = collections.defaultdict(list)
    chan_revs_d = collections.defaultdict(set)
    chan_tag_d = collections.defaultdict(
        lambda : collections.defaultdict(set))
    chan_lcr_d = collections.defaultdict(list)
    for rid, row in chan_rev_df.iterrows():
        rev_code = row["REVIEWER_CODE"]
        chan_id = row["CHANNEL_ID"]
        if rev_code in filt_reviewers_s:
            continue
        # Channel relevance
        rev_rel = row["REVIEWER_RELEVANCE"]
        chan_rel_d[chan_id].append(rev_rel)
        if rev_rel < relevance_thresh:
            continue
        # Soft tags
        chan_revs_d[chan_id].add(rev_code)
        if type(row["REVIEWER_TAGS"]) == str:
            for soft_tag in row["REVIEWER_TAGS"].split("|"):
                chan_tag_d[chan_id][soft_tag].add(rev_code)
        # L/C/R
        rev_lr = row["REVIEWER_LR"]
        if rev_lr:
            chan_lcr_d[chan_id].append(rev_lr)
    # Output results
    pol_class_f = open(pol_class_fp, "w")
    soft_tag_f = open(soft_tag_fp, "w")
    pol_lean_f = open(pol_lean_fp, "w")
    for chan_id, rel_l in chan_rel_d.items():
        # Determine if political
        avg_rel = np.mean(rel_l)
        if chan_id in pol_class_override_d:
            is_pol = pol_class_override_d[chan_id]
        else:
            is_pol = 1 if avg_rel >= relevance_thresh else 0
        pol_class_f.write(chan_id + "\t" + str(is_pol) + "\n")
        if not is_pol:
            continue
        # Get soft tags
        num_revs = len(chan_revs_d[chan_id])
        if num_revs == 0:
            continue # Only the case for overrides...
        for soft_tag, st_rev_s in chan_tag_d[chan_id].items():
            if len(st_rev_s) >= num_revs*0.5 or (soft_tag in ov_soft_tag_s and st_rev_s.intersection(ov_st_revs_s)):
                soft_tag_f.write(chan_id + "\t" + soft_tag + "\n")
        # Get L/C/R (include in Soft Tags as well for now)
        lcr_reg_l = [-1 if lcr == "L" else (0 if lcr == "C" else 1) for lcr in chan_lcr_d[chan_id]]
        lcr_int = int(round(np.mean(lcr_reg_l)))
        pol_lean_f.write(chan_id + "\t" + str(lcr_int) + "\n")
        lcr_str = "L" if lcr_int == -1 else ("C" if lcr_int == 0 else "R")
        soft_tag_f.write(chan_id + "\t" + lcr_str + "\n")
    pol_class_f.close()
    soft_tag_f.close()
    pol_lean_f.close()

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chan-rev-fp')
    parser.add_argument('--filt-reviewers')
    parser.add_argument('--override-soft-tags', default=None)
    parser.add_argument('--override-reviewers', default=None)
    parser.add_argument('--pol-class-override-fp', default=None)
    parser.add_argument('--pol-class-fp')
    parser.add_argument('--soft-tag-fp')
    parser.add_argument('--pol-lean-fp')
    parser.add_argument('--relevance-thresh', type=float, default=0.5)
    args=parser.parse_args()
    parse_chan_revs(args.chan_rev_fp, args.filt_reviewers, args.pol_class_fp, args.soft_tag_fp, args.pol_lean_fp,
                    args.pol_class_override_fp, args.override_soft_tags, args.override_reviewers,
                    relevance_thresh=args.relevance_thresh)
