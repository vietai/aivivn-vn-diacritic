#!/usr/bin/env bash
set -euxo pipefail

export CUDA_VISIBLE_DEVICES=${1:-0}

SUFFIX=${2:-1}
HPARAMS=${3:-transformer_base}
MODEL=${4:-transformer}
PROBLEM=${5:-translate_vndt}

PROJECT=$(dirname ${BASH_SOURCE[0]})
T2T_CUSTOM=${PROJECT}/t2t
DATA_DIR=${PROJECT}/t2t_datagen
TMP_DIR=${PROJECT}/input
PREFIX=${PROBLEM}-${MODEL}-${HPARAMS}-${SUFFIX}
TRAIN_DIR=${PROJECT}/t2t_train/${PROBLEM}/${MODEL}-${HPARAMS}-${SUFFIX}

# Decode

DECODE_FILE=${TMP_DIR}/dev.d

BEAM_SIZE=4
ALPHA=0.6

t2t-decoder \
  --t2t_usr_dir=${T2T_CUSTOM} \
  --data_dir=${DATA_DIR} \
  --problem=${PROBLEM} \
  --model=${MODEL} \
  --hparams_set=${HPARAMS} \
  --output_dir=${TRAIN_DIR} \
  --decode_hparams="beam_size=${BEAM_SIZE},alpha=${ALPHA},batch_size=64" \
  --decode_from_file=${DECODE_FILE} \
  --decode_to_file=dev-raw-${PREFIX}.pred
