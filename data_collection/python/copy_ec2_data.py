import argparse
import subprocess
import datetime
import time
import os
import sys

def check_file_size(data_loc_fp, local_work_dir, sub_string, comb_fp):
    if not os.path.exists(local_work_dir):
        os.makedirs(local_work_dir)
    of = open(comb_fp, "w")
    for line in open(data_loc_fp):
        ec2_file_fp = line.strip()
        if sub_string not in ec2_file_fp: continue
        ec2_ip, file_fp = ec2_file_fp.split(":")
        local_fp = local_work_dir + "/" + file_fp.split("/")[-1]
        cmd = 'scp %(ec2_file_fp)s %(local_fp)s' % vars()
        print(cmd)
        os.system(cmd)
        # Add to file
        for line in open(local_fp):
            of.write(line.strip("\n") + "\n")
        # Compress
        os.system("gzip " + local_fp)
    of.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-loc-fp')
    parser.add_argument('--local-work-dir')
    parser.add_argument('--sub-string', default='')
    parser.add_argument('--comb-fp')
    args=parser.parse_args()
    check_file_size(args.data_loc_fp, args.local_work_dir, args.sub_string, args.comb_fp)
