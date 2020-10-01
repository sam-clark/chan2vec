import collections

NUM_FOLDS = 5
ALL_FOLD_DIR = 'data/pol_chan_disc_cross_val/init_round/'

FILTER_FP = 'data/datasets/pol_class_ds_filter_20200904.txt'
NO_API_DATA_FP = 'data/datasets/channels_no_api_data.txt'

#FINAL_MODEL_PREDS_FP = 'data/pol_chan_class/ensemble_scores/round3_channels_ds_20200904/knn_lang_ps_t20_topics_raw_embed.comb.txt'
FINAL_MODEL_PREDS_FP = 'data/pol_chan_class/chan2vec_knn_scores/r3_ds_20200904/chan2vec_round3_channels_ds.comb_16_200_dim_pol_pred.new_labs.txt'

# Get the channels that should be filtered out (due to being terminated, etc.)
filter_s = set([])
for l in open(FILTER_FP):
    filter_s.add(l.strip())
for l in open(NO_API_DATA_FP):
    filter_s.add(l.strip())

# Check held out stats
all_held_out_chan_s = set([])
all_found_chan_s = set([])
for i in range(NUM_FOLDS):
    fold_dir = ALL_FOLD_DIR + "/fold_" + str(i)
    # Read held out chans
    held_out_chan_s = set([])
    for line in open(fold_dir + "/held_out_chans.txt"):
        chan_id = line.strip()
        if chan_id not in filter_s:
            held_out_chan_s.add(chan_id)
    # Check which have been found
    found_chan_s = set([])
    for line in open(fold_dir + "/new_candidate_fp.txt"):
        chan_id = line.strip()
        if chan_id in held_out_chan_s:
            found_chan_s.add(chan_id)
    all_held_out_chan_s = all_held_out_chan_s.union(held_out_chan_s)
    all_found_chan_s = all_found_chan_s.union(found_chan_s)

print("High recall model -")
print("Total held out:", len(all_held_out_chan_s))
print("Total found:", len(all_found_chan_s))
print("Perc coverage:", "%.3f" % (len(all_found_chan_s) / len(all_held_out_chan_s)))
print()

# Read in final model preds
chan_final_pred_d = {}
for line in open(FINAL_MODEL_PREDS_FP):
    chan_id, pred_prob = line.strip("\n").split("\t")
    chan_final_pred_d[chan_id] = float(pred_prob)

no_pred_s = set([])
found_final_08_s = set([])
for chan_id in all_found_chan_s:
    if chan_id not in chan_final_pred_d:
        no_pred_s.add(chan_id)
    elif chan_final_pred_d[chan_id] >= 0.8:
        found_final_08_s.add(chan_id)

print("Final pred - ")
print("No preds:", len(no_pred_s))
print("With >= 0.8:", len(found_final_08_s))
print("With >= 0.8 - held out coverage:", "%.3f" % (len(found_final_08_s) / len(all_held_out_chan_s)))
print()

# Get soft tag stats
st_tot_c = collections.defaultdict(int)
st_found_cand_c = collections.defaultdict(int)
st_found_final_c = collections.defaultdict(int)
for line in open("data/datasets/recfluence_vis_channel_stats_20200727.soft_tags.txt"):
    chan_id, soft_tag = line.strip("\n").split("\t")
    if chan_id not in all_held_out_chan_s:
        continue
    st_tot_c[soft_tag] += 1
    if chan_id in all_found_chan_s:
        st_found_cand_c[soft_tag] += 1
    if chan_id in found_final_08_s:
        st_found_final_c[soft_tag] += 1

print("Soft tag coverage - ")
for soft_tag, tot_c in sorted(st_tot_c.items(), key=lambda x: x[1], reverse=True):
    found_cand_c = st_found_cand_c[soft_tag]
    found_cand_perc = "%.3f" % (found_cand_c / tot_c)
    found_final_c = st_found_final_c[soft_tag]
    found_final_perc = "%.3f" % (found_final_c / tot_c)
    print("\t".join(map(str, [tot_c, found_cand_c, found_cand_perc, found_final_c, found_final_perc, soft_tag])))
    #print(";".join(map(str, [soft_tag, tot_c, found_cand_c, found_cand_perc, found_final_c, found_final_perc])))
print()
    
