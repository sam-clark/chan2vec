import argparse

def filter_comment_files(comment_fps, samp_fps, chan_filter_fp,
                         out_commenters_fp, out_commenters_samp_fp):
    # Only include commenters from these channels
    chan_filt_s = set([l.strip() for l in open(chan_filter_fp)])
    # Get all curl commenters from correct chans
    all_commenters_filt_s = set([])
    for comment_fp in comment_fps.split(","):
        for line in open(comment_fp):
            try:
                chan_id, vid_id, commenter_chan_id = line.replace("\\", "").strip("\n").split("\t")[0:3]
            except:
                continue
            if chan_id in chan_filt_s:
                all_commenters_filt_s.add(commenter_chan_id)
    # Output curl commenters
    of = open(out_commenters_fp, "w")
    of.write("\n".join(all_commenters_filt_s) + "\n")
    of.close()
    # Filter out sample chans
    samp_filt_s = set([])
    for samp_fp in samp_fps.split(","):
        for line in open(samp_fp):
            chan_id, commenter_id = line.strip("\n").split("\t")
            if chan_id in chan_filt_s:
                samp_filt_s.add(line.strip("\n"))
    # Output commenters from the sample that are from the appropriate commenter
    of = open(out_commenters_samp_fp, "w")
    of.write("\n".join(samp_filt_s) + "\n")
    of.close()
    
        
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--comment-fps')
    parser.add_argument('--samp-fps')
    parser.add_argument('--chan-filter-fp')
    parser.add_argument('--out-commenters-fp')
    parser.add_argument('--out-commenters-samp-fp')
    args=parser.parse_args()
    filter_comment_files(args.comment_fps, args.samp_fps, args.chan_filter_fp,
                         args.out_commenters_fp, args.out_commenters_samp_fp)
