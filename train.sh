#!/usr/bin/env bash
set -euxo pipefail

export CUDA_VISIBLE_DEVICES=${1:-0,1,2,3}
N_GPUS=$[$(echo ${CUDA_VISIBLE_DEVICES} | grep -o ',' | wc -l)+1]

HPARAMS=${2:-transformer_relative}
MODEL=${3:-transformer}
PROBLEM=${4:-translate_vndt_large}

PROJECT=$(dirname ${BASH_SOURCE[0]})
T2T_CUSTOM=${PROJECT}/t2t
DATA_DIR=${PROJECT}/t2t_datagen
TMP_DIR=${PROJECT}/input
TRAIN_DIR=${PROJECT}/t2t_train/${PROBLEM}/${MODEL}-${HPARAMS}-${N_GPUS}

mkdir -p ${TRAIN_DIR}

# Train
t2t-trainer \
  --t2t_usr_dir=${T2T_CUSTOM} \
  --data_dir=${DATA_DIR} \
  --problem=${PROBLEM} \
  --model=${MODEL} \
  --hparams_set=${HPARAMS} \
  --output_dir=${TRAIN_DIR} \
  --worker_gpu=${N_GPUS} \
  --train_steps=10000000 \
  --local_eval_frequency=5000
