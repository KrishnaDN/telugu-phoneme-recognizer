#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 02:18:39 2020

@author: krishna
"""


import os
import argparse
from shutil import copyfile

def main(parser):
    lexicon_path =args.lexicon_path
    read_data = [line.strip('\n') for line in open(lexicon_path)]
    if not os.path.exists(args.vocab_folder):
        os.makedirs(args.vocab_folder)
    fid = open(os.path.join(args.vocab_folder,'vocab.txt'),'w')
    for item in read_data:
        word = item.split('\t')[0]
        fid.write(word+'\n')
    fid.close()
    dest_lexicon = os.path.join(args.vocab_folder,'lexicon.txt')
    copyfile(args.lexicon_path,dest_lexicon)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Configuration for data preparation")
    parser.add_argument("--lexicon_path", default="/home/krishna/Krishna/kaldi/egs/telugu_asr/s5/data_utils/lexicon.txt", type=str,help='Dataset path')
    parser.add_argument("--vocab_folder", default="data/local/lm", type=str,help='Save directory after processing')
    args = parser.parse_args()
    main(parser)