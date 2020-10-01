import argparse
import random
import collections

import numpy as np
from xgboost import XGBClassifier

def create_feats(chan_l, chan_lab_d, chan_knn_pred_d, chan_lang_pred_d,
                 chan_topic_d, chan_embed_d, top20_topic_l, get_labs=True,
                 no_knn=False, top20_topics=False, ps_topics=False):
    random.shuffle(chan_l)
    features_l = []
    lab_l = []
    feat_chan_l = []
    for chan_id in chan_l:
        feat_vals_l = []
        # KNN
        if chan_id not in chan_knn_pred_d:
            continue
        if not no_knn:
            feat_vals_l.append(chan_knn_pred_d[chan_id])
        # Language
        if len(chan_lang_pred_d) > 0 :
            if chan_id not in chan_lang_pred_d:
                continue
            feat_vals_l.append(float(chan_lang_pred_d[chan_id]))
        # API Topic
        if len(chan_topic_d) > 0:
            if chan_id not in chan_topic_d:
                continue
            if ps_topics:
                feat_vals_l.append(1 if 'Politics' in chan_topic_d[chan_id] else 0)
                feat_vals_l.append(1 if 'Society' in chan_topic_d[chan_id] else 0)
            if top20_topics:
                for topic in top20_topic_l:
                    if topic == 'Society': continue
                    feat_vals_l.append(1 if topic in chan_topic_d[chan_id] else 0)
        # Embeddings
        if len(chan_embed_d) > 0:
            if chan_id not in chan_embed_d:
                continue
            for dim in chan_embed_d[chan_id]:
                feat_vals_l.append(float(dim))
        feat_chan_l.append(chan_id)
        features_l.append(feat_vals_l)
        if get_labs:
            lab_l.append(chan_lab_d[chan_id])
    return feat_chan_l, np.array(features_l), np.array(lab_l)


def create_feats_score(train_labs_fp, knn_score_train_fp, knn_score_test_fp,
                       lang_score_fp, api_topics_fp, raw_embedding_fp, out_fp,
                       no_knn=False, top20_topics=False, ps_topics=False, verbose=True):
    # Read in KNN preds
    chan_knn_pred_d = {}
    for line in open(knn_score_train_fp):
        chan_id, pred_prob = line.strip("\n").split("\t")
        chan_knn_pred_d[chan_id] = float(pred_prob)
    score_chans_l = []
    for line in open(knn_score_test_fp):
        chan_id, pred_prob = line.strip("\n").split("\t")
        chan_knn_pred_d[chan_id] = float(pred_prob)
        score_chans_l.append(chan_id)
    # Read in language pred
    chan_lang_pred_d = {}
    if lang_score_fp is not None:
        chan_lang_pred_d = dict([l.strip("\n").split("\t") for l in open(lang_score_fp)])
    # Read in topics
    chan_topic_d = {}
    top20_topic_l = []
    if api_topics_fp:
        topic_c = collections.defaultdict(int)
        for line in open(api_topics_fp):
            chan_id, topic = line.strip("\n").split("\t")
            if chan_id not in chan_topic_d:
                chan_topic_d[chan_id] = set([])
            chan_topic_d[chan_id].add(topic)
            topic_c[topic] += 1
        top20_topic_l = [topic for topic, c in sorted(topic_c.items(), key=lambda x: x[1], reverse=True)][0:20]
    # Read in raw vector
    chan_embed_d = {}
    if raw_embedding_fp is not None:
        for line in open(raw_embedding_fp):
            tpl = line.strip("\n").split("\t")
            chan_embed_d[tpl[0]] = tpl[1:]
    # Read in labels
    chan_lab_d = dict([l.strip("\n").split("\t") for l in open(train_labs_fp)])
    train_chans_l = list(chan_lab_d.keys())
    # Create features
    train_chans_filt_l, X_train, y_train = create_feats(train_chans_l, chan_lab_d, chan_knn_pred_d,
                                                        chan_lang_pred_d, chan_topic_d, chan_embed_d, top20_topic_l, get_labs=True,
                                                        no_knn=no_knn, top20_topics=top20_topics, ps_topics=ps_topics)
    score_chans_filt_l, X_score, _       = create_feats(score_chans_l, chan_lab_d, chan_knn_pred_d,
                                                        chan_lang_pred_d, chan_topic_d, chan_embed_d, top20_topic_l, get_labs=False,
                                                        no_knn=no_knn, top20_topics=top20_topics, ps_topics=ps_topics)
    if verbose:
        print("Features:")
        for i in range(len(X_train[0])):
            print("Mean val:", np.mean([l[i] for l in X_train]))
        
    # Train model
    clf = XGBClassifier()
    clf.fit(X_train, y_train)
    # Score instances
    pred_probs = [pred[1] for pred in clf.predict_proba(X_score)]
    of = open(out_fp, "w")
    for i in range(len(pred_probs)):
        prob = "%.4f" % pred_probs[i]
        chan_id = score_chans_filt_l[i]
        of.write(chan_id + "\t" + prob + "\n")
    of.close()



if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--train-labs-fp')
    parser.add_argument('--knn-score-train-fp')
    parser.add_argument('--knn-score-test-fp')
    parser.add_argument('--lang-score-fp', default=None)
    parser.add_argument('--api-topics-fp',  default=None)
    parser.add_argument('--top20-topics', type=bool, default=False)
    parser.add_argument('--ps-topics', type=bool, default=False)
    parser.add_argument('--raw-embedding-fp', default=None)
    parser.add_argument('--no-knn', type=bool, default=False)
    parser.add_argument('--out-fp')
    args=parser.parse_args()
    create_feats_score(args.train_labs_fp, args.knn_score_train_fp, args.knn_score_test_fp,
                       args.lang_score_fp, args.api_topics_fp,
                       args.raw_embedding_fp, args.out_fp, no_knn=args.no_knn,
                       top20_topics=args.top20_topics, ps_topics=args.ps_topics)

