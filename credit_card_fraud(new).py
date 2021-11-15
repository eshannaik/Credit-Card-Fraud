# -*- coding: utf-8 -*-
"""Credit Card Fraud.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1W1ESrNB3gcI_phv0oPYuKesuvaJST6UR

# Credit Card Fraud

### Importing and Understanding the dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import keras
from keras.layers import Dense,Input
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import regularizers
from keras.models import Model, Sequential
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score

d = pd.read_csv('creditcard.csv')

d.head()

zero = d['Class'].isin(['0']).sum()
zero

one = d['Class'].isin(['1']).sum()
one

d.info()

d.shape

d.describe()

d.isna().sum()

d.dropna(inplace=True)

d.isna().sum()

"""### Visualization"""

l=["Not Fraud","Fraud"]
a=[zero,one]
plt.pie(x=a,labels=l,autopct="%1.1f%%")
plt.legend()
plt.show()

"""##### Due to imbalance in data we will be taking only 1000 non fraud cases"""

fraud = d[d['Class']==1]
non_fraud = d[d['Class']==0].sample(1000)

df = non_fraud.append(fraud).sample(frac=1).reset_index(drop=True)

x = df.drop(['Class'], axis = 1).values
y = df['Class'].values

x.shape

print(y)

tsne = TSNE(n_components=2, random_state=0)
x1 = tsne.fit_transform(x)

plt.figure(figsize=(12,8))
plt.scatter(x1[np.where(y==0),0],x1[np.where(y==0),1],color='green',alpha=0.8, label="Not a Fraud")
plt.scatter(x1[np.where(y==1),0],x1[np.where(y==1),1],color='red',alpha=0.8, label="A Fraud")
plt.legend()
plt.show()

"""### Auto Encoder"""

mms=MinMaxScaler()
x_mms = mms.fit_transform(x)
x_nf = x_mms[y==0]
x_f = x_mms[y==1]

i = Input(shape=(x.shape[1],))

h1 = Dense(units=128,activation='tanh',activity_regularizer=regularizers.l1(10e-5))(i)
code = Dense(units=64,activation='sigmoid')(h1)

h2 = Dense(units=64,activation='tanh')(code)
h3 = Dense(units=128,activation='tanh')(h2)

o = Dense(x.shape[1],activation="softmax")(h3)

autoencoder = Model(i,o)

autoencoder.compile(optimizer="adam",loss="mse",metrics=['accuracy'])

autoencoder.fit(x_nf[0:2000], x_nf[0:2000], batch_size = 64, epochs = 200, shuffle = True, validation_split = 0.20)

hr = Sequential()

hr.add(autoencoder.layers[0])
hr.add(autoencoder.layers[1])
hr.add(autoencoder.layers[2])

normal = hr.predict(x_nf[:6000])
fraud = hr.predict(x_f)

rep_x = np.append(normal, fraud, axis = 0)
y_n = np.zeros(normal.shape[0])
y_f = np.ones(fraud.shape[0])
rep_y = np.append(y_n, y_f)

tsne = TSNE(n_components=2, random_state=0)
normal1 = tsne.fit_transform(rep_x)

plt.figure(figsize=(12,8))
plt.scatter(normal1[np.where(rep_y==0),0],normal1[np.where(rep_y==0),1],color='green',alpha=0.8, label="Not a Fraud")
plt.scatter(normal1[np.where(rep_y==1),0],normal1[np.where(rep_y==1),1],color='red',alpha=0.8, label="A Fraud")
plt.legend()
plt.show()

temp_x = d.drop(['Class'], axis = 1).sample(10000)
temp_y = d['Class'].sample(10000)

x_test_mms = mms.fit_transform(temp_x)

# temp_x = x_test_mms.drop(['Class'], axis = 1)
# temp_y = x_test_mms['Class']

x_train, x_test, y_train, y_test = train_test_split(temp_x, temp_y, test_size=0.20)
AC_AE = autoencoder.evaluate(x_test,y_test)
# y_pred_AE = autoencoder.predict(x_test)
# AC_AE = accuracy_score(rep_x,rep_y)
# print("test Loss", AC_AE[0])
print ("Accuracy Score: ", AC_AE)

"""### Logistic Regression"""

x_train, x_test, y_train, y_test = train_test_split(rep_x, rep_y, test_size=0.20)

lr = LogisticRegression()
lr.fit(x_train,y_train)

y_pred_lr = lr.predict(x_test)

print ("Classification Report: ")
print (classification_report(y_test, y_pred_lr))

AC_LR = accuracy_score(y_test, y_pred_lr)
print ("Accuracy Score: ", AC_LR)

"""### Random Forest"""

rf=RandomForestClassifier(n_estimators=100,random_state=0) 
rf.fit(x_train,y_train)

y_pred_rf = rf.predict(x_test)

print ("Classification Report: ")
print (classification_report(y_test, y_pred_rf))

AC_RFC = accuracy_score(y_test, y_pred_rf)
print ("Accuracy Score: ", AC_RFC)

"""### K Nearest Neighbours"""

knn = KNeighborsClassifier()
knn.fit(x_train,y_train)

y_pred_knn=knn.predict(x_test)

print ("Classification Report: ")
print (classification_report(y_test, y_pred_knn))

AC_KNN = accuracy_score(y_test,y_pred_knn)
print ("Accuracy Score: ", AC_KNN)

"""### Comparing Scores"""

plt.figure(figsize=(10,6))
scores=[AC_LR,AC_RFC,AC_KNN]
label=['Logistic Regression','Random Forest Classifier','K Nearest Neighbours']
for i in range(0,len(scores)):
    scores[i]=np.round(scores[i]*100,decimals=3)
ax=sns.barplot(x=label,y=scores)
plt.title('Comparing the Accuracy Scores of all the Models')
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.annotate('{:.3f}%'.format(height), (x +0.25, y + height + 0.8))
plt.show()

