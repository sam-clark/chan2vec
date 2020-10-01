import argparse
import collections
import random

def main(lab_fp, score_fp, thresh=0.5, limit_reviewer_comparison=False):
    # Read in reviewer labels
    chan_soft_tag_reviewer_lab_d = collections.defaultdict(
        lambda : collections.defaultdict(dict))
    for line in open(lab_fp):
        chan_id, chan_name, reviewer, soft_tag, _, lab = line.strip("\n").split("\t")
        chan_soft_tag_reviewer_lab_d[chan_id][soft_tag][reviewer] = (lab == 'True')
    # Read in predicted labels
    chan_soft_tag_pred_d = {}
    for line in open(score_fp):
        chan_id, soft_tag, pred = line.strip("\n").split("\t")
        if float(pred) < thresh: continue
        if chan_id not in chan_soft_tag_pred_d:
            chan_soft_tag_pred_d[chan_id] = set([])
        chan_soft_tag_pred_d[chan_id].add(soft_tag)
    # Get agreement
    soft_tag_rev_pos_c = collections.defaultdict(int)
    soft_tag_rev_agree_c = collections.defaultdict(int)
    soft_tag_rev_disagree_c = collections.defaultdict(int)
    soft_tag_pred_agree_c = collections.defaultdict(int)
    soft_tag_pred_disagree_c = collections.defaultdict(int)
    soft_tag_bl_agree_c = collections.defaultdict(int)
    soft_tag_bl_disagree_c = collections.defaultdict(int)
    soft_tag_max_agree_c = collections.defaultdict(int)
    soft_tag_max_disagree_c = collections.defaultdict(int)
    for chan_id, soft_tag_reviewer_lab_d in chan_soft_tag_reviewer_lab_d.items():
        # Only keep channels we have predictions for to ensure consistent comparison
        if chan_id not in chan_soft_tag_pred_d:
            continue
        for soft_tag, reviewer_lab_d in soft_tag_reviewer_lab_d.items():
            max_lab, max_c = collections.Counter([lab for lab in reviewer_lab_d.values()]).most_common(1)[0]
            reviewer_lab_l = [tpl for tpl in reviewer_lab_d.items()]
            for reviwer, lab in reviewer_lab_l:
                if lab:
                    soft_tag_rev_pos_c[soft_tag] += 1
                # Compare against other reviewers
                for reviewer_comp, lab_comp in reviewer_lab_d.items():
                    if reviwer == reviewer_comp: continue
                    if lab == lab_comp:
                        soft_tag_rev_agree_c[soft_tag] += 1
                    else:
                        soft_tag_rev_disagree_c[soft_tag] += 1
                # Compare baseline of always predicting negative
                if lab:
                    soft_tag_bl_disagree_c[soft_tag] += 1
                else:
                    soft_tag_bl_agree_c[soft_tag] += 1
                # Get upper bound
                if lab == max_lab:
                    soft_tag_max_agree_c[soft_tag] += 1
                else:
                    soft_tag_max_disagree_c[soft_tag] += 1
            # Limit the number of comparisons for preds if chosen
            if limit_reviewer_comparison:
                random.shuffle(reviewer_lab_l)
                reviewer_lab_l = reviewer_lab_l[0:2]
            for reviwer, lab in reviewer_lab_l:
                # Compare against prediction
                if (lab and soft_tag in chan_soft_tag_pred_d[chan_id]) \
                   or (not lab and soft_tag not in chan_soft_tag_pred_d[chan_id]):
                    soft_tag_pred_agree_c[soft_tag] += 1
                else:
                    soft_tag_pred_disagree_c[soft_tag] += 1
    # Output results
    for soft_tag, pos_c in sorted(soft_tag_rev_pos_c.items(), key=lambda x: x[1], reverse=True):
        rev_agree_perc = soft_tag_rev_agree_c[soft_tag] / (soft_tag_rev_disagree_c[soft_tag] + soft_tag_rev_agree_c[soft_tag])
        pred_agree_perc = soft_tag_pred_agree_c[soft_tag] / (soft_tag_pred_disagree_c[soft_tag] + soft_tag_pred_agree_c[soft_tag])
        bl_agree_perc = soft_tag_bl_agree_c[soft_tag] / (soft_tag_bl_disagree_c[soft_tag] + soft_tag_bl_agree_c[soft_tag])
        max_agree_perc = soft_tag_max_agree_c[soft_tag] / (soft_tag_max_disagree_c[soft_tag] + soft_tag_max_agree_c[soft_tag])
        print("\t".join([str(pos_c), "%.3f" % rev_agree_perc, "%.3f" % pred_agree_perc, "%.3f" % bl_agree_perc,
                         "%.3f" % max_agree_perc, soft_tag]))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--lab-fp')
    parser.add_argument('--score-fp')
    parser.add_argument('--pred-thresh', type=float, default=0.5)
    parser.add_argument('--limit-reviewer-comparison', type=bool, default=False)
    args=parser.parse_args()
    main(args.lab_fp, args.score_fp, thresh=args.pred_thresh, limit_reviewer_comparison=args.limit_reviewer_comparison)
