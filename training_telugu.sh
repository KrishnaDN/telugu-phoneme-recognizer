#!/bin/bash

# Change this location to somewhere where you want to put the data.


. ./cmd.sh
. ./path.sh

stage=0
. utils/parse_options.sh

set -euo pipefail

data=/media/newhd/MSR/train/telugu
lexicon_path=/home/krishna/Krishna/kaldi/egs/telugu_asr/s5/data_utils/lexicon.txt
local_lm_folder=data/local/lm


### Data preperation
python local/data_prep.py --dataset_path $data --processed_store_path data

## text prep
python local/lm_prep.py --lexicon_path $lexicon_path --vocab_folder $local_lm_folder

local/prepare_dict.sh --stage 3 --nj 30 --cmd run.pl \
data/local/lm data/local/lm data/local/dict_nosp

utils/prepare_lang.sh data/local/dict_nosp \
"<UNK>" data/local/lang_tmp_nosp data/lang_nosp



######################################################################
######### MFCC feature extraction
######################################################################
if [ $stage -le 2 ]; then
  mfccdir=mfcc

  for part in train test; do
    steps/make_mfcc.sh --cmd run.pl --nj 10 data/$part exp/make_mfcc/$part $mfccdir
    steps/compute_cmvn_stats.sh data/$part exp/make_mfcc/$part $mfccdir
  done

  utils/subset_data_dir.sh --shortest data/train 500 data/train_500short
fi

echo ============================================================================
echo "Finished successfully Training Monophone model."
echo ============================================================================
if [ $stage -le 3 ]; then
  steps/train_mono.sh --boost-silence 1.25 --nj 5 --cmd run.pl \
    data/train_500short data/lang_nosp exp/mono

  ### Generate alignments
  steps/align_si.sh --boost-silence 1.25 --nj 5 --cmd run.pl \
    data/train data/lang_nosp exp/mono exp/mono_ali_train
    
 steps/align_si.sh --boost-silence 1.25 --nj 5 --cmd run.pl \
    data/test data/lang_nosp exp/mono exp/mono_ali_test
fi

echo ============================================================================
echo "Finished successfully Training an delta + delta-delta triphone."
echo ============================================================================


# train a first delta + delta-delta triphone system on all utterances
if [ $stage -le 4 ]; then
  steps/train_deltas.sh --boost-silence 1.25 --cmd run.pl \
    2000 10000 data/train data/lang_nosp exp/mono_ali_train exp/tri1

  # decode using the tri1 model
  steps/align_si.sh --nj 5 --cmd run.pl \
    data/train data/lang_nosp exp/tri1 exp/tri1_ali_train
    
  steps/align_si.sh --nj 5 --cmd run.pl \
    data/test data/lang_nosp exp/tri1 exp/tri1_ali_test
fi


echo ============================================================================
echo "Finished successfully Training an LDA+MLLT system."
echo ============================================================================


if [ $stage -le 5 ]; then
  steps/train_lda_mllt.sh --cmd run.pl \
    --splice-opts "--left-context=3 --right-context=3" 2500 15000 \
    data/train data/lang_nosp exp/tri1_ali_train exp/tri2b


  # Align utts using the tri2b model
  steps/align_si.sh  --nj 5 --cmd run.pl --use-graphs true \
    data/train data/lang_nosp exp/tri2b exp/tri2b_ali_train

  steps/align_si.sh  --nj 5 --cmd run.pl --use-graphs false \
    data/test data/lang_nosp exp/tri2b exp/tri2b_ali_test
fi

echo ============================================================================
echo "Finished successfully Training LDA+MLLT+SAT"
echo ============================================================================

# Train tri3b, which is LDA+MLLT+SAT
if [ $stage -le 6 ]; then
  steps/train_sat.sh --cmd run.pl 2500 15000 \
    data/train data/lang_nosp exp/tri2b_ali_train exp/tri3b
 
 steps/align_si.sh  --nj 5 --cmd run.pl --use-graphs true \
    data/train data/lang_nosp exp/tri2b exp/tri3b_ali_train
 
 steps/align_si.sh  --nj 5 --cmd run.pl --use-graphs false \
    data/test data/lang_nosp exp/tri2b exp/tri3b_ali_test

fi


: '
# DNN hybrid system training parameters
dnn_mem_reqs="--mem 1G"
dnn_extra_opts="--num_epochs 20 --num-epochs-extra 10 --add-layers-period 1 --shrink-interval 3"

steps/nnet2/train_tanh.sh --mix-up 5000 --initial-learning-rate 0.015 \
  --final-learning-rate 0.002 --num-hidden-layers 5  \
  --num-jobs-nnet  5 --cmd run.pl "${dnn_train_extra_opts[@]}" \
  data/train data/lang_nosp exp/tri3b_ali_train exp/tri4_nnet

echo ============================================================================
echo "Finished successfully on" `date`
echo ============================================================================
'


