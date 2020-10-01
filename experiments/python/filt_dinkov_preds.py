import argparse

def filt_preds(chan_stats_fp, preds_fp, filt_chans_fp, out_fp):
    # Read in filt chans
    filt_chan_s = set([l.strip("\n").split("\t")[0] for l in open(filt_chans_fp)])
    # Read in overall stats
    chan_subs_d = {}
    chan_views_d = {}
    for line in open(chan_stats_fp):
        chan_id, subs, views, num_vids = line.strip("\n").split("\t")
        if chan_id in filt_chan_s:
            chan_subs_d[chan_id] = int(float(subs))
            chan_views_d[chan_id] = int(float(views))
    # Get stats
    print("Total Channels:", len(chan_subs_d))
    print("Total Channels w/ 10K+ Subs:", sum([1 for subs in chan_subs_d.values() if subs >= 10000]))
    print("Total Channels w/ 1K+ Subs:", sum([1 for subs in chan_subs_d.values() if subs >= 1000]))
    print("Subs sum:", sum(chan_subs_d.values()))
    print("Views sum:", sum(chan_views_d.values()))
    # Output filtered preds
    of = open(out_fp, "w")
    for line in open(preds_fp):
        if line.split("\t")[0] in filt_chan_s:
            of.write(line)
    of.close()
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chan-stats-fp')
    parser.add_argument('--preds-fp')
    parser.add_argument('--filt-chans-fp')
    parser.add_argument('--out-fp')
    args=parser.parse_args()
    filt_preds(args.chan_stats_fp, args.preds_fp, args.filt_chans_fp, args.out_fp)
