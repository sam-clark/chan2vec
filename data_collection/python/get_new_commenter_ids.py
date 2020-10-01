import argparse
import collections
import os

def get_new_commenters(all_com_subs_dir, comments_fp, all_commenter_fp, need_sub_scrape_fp):
    # Get set of previously scraped chans
    prev_scrape_commenters_s = set([])
    for subs_fn in os.listdir(all_com_subs_dir):
        for line in open(all_com_subs_dir + "/" + subs_fn):
            commenter_chan_id = line.strip("\n").split("\t")[0]
            prev_scrape_commenters_s.add(commenter_chan_id)
    # Read over latest commenters fp
    latest_commenter_s = set([])
    bad_line_c = 0
    for line in open(comments_fp):
        try:
            chan_id, vid_id, commenter_chan_id = line.strip("\n").split("\t")[0:3]
        except:
            bad_line_c += 1
            continue
        latest_commenter_s.add(commenter_chan_id)
    # Output
    need_scrap_s = latest_commenter_s.difference(prev_scrape_commenters_s)
    of = open(need_sub_scrape_fp, "w")
    of.write("\n".join(need_scrap_s))
    of.close()
    of = open(all_commenter_fp, "w")
    of.write("\n".join(latest_commenter_s))
    of.close()
    print("All commenters:", len(latest_commenter_s))
    print("All need scrape:", len(need_scrap_s))
    print("All prev scrape:", len(prev_scrape_commenters_s))
    print("Bad lines:", bad_line_c)

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--all-com-subs-dir')
    parser.add_argument('--comments-fp')
    parser.add_argument('--all-commenter-fp')
    parser.add_argument('--need-sub-scrape-fp')
    args=parser.parse_args()
    get_new_commenters(args.all_com_subs_dir, args.comments_fp, args.all_commenter_fp, args.need_sub_scrape_fp)
