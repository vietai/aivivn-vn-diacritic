#!/usr/bin/env bash

PROBLEM=${1:-translate_vndt}

PROJECT=$(dirname ${BASH_SOURCE[0]})
T2T_CUSTOM=${PROJECT}/t2t
DATA_DIR=${PROJECT}/t2t_datagen
TMP_DIR=${PROJECT}/input

mkdir -p ${DATA_DIR}

# Generate data
t2t-datagen \
  --t2t_usr_dir=${T2T_CUSTOM} \
  --data_dir=${DATA_DIR} \
  --tmp_dir=${TMP_DIR} \
  --problem=${PROBLEM}
