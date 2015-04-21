#! /usr/bin/env python2
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2012-2015. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt.
# Contact: khmer-project@idyll.org
#
# pylint: disable=missing-docstring,invalid-name
"""
Count the overlap k-mers.

Overlap k-mers are those appearing in two sequence datasets.

usage: count-overlap_cpp.py [-h] [-q] [--ksize KSIZE] [--n_tables N_HASHES]
        [--tablesize HASHSIZE]
        1st_dataset(htfile generated by load-graph.py) 2nd_dataset(fastafile)
        result

Use '-h' for parameter help.
"""
from __future__ import print_function
import sys
import csv
import khmer
import textwrap
from khmer.kfile import check_input_files, check_space
from khmer.khmer_args import (build_hashbits_args, report_on_config, info)

DEFAULT_K = 32
DEFAULT_N_HT = 4
DEFAULT_HASHSIZE = 1e6


def get_parser():
    epilog = """
    An additional report will be written to ${output_report_filename}.curve
    containing the increase of overlap k-mers as the number of sequences in the
    second database increases.
    """
    parser = build_hashbits_args(
        descr='Count the overlap k-mers which are the k-mers appearing in two '
        'sequence datasets.', epilog=textwrap.dedent(epilog))
    parser.add_argument('ptfile', metavar='input_presence_table_filename',
                        help="input k-mer presence table filename")
    parser.add_argument('fafile', metavar='input_sequence_filename',
                        help="input sequence filename")
    parser.add_argument('report_filename', metavar='output_report_filename',
                        help='output report filename')
    parser.add_argument('--csv', default=False, action='store_true',
                        help='Use the CSV format for the curve output '
                        'in ${output_report_filename}.curve, '
                        'including column headers.')
    parser.add_argument('-f', '--force', default=False, action='store_true',
                        help='Overwrite output file if it exists')
    return parser


def main():
    info('count-overlap.py', ['counting'])
    args = get_parser().parse_args()
    report_on_config(args, hashtype='hashbits')

    for infile in [args.ptfile, args.fafile]:
        check_input_files(infile, args.force)

    check_space([args.ptfile, args.fafile], args.force)

    print('loading k-mer presence table from', args.ptfile, file=sys.stderr)
    ht1 = khmer.load_hashbits(args.ptfile)
    kmer_size = ht1.ksize()

    output = open(args.report_filename, 'w')
    f_curve_obj = open(args.report_filename + '.curve', 'w')
    if args.csv:
        f_curve_obj_csv = csv.writer(f_curve_obj)
        # write headers:
        f_curve_obj_csv.writerow(['input_seq', 'overlap_kmer'])

    ht2 = khmer.new_hashbits(kmer_size, args.min_tablesize, args.n_tables)

    (n_unique, n_overlap, list_curve) = ht2.count_overlap(args.fafile, ht1)

    printout1 = """\
dataset1(pt file): %s
dataset2: %s

# of unique k-mers in dataset2: %d
# of overlap unique k-mers: %d

""" % (args.ptfile, args.fafile, n_unique, n_overlap)
    output.write(printout1)

    for i in range(100):
        if args.csv:
            f_curve_obj_csv.writerow([list_curve[100 + i], list_curve[i]])
        else:
            print(list_curve[100 + i], list_curve[i], file=f_curve_obj)

    print('wrote to: ' + args.report_filename, file=sys.stderr)

if __name__ == '__main__':
    main()

# vim: set ft=python ts=4 sts=4 sw=4 et tw=79:
