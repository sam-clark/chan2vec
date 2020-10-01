import argparse
import random
import os

import numpy as np
from sklearn.model_selection import KFold

import chan2vec_knn

def split_score(vec_fp, chan_info_fp, lab_fp, out_dir, num_neighbs=5, use_gpu=False,
                multi_lab=False, output_sims=False, weight_neighbs=False, bin_prob=False,
                multi_lab_prob=False, num_folds=10):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        for fn in os.listdir(out_dir):
            os.remove(out_dir + "/" + fn)
    # Read in labels
    labels_a = np.array([l.strip("\n") for l in open(lab_fp)])
    # Split and score each
    kf = KFold(n_splits=num_folds, shuffle=True)
    for fold_i, (train_index, test_index) in enumerate(kf.split(labels_a)):
        # Generate train / test files
        train_lab_fp = "%(out_dir)s/train.%(fold_i)s.labs.txt" % vars()
        test_lab_fp = "%(out_dir)s/test.%(fold_i)s.labs.txt" % vars()
        of = open(train_lab_fp, "w")
        of.write("\n".join([l for l in labels_a[train_index]]) + "\n")
        of.close()
        of = open(test_lab_fp, "w")
        of.write("\n".join([l for l in labels_a[test_index]]) + "\n")
        of.close()
        train_chan_fp = "%(out_dir)s/train.%(fold_i)s.chans.txt" % vars()
        test_chan_fp = "%(out_dir)s/test.%(fold_i)s.chans.txt" % vars()
        of = open(train_chan_fp, "w")
        of.write("\n".join([l.split("\t")[0] for l in labels_a[train_index]]) + "\n")
        of.close()
        of = open(test_chan_fp, "w")
        of.write("\n".join([l.split("\t")[0] for l in labels_a[test_index]]) + "\n")
        of.close()
        # Score *BOTH* using the train file
        # Train score
        train_pred_fp = "%(out_dir)s/train.%(fold_i)s.preds.txt" % vars()
        chan2vec_knn.score_file_faiss(vec_fp, chan_info_fp, train_lab_fp, train_chan_fp,
                                      train_pred_fp, num_neighbs=num_neighbs, use_gpu=use_gpu,
                                      multi_lab=multi_lab, output_sims=output_sims,
                                      weight_neighbs=weight_neighbs, bin_prob=bin_prob,
                                      multi_lab_prob=multi_lab_prob)
        test_pred_fp = "%(out_dir)s/test.%(fold_i)s.preds.txt" % vars()
        chan2vec_knn.score_file_faiss(vec_fp, chan_info_fp, train_lab_fp, test_chan_fp,
                                      test_pred_fp, num_neighbs=num_neighbs, use_gpu=use_gpu,
                                      multi_lab=multi_lab, output_sims=output_sims,
                                      weight_neighbs=weight_neighbs, bin_prob=bin_prob,
                                      multi_lab_prob=multi_lab_prob)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--vec-fp')
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--label-fp')
    parser.add_argument('--score-chan-fp')
    parser.add_argument('--out-dir')
    parser.add_argument('--num-neighbs', type=int, default=5)
    parser.add_argument('--weight-neighbs', type=bool, default=False)
    parser.add_argument('--use-gpu', type=bool, default=False)
    parser.add_argument('--multi-lab', type=bool, default=False)
    parser.add_argument('--multi-lab-prob', type=bool, default=False)
    parser.add_argument('--output-sims', type=bool, default=False)
    parser.add_argument('--bin-prob', type=bool, default=False)
    parser.add_argument('--num-folds', type=int, default=10)
    args=parser.parse_args()
    split_score(args.vec_fp, args.chan_info_fp, args.label_fp,
                args.out_dir, num_neighbs=args.num_neighbs, use_gpu=args.use_gpu,
                multi_lab=args.multi_lab, output_sims=args.output_sims,
                weight_neighbs=args.weight_neighbs, bin_prob=args.bin_prob,
                multi_lab_prob=args.multi_lab_prob, num_folds=args.num_folds)
