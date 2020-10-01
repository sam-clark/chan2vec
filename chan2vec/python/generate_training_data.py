import argparse
import json
import os
import random

COMMENTERS_FP_LIST = 'commenters_fp_list'
COMMENTERS_SEL_SAMP_FP_LIST = 'commenters_sel_samp_fp_list'
COMMENTERS_SUBS_DIR = 'commenters_subs_dir'
COMMENTERS_SUBS_SELENIUM_DIR = 'commenters_subs_selenium_dir'
TERMINATED_CHANNELS_FP = 'terminated_channels_fp'


def store_chan_sub_info(commenter_subs_d, chan_name_d, chan_subs_d, chan_commenters_d,
                        chan_int_d, commenter_chan_id, chan_id, chan_name, subs):
    if len(chan_id) != 24 or len(commenter_chan_id) != 24:
        return
    # Record sub info
    if commenter_chan_id not in commenter_subs_d:
        commenter_subs_d[commenter_chan_id] = set([])
    commenter_subs_d[commenter_chan_id].add(chan_id)
    # Record chan info
    try:
        subs = int(float(subs))
    except:
        subs = -1
    if chan_id not in chan_name_d or len(chan_name_d[chan_id]) < len(chan_name):
        chan_name_d[chan_id] = chan_name
    if chan_id not in chan_subs_d or chan_subs_d[chan_id] < subs:
        chan_subs_d[chan_id] = subs
    if chan_id not in chan_commenters_d:
        chan_commenters_d[chan_id] = set([])
    chan_commenters_d[chan_id].add(commenter_chan_id)
    if chan_id not in chan_int_d:
        chan_int = len(chan_int_d)
        chan_int_d[chan_id] = chan_int


def generate_training_data(commenter_config_fp, chan_docs_fp, chan_info_fp,
                           num_ds_shuf=3, min_chan_scrap_subs=5, min_doc_size=2,
                           limit_doc_chan_fp=None):
    config_obj = json.load(open(commenter_config_fp))
    # Get channels that *MUST* be in doc for doc to be included
    limit_doc_chan_s = set([])
    if limit_doc_chan_fp is not None:
        limit_doc_chan_s = set([l.strip() for l in open(limit_doc_chan_fp)])
    # Get terminated channels to ensure vectors aren't created for them
    term_chans_s = set([l.strip() for l in open(config_obj[TERMINATED_CHANNELS_FP])])
    # Read in "curl" subs
    eligible_commenters_s = set([])
    for fp in config_obj[COMMENTERS_FP_LIST]:
        for line in open(fp):
            eligible_commenters_s.add(line.strip())
    no_subs_s = set([])
    commenters_subs_dir = config_obj[COMMENTERS_SUBS_DIR]
    commenter_subs_d = {}
    chan_name_d = {}
    chan_subs_d = {}
    chan_commenters_d = {}
    chan_int_d = {}
    for fn in sorted(os.listdir(commenters_subs_dir)):
        print("LOADING CURL:", fn)
        for line in open(commenters_subs_dir + "/" + fn):
            try:
                commenter_chan_id, chan_id, chan_name, subs = line.replace("\\", "").strip("\n").split("\t")[0:4]
            except:
                continue
            if commenter_chan_id not in eligible_commenters_s or chan_id in term_chans_s: continue
            if chan_id == "":
                no_subs_s.add(commenter_chan_id)
            else:
                # Record sub / chan info
                store_chan_sub_info(commenter_subs_d, chan_name_d, chan_subs_d, chan_commenters_d,
                                    chan_int_d, commenter_chan_id, chan_id, chan_name, subs)
    # Read in "selenium" subs
    eligible_sel_commenters_s = set([])
    for fp in config_obj[COMMENTERS_SEL_SAMP_FP_LIST]:
        for line in open(fp):
            eligible_sel_commenters_s.add(line.strip("\n").split("\t")[1])
    commenters_subs_selenium_dir = config_obj[COMMENTERS_SUBS_SELENIUM_DIR]
    no_sel_subs_s = set([])
    has_sel_subs_s = set([])
    for fn in sorted(os.listdir(commenters_subs_selenium_dir)):
        print("LOADING SELENIUM:", fn)
        for line in open(commenters_subs_selenium_dir + "/" + fn):
            try:
                commenter_chan_id, chan_id, chan_name, subs = line.replace("\\", "").strip("\n").split("\t")[0:4]
            except:
                continue
            if commenter_chan_id not in	eligible_sel_commenters_s or chan_id in term_chans_s: continue
            if chan_id == "":
                no_sel_subs_s.add(commenter_chan_id)
            else:
                # Record sub / chan info
                has_sel_subs_s.add(commenter_chan_id)
                store_chan_sub_info(commenter_subs_d, chan_name_d, chan_subs_d, chan_commenters_d,
                                    chan_int_d, commenter_chan_id, chan_id, chan_name, subs)
    # Filter chans by min scrap
    ds_chan_s = set([chan_id for chan_id, scrap_sub_s in chan_commenters_d.items()
                     if len(scrap_sub_s) >= min_chan_scrap_subs])
    # Create docs
    chan_docs_f = open(chan_docs_fp, "w")
    for commenter_id, subs_s in commenter_subs_d.items():
        if limit_doc_chan_s and len(limit_doc_chan_s.intersection(subs_s)) == 0: continue
        filt_sub_l = [str(chan_int_d[chan_id]) for chan_id in subs_s if chan_id in ds_chan_s]
        if len(filt_sub_l) < min_doc_size: continue
        for _ in range(num_ds_shuf):
            random.shuffle(filt_sub_l)
            chan_docs_f.write(" ".join(filt_sub_l) + "\n")
    chan_docs_f.close()
    # Output channel info
    chan_info_f = open(chan_info_fp, "w")
    for chan_id in ds_chan_s:
        chan_info_f.write("\t".join([chan_id, str(chan_int_d[chan_id]), chan_name_d[chan_id],
                                     str(len(chan_commenters_d[chan_id])), str(chan_subs_d[chan_id])]) + "\n")
    chan_info_f.close()
    # Print out stats
    print("\nScrape stats-")
    print("Eligible commenters:", len(eligible_commenters_s))
    print("Commenters no subs:", len(no_subs_s))
    print("Commenters w/ subs:", len(commenter_subs_d))
    print("Eligible sel commenters:", len(eligible_sel_commenters_s))
    print("Commenters selenium no subs:", len(no_sel_subs_s))
    print("Commenters selenium w/ subs:", len(has_sel_subs_s))
    print("All channels found:", len(chan_commenters_d))
    print("Channels w/ min scrap subs:", len(ds_chan_s))
    tot_comb_subs  = sum([len(scrap_sub_s) for chan_id, scrap_sub_s in chan_commenters_d.items()])
    print("Total combined subs:", tot_comb_subs)
    
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--commenter-config-fp')
    parser.add_argument('--chan-docs-fp')
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--limit-doc-chan-fp', default=None)
    parser.add_argument('--num-ds-shuf', type=int, default=3)
    parser.add_argument('--min-chan-scrap-subs', type=int, default=5)
    parser.add_argument('--min-doc-size', type=int, default=3)
    args=parser.parse_args()
    generate_training_data(args.commenter_config_fp, args.chan_docs_fp, args.chan_info_fp,
                           num_ds_shuf=args.num_ds_shuf, min_chan_scrap_subs=args.min_chan_scrap_subs,
                           min_doc_size=args.min_doc_size, limit_doc_chan_fp=args.limit_doc_chan_fp)

