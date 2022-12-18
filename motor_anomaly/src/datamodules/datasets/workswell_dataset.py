from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch
from PIL import Image
from albumentations import Compose
from torch.utils.data import Dataset


class WorkswellThermoDataset(Dataset):
    classes = {0: 'correct', 1: 'misalignment', 2: 'rotor'}

    def __init__(self,
                 images_list: List[Path],
                 augmentations: Compose
                 ):
        self._images_list = images_list
        self._augmentations = augmentations

    def _normalize(self, data):
        return (data - data.min()) / (data.max() - data.min()).astype(np.float32)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        image, frame_class = self._load_data(index)
        # image = self._normalize(image)

        image = np.stack([image, image, image], axis=-1)

        transformed = self._augmentations(image=image)
        image = transformed['image']
        
        # frame_class = torch.nn.functional.one_hot(torch.tensor(frame_class), num_classes=len(self.classes))
        frame_class = torch.tensor(frame_class)

        return image, frame_class

    def _load_data(self, index: int) -> Tuple[np.ndarray, int]:
        image_path = self._images_list[index]

        frame = np.asarray(Image.open(image_path), dtype=np.uint16)
        frame = frame[96:-96, 320:] # crop only squirrel cage motor

        if 'misalignment' in image_path.parents[1].name:
            frame_class = 1
        elif 'rotor' in image_path.parents[1].name:
            frame_class = 2
        else:
            frame_class = 0

        return frame, frame_class

    def __len__(self) -> int:
        return len(self._images_list)
