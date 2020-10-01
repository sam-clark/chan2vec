import argparse


def add_labs(chan_lab_d, chan_s, filter_chan_s, lab):
    for chan_id in chan_s:
        if chan_id in filter_chan_s or chan_id in chan_lab_d:
            continue
        chan_lab_d[chan_id] = lab
    

def generate_pol_class_labs(pos_fp, neg_fp, filter_fp, vec_chan_info_fp,
                            min_heuristic_neg_subs, out_fp, out_no_heur_fp,
                            prev_candidate_fps=None):
    prev_cand_chan_s = set([])
    if prev_candidate_fps is not None:
        for fp in prev_candidate_fps.split(","):
            for line in open(fp):
                prev_cand_chan_s.add(line.strip())
    filter_chan_s = set([l.strip() for l in open(filter_fp)])
    chan_lab_d = {}
    # Get pos labs
    pos_chan_s = set([l.strip() for l in open(pos_fp)])
    add_labs(chan_lab_d, pos_chan_s, filter_chan_s, 1)
    # Get neg labs
    neg_chan_s = set([l.strip() for l in open(neg_fp)])
    add_labs(chan_lab_d, neg_chan_s, filter_chan_s, 0)
    # Output - no heuristic
    of = open(out_no_heur_fp, "w")
    for chan_id, lab in chan_lab_d.items():
        of.write(chan_id + "\t" + str(lab) + "\n")
    of.close()    
    # Get heuristic neg labs
    heur_neg_s = set([])
    for line in open(vec_chan_info_fp):
        chan_id, chan_int, chan_name, chan_scrap_subs, chan_tot_subs = line.strip("\n").split("\t")
        if float(chan_tot_subs) >= min_heuristic_neg_subs and (prev_candidate_fps is None or chan_id in prev_cand_chan_s):
            heur_neg_s.add(chan_id)
    add_labs(chan_lab_d, heur_neg_s, filter_chan_s, 0)
    # Output
    of = open(out_fp, "w")
    for chan_id, lab in chan_lab_d.items():
        of.write(chan_id + "\t" + str(lab) + "\n")
    of.close()

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pos-fp')
    parser.add_argument('--neg-fp')
    parser.add_argument('--filter-fp')
    parser.add_argument('--vec-chan-info-fp')
    parser.add_argument('--min-heuristic-neg-subs', type=int, default=3000000)
    parser.add_argument('--out-fp')
    parser.add_argument('--out-no-heur-fp')
    parser.add_argument('--prev-candidate-fps', default=None)
    args=parser.parse_args()
    generate_pol_class_labs(args.pos_fp, args.neg_fp, args.filter_fp, args.vec_chan_info_fp,
                            args.min_heuristic_neg_subs, args.out_fp, args.out_no_heur_fp,
                            prev_candidate_fps=args.prev_candidate_fps)
