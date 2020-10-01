import os
import argparse

import pol_class_ensemble

def create_feats_score_cv(knn_fold_dir, lang_score_fp, api_topics_fp,
                          api_topic_feats, raw_embedding_fp, out_dir,
                          no_knn=False, top20_topics=False, ps_topics=False):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        for fn in os.listdir(out_dir):
            os.remove(out_dir + "/" + fn)
    # Apply model to each fold
    fold_s = set([int(fn.split(".")[1]) for fn in os.listdir(knn_fold_dir)])
    for fold in sorted(fold_s):
        print("RUNNING FOLD:", fold)
        train_labs_fp = "%(knn_fold_dir)s/train.%(fold)s.labs.txt" % vars()
        knn_score_train_fp = "%(knn_fold_dir)s/train.%(fold)s.preds.txt" % vars()
        knn_score_test_fp = "%(knn_fold_dir)s/test.%(fold)s.preds.txt" % vars()
        out_fp = "%(out_dir)s/test.%(fold)s.preds.txt" % vars()
        pol_class_ensemble.create_feats_score(train_labs_fp, knn_score_train_fp, knn_score_test_fp,
                                              lang_score_fp, api_topics_fp,
                                              raw_embedding_fp, out_fp, no_knn=no_knn,
                                              top20_topics=top20_topics, ps_topics=ps_topics)

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--knn-fold-dir')
    parser.add_argument('--lang-score-fp', default=None)
    parser.add_argument('--api-topics-fp',  default=None)
    parser.add_argument('--api-topic-feats', default=None)
    parser.add_argument('--top20-topics', type=bool, default=False)
    parser.add_argument('--ps-topics', type=bool, default=False)
    parser.add_argument('--raw-embedding-fp', default=None)
    parser.add_argument('--no-knn', type=bool, default=False)
    parser.add_argument('--out-dir')
    args=parser.parse_args()
    create_feats_score_cv(args.knn_fold_dir, args.lang_score_fp, args.api_topics_fp,
                          args.api_topic_feats, args.raw_embedding_fp, args.out_dir,
                          no_knn=args.no_knn, top20_topics=args.top20_topics, ps_topics=args.ps_topics)

