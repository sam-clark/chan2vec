# chan2vec

The methods and experiment results are described in the following paper:
- https://arxiv.org/abs/2010.09892

Directions for running experiments from the paper and generating the https://transparency.tube/ channel classifications data are [here](#transparencytube-data).

Directions for doing basic classification with pre-existing embeddings can be found [here](#chan2vec-knn-basic-example).

## Political Channel Discovery

Commands from the following docs were used for political channel discovery (some data of which is used in Dinkov experiments)

1. Find candidate channels:
- experiments/docs/political_channel_discovery_init_round.txt
- experiments/docs/political_channel_discovery_round1.txt
- experiments/docs/political_channel_discovery_round2.txt
- experiments/docs/political_channel_discovery_round3.txt

2. Final political channel classification, out-of-sample performance stats, and language prediction stats
- experiments/docs/channel_language_prediction.txt
- experiments/docs/political_channel_classification_knn_only.txt

3. Channel discovery hold out analysis
- experiments/docs/political_channel_classification_coverage_analysis.txt

Note, for data collections, all scripts that require --ec2-ip-fp must have a file with the IPs of AWS instances that have been launched.
An example can be found here: data_collection/configs/comment_scrape_instances.SAMPLE.txt


## Dinkov Media Bias / Fact Check Experiment

The results of comparing chan2vec to Dinkov's model can be generated by running commands in the following doc
- experiments/docs/dinkov_political_preds.txt

Note, the Dinkov predictions were generated by modifying their code so that they would output predictions for individual channels.


## Soft Tag Predictions

Experiment results and commands for scoring all out of sample are in this doc:
- experiments/docs/political_soft_tags.txt


## Newly Discovered Political Channel Traffic Analysis

Experiment results can be found here:
- experiments/docs/political_soft_tags_traffic_analysis.txt
- experiments/docs/political_soft_tags_traffic_analysis_trends.txt

## Transparency.tube Data

The latest data was generated using commands in the following doc:
- experiments/docs/latest_site_data_20201006.txt

Tag definitions can be found here:
- https://github.com/markledwich2/Recfluence

Tag metrics from hold-one-out cross validation:
| Tag | # Channels | Precision | Recall |
| --- | --- | --- | --- |
| AntiSJW | 271 | 0.786 | 0.827 | 
| PartisanRight | 250 | 0.746 | 0.832 | 
| PartisanLeft | 146 | 0.733 | 0.678 | 
| SocialJustice | 141 | 0.770 | 0.617 | 
| Conspiracy | 118 | 0.856 | 0.805 | 
| MainstreamNews | 96 | 0.693 | 0.823 | 
| ReligiousConservative | 69 | 0.696 | 0.232 | 
| Socialist | 49 | 0.683 | 0.837 | 
| AntiTheist | 47 | 0.857 | 0.766 | 
| Educational | 44 | 0.909 | 0.227 | 
| Libertarian | 41 | 0.739 | 0.415 | 
| MissingLinkMedia | 39 | 0.286 | 0.051 | 
| StateFunded | 39 | 0.850 | 0.436 | 
| WhiteIdentitarian | 37 | 0.676 | 0.676 | 
| QAnon | 34 | 0.784 | 0.853 | 
| Provocateur | 21 | 0.500 | 0.143 | 
| MRA | 21 | 0.818 | 0.429 | 
| LateNightTalkShow | 10 | 0.700 | 0.700 | 
| Revolutionary | 9 | 0.500 | 0.111 | 

Political lean metrics from hold-one-out cross validation:
| Political Lean | # Channels | Precision | Recall |
| --- | --- | --- | --- |
| Left | 263 | 0.891 | 0.779 |
| Center | 236 | 0.633 | 0.644 |
| Right | 415 | 0.863 | 0.923 |


The predictions are available here:
- data/site_preds/labels_20201006/all_political_soft_tags_20201006.txt

Columns are:
- Channel ID
- Probability the channel is political (all over 0.8)
- Soft tag or political lean
- Probability of soft tag or political lean (use threshold of 0.5)

## Chan2vec KNN Basic Example

Install numpy and faiss
```
pip3 install faiss numpy
```

Download pre-existing emebddings (can reach out to the chan2vec author for these) and add to the specified locations below. Add "--use-gpu True" in order to speed up the command below, otherwise will take > 3 mins.
```
python3 chan2vec/python/chan2vec_knn.py \
        --vec-fp data/pol_chan_disc/chan2vec_training_data/chan2vec_round3_channels_ds.vectors.txt \
        --chan-info-fp data/pol_chan_disc/chan2vec_training_data/chan2vec_round3_channels_ds.chan_info.txt \
        --label-fp data/datasets/tt_ds_20201031.is_pol.txt \
        --score-chan-fp data/pol_chan_disc/chan2vec_training_data/chan2vec_round3_channels_ds.chan_info.channel_ids.txt \
        --out-fp ./all_political_predictions.txt \
        --num-neighbs 10 --bin-prob True
```

Get performance of model
```
python3 chan2vec/python/gen_pred_stats_bin.py \
        --lab-fp data/datasets/tt_ds_20201031.is_pol.txt \
        --score-fp ./all_political_predictions.txt \
        --no-fold-lab-col True --pred-thresh 0.5
```
Output:
```
Num instances: 6615
AUC:           0.9906
Accuracy:      0.9587
Precision:     0.8153
Recall:        0.9708
```

The columns for chan-info-fp are:
- Channel ID
- Assigned int for channel ID
- Channel Name
- Scraped comment subscriptions
- Total subscriptions

The larger the number of "scraped comment subscriptions", the more useful the channel embedding is likely to be for a given task. For political channel classification we filter out all channels with less than 20 "scraped comment subscriptions.
