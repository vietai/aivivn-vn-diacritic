from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.data_generators import translate
from tensor2tensor.utils import registry, metrics

# End-of-sentence marker.
EOS = text_encoder.EOS_ID

_VNDT_TRAIN_DATASETS = [["", ("train.d", "train.t")]]

_VNDT_DEV_DATASETS = [["", ("dev.d", "dev.t")]]

_VNDT_LARGE_TRAIN_DATASETS = [["", ("train_large.d", "train_large.t")]]

_VNDT_LARGE_DEV_DATASETS = [["", ("dev_large.d", "dev_large.t")]]


@registry.register_problem
class TranslateVndt(translate.TranslateProblem):
    @property
    def approx_vocab_size(self):
        return 2**15  # 32768

    def source_data_files(self, dataset_split):
        train = dataset_split == problem.DatasetSplit.TRAIN
        return _VNDT_TRAIN_DATASETS if train else _VNDT_DEV_DATASETS


@registry.register_problem
class TranslateVndtLarge(translate.TranslateProblem):
    @property
    def approx_vocab_size(self):
        return 2**15  # 32768

    def source_data_files(self, dataset_split):
        train = dataset_split == problem.DatasetSplit.TRAIN
        return _VNDT_LARGE_TRAIN_DATASETS if train else _VNDT_LARGE_DEV_DATASETS

    @property
    def decode_hooks(self):
        return []

    def eval_metrics(self):
        return [
            metrics.Metrics.ACC, metrics.Metrics.ACC_TOP5,
            metrics.Metrics.ACC_PER_SEQ, metrics.Metrics.NEG_LOG_PERPLEXITY,
        ]
