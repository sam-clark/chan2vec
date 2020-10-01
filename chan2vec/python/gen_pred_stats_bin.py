import argparse

from sklearn.metrics import roc_auc_score

def print_stats(lab_l, pred_l, pred_bin_l):
    auc = roc_auc_score(lab_l, pred_l)
    accuracy = sum([int(lab_l[i] == pred_bin_l[i]) for i in range(len(lab_l))]) / len(lab_l)
    cor_c = sum([int((lab_l[i] == 1) and (pred_bin_l[i] == 1)) for i in range(len(lab_l))])
    prec = cor_c / sum(pred_bin_l)
    rec = cor_c / sum(lab_l)
    print("Num instances:", len(lab_l))
    print("AUC:          ", "%.4f" % auc)
    print("Accuracy:     ", "%.4f" % accuracy)
    print("Precision:    ", "%.4f" % prec)
    print("Recall:       ", "%.4f" % rec)

    
def main(lab_fp, score_fp, thresh=0.5, out_fp=None, no_fold_lab_col=False):
    chan_lab_d = {}
    for line in open(lab_fp):
        chan_id, lab = line.strip("\n").split("\t")
        chan_lab_d[chan_id] = int(float(lab) >= 0.5)
    chan_pred_d = {}
    out_l = []
    for line in open(score_fp):
        if no_fold_lab_col:
            chan_id, pred = line.strip("\n").split("\t")
            fold = None
        else:
            fold, chan_id, _, pred = line.strip("\n").split("\t")
        chan_pred_d[chan_id] = float(pred)
        if chan_id in chan_lab_d:
            out_l.append((fold, chan_id, chan_lab_d[chan_id], pred))
    lab_l = []
    pred_l = []
    pred_bin_l = []
    for chan_id, lab in chan_lab_d.items():
        if chan_id in chan_pred_d:
            lab_l.append(lab)
            pred = chan_pred_d[chan_id]
            pred_l.append(pred)
            pred_bin_l.append(int(pred >= thresh))
    # Print stats
    print_stats(lab_l, pred_l, pred_bin_l)
    # Output results
    if out_fp is not None:
        of = open(out_fp, "w")
        for tpl in out_l:
            of.write("\t".join(map(str, tpl)) + "\n")
        of.close()

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--lab-fp')
    parser.add_argument('--score-fp')
    parser.add_argument('--pred-thresh', type=float, default=0.5)
    parser.add_argument('--out-fp', default=None)
    parser.add_argument('--no-fold-lab-col', type=bool, default=False)
    args=parser.parse_args()
    main(args.lab_fp, args.score_fp, thresh=args.pred_thresh, out_fp=args.out_fp,
         no_fold_lab_col=args.no_fold_lab_col)
