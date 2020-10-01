import collections
import argparse

from sklearn.metrics import roc_auc_score

def read_file(lab_fp, score_fp, pred_thresh, bin_prob=False, bin_prob_pos_class=None,
              bin_prob_neg_class=None, regression_round=False):
    chan_lab_d = dict([l.strip().split("\t") for l in open(lab_fp)])
    lab_with_pred_l = []
    lab_pred_d = collections.defaultdict(
        lambda : collections.defaultdict(int))
    tot_pred_d = collections.defaultdict(int)
    tot_insts = 0
    for line in open(score_fp):
        if bin_prob:
            chan_id, pred_perc = line.strip("\n").split("\t")
            pred = bin_prob_pos_class if float(pred_perc) >= 0.5 else bin_prob_neg_class
        else:
            tpl = line.strip("\n").split("\t")
            if len(tpl) == 3:
                chan_id, pred, pred_perc = tpl
            else:
                chan_id, pred = tpl
                pred_perc = None
                if regression_round:
                    pred = str(round(float(pred)))
        if chan_id not in chan_lab_d: continue
        lab = chan_lab_d[chan_id]
        lab = lab.replace(" ", "")
        pred = pred.replace(" ", "")
        lab_with_pred_l.append(lab)
        if pred_thresh is not None and float(pred_perc) < pred_thresh:
            pred = "NONE"
        lab_pred_d[lab][pred] += 1
        tot_pred_d[pred] += 1
        tot_insts += 1
    return lab_with_pred_l, lab_pred_d, tot_pred_d, tot_insts


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


def get_stats(lab_fp, score_fp, lab_conf_matrix_order_l=None, pred_thresh=None,
              multi_lab=False, bin_prob=False, bin_prob_pos_class=None,
              bin_prob_neg_class=None, regression_round=False):
    # Read in data
    pred_thresh = None if pred_thresh is None else float(pred_thresh)
    if not multi_lab:
        lab_with_pred_l, lab_pred_d, tot_pred_d, tot_insts = read_file(lab_fp, score_fp, pred_thresh, bin_prob=bin_prob,
                                                                       bin_prob_pos_class=bin_prob_pos_class,
                                                                       bin_prob_neg_class=bin_prob_neg_class,
                                                                       regression_round=regression_round)
    else:
        lab_with_pred_l, lab_pred_d, tot_pred_d, tot_insts = read_file_multi_lab(lab_fp, score_fp, pred_thresh)
    # Ouput stats
    print("Number Instances:", tot_insts)
    max_lab, max_c = max(collections.Counter(lab_with_pred_l).items(),
                         key=lambda x: x[1])
    print("Max Label", max_c, max_lab)
    print("Baseline:", "%.3f" % (max_c / tot_insts))
    if not multi_lab:
        cor_c = sum([pred_d[lab] for lab, pred_d in lab_pred_d.items()])
        print("Accuracy:", "%.3f" % (cor_c / tot_insts))
    print("\nPrecision Recall:")
    for lab, pred_d in sorted(lab_pred_d.items(), key=lambda x: sum(x[1].values()),
                              reverse=True):
        if multi_lab and lab == "NONE": continue
        num_lab_insts = sum(pred_d.values())
        rec = pred_d[lab] / num_lab_insts
        if tot_pred_d[lab] > 0:
            prec = pred_d[lab] / tot_pred_d[lab]
        else:
            prec = 0
        print("\t".join([str(num_lab_insts), "%.3f" % prec,
                         "%.3f" % rec, lab]))
    if lab_conf_matrix_order_l is not None:
        print("\nConfusion Matrix:")
        print("Label order: ", ", ".join(lab_conf_matrix_order_l))
        for lab in lab_conf_matrix_order_l:
            c_l = []
            for pred in lab_conf_matrix_order_l:
                c_l.append(str(lab_pred_d[lab][pred]))
            print("\t".join(c_l))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--lab-fp')
    parser.add_argument('--score-fp')
    parser.add_argument('--lab-conf-matrix-order', default="")
    parser.add_argument('--pred-thresh', default=None)
    parser.add_argument('--multi-lab', type=bool, default=False)
    parser.add_argument('--bin-prob', type=bool, default=False)
    parser.add_argument('--bin-prob-pos-class', default=None)
    parser.add_argument('--bin-prob-neg-class', default=None)
    parser.add_argument('--regression-round', type=bool, default=False)
    args=parser.parse_args()
    lab_conf_matrix_order_l = None if args.lab_conf_matrix_order == "" else args.lab_conf_matrix_order.split(",")
    get_stats(args.lab_fp, args.score_fp, lab_conf_matrix_order_l, pred_thresh=args.pred_thresh,
              multi_lab=args.multi_lab, bin_prob=args.bin_prob, bin_prob_pos_class=args.bin_prob_pos_class,
              bin_prob_neg_class=args.bin_prob_neg_class, regression_round=args.regression_round)
