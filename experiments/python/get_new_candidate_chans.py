import argparse

def get_new_candidate_chans(chan_info_fp, scores_fp, scores_lang_fp, prev_candidate_fps, out_fp,
                            min_prob=0.9, min_subs=10000):
    # Read in language preds
    eng_chan_s = set([])
    if scores_lang_fp is not None:
        for line in open(scores_lang_fp):
            chan_id, pred_prob = line.strip("\n").split("\t")
            if float(pred_prob) >= 0.5:
                eng_chan_s.add(chan_id)
    # Previous candidate chans
    prev_cand_chan_s = set([])
    for fp in prev_candidate_fps.split(","):
        for line in open(fp):
            prev_cand_chan_s.add(line.strip())
    # Get scores
    chan_prob_d = {}
    for line in open(scores_fp):
        chan_id, pred_prob = line.strip("\n").split("\t")
        chan_prob_d[chan_id] = float(pred_prob)
    # Find new cands
    cand_s = set([])
    new_pos_c = 0
    new_heur_c = 0
    chan_subs_d = {}
    new_pos_tot_subs = 0
    for line in open(chan_info_fp):
        chan_id, chan_int, chan_name, chan_scrap_subs, chan_tot_subs = line.strip("\n").split("\t")
        chan_tot_subs_int = int(float(chan_tot_subs))
        chan_subs_d[chan_id] = chan_tot_subs_int
        if chan_id not in prev_cand_chan_s:
            if chan_id in chan_prob_d and chan_prob_d[chan_id] >= min_prob and chan_tot_subs_int >= min_subs and (scores_lang_fp is None or chan_id in eng_chan_s):
                new_pos_c += 1
                new_pos_tot_subs += chan_tot_subs_int
                cand_s.add(chan_id)
            elif chan_tot_subs_int >= 3000000:
                cand_s.add(chan_id)
                new_heur_c += 1
    # Get number of previous candidates predicted pos
    prev_cand_neg_c = 0
    prev_cand_pos_c = 0
    prev_can_pos_tot_subs = 0
    for chan_id in prev_cand_chan_s:
        if chan_id in chan_prob_d:
            if chan_prob_d[chan_id] >= min_prob and (scores_lang_fp is None or chan_id in eng_chan_s):
                prev_cand_pos_c += 1
                prev_can_pos_tot_subs += chan_subs_d[chan_id]
            else:
                prev_cand_neg_c += 1
                
    of = open(out_fp, "w")
    of.write("\n".join(cand_s))
    of.close()
    print("All previous candidate negative predictions:", prev_cand_neg_c)
    print("All previous candidate positive predictions:", prev_cand_pos_c)
    print("All previous candidate positive predictions - Tot Subs:", prev_can_pos_tot_subs)
    print("New heuristic chans:", new_heur_c)
    print("New positive chans:", new_pos_c)
    print("New positive chans - Tot Subs:", new_pos_tot_subs)
    
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--scores-fp')
    parser.add_argument('--scores-lang-fp', default=None)
    parser.add_argument('--prev-candidate-fps')
    parser.add_argument('--out-fp')
    parser.add_argument('--min-tot-subs', type=int, default=10000)
    parser.add_argument('--min-prob', type=float, default=0.9)
    args=parser.parse_args()
    get_new_candidate_chans(args.chan_info_fp, args.scores_fp, args.scores_lang_fp, args.prev_candidate_fps,
                            args.out_fp, min_subs=args.min_tot_subs, min_prob=args.min_prob)
