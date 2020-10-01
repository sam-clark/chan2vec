import argparse

import chan2vec_knn

def main(vec_fp, chan_info_fp, out_fp):
    aid_chan_d, embed_m_lab = chan2vec_knn.read_vec_fp(vec_fp, chan_info_fp, include_s=None)
    of = open(out_fp, "w")
    for aid, chan_id in aid_chan_d.items():
        of.write("\t".join(map(str, [chan_id] + list(embed_m_lab[aid]))) + "\n")
    of.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--vec-fp')
    parser.add_argument('--chan-info-fp')
    parser.add_argument('--out-fp')
    args=parser.parse_args()
    main(args.vec_fp, args.chan_info_fp, args.out_fp)
