#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 10:05:53 2020

@author: krishna
"""

import kaldi_io
import glob
import os
import sys
import numpy as np
import argparse

class Alignments(object):
    def __init__(self,config):
        super(Alignments, self).__init__()
        self.align_train_root = config.alignments_train_root
        self.align_test_root = config.alignments_test_root
        self.kaldi_root = config.kaldi_root
        self.store_aligns = config.store_path
        
        
    def convert_alignments(self,mode='train'):
        if mode=='train':
            gz_files = sorted(glob.glob(self.align_train_root+'/*.gz'))
        elif mode=='test':
            gz_files = sorted(glob.glob(self.align_test_root+'/*.gz'))
            
        model_file = os.path.join(self.align_train_root,'final.mdl')
        for gz_file in gz_files:
            src = '"ark:gunzip -c '+gz_file+'|"'
            dest = 'ark,t:'+gz_file[:-3]+'_ali.txt'
            convert = self.kaldi_root+'/src/bin/ali-to-pdf'+' '+model_file+' '+src+' '+dest
            os.system(convert)
            print('Successfully converted .gz to .txt')
    
    def extract_alignments(self,mode='train'):
        
        if mode=='train':
            self.convert_alignments(mode='train')
            all_aligns = sorted(glob.glob(self.align_train_root+'/*_ali.txt'))
        elif mode=='test':
            self.convert_alignments(mode='test')
            all_aligns = sorted(glob.glob(self.align_test_root+'/*_ali.txt'))
        else:
            print('Unknown mode')
            sys.exit()
                
        create_store = os.path.join(self.store_aligns,mode)
        if not os.path.exists(create_store):
            os.makedirs(create_store)
        for align_file in all_aligns:
            for key,mat in kaldi_io.read_ali_ark(align_file):
                save_path = os.path.join(create_store,key+'.npy')
                np.save(save_path,mat)
                print('Saving alignments for {}'.format(save_path))



if __name__ == '__main__':
    parser = argparse.ArgumentParser("Configuration for data preparation")
    parser.add_argument("--alignments_train_root", default="/home/krishna/Krishna/kaldi/egs/telugu_asr/s5/exp/tri3b_ali_train", type=str,help='Dataset path')
    parser.add_argument("--alignments_test_root", default="/home/krishna/Krishna/kaldi/egs/telugu_asr/s5/exp/tri3b_ali_test", type=str,help='Save directory after processing')
    parser.add_argument("--kaldi_root", default="/home/krishna/Krishna/kaldi", type=str,help='Dataset path')
    parser.add_argument("--store_path", default="/media/newhd/MSR/train/telugu/phoneme_alignments", type=str,help='Save directory after processing')
    

    config = parser.parse_args()
    align = Alignments(config)
    align.extract_alignments(mode='train')
    align.extract_alignments(mode='test')
    
