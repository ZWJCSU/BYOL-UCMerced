import torch
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image

root = "UCMerced_LandUse"

# 自定义图片图片读取方式，可以自行增加resize、数据增强等操作
def MyLoader(path):
    return Image.open(path).convert('RGB')
    
class MyDataset (Dataset):
    # 构造函数设置默认参数
    def __init__(self, txt, transform=None, target_transform=None, loader=MyLoader):
        with open(txt, 'r') as fh:
            imgs = []
            for line in fh:
                line = line.strip('\n')  # 移除字符串首尾的换行符
                line = line.rstrip()  # 删除末尾空
                words = line.split( )  # 以空格为分隔符 将字符串分成
                imgs.append((words[0], int(words[1]))) # imgs中包含有图像路径和标签
        self.imgs = imgs
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader

    def __getitem__(self, index):
        fn, label = self.imgs[index]
        #调用定义的loader方法
        img = self.loader(fn)
        if self.transform is not None:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.imgs)


train_data = MyDataset(txt=root + '/' + 'train.txt', transform=transforms.ToTensor())
test_data = MyDataset(txt=root + '/' + 'test.txt', transform=transforms.ToTensor())

#train_data 和test_data包含多有的训练与测试数据，调用DataLoader批量加载
train_loader = DataLoader(dataset=train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(dataset=test_data, batch_size=64)

print('加载成功！')
