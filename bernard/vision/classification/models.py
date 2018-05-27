import torch.nn as nn
import torchvision.models as models
import torch.optim as optim

class PretrainedModel:
    _models = {
        "resnet18": models.resnet18,
        "alexnet": models.alexnet,
        "squeezenet": models.squeezenet1_0,
        "vgg16": models.vgg16,
        "densenet": models.densenet161,
        "incepetion": models.inception_v3,
    }

    def __init__(self, model_name, pretrained=True, finetune=False):
        self.model_name = model_name
        self.finetune = finetune
        self.model = self._get_model(model_name, pretrained)




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

    def _set_linear_layer(self, model, nb_params, nb_classes):
        """

        :param model:
        :param nb_classes:
        :return:
        """

        model.fc = nn.Linear(nb_params, nb_classes)

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

    def _get_model(self, model_name, pretrained):
        if model_name not in self._models:
            raise ValueError("The model \"{}\" is not defined!")

        return self._models[model_name](pretrained)


    def _get_trainable_params(self):
        if self.finetune:
            return self.model
        else:
            return self.model.fc.params()


    def fit(self):
        params = self._get_trainable_params()

        optim.SGD(params, lr=1e-2, momentum=0.9)
