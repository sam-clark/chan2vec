import os
import argparse

import numpy as np

from sklearn.metrics import roc_auc_score, precision_recall_fscore_support

def get_stats(lab_fp, score_dir, thresh=0.5):
    chan_lab_d = {}
    for line in open(lab_fp):
        chan, lab = line.strip("\n").split("\t")
        chan_lab_d[chan] = int(float(lab))
    # Going over each fold
    auc_l = []
    prec_l = []
    rec_l = []
    f1_l = []
    base_rate_l = []
    tot_lab_l = []
    tot_pred_l = []
    tot_pred_prob_l = []
    for fn in os.listdir(score_dir):
        if not (fn.startswith("test.") and fn.endswith(".preds.txt")):
            continue
        lab_l = []
        pred_l = []
        pred_prob_l = []
        for line in open(score_dir + "/" + fn):
            chan_id, pred_prob = line.strip("\n").split("\t")
            pred_prob = float(pred_prob)
            if chan_id not in chan_lab_d:
                continue
            lab_l.append(chan_lab_d[chan_id])
            pred_l.append(int(pred_prob >= thresh))
            pred_prob_l.append(pred_prob)
            tot_lab_l.append(chan_lab_d[chan_id])
            tot_pred_l.append(int(pred_prob >= thresh))
            tot_pred_prob_l.append(pred_prob)
        # Get stats
        auc = roc_auc_score(lab_l, pred_prob_l)
        prec, rec, f1_score, support = precision_recall_fscore_support(lab_l, pred_l, average='binary')
        prec_l.append(prec)
        rec_l.append(rec)
        f1_l.append(f1_score)
        base_rate_l.append(np.mean(lab_l))
        auc_l.append(auc)
    # Get tot stats
    auc = roc_auc_score(tot_lab_l, tot_pred_prob_l)
    prec, rec, f1_score, support = precision_recall_fscore_support(tot_lab_l, tot_pred_l, average='binary')
    base_rate = np.mean(tot_lab_l)
    # Output
    print("Total instances:", len(tot_lab_l))
    print("Metric \ Min \ Avg \ Max \ Total")
    for mt, ml, tot in [('  ROC-AUC', auc_l, auc), ('Precision', prec_l, prec), ('   Recall', rec_l, rec),
                   (' F1 Score', f1_l, f1_score), ('Base Rate', base_rate_l, base_rate)]:
        m_min = "%.4f" % min(ml)
        m_avg = "%.4f" % np.mean(ml)
        m_max = "%.4f" % max(ml)
        tot = "%.4f" % tot
        print("\t".join([mt, m_min, m_avg, m_max, tot])) 

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--lab-fp')
    parser.add_argument('--score-dir')
    parser.add_argument('--pred-thresh', type=float, default=0.5)
    args=parser.parse_args()
    get_stats(args.lab_fp, args.score_dir, thresh=args.pred_thresh)
