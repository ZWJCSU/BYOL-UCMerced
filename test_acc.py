# -*- coding: utf-8 -*-
"""UCMerced_linear_feature_eval.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1866eTCYkCpZd_9XeIJ54MatLGHhtBGsF
"""



import torch
import sys
import yaml
from torchvision import transforms, datasets
import torchvision
import numpy as np
import os
from sklearn import preprocessing
from torch.utils.data.dataloader import DataLoader
from models.resnet_base_network import ResNet18



# train_dataset = datasets.STL10('/home/thalles/Downloads/', split='train', download=False,
#                                transform=data_transforms)

# test_dataset = datasets.STL10('/home/thalles/Downloads/', split='test', download=False,
#                                transform=data_transforms)
from data.dataloader import MyDataset
from torchvision import datasets
from data.multi_view_data_injector import MultiViewDataInjector
from data.transforms import get_simclr_data_transforms
from data.dataloader import MyDataset
from models.mlp_head import MLPHead
from models.resnet_base_network import ResNet18





class LogisticRegression(torch.nn.Module):
    def __init__(self, input_dim, output_dim):
        super(LogisticRegression, self).__init__()
        self.linear = torch.nn.Linear(input_dim, output_dim)
        
    def forward(self, x):
        return self.linear(x)



def get_features_from_encoder(encoder, loader):
    
    x_train = []
    y_train = []

    # get the features from the pre-trained model
    for i, ((x1,x2),y) in enumerate(loader):
        # i=i.to(device)
        # x=x.to(device)
        # y=y.to(device)
        x1=torch.tensor([item.cpu().detach().numpy() for item in x1]).cuda() 
        with torch.no_grad():
            feature_vector = encoder(x1)
            x_train.extend(feature_vector)
            y_train.extend(y.numpy())

            
    x_train = torch.stack(x_train)
    y_train = torch.tensor(y_train)
    return x_train, y_train



def create_data_loaders_from_arrays(X_train, y_train, X_test, y_test):

    train = torch.utils.data.TensorDataset(X_train, y_train)
    train_loader = torch.utils.data.DataLoader(train, batch_size=64, shuffle=True)

    test = torch.utils.data.TensorDataset(X_test, y_test)
    test_loader = torch.utils.data.DataLoader(test, batch_size=512, shuffle=False)
    return train_loader, test_loader



def get_acc():
 batch_size = 8
 data_transforms = torchvision.transforms.Compose([transforms.ToTensor()])

 config = yaml.load(open("/content/BYOL-UCMerced/config/config.yaml", "r"), Loader=yaml.FullLoader)

 data_transform = get_simclr_data_transforms(**config['data_transforms'])

 train_dataset = MyDataset(txt='/content/BYOL-UCMerced/data/UCMerced_LandUse/Images/train.txt', transform=MultiViewDataInjector([data_transform, data_transform]))
 test_dataset = MyDataset(txt='/content/BYOL-UCMerced/data/UCMerced_LandUse/Images/test.txt', transform=MultiViewDataInjector([data_transform, data_transform]))

 print("Input shape:", len(train_dataset))

 train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size,
                           num_workers=0, drop_last=False, shuffle=True)

 test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size,
                           num_workers=0, drop_last=False, shuffle=True)

 print(type(train_loader))

 device = 'cuda' if torch.cuda.is_available() else 'cpu' #'cuda' if torch.cuda.is_available() else 'cpu'
 encoder = ResNet18(**config['network'])
 output_feature_dim = encoder.projetion.net[0].in_features



 #load pre-trained parameters
 load_params = torch.load(os.path.join('/content/BYOL-UCMerced/checkpoints/model.pth'),
                          map_location=torch.device(torch.device(device)))

 if 'online_network_state_dict' in load_params:
     encoder.load_state_dict(load_params['online_network_state_dict'])
     print("Parameters successfully loaded.")

 # remove the projection head
 encoder = torch.nn.Sequential(*list(encoder.children())[:-1])
 encoder = encoder.to(device)
 encoder.eval()
 
 logreg = LogisticRegression(output_feature_dim, 21)
 logreg = logreg.to(device)
 
 x_train, y_train = get_features_from_encoder(encoder, train_loader)
 x_test, y_test = get_features_from_encoder(encoder, test_loader)

 if len(x_train.shape) > 2:
     x_train = torch.mean(x_train, dim=[2, 3])
     x_test = torch.mean(x_test, dim=[2, 3])
     
 print("Training data shape:", x_train.shape, y_train.shape)
 print("Testing data shape:", x_test.shape, y_test.shape)
 
 scaler = preprocessing.StandardScaler()
 scaler.fit(x_train.cpu())
 x_train = scaler.transform(x_train.cpu()).astype(np.float32)
 x_test = scaler.transform(x_test.cpu()).astype(np.float32)

 train_loader, test_loader = create_data_loaders_from_arrays(torch.from_numpy(x_train), y_train, torch.from_numpy(x_test), y_test)

 optimizer = torch.optim.Adam(logreg.parameters(), lr=3e-4)
 criterion = torch.nn.CrossEntropyLoss()
 eval_every_n_epochs = 10

 for epoch in range(200):
#     train_acc = []
    for x, y in train_loader:
        x = x.to(device)
        y = y.to(device)
        # zero the parameter gradients
        optimizer.zero_grad()        
        
        logits = logreg(x)
        predictions = torch.argmax(logits, dim=1)
        
        loss = criterion(logits, y)
    
        loss.backward()
        optimizer.step()
    
    
    if epoch % eval_every_n_epochs == 0:
        train_total,total = 0,0
        train_correct,correct = 0,0
        for x, y in train_loader:
            x = x.to(device)
            y = y.to(device)

            logits = logreg(x)
            predictions = torch.argmax(logits, dim=1)
            
            train_total += y.size(0)
            train_correct += (predictions == y).sum().item()
        for x, y in test_loader:
            x = x.to(device)
            y = y.to(device)

            logits = logreg(x)
            predictions = torch.argmax(logits, dim=1)
            
            total += y.size(0)
            correct += (predictions == y).sum().item()
        train_acc=  train_correct / train_total 
        acc =  correct / total
        print(f"Training accuracy: {np.mean(train_acc)}")
        print(f"Testing accuracy: {np.mean(acc)}")

