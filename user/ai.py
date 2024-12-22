import torchvision.utils
import torch
import torch.nn as nn
import torch.nn.functional as F
from django.core.files.storage import default_storage
from torchvision import transforms
from PIL import Image

from .models import User

import os


class SiameseNetwork(nn.Module):
    def __init__(self):
        super(SiameseNetwork, self).__init__()

        self.cnn1 = nn.Sequential(
            nn.Conv2d(1, 96, kernel_size=11, stride=4),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2),

            nn.Conv2d(96, 256, kernel_size=5, stride=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),

            nn.Conv2d(256, 384, kernel_size=3, stride=1),
            nn.ReLU(inplace=True)
        )

        self.fc1 = nn.Sequential(
            nn.Linear(384, 1024),
            nn.ReLU(inplace=True),

            nn.Linear(1024, 256),
            nn.ReLU(inplace=True),

            nn.Linear(256, 2)
        )

    def forward_once(self, x):
        output = self.cnn1(x)
        output = output.view(output.size()[0], -1)
        output = self.fc1(output)
        return output

    def forward(self, input1, input2):
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)

        return output1, output2


def check_photo(user_photo, input_photo):
    net = SiameseNetwork()
    net.load_state_dict(torch.load("./ai/siamese-model.pth"))
    net.eval()

    transform = transforms.Compose([
        transforms.Resize((100, 100)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])

    image1_transformed = transform(user_photo.convert('L')).unsqueeze(0)
    image2_transformed = transform(input_photo.convert('L')).unsqueeze(0)

    output1, output2 = net(image1_transformed, image2_transformed)
    euclidean_distance = F.pairwise_distance(output1, output2)

    print(f'Dissimilarity: {euclidean_distance.item():.2f}')

    if euclidean_distance.item() <= 1.1:
        print('Confirmed')
        return True
    else:
        print('Denied')
        return False


def compare_user_photos(input_image):
    users = User.objects.all()
    for user in users:
        if user.photo:
            check_photo(user.photo, input_image)
