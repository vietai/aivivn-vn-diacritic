from tensor2tensor.models.transformer import transformer_base
from tensor2tensor.utils import registry


@registry.register_hparams
def transformer_base_h256():
    hparams = transformer_base()
    hparams.hidden_size = 256
    return hparams
