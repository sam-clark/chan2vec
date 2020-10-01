import argparse
import subprocess
import datetime
import time
import os
import sys

def check_file_size(data_loc_fp, col_check, sub_string, email):
    file_last_val_d = {}
    while True:
        # Check all files
        print(datetime.datetime.now())
        same_c = 0
        file_vals_l = []
        for line in open(data_loc_fp):
            ec2_file_fp = line.strip()
            if sub_string not in ec2_file_fp: continue
            ec2_ip, file_fp = ec2_file_fp.split(":")
            cmd = 'ssh %(ec2_ip)s "cut -f %(col_check)s %(file_fp)s | sort | uniq | wc -l"' % vars()
            try:
                num_vals = int(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].strip())
            except:
                print("DATA PULL ERROR:", num_vals)
                num_vals = 0
            print(num_vals, ec2_file_fp)
            if ec2_file_fp in file_last_val_d:
                last_num_vals = file_last_val_d[ec2_file_fp]
                if last_num_vals == num_vals:
                    print("NO CHANGE.")
                    same_c += 1
                file_vals_l.append("\t".join(map(str, [last_num_vals, num_vals, ec2_file_fp])))
            file_last_val_d[ec2_file_fp] = num_vals
        print()
        # Notify if there is an issue
        if same_c > 0:
            body = "\n".join(file_vals_l)
            cmd = 'echo "%(body)s" | mail -s "SCRAPING ERROR - %(same_c)d stalled." %(email)s' % vars()
            os.system(cmd)
            sys.exit(1)
        time.sleep(300)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-loc-fp')
    parser.add_argument('--col-check', type=int, default=1)
    parser.add_argument('--sub-string', default='')
    parser.add_argument('--email', default='')
    args=parser.parse_args()
    check_file_size(args.data_loc_fp, args.col_check, args.sub_string, args.email)
