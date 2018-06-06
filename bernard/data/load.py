import os
import random

from torch.utils.data import Dataset, DataLoader
from skimage import io, transform
from util.filesys import read_all_files


class TinderProfileImageDataset(Dataset):
    """
    Tinder profile images dataset.
    """

    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir


        postive_example_dir = os.path.join(root_dir, "swipe_right")
        negative_example_dir = os.path.join(root_dir, "swipe_left")
        # Images that would result in a "right swipe"
        positive_example_files = [(path, 1) for path in
                                 read_all_files(postive_example_dir, "jpg")]

        # Image that would result in a "left swipe"
        negative_examples_files = [(path, 0) for path in
                                   read_all_files(negative_example_dir, "jpg")]

        # Combine the two lists and shuffle
        self.examples = positive_example_files + negative_examples_files
        random.shuffle(self.examples)

        self.transform = transform

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        img_path = self.examples[idx][0]
        label = self.examples[idx][1]

        image = io.imread(img_path)

        sample = {'image': image, 'label': label}

        if self.transform:
            sample = self.transform(sample)

        return sample