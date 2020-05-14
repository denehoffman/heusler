#!/usr/bin/python3
import os
import argparse
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description='Generates subdirectories with XYZ files based\n' \
                    'on the configurations given in JKCONFIG.\n\n' \
                    'XYZ is the standard format used by our group\n\n' \
                    'OUTPUT is the ouput directory. It must already\n' \
                    'exist, and when run, it will be populated by\n' \
                    'subdirectories labeled \'variation_<uid>\'\n' \
                    'where \'uid\' is the configuration string\n' \
                    'converted to decimal (assuming a base of\n' \
                    'n = number of species). Each directory will\n' \
                    'contain a modified XYZ file for the\n' \
                    'configurations listed in JKCONFIG\n\n' \
                    'JKCONFIG is a comma-delimited file with no header\n' \
                    'and columns \'J\' and \'K\' along with a final file\n' \
                    'which is a string of digits (starting at 0)\n' \
                    'typically obtained from enum.x. The length of\n' \
                    'this string must equal the number of points in XYZ',
        epilog='Written by Nathaniel D. Hoffman',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('XYZ', help='Original XYZ File')
    parser.add_argument('OUTPUT', help='Ouput Directory')
    parser.add_argument('JKCONFIGS',
                        help='CSV of J, K, Configuration (001010...)')
    args = parser.parse_args()
    filename = args.XYZ
    outputdir = args.OUTPUT
    configlist = args.JKCONFIGS
    XYZfile = open(filename, 'r')
    headerdata = ""
    for i in range(4):
        headerdata = headerdata + XYZfile.readline()
    dtypedict = {
        'X': str,
        'Y': str,
        'Z': str,
        'Atomic Number': int,
        'Species Number': int,
        'Atomic Symbol': str
    }
    df = pd.read_csv(filename,
                     delim_whitespace=True,
                     header=3,
                     names=[
                         'X', 'Y', 'Z', 'Atomic Number', 'Species Number',
                         'Atomic Symbol'
                     ],
                     dtype=dtypedict)
    configs = pd.read_csv(configlist, names=['J', 'K', 'Config'], dtype=str)

    # Figure out which atomic number and symbol go with which species:

    grouped = df.groupby('Species Number')
    at_nums = np.empty(len(grouped), dtype=object)
    at_sbls = np.empty(len(grouped), dtype=object)
    for sp_num, group in grouped:
        at_nums[sp_num - 1] = group['Atomic Number'].to_numpy()[0]
        # sp_num - 1 because FORTRAN arrays start at 1
        at_sbls[sp_num - 1] = group['Atomic Symbol'].to_numpy()[0]

    for config in configs['Config'].to_numpy():
        at_nums_list = np.empty(len(config), dtype=object)
        at_sbls_list = np.empty(len(config), dtype=object)
        sp_list = np.empty(len(config), dtype=object)
        uid = 0
        for i, charac in enumerate(config):
            sp_list[i] = int(charac) + 1
            uid += int(charac) * (len(at_nums))**i
            # Generate a unique ID from converting
            # the configuration to a decimal number
            at_nums_list[i] = at_nums[int(charac)]
            at_sbls_list[i] = at_sbls[int(charac)]
        temp = df.copy()
        temp['Species Number'] = sp_list
        temp['Atomic Number'] = at_nums_list
        temp['Atomic Symbol'] = at_sbls_list
        bodydata = temp.to_csv(index=False, header=False, sep='\t')
        dirname = "variation_{}".format(uid)
        dirpath = os.path.join(outputdir, dirname)
        try:
            os.mkdir(dirpath)
            XYZoutputpath = os.path.join(dirpath, 'XYZ')
            try:
                f = open(XYZoutputpath, 'a')
                f.write(headerdata)
                f.write(bodydata)
                f.close()
            except:
                print("Failed to write file {}".format(XYZoutputpath))
        except:
            print('Directory already present')


if __name__ == "__main__":
    main()
