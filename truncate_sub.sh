#!/usr/bin/env bash

INPUT=${1:-submission.csv}

cut -d ',' -f 1 ${INPUT} > ${INPUT}.ids
grep -Fxvf input/sample_submission.ids ${INPUT}.ids > diff.ids
grep -xvf diff.ids ${INPUT} > trunc_${INPUT}
rm diff.ids ${INPUT}.ids
