#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 00:59:28 2020

@author: krishna
"""


import os
import glob
import argparse


class Telugu(object):
    def __init__(self,config):
        super(Telugu, self).__init__()
        self.dataset_path = config.dataset_path
        self.processed_store_path = config.processed_store_path
    
    def create_sent_dict(self,folder,mode='train'):
        self.transcripts_path  = os.path.join(folder,'transcription.txt')
        read_transcripts = [line.rstrip('\n') for line in open(self.transcripts_path)]
        sent_dict= {}
        for row in read_transcripts:
            filename = row.split('\t')[0]
            text_data = row.split('\t')[1]
            sent_dict[filename] = text_data
        return sent_dict
            
    
    
    def create_kaldi_files(self,mode='train'):
        folder = os.path.join(self.dataset_path,mode)
        
        self.data_root = os.path.join(folder,'Audios')
        self.transcripts_path  = os.path.join(folder,'transcription.txt')
        all_audio_files = sorted(glob.glob(self.data_root+'/*.wav'))
        wav_file = self.processed_store_path+'/'+mode+'/wav.scp'
        spk2utt = self.processed_store_path+'/'+mode+'/spk2utt'
        utt2spk = self.processed_store_path+'/'+mode+'/utt2spk'
        text_file = self.processed_store_path+'/'+mode+'/text'
        
        if not os.path.exists(self.processed_store_path+'/'+mode):
            os.makedirs(self.processed_store_path+'/'+mode)
        fid_wav = open(wav_file,'w')
        fid_spk2utt = open(spk2utt,'w')
        fid_utt2spk = open(utt2spk,'w')
        fid_text = open(text_file,'w')
        sent_dict = self.create_sent_dict(folder,mode)
        #print(all_audio_files)
        for audio_filepath in all_audio_files:
            filename = audio_filepath.split('/')[-1][:-4]
            to_write_wav=filename+' '+audio_filepath
            fid_wav.write(to_write_wav+'\n')
            to_write_spk2utt=filename+' '+filename
            fid_spk2utt.write(to_write_spk2utt+'\n')
            fid_utt2spk.write(to_write_spk2utt+'\n')
            to_write_text=filename+' '+sent_dict[filename]
            print(to_write_text)
            fid_text.write(to_write_text+'\n')
            
        fid_wav.close()
        fid_spk2utt.close()
        fid_utt2spk.close()
        fid_text.close()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser("Configuration for data preparation")
    parser.add_argument("--dataset_path", default="/media/newhd/MSR/train/telugu", type=str,help='Dataset path')
    parser.add_argument("--processed_store_path", default="data", type=str,help='Save directory after processing')

    config = parser.parse_args()    
                
    telugu = Telugu(config)
    telugu.create_kaldi_files(mode='train')
    telugu.create_kaldi_files(mode='test')

            
            
            
            
            
        