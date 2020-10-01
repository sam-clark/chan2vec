
import argparse

def filter_pol_class_chans(pol_class_fp, chan_info_fp, lang_class_fp, out_fp, lang_thresh=0.5,
                           pol_thresh=0.9, min_scrap_subs=0):
    # Read in language chans to filter out
    non_eng_s = set([])
    for line in open(lang_class_fp):
        chan_id, pred_prob = line.strip("\n").split("\t")
        if float(pred_prob) <= lang_thresh:
            non_eng_s.add(chan_id)
    # Find topic channels / get scrap subs
    topic_chan_s = set([])
    chan_scrap_subs_d = {}
    for line in open(chan_info_fp):
        chan_id, chan_int, chan_name, scrap_subs, subs = line.strip("\n").split("\t")
        if chan_name.endswith(" - Topic"):
            topic_chan_s.add(chan_id)
        chan_scrap_subs_d[chan_id] = int(float(scrap_subs))
    # Output
    of = open(out_fp, "w")
    for line in open(pol_class_fp):
        chan_id, pred_prob = line.strip("\n").split("\t")
        if float(pred_prob) >= pol_thresh and chan_id not in non_eng_s \
           and chan_id not in topic_chan_s and chan_scrap_subs_d[chan_id] >= min_scrap_subs:
            of.write(chan_id + "\t" + pred_prob + "\n")
    of.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pol-class-fp')
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--lang-class-fp')
    parser.add_argument('--out-fp')
    parser.add_argument('--lang-thresh', type=float, default=0.5)
    parser.add_argument('--pol-thresh', type=float, default=0.9)
    parser.add_argument('--min-scrap-subs', type=int, default=0)
    args=parser.parse_args()
    filter_pol_class_chans(args.pol_class_fp, args.chan_info_fp, args.lang_class_fp, args.out_fp,
                           lang_thresh=args.lang_thresh, pol_thresh=args.pol_thresh,
                           min_scrap_subs=args.min_scrap_subs)
