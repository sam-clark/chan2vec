import sys
import argparse

def main(multi_lab_fp, out_fp, keep_tags_l, add_pred_fp=None, regression_lcr_fp=None):
    # Add another prediction column
    add_pred_d = None if add_pred_fp is None else dict((l.strip("\n").split("\t") for l in open(add_pred_fp)))
    # Improved L/C/R preds
    chan_improved_lcr_pred = {}
    if regression_lcr_fp is not None:
        for line in open(regression_lcr_fp):
            chan_id, lcr_reg_pred = line.strip("\n").split("\t")
            lcr_reg_pred = float(lcr_reg_pred)
            lcr_reg_pred_int = int(round(lcr_reg_pred))
            if lcr_reg_pred_int == -1:
                lcr_str = "L"
                lcr_prob = 1 - abs(-1 - lcr_reg_pred)
            elif lcr_reg_pred_int == 0:
                lcr_str = "C"
                lcr_prob = 1 - abs(0 - lcr_reg_pred)
            elif lcr_reg_pred_int == 1:
                lcr_str = "R"
                lcr_prob = 1 - abs(1 - lcr_reg_pred)
            else:
                print("ERROR - BAD LCR PRED:", lcr_reg_pred_int)
                sys.exit(1)
            chan_improved_lcr_pred[chan_id] = (lcr_str, "%.3f" % lcr_prob)
    
    # Keep certain tags and output
    keep_tags_s = set(keep_tags_l) if keep_tags_l is not None else None
    of = open(out_fp, 'w')
    for line in open(multi_lab_fp):
        chan_id, preds_str = line.strip('\n').split('\t')
        # Get extra pred if necessary
        extra_pred = None
        if add_pred_d is not None:
            if chan_id not in add_pred_d:
                print("CHAN ID NOT FOUND:", chan_id)
                continue
            extra_pred = add_pred_d[chan_id]
        # Convert soft tags
        for tag_pred in preds_str.split(','):
            tag, perc = tag_pred.split('|')
            # Only include L/C/R if improved ones aren't available
            if chan_improved_lcr_pred and tag in set(["L", "C", "R"]):
                continue
            # Filter tags if specified
            if keep_tags_s is None or tag in keep_tags_s:
                cols = [chan_id, extra_pred, tag, perc] if extra_pred is not None else [chan_id, tag, perc]
                of.write('\t'.join(cols) + '\n')
        # Write out new L/C/R tags
        if chan_improved_lcr_pred:
            tag, prob = chan_improved_lcr_pred[chan_id]
            cols = [chan_id, extra_pred, tag, prob] if extra_pred is not None else [chan_id, tag, prob]
            of.write('\t'.join(cols) + '\n')
    of.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--multi-lab-fp')
    parser.add_argument('--out-fp')
    parser.add_argument('--add-pred-fp', default=None)
    parser.add_argument('--regression-lcr-fp', default=None)
    parser.add_argument('--keep-tags', default=None)
    args=parser.parse_args()
    keep_tags_str = args.keep_tags
    keep_tags_l = None if keep_tags_str is None else keep_tags_str.split(',')
    main(args.multi_lab_fp, args.out_fp, keep_tags_l, add_pred_fp=args.add_pred_fp,
         regression_lcr_fp=args.regression_lcr_fp)

    
