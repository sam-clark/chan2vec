import json
import os
import collections
import random

NUM_FOLDS = 5
DS_FP = 'data/datasets/recfluence_political_channels_20200727.txt'
COMMENTS_FP = 'data/pol_chan_disc/candidate_chan_videos_top10_comments/initial_channels_20200827_top10_video_comments.txt'
SEL_SAMP_FP = 'data/pol_chan_disc/commenter_need_sub_scrap/initial_channels_20200827_top10_video_samp_commenters.txt'
PREV_LABS = 'data/pol_chan_disc/chan2vec_training_data/chan2vec_initial_channels_ds.pol_class_no_heur_lab.txt'
OUT_DIR = 'data/pol_chan_disc_cross_val/init_round/'

# Get folds
fold_chans_d = collections.defaultdict(set)
all_rec_chan_id_l = [l.strip() for l in open(DS_FP)]
random.shuffle(all_rec_chan_id_l)
for i, chan_id in enumerate(all_rec_chan_id_l):
    fold_chans_d[i % NUM_FOLDS].add(chan_id)

# Create scripts and files for each fold
script_l = []
for fold, fold_chan_s in fold_chans_d.items():
    OUT_DIR_FOLD = OUT_DIR + "/fold_" + str(fold)
    if not os.path.exists(OUT_DIR_FOLD):
        os.makedirs(OUT_DIR_FOLD)
    of = open(OUT_DIR_FOLD + "/held_out_chans.txt", "w")
    of.write("\n".join(fold_chan_s) + "\n")
    of.close()
    # New labeled DS
    lab_fp = OUT_DIR_FOLD + "/pol_class_labs.txt"
    of = open(lab_fp, "w")
    init_chans_fp = OUT_DIR_FOLD + "/initial_chans.txt"
    of_init = open(init_chans_fp, "w")
    for l in open(PREV_LABS):
        chan_id = l.split("\t")[0]
        if chan_id not in fold_chan_s:
            of.write(l)
            of_init.write(chan_id + "\n")
    of.close()
    of_init.close()
    # New curl commenter fp
    latest_commenter_s = set([])
    for line in open(COMMENTS_FP):
        try:
            chan_id, vid_id, commenter_chan_id = line.strip("\n").split("\t")[0:3]
        except:
            continue
        if chan_id not in fold_chan_s:
            latest_commenter_s.add(commenter_chan_id)
    curl_com_fp = OUT_DIR_FOLD + "/curl_commenters.txt"
    of = open(curl_com_fp, "w")
    of.write("\n".join(latest_commenter_s) + "\n")
    of.close()
    # New selenium sample fp
    sel_samp_fp = OUT_DIR_FOLD + "/sel_commenters_samp.txt"
    of = open(sel_samp_fp, "w")
    for l in open(SEL_SAMP_FP):
        if l.split("\t")[0] not in fold_chan_s:
            of.write(l)
    of.close()
    # Create config
    config_d = {"commenters_subs_dir" : "data/pol_chan_disc/all_commenter_subs",
                "commenters_subs_selenium_dir" : "data/pol_chan_disc/all_commenter_subs_selenium",
                "terminated_channels_fp" : "data/datasets/channels_no_api_data.txt"}
    config_d["commenters_fp_list"] = [curl_com_fp]
    config_d["commenters_sel_samp_fp_list"] = [sel_samp_fp]
    ds_config_fp = OUT_DIR_FOLD + "/chan2vec_ds_gen_config.json"
    of = open(ds_config_fp, "w")
    of.write(json.dumps(config_d))
    of.close()
    # Output script
    docs_fp = OUT_DIR_FOLD + "/chan2vec_init_channels_ds.docs.txt"
    chan_info_fp = OUT_DIR_FOLD + "/chan2vec_init_channels_ds.chan_info.txt"
    docs_shuf_fp = OUT_DIR_FOLD + "/chan2vec_init_channels_ds.docs.shuf.txt"
    vecs_fp = OUT_DIR_FOLD + "/chan2vec_init_channels_ds.vectors.txt"
    chan_id_fp = OUT_DIR_FOLD + "/chan2vec_init_channels_ds.chan_info.chan_ids.txt"
    preds_fp = OUT_DIR_FOLD + "/chan2vec_init_channels_ds.pol_class_preds.txt"
    new_cand_fp = OUT_DIR_FOLD + "/new_candidate_fp.txt"
    script_fp = OUT_DIR_FOLD + "/gen_cands.sh"
    script = """
python3 chan2vec/python/generate_training_data.py \
        --commenter-config-fp %(ds_config_fp)s \
        --chan-docs-fp %(docs_fp)s \
        --chan-info-fp %(chan_info_fp)s

shuf %(docs_fp)s > %(docs_shuf_fp)s

cd ~/word2vec/
cp ~/youtube-channel-classification/%(docs_shuf_fp)s temp.in
time ./word2vec -train temp.in -output temp.out -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 0 -iter 15
cp temp.out ~/youtube-channel-classification/%(vecs_fp)s
cd ~/youtube-channel-classification/

cut -f 1 %(chan_info_fp)s \
    > %(chan_id_fp)s
python3 chan2vec/python/chan2vec_knn.py \
        --vec-fp %(vecs_fp)s \
        --chan-info-fp %(chan_info_fp)s \
        --label-fp %(lab_fp)s \
        --score-chan-fp %(chan_id_fp)s \
        --out-fp %(preds_fp)s \
        --num-neighbs 10 --use-gpu True --bin-prob True

python3 experiments/python/get_new_candidate_chans.py \
        --chan-info-fp %(chan_info_fp)s \
        --scores-fp %(preds_fp)s \
        --prev-candidate-fps %(init_chans_fp)s \
        --out-fp %(new_cand_fp)s
""" % vars()
    of = open(script_fp, "w")
    of.write(script)
    of.close()
    script_l.append(script_fp)

of = open("chan_discovery_cross_val.sh", "w")
of.write("\n".join(script_l))
of.close()
