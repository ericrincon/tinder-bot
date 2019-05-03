import torch.nn as nn
import torchvision.models as models

_models = {
    "resnet18": models.resnet18,
    "alexnet": models.alexnet,
    "squeezenet": models.squeezenet1_0,
    "vgg16": models.vgg16,
    "densenet": models.densenet161,
    "incepetion": models.inception_v3,
}


def get_predefined_model(model_name: str):
    model_name = model_name.lower().strip()

    if model_name not in _models:
        raise ValueError("Model {} not defined".format(model_name))

    return _models[model_name]


class PretrainedModel(nn.Module):

    def __init__(self, model_name: str, nb_classes: int, pretrained: bool = True,
                 finetune: bool = False):
        super(PretrainedModel, self).__init__()

        self.feature_extractor = self._build_feature_extractor(model_name, pretrained)
        self.output = nn.Linear(self.feature_extractor, nb_classes)
        self.finetune = finetune

    def _set_model_trainable(self, model, trainable):
        """
        Sets the parameters of model so that they can be trainable or not

        :param model: a torchvision pretrained model
        :param trainable: boolean, True means the model parameters will be updated during training,
        false otherwise

        :return: model with updated parameters
        """

        for param in model.parameters():
            param.requires_grad = trainable

        return model

    def _fine_tune_model(self, model):
        """

        :param model:
        :return:
        """

        model = self._set_model_trainable(model, True)

        return model

    def _train_last_layer(self, model):
        """
        Replace the last layer in the model with a fully-connected layer, and freeze
        all layers before.

        :param model: a torchvision pretrained model
        :return: torchviison pretrained model with linear layer

        """

        model = self._set_model_trainable(model, False)

        model = self._set_linear_layer(model, None, None)

        return model

    def _build_feature_extractor(self, model_name, pretrained):
        Model = get_predefined_model(model_name)
        model = Model(pretrained)

        return model

    def _get_trainable_params(self):
        if self.finetune:
            return self.feature_extractor
        else:
            return self.feature_extractor.fc.params()

