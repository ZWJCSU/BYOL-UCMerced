# UCMerced-BYOL
### Using BYOL method to classify UCMerced dataset
![Image of Yaktocat](./assets/arch.png)

## Installation

Clone the repository and run
```
$ conda env create --name byol --file env.yml
$ conda activate byol
$ python main.py
```

## dataset

(http://weegee.vision.ucmerced.edu/datasets/landuse.html)

## Train preparation
![file list](img/file.png)

## Result
The Logistic Regression evaluation file is in eval/BYOL_UCMerced.ipynb
I update results every 40 epochs and save the model in checkpoints/model.pth
This is after I train for 80 epochs model's accuray
![file list](img/result.png)






## Feature Evaluation

We measure the quality of the learned representations by linear separability.

During training, BYOL learns features using the UCMerced ```train+unsupervised``` set and evaluates in the held-out ```test``` set.

|       Linear Classifier      | Feature  Extractor | Architecture | Feature dim | Projection Head  dim | Epochs | Batch  Size | Classification-accuracy |
|:----------------------------:|:------------------:|:------------:|:-----------:|:--------------------:|:------:|:-----------:|:-----------:|
| Logistic Regression  (Adam) |     BYOL (SGD)     |   [ResNet-18](https://drive.google.com/file/d/1Qj01H8cox8067cpCwhHZSQ0nfQl2RHbQ/view?usp=sharing)  |     512     |          128         |   120   | 16          |    58%    |

