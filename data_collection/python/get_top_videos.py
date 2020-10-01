import argparse
import collections


def get_top_videos(vid_fp, out_fp, most_recent_num=30, num_keep=10):
    chan_vid_l = collections.defaultdict(list)
    bad_vid_c = 0
    for line in open(vid_fp):
        try:
            chan_id, vid_id, views, date_raw, date_posted = line.strip("\n").split("\t")[0:5]
        except:
            bad_vid_c += 1
        if vid_id == "":
            continue
        try:
            views_c = int(views)
        except:
            views_c = -1
        chan_vid_l[chan_id].append((date_posted, views_c, vid_id))
    of = open(out_fp, "w")
    for chan_id, vid_l in chan_vid_l.items():
        recent_l = sorted(vid_l, reverse=True)[0:most_recent_num]
        most_viewed = sorted(recent_l, key=lambda x: x[1], reverse=True)
        for date_posted, views, vid_id in most_viewed[0:num_keep]:
            of.write("\t".join(map(str, [chan_id, vid_id, views])) + "\n")
    of.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--vid-fp')
    parser.add_argument('--out-fp')
    parser.add_argument('--scrape-date')
    parser.add_argument('--most-recent-num', type=int, default=30)
    parser.add_argument('--num-keep', type=int, default=10)
    args=parser.parse_args()
    get_top_videos(args.vid_fp, args.out_fp, most_recent_num=args.most_recent_num, num_keep=args.num_keep)
