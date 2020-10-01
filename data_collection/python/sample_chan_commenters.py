import argparse
import collections
import random
import os

def sample_chan_commenters(num_samp_commenters, min_subs, comments_fp,
                           all_com_subs_dir, all_com_sel_subs_dir,
                           commenters_samp_fp, commenters_samp_need_sel_fp):
    # Read in the comments to sample commenters from
    latest_commenter_s = set([])
    chan_commenters_d = collections.defaultdict(set)
    bad_line_c = 0
    for line in open(comments_fp):
        try:
            chan_id, vid_id, commenter_chan_id = line.strip("\n").split("\t")[0:3]
        except:
            bad_line_c += 1
            continue
        latest_commenter_s.add(commenter_chan_id)
        chan_commenters_d[chan_id].add(commenter_chan_id)
    # Get elegible commenters
    eleg_commenter_subs_d = collections.defaultdict(set)
    for subs_fn in sorted(os.listdir(all_com_subs_dir)):
        print("LOADING:", subs_fn)
        for line in open(all_com_subs_dir + "/" + subs_fn):
            commenter_chan_id, chan_id = line.strip("\n").split("\t")[0:2]
            if commenter_chan_id in latest_commenter_s:
                eleg_commenter_subs_d[commenter_chan_id].add(chan_id)
    elegible_commenters_s = set([])
    for commenter_chan_id, subs_s in eleg_commenter_subs_d.items():
        if len(subs_s) >= min_subs:
            elegible_commenters_s.add(commenter_chan_id)
    # Get all selenium subs
    prev_sel_sub_scrap = set([])
    for subs_fn in sorted(os.listdir(all_com_sel_subs_dir)):
        print("LOADING:", subs_fn)
        for line in open(all_com_sel_subs_dir + "/" + subs_fn):
            commenter_chan_id = line.strip("\n").split("\t")[0]
            prev_sel_sub_scrap.add(commenter_chan_id)
    # Sample and output channels
    of_samp = open(commenters_samp_fp, "w")
    of_need_sel = open(commenters_samp_need_sel_fp, "w")
    need_sel_out_s = set([])
    for chan_id, commenters_s in chan_commenters_d.items():
        chan_eleg_l = list(elegible_commenters_s.intersection(commenters_s))
        random.shuffle(chan_eleg_l)
        for commenter_chan_id in chan_eleg_l[0:num_samp_commenters]:
            of_samp.write(chan_id + "\t" + commenter_chan_id + "\n")
            # Check if has already been scraped
            if commenter_chan_id not in prev_sel_sub_scrap and commenter_chan_id not in need_sel_out_s:
                of_need_sel.write(commenter_chan_id + "\n")
                need_sel_out_s.add(commenter_chan_id)
    of_samp.close()
    of_need_sel.close()
    
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--num-samp-commenters', type=int, default=10)
    parser.add_argument('--min-subs', type=int, default=25)
    parser.add_argument('--comments-fp')
    parser.add_argument('--all-com-subs-dir')
    parser.add_argument('--all-com-sel-subs-dir')
    parser.add_argument('--commenters-samp-fp')
    parser.add_argument('--commenters-samp-need-sel-fp')
    args=parser.parse_args()
    sample_chan_commenters(args.num_samp_commenters, args.min_subs, args.comments_fp,
                           args.all_com_subs_dir, args.all_com_sel_subs_dir,
                           args.commenters_samp_fp, args.commenters_samp_need_sel_fp)
