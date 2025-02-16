# -*- coding: utf-8 -*-
"""traffic_signs_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YZkscOebB4_Opq7pOPWUnCq0Bv87-SJU
"""

! git clone https://bitbucket.org/jadslim/german-traffic-signs.git

! ls
! ls german-traffic-signs

# libraries to be used in code
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import keras
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers import Flatten, Dropout, Dense
from keras.layers import Dropout
from keras.models import Model
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator
from keras.utils.np_utils import to_categorical
import requests
import random
import pickle
import cv2 as cv
from PIL import Image

# getting data and loading as training,valid and testing 
with open('german-traffic-signs/train.p', 'rb') as binary_file:
    train = pickle.load(binary_file)
with open('german-traffic-signs/valid.p', 'rb') as binary_file:
    valid = pickle.load(binary_file)
with open('german-traffic-signs/test.p', 'rb') as binary_file:
    test = pickle.load(binary_file)
   
# for k,v in train.items():
#     print(k,v)
    
x_train, y_train = train['features'], train['labels']
x_valid, y_valid = valid['features'], valid['labels']   
x_test,  y_test  =  test['features'],  test['labels']
# to see shapes
print(x_train.shape,y_train.shape)      
print(x_valid.shape,y_valid.shape)      
print(x_test.shape,y_test.shape)

# performing checks on data so that there might not be any incosistency
assert(x_train.shape[0] == y_train.shape[0]),'Number of samples and lables are not equal in train set'
assert(x_valid.shape[0] == y_valid.shape[0]),'Number of samples and lables are not equal in valid set'
assert(x_test.shape[0] == y_test.shape[0]),'Number of samples and lables are not equal in test set'

assert(x_train.shape[1:] == (32,32,3)),'shapes of images is not 32x32x3 in train set'
assert(x_valid.shape[1:] == (32,32,3)),'shapes of images is not 32x32x3 in valid set'
assert(x_test.shape[1:] == (32,32,3)),'shapes of images is not 32x32x3 in test set'

# visulization of dataset using matplotlib
np.random.seed(0)
classes_samples = []
classes = 43
cols = 5
data = pd.read_csv('german-traffic-signs/signnames.csv')
fig, axs = plt.subplots(nrows=classes,ncols=cols,figsize=(5,50))
fig.tight_layout()
for i in range(cols):
    for j,row in data.iterrows():
        x_selected = x_train[y_train == j]
        axs[j][i].imshow(x_selected[random.randint(0,len(x_selected)-1),:,:])
        axs[j][i].axis('off')
        if(i == 2):
            axs[j][i].set_title(str(j)+'-'+row[1])
            classes_samples.append(len(x_selected))
# print(axs.shape)

#plot image distribution
plt.figure(figsize=(15,5))
plt.bar(np.arange(classes),classes_samples)
plt.xlabel('class type')
plt.ylabel('No of samples')

def gray_scale(img):
    img = cv.cvtColor(img,cv.COLOR_RGB2GRAY)
    return img
def equalize(img):
    img = cv.equalizeHist(img)
    return img
def normalize(img):
    img = img/255
    return img
def preprocess(img):
    img = gray_scale(img)
    img = equalize(img)
    img = normalize(img)
    return img

x_train = np.array(list(map(preprocess,x_train)))
x_valid = np.array(list(map(preprocess,x_valid)))
x_test  = np.array(list(map(preprocess,x_test)))
x_train = x_train.reshape((34799,32,32,1))
x_valid = x_valid.reshape((4410,32,32,1))
x_test  = x_test.reshape((12630,32,32,1))
print(x_train.shape)
y_train = to_categorical(y_train)
y_valid = to_categorical(y_valid)
y_test = to_categorical(y_test)
print(y_valid.shape)

plt.imshow(x_train[1100].reshape(32,32),cmap = plt.get_cmap('gray'))

# performing checks on data so that there might not be any incosistency
assert(x_train.shape == (34799,32,32,1)),'shapes of images is not 34799x32x3x1 in train set'
assert(x_valid.shape == (4410,32,32,1)),'shapes of images is not 4410x32x3x1 in valid set'
assert(x_test.shape == (12630,32,32,1)),'shapes of images is not 12630x32x32x1 in test set'

assert(y_train.shape == (34799,43)),'shapes of images is not 34799x43 in train set'
assert(y_valid.shape == (4410,43)),'shapes of images is not 4410x43 in valid set'
assert(y_test.shape == (12630,43)),'shapes of images is not 12630x43 in test set'

# Data augmentation
data = ImageDataGenerator(width_shift_range=0.1,
                   height_shift_range=0.1,
                   zoom_range=[1,1.5],
                   rotation_range=0.1,
                   shear_range=10)
data.fit(x=x_train)

batches = data.flow(x=x_train,y=y_train,batch_size=20)
x_batch, y_batch = next(batches)

fig, axs = plt.subplots(1,15,figsize=(20,5))
fig.tight_layout()
print(x_batch.shape)
for i in range(15):
    axs[i].imshow(x_batch[i].reshape(32,32),cmap = plt.get_cmap('gray'))
    axs[i].axis('off')

# making model
def my_model():
    model = Sequential()
    model.add(Conv2D(120,
                     (5,5),
                     input_shape = (32,32,1),
                     activation='relu'))
    model.add(Conv2D(120,
                     (5,5),
                     activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Conv2D(60,
                     (5,5),
                     activation='relu'))
    model.add(Conv2D(60,
                     (5,5),
                     activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    # model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(units = 500,
                    activation='relu'))
    #model.add(Dropout(0.5))
    model.add(Dense(units = classes,
                    activation ='softmax'))
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

model = my_model()
H = model.fit_generator(data.flow(x=x_train,
              y = y_train,
              batch_size=50),
              steps_per_epoch=len(x_train)/50,          
              validation_data = (x_valid,y_valid),
              verbose= 1,
              epochs=10)

print(model.summary())

#  see statistics 
for key,value in H.history.items():
    print([key])
    
plt.plot(H.history['accuracy'])
plt.plot(H.history['val_accuracy'])
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['accuracy','val_accuracy'])
plt.show()

plt.plot(H.history['loss'])
plt.plot(H.history['val_loss'])
plt.legend(['loss','val_loss'])
plt.xlabel('epochs')
plt.ylabel('loss')
plt.show()

# evaluating on test set
scores = model.evaluate(x=x_test,y=y_test,verbose=1)
print('The loss is: ',scores[0]*100,'%')
print('The accuracy is: ',scores[1]*100,'%')

# testing model on a picture got from web (a real example)
url = 'https://sheelabhadra.github.io/assets/img/traffic_sign/stop.jpg'
raw_img = requests.get(url,stream=True)
img = Image.open(raw_img.raw)
plt.imshow(img)
plt.show()
img = np.asarray(img)
# print(img.shape)

img = cv.resize(img, (32, 32))
img = preprocess(img)
plt.imshow(img, cmap = plt.get_cmap('gray'))
# print(img.shape)
img = img.reshape(1, 32, 32, 1)
# print(img.shape)
print("predicted sign: "+ str(model.predict_classes(img)))

