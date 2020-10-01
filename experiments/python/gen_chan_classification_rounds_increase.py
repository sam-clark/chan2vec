import argparse

def round_increase(chan_info_fp, final_model_preds_fp, rounds_fp, heuristic_lim=3000000):
    # Get channel info
    chan_tot_subs_d = {}
    for line in open(chan_info_fp):
        chan_id, chan_int, chan_name, scrap_subs, tot_subs = line.strip("\n").split("\t")
        chan_tot_subs_d[chan_id] = int(float(tot_subs))
    # Get pos preds (and recfluence)
    pos_chans_s = set([l.strip() for l in open(final_model_preds_fp)])
    # See how coverage increases
    tot_chans = 0
    tot_chan_subs = 0
    for fp_round, fp in enumerate(rounds_fp.split(",")):
        num_cands = 0
        new_chans = 0
        new_chan_subs = 0
        for line in open(fp):
            chan_id = line.strip()
            # Getting rid of terminated channels
            if chan_id not in chan_tot_subs_d:
                continue
            # Accounting for heuristic negative examples
            if fp_round > 0 and chan_tot_subs_d[chan_id] >= heuristic_lim:
                continue
            # Check if chan is pos
            num_cands += 1
            if chan_id in pos_chans_s:
                new_chans += 1
                new_chan_subs += chan_tot_subs_d[chan_id]
        # Output stats
        tot_chans += new_chans
        tot_chan_subs += new_chan_subs
        print(";".join(map(str, [fp_round, new_chans, new_chan_subs, tot_chans, tot_chan_subs])))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--final-model-preds-fp')
    parser.add_argument('--rounds-fp')
    args=parser.parse_args()
    round_increase(args.chan_info_fp, args.final_model_preds_fp, args.rounds_fp)
