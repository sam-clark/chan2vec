import argparse
import sklearn
import collections

import numpy as np

from sklearn.cluster import KMeans

import chan2vec_knn


def cluster_channels(vec_fp, chan_info_fp, limit_chan_fp,
                     num_clusters, output_fp_pref, extra_tags_fp=None):
    # Get extra tags
    extra_tags_d = collections.defaultdict(set)
    if extra_tags_fp is not None:
        for line in open(extra_tags_fp):
            chan_id, tag = line.strip("\n").split("\t")
            extra_tags_d[chan_id].add(tag)
    # Only cluster these channels
    chan_limit_s = set([l.strip("\n") for l in open(limit_chan_fp)])
    # Read in vectors
    aid_chan_d, embed_m = chan2vec_knn.read_vec_fp(vec_fp, chan_info_fp,
                                                   include_s=chan_limit_s)
    # Get clusters
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(embed_m)
    # Read in channel info
    chan_info_d = {}
    for line in open(chan_info_fp):
        chan_id, _, chan_name, scrap_subs, tot_subs = line.strip("\n").split("\t")
        if chan_id in chan_limit_s:
            chan_info_d[chan_id] = (chan_name, scrap_subs, tot_subs)
    # Add info to clusters
    clust_centers = kmeans.cluster_centers_
    clust_chans_d = collections.defaultdict(list)
    for lid, lab in enumerate(kmeans.labels_):
        chan_id = aid_chan_d[lid]
        chan_name, scrap_subs, tot_subs = chan_info_d[chan_id]
        dist = np.linalg.norm(embed_m[lid] - clust_centers[lab])
        l = [chan_id, chan_name, dist, int(scrap_subs), int(tot_subs)]
        if extra_tags_fp is not None:
            l.append("|".join(sorted(extra_tags_d[chan_id])))
        clust_chans_d[lab].append(l)
    # Output clusters
    for clust, chan_l in clust_chans_d.items():
        of = open(output_fp_pref + str(clust) + ".txt", "w")
        for tpl in sorted(chan_l, key=lambda x: x[2]):
            of.write("\t".join(map(str, tpl)) + "\n")
        of.close()
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--vec-fp')
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--limit-chan-fp')
    parser.add_argument('--num-clusters', type=int, default=5)
    parser.add_argument('--extra_tags_fp', default=None)
    parser.add_argument('--output-fp-pref')
    args=parser.parse_args()
    cluster_channels(args.vec_fp, args.chan_info_fp, args.limit_chan_fp,
                     args.num_clusters, args.output_fp_pref,
                     extra_tags_fp=args.extra_tags_fp)

