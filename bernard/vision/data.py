import os

from torch.utils.data import Dataset

from typing import List, Tuple
from torchvision import transforms, utils
from skimage import io, transform

import math


def split_files_training_splits(file_path):
    pass


def list_dir(dir_path: str, file_ext: Tuple = (".jpg", ".png"),
             file_filter: List[str] = None) -> List[str]:
    """
    List all the files in a given directory
    :param dir_path:
    :param file_ext:
    :param file_filter:
    :return:
    """

    files = []

    for file in os.listdir(dir_path):
        if file.endswith(file_ext):

            if file_filter is not None and not any(map(lambda s: s in file.lower(), file_filter)):
                continue

            files.append(os.path.join(dir_path, file))

    return files


def _parse_space_label(base_file_name: str) -> float:
    label = float(base_file_name.split(" ")[-1])

    return label

def _parse_underline_label(base_file_name: str) -> float:
    label = float(base_file_name.split("_")[-1])

    return label

def parse_label(file_name: str) -> int:

    base_file_name = str(os.path.basename(file_name).split(".")[0])

    if "_" in base_file_name:
        label = _parse_underline_label(base_file_name)
    elif " "in base_file_name:
        label = _parse_space_label(base_file_name)
    else:
        raise ValueError("Could not parse label from file: {}".format(base_file_name))

    return round(label)





class RateMeDataset(Dataset):
    def __init__(self, genders: List[str], dir_path=None, file_paths=None):
        super(RateMeDataset, self).__init__()

        if file_paths is None and dir_path is None:
            raise ValueError("You must either pass a directory path or a list of file paths!")

        if file_paths is not None and dir_path is not None:
            raise ValueError("You must either pass a directory path or a list of file paths not both!")

        if dir_path is not None:
            file_paths = list_dir(dir_path, file_filter=genders)

        self.dir_path = dir_path
        self.file_paths = file_paths

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, item):
        file_path = self.file_paths[item]
        print(file_path)
        image = io.imread(file_path)
        label = parse_label(file_path)

        return {"image": image, "label": label}
