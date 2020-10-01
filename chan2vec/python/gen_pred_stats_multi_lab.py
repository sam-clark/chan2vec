import collections
import argparse


def read_file_multi_lab(lab_fp, score_fp, pred_thresh):
    # Read in labels
    chan_lab_d = {}
    for line in open(lab_fp):
        chan_id, lab = line.strip("\n").split("\t")
        if chan_id not in chan_lab_d:
            chan_lab_d[chan_id] = set([])
        chan_lab_d[chan_id].add(lab.replace(" ", ""))
    # Read in predictions
    lab_with_pred_l = []
    lab_pred_d = collections.defaultdict(
        lambda : collections.defaultdict(int))
    tot_pred_d = collections.defaultdict(int)
    tot_insts = 0
    for line in open(score_fp):
        chan_id, pred_l_str = line.strip("\n").split("\t")[0:2]
        if chan_id not in chan_lab_d: continue
        tot_insts += 1
        lab_s = chan_lab_d[chan_id]
        pred_s = set([])
        for pred_perc_str in pred_l_str.split(","):
            pred, pred_perc = pred_perc_str.split("|")
            pred = pred.replace(" ", "")
            if pred_thresh is None or float(pred_perc) >= pred_thresh:
                pred_s.add(pred)
        for lab in lab_s:
            lab_with_pred_l.append(lab)
            pred = "NONE" if lab not in pred_s else lab
            lab_pred_d[lab][pred] += 1
        for pred in pred_s:
            tot_pred_d[pred] += 1
    return lab_with_pred_l, lab_pred_d, tot_pred_d, tot_insts


def get_stats(lab_fp, score_fp, pred_thresh=None):
    # Read in data
    pred_thresh = None if pred_thresh is None else float(pred_thresh)
    lab_with_pred_l, lab_pred_d, tot_pred_d, tot_insts = read_file_multi_lab(lab_fp, score_fp, pred_thresh)
    # Ouput stats
    print("Number Instances:", tot_insts)
    max_lab, max_c = max(collections.Counter(lab_with_pred_l).items(),
                         key=lambda x: x[1])
    print("Max Label", max_c, max_lab)
    print("Baseline:", "%.3f" % (max_c / tot_insts))
    print("\nPrecision Recall:")
    for lab, pred_d in sorted(lab_pred_d.items(), key=lambda x: sum(x[1].values()),
                              reverse=True):
        if lab == "NONE": continue
        num_lab_insts = sum(pred_d.values())
        rec = pred_d[lab] / num_lab_insts
        if tot_pred_d[lab] > 0:
            prec = pred_d[lab] / tot_pred_d[lab]
        else:
            prec = 0
        print("\t".join([str(num_lab_insts), "%.3f" % prec,
                         "%.3f" % rec, lab]))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--lab-fp')
    parser.add_argument('--score-fp')
    parser.add_argument('--pred-thresh', default=None)
    args=parser.parse_args()
    get_stats(args.lab_fp, args.score_fp, pred_thresh=args.pred_thresh)


