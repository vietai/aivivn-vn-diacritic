# Vietnamese Diacritic Restoration
Vietnamese Diacritic Restoration using Transformer Sequence-to-Sequence Moddel


## Requirement
```
tensorflow-gpu==1.14.0
tensor2tensor==1.14.1
```

## Generate data
Generate data for default problem translate_vndt
```bash
./gen_data.sh
```

Generate data for custom problem A
```bash
./gen_data.sh A
```

## Train model
### Define problem 
```python
@registry.register_problem
class TranslateVndt(translate.TranslateProblem):
    @property
    def approx_vocab_size(self):
        return 2**15  # 32768

    def source_data_files(self, dataset_split):
        train = dataset_split == problem.DatasetSplit.TRAIN
        return _VNDT_TRAIN_DATASETS if train else _VNDT_DEV_DATASETS
```

### Define hyperparams
```python
@registry.register_hparams
def transformer_base_h256():
    hparams = transformer_base()
    hparams.hidden_size = 256
    return hparams
```

On problem `translate_vndt`, to train model `transformer` with hparams `transformer_base` on GPUs `0,1`
```bash
./train.sh 0,1 transformer_base transformer translate_vndt
```

## Predict
Similar to `train.sh`
```bash
./predict.sh 0,1 transformer_base transformer translate_vndt
```

The output is stored in `sub-translate_vndt-transformer-transformer_base.csv`