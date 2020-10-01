import collections
import argparse


def compare_groups(chan_info_fp, soft_tags_fp, recfluence_fp=None, soft_tag_thresh=0.5, soft_tag_order=None,
                   soft_pred_pr_fp=None, soft_tag_pol_class_rec_fp=None, monthly_views_fp=None, start_views_dt=None, end_views_dt=None,
                   show_missing_views=False, final_pol_class_recall=0.85, final_pol_class_precision=0.85,
                   spreadsheet_form=False, pol_class_thresh=None, use_traffic_perc=False, use_channel_counts=False):
    # Correct for political channel classification recall and soft tag prediction P/R 
    soft_tag_multiple_d = {}
    if soft_pred_pr_fp is not None and soft_tag_pol_class_rec_fp is not None:
        for line in open(soft_tag_pol_class_rec_fp):
            tot_chans, cand_found_c, cand_found_perc, final_found_c, final_found_perc, soft_tag = line.strip("\n").split("\t")
            cand_found_perc = float(cand_found_perc)
            if cand_found_perc > 0:
                soft_tag_multiple_d[soft_tag] = final_pol_class_precision / (cand_found_perc*final_pol_class_recall)
        for line in open(soft_pred_pr_fp):
            tot_chans, precision, recall, soft_tag = line.strip("\n").split("\t")
            prev_multiple = soft_tag_multiple_d[soft_tag] if soft_tag in soft_tag_multiple_d else 1.0
            if float(recall) > 0:
                soft_tag_multiple_d[soft_tag] = prev_multiple * (float(precision) / float(recall))
    elif soft_pred_pr_fp != soft_tag_pol_class_rec_fp:
        print("NEED TO HAVE BOTH SOFT TAG METRICS.")
    # Read in views data
    chan_month_views_d = {}
    if monthly_views_fp is not None:
        for line in open(monthly_views_fp):
            chan_id, view_dt, views = line.strip("\n").split("\t")
            views = int(float(views))
            if views < 0 or (start_views_dt is not None and view_dt < start_views_dt) \
               or (end_views_dt is not None and view_dt > end_views_dt): continue
            if chan_id not in chan_month_views_d:
                chan_month_views_d[chan_id] = {}
            month = view_dt[0:7]
            chan_month_views_d[chan_id][month] = views
    # For all tasks, limit to these channels (accounts for terminated channels)
    chan_tot_subs_d = {}
    for line in open(chan_info_fp):
        chan_id, chan_int, chan_name, scrap_subs, tot_subs = line.strip("\n").split("\t")
        chan_tot_subs_d[chan_id] = int(float(tot_subs))
    # Get recfluence channels in case split is on these
    recfluence_chan_s = set([l.strip() for l in open(recfluence_fp)]) if recfluence_fp is not None else None
    # Get group stats
    month_group_chan_c = collections.defaultdict(
        lambda : collections.defaultdict(int))
    month_group_traffic_c = collections.defaultdict(
        lambda : collections.defaultdict(int))
    missing_views_d = {}
    month_chan_traffic_adjust_d = collections.defaultdict(dict)
    for line in open(soft_tags_fp):
        chan_id, pol_class_prob, soft_tag, soft_tag_prob = line.strip("\n").split("\t")
        if pol_class_thresh is not None and float(pol_class_prob) < pol_class_thresh:
            continue
        if float(soft_tag_prob) < soft_tag_thresh or chan_id not in chan_tot_subs_d:
            continue
        # TODO: FIX IN DATASET - Discussed with Mark and decided Joe Rogan is not Conspiracy
        if soft_tag == 'Conspiracy' and (chan_id == 'UCzQUP1qoWDoEbmsQxvdjxgQ' or chan_id == 'UCnxGkOGNMqQEUMvroOWps6Q'):
            continue
        # Get stats for each month
        if chan_id not in chan_month_views_d:
            continue
        for month, traffic in chan_month_views_d[chan_id].items():
            # Take care of multiple if possible
            chan_c = 1
            if soft_tag in soft_tag_multiple_d and chan_id not in recfluence_chan_s:
                chan_c = soft_tag_multiple_d[soft_tag]
                traffic = traffic*soft_tag_multiple_d[soft_tag]
            # Keep max adjusted traffic estimated for a channel
            if chan_id not in month_chan_traffic_adjust_d[month] or traffic < month_chan_traffic_adjust_d[month][chan_id]:
                month_chan_traffic_adjust_d[month][chan_id] = traffic
            month_group_chan_c[month][soft_tag] += chan_c
            month_group_traffic_c[month][soft_tag] += traffic
    # Output group stats
    if soft_tag_order is not None:
        soft_tag_l = soft_tag_order
    else:
        soft_tag_l = [st for st, chan_c in sorted(g1_chan_c.items(), key=lambda x: x[1], reverse=True)]
    # Header
    if not spreadsheet_form:
        print("\t".join(["month"] + soft_tag_l))
    else:
        print(";".join(["month"] + soft_tag_l))
    # Data
    for month in sorted(month_group_chan_c.keys()):
        use_traffic_perc
        cols = [month]
        overall_traffic = sum(month_chan_traffic_adjust_d[month].values())
        for soft_tag in soft_tag_l:
            if use_channel_counts:
                # Channels
                chan_c = month_group_chan_c[month][soft_tag]
                cols.append(str(int(chan_c)))
            else:
                # Views
                tot_traffic = month_group_traffic_c[month][soft_tag]
                if use_traffic_perc:
                    overall_traffic_perc = "%.3f" % (tot_traffic / overall_traffic)
                    cols.append(overall_traffic_perc)
                else:
                    cols.append(str(int(tot_traffic)))
        # Output
        if not spreadsheet_form:
            print("\t".join(cols))
        else:
            print(";".join(cols))
    if show_missing_views:
        print()
        print("Total missing views:", len(missing_views_d))
        for chan, subs in sorted(missing_views_d.items(), key=lambda x: x[1], reverse=True)[0:10]:
            print(chan, subs)

            
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--soft-tags-fp')
    parser.add_argument('--recfluence-fp', default=None)
    parser.add_argument('--soft-tag-order', default=None)
    parser.add_argument('--soft-pred-pr-fp', default=None)
    parser.add_argument('--soft-tag-pol-class-rec-fp', default=None)
    parser.add_argument('--monthly-views-fp', default=None)
    parser.add_argument('--start-views-dt', default=None)
    parser.add_argument('--end-views-dt', default=None)
    parser.add_argument('--spreadsheet-form', default=False, type=bool)
    parser.add_argument('--pol-class-thresh', default=None, type=float)
    parser.add_argument('--use-traffic-perc', default=False, type=bool)
    parser.add_argument('--use-channel-counts', default=False, type=bool)
    args=parser.parse_args()
    soft_tag_order = args.soft_tag_order.split(",") if args.soft_tag_order is not None else None
    compare_groups(args.chan_info_fp, args.soft_tags_fp, recfluence_fp=args.recfluence_fp,
                   soft_tag_order=soft_tag_order, soft_pred_pr_fp=args.soft_pred_pr_fp,
                   soft_tag_pol_class_rec_fp=args.soft_tag_pol_class_rec_fp,
                   monthly_views_fp=args.monthly_views_fp, start_views_dt=args.start_views_dt, end_views_dt=args.end_views_dt,
                   spreadsheet_form=args.spreadsheet_form, pol_class_thresh=args.pol_class_thresh,
                   use_traffic_perc=args.use_traffic_perc, use_channel_counts=args.use_channel_counts)
