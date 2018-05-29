"""
Basic script for training a pretrained classifier on Tinder swiping data
"""

import argparse

import torchvision.transforms as transforms

from bernard.data.load import TinderProfileImageDataset
from bernard.vision.classification.models import PretrainedModel


def str2bool(value):
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')







def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--model", default="alexnet")
    arg_parser.add_argument("--pretrained", type=str2bool, default="1")
    arg_parser.add_argument("--data", default="tinder_data")
    args = arg_parser.parse_args()

    model = PretrainedModel(args.model, args.pretrained)

    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    tinder_profile_images = TinderProfileImageDataset(args.data)

if __name__ == '__main__':
    main()