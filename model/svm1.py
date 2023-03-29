import os
import glob
import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score 

print('SVM')

files = glob.glob("./stock_dataset_with_label/2330/ask/*")
data = pd.read_csv(files[0], index_col=None)
data = data.drop(columns=['matchPri','openPri','bidPri1','bidPri2','bidPri3','bidPri4','bidPri5','askPri1','askPri2','askPri3','askPri4','askPri5'])


files = files[1:]

for f in files:
    d = pd.read_csv(f, index_col=None)
    d = d.drop(columns=['matchPri','openPri','bidPri1','bidPri2','bidPri3','bidPri4','bidPri5','askPri1','askPri2','askPri3','askPri4','askPri5'])
    data = data.append(d, ignore_index=True)


length = len(data)
train_length = int(length*7/10)
train_data = data[:train_length]
X_train = train_data.drop(columns=['label'])
y_train = train_data['label'].to_numpy()

test_data = data[train_length:]
X_test = test_data.drop(columns=['label'])
y_test = test_data['label'].to_numpy()

print(len(X_train))
print(len(X_test))

# Training a SVM classifier using SVC class
svm = SVC(kernel= 'linear', random_state=1, C=0.1, class_weight='balanced')
# svm = SVC(kernel= 'poly', degree=3, gamma='auto', C=1, class_weight='balanced')
svm.fit(X_train, y_train)

pred = svm.predict(X_test)
print(f"Precision Score: {precision_score(y_test, pred)*100:.2f}%")
print(f"Recall Score: {recall_score(y_test, pred)*100:.2f}%")
print(f"F1 score: {f1_score(y_test, pred)*100:.2f}%")
print(accuracy_score(y_test, pred))