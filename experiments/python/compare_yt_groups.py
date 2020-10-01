import collections
import argparse


def compare_groups(chan_info_fp, soft_tags_fp, recfluence_fp=None, soft_tag_thresh=0.5, soft_tag_order=None,
                   soft_pred_pr_fp=None, soft_tag_pol_class_rec_fp=None, monthly_views_fp=None, start_views_dt=None, end_views_dt=None,
                   show_missing_views=False, head_subs_thresh=None, mainstream_split=False, final_pol_class_recall=0.85, final_pol_class_precision=0.85,
                   spreadsheet_form=False, pol_class_thresh=None):
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
    chan_views_d = {}
    if monthly_views_fp is not None:
        for line in open(monthly_views_fp):
            chan_id, view_dt, views = line.strip("\n").split("\t")
            views = int(float(views))
            if views < 0 or (start_views_dt is not None and view_dt < start_views_dt) \
               or (end_views_dt is not None and view_dt > end_views_dt): continue
            if chan_id not in chan_views_d:
                chan_views_d[chan_id] = 0
            chan_views_d[chan_id] += views
    # Get mainstream chans
    mainstream_chan_s = set([])
    if mainstream_split:
        for line in open(soft_tags_fp):
            chan_id, pol_class_prob, soft_tag, soft_tag_prob = line.strip("\n").split("\t")
            if float(soft_tag_prob) >= 0.5 and soft_tag == 'MainstreamMedia':
                mainstream_chan_s.add(chan_id)
    # For all tasks, limit to these channels (accounts for terminated channels)
    chan_tot_subs_d = {}
    for line in open(chan_info_fp):
        chan_id, chan_int, chan_name, scrap_subs, tot_subs = line.strip("\n").split("\t")
        chan_tot_subs_d[chan_id] = int(float(tot_subs))
    # Get recfluence channels in case split is on these
    recfluence_chan_s = set([l.strip() for l in open(recfluence_fp)]) if recfluence_fp is not None else None
    # Get group stats
    g1_chan_c = collections.defaultdict(int)
    g1_traffic_c = collections.defaultdict(int)
    g2_chan_c = collections.defaultdict(int)
    g2_traffic_c = collections.defaultdict(int)
    missing_views_d = {}
    chan_traffic_adjust_d = {}
    for line in open(soft_tags_fp):
        chan_id, pol_class_prob, soft_tag, soft_tag_prob = line.strip("\n").split("\t")
        if pol_class_thresh is not None and float(pol_class_prob) < pol_class_thresh:
            continue
        if float(soft_tag_prob) < soft_tag_thresh or chan_id not in chan_tot_subs_d:
            continue
        # TODO: FIX IN DATASET - Discussed with Mark and decided Joe Rogan is not Conspiracy
        if soft_tag == 'Conspiracy' and (chan_id == 'UCzQUP1qoWDoEbmsQxvdjxgQ' or chan_id == 'UCnxGkOGNMqQEUMvroOWps6Q'):
            continue
        # Use views if available
        chan_subs = chan_tot_subs_d[chan_id]
        if chan_views_d:
            if chan_id not in chan_views_d:
                missing_views_d[chan_id] = chan_subs
                continue
            traffic = chan_views_d[chan_id]
        else:
            traffic = chan_subs
        # Take care of multiple if possible
        chan_c = 1
        if soft_tag in soft_tag_multiple_d and chan_id not in recfluence_chan_s:
            chan_c = soft_tag_multiple_d[soft_tag]
            traffic = traffic*soft_tag_multiple_d[soft_tag]
        # Keep max adjusted traffic estimated for a channel
        if chan_id not in chan_traffic_adjust_d or traffic < chan_traffic_adjust_d[chan_id]:
            chan_traffic_adjust_d[chan_id] = traffic
        # Split chans
        if head_subs_thresh is not None:
            # Split groups based on number of subs
            if  chan_subs >= head_subs_thresh:
                g1_chan_c[soft_tag] += 1
                g1_traffic_c[soft_tag] += traffic
            else:
                g2_chan_c[soft_tag] += chan_c
                g2_traffic_c[soft_tag] += traffic
        elif mainstream_split:
            # Check mainstream vs. YouTube
            if chan_id in mainstream_chan_s:
                g1_chan_c[soft_tag] += 1
                g1_traffic_c[soft_tag] += traffic
            else:
                g2_chan_c[soft_tag] += chan_c
                g2_traffic_c[soft_tag] += traffic                
        else:
            # Split groups on whether the channel was in Recfluence or not
            if chan_id in recfluence_chan_s:
                g1_chan_c[soft_tag] += 1
                g1_traffic_c[soft_tag] += traffic
            else:
                g2_chan_c[soft_tag] += chan_c
                g2_traffic_c[soft_tag] += traffic
    # Output group stats
    if soft_tag_order is not None:
        soft_tag_l = soft_tag_order
    else:
        soft_tag_l = [st for st, chan_c in sorted(g1_chan_c.items(), key=lambda x: x[1], reverse=True)]
    overall_traffic = sum(chan_traffic_adjust_d.values())
    for soft_tag in soft_tag_l:
        tot_traffic = g1_traffic_c[soft_tag] + g2_traffic_c[soft_tag]
        overall_traffic_perc = "%.3f" % (tot_traffic / overall_traffic)
        g1_perc = "%.2f" % (g1_traffic_c[soft_tag] / (g1_traffic_c[soft_tag] + g2_traffic_c[soft_tag]))
        cols = [overall_traffic_perc, int(tot_traffic), int(g1_chan_c[soft_tag]), int(g1_traffic_c[soft_tag]),
                int(g2_chan_c[soft_tag]), int(g2_traffic_c[soft_tag]), g1_perc]
        # Add multiple if it exists
        if soft_tag_multiple_d:
            cols.insert(0, '%.2f' % soft_tag_multiple_d[soft_tag])
        if not spreadsheet_form:
            print("\t".join(map(str, cols + [soft_tag])))
        else:
            print(";".join(map(str, [soft_tag] + cols)))
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
    parser.add_argument('--head-subs-thresh', default=None, type=float)
    parser.add_argument('--mainstream-split', default=False, type=bool)
    parser.add_argument('--spreadsheet-form', default=False, type=bool)
    parser.add_argument('--pol-class-thresh', default=None, type=float)
    args=parser.parse_args()
    soft_tag_order = args.soft_tag_order.split(",") if args.soft_tag_order is not None else None
    compare_groups(args.chan_info_fp, args.soft_tags_fp, recfluence_fp=args.recfluence_fp,
                   soft_tag_order=soft_tag_order, soft_pred_pr_fp=args.soft_pred_pr_fp,
                   soft_tag_pol_class_rec_fp=args.soft_tag_pol_class_rec_fp,
                   monthly_views_fp=args.monthly_views_fp, start_views_dt=args.start_views_dt, end_views_dt=args.end_views_dt,
                   head_subs_thresh=args.head_subs_thresh, mainstream_split=args.mainstream_split,
                   spreadsheet_form=args.spreadsheet_form, pol_class_thresh=args.pol_class_thresh)
