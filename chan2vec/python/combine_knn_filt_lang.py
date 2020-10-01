import argparse
import collections
import numpy as np

def combine_filt_preds(knn_pred_fps, lang_pred_fp, out_fp, lang_pred_thresh=0.5):
    chan_lang_pred_d = {}
    for line in open(lang_pred_fp):
        chan_id, lang_pred = line.strip("\n").split("\t")
        chan_lang_pred_d[chan_id] = float(lang_pred)
    chan_preds_d = collections.defaultdict(list)
    for fp in knn_pred_fps.split(","):
        for line in open(fp):
            chan_id, pred = line.strip("\n").split("\t")
            chan_preds_d[chan_id].append(float(pred))
    of = open(out_fp, "w")
    for chan_id, pred_l in chan_preds_d.items():
        if chan_lang_pred_d[chan_id] <= lang_pred_thresh:
            of.write(chan_id + "\t0.0\n")
        else:
            pred = np.mean(pred_l)
            of.write(chan_id + "\t" + ("%.3f" % pred) + "\n")
    of.close()
    

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--knn-pred-fps')
    parser.add_argument('--lang-pred-fp')
    parser.add_argument('--lang-pred-thresh', type=float, default=0.5)
    parser.add_argument('--out-fp')
    args=parser.parse_args()
    combine_filt_preds(args.knn_pred_fps, args.lang_pred_fp, args.out_fp, lang_pred_thresh=args.lang_pred_thresh)
