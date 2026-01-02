

import pandas as pd

df = pd.read_csv(r"C:\Users\Stuteelekha Patnaik\fraud_detection\data\creditcard.csv")
# # print(df.head())


# # print(df.shape)
# # print(df.info())
# print(df['Class'].value_counts())

# import matplotlib.pyplot as plt
# import seaborn as sns

# sns.countplot(x='Class', data=df)
# plt.title("Fraud vs Normal Transactions")
# plt.show()
# print(df.describe())
# corr = df.corr()
# plt.figure(figsize=(12,8))
# sns.heatmap(corr, cmap='coolwarm', center=0)
# plt.title("Correlation Matrix")
# plt.show()



# model testing
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib

df['Amount'] = StandardScaler().fit_transform(df[['Amount']])
joblib.dump(StandardScaler().fit(df[['Amount']]), "model/scaler.pkl")
df['Hour'] = (df['Time'] // 3600) % 24
df.drop('Time', axis=1, inplace=True)
X = df.drop('Class', axis=1)
y = df['Class']

X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42, stratify=y
)

sm = SMOTE(random_state=42) 

X_train_res, y_train_res = sm.fit_resample(X_train, y_train) # pyright: ignore[reportAssignmentType]
print("Original:", y_train.value_counts())
print("After SMOTE:", y_train_res.value_counts())

import os
os.makedirs("processed", exist_ok=True)


X_train_res.to_csv('processed/X_train.csv', index=False)
X_test.to_csv('processed/X_test.csv', index=False)
y_train_res.to_csv('processed/y_train.csv', index=False)
y_test.to_csv('processed/y_test.csv', index=False)


# logistic regression

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

lr = LogisticRegression(max_iter=2000)
lr.fit(X_train, y_train)

lr_pred = lr.predict(X_test)
print("Logistic Regression:")
print(classification_report(y_test, lr_pred))

# random forest 
# rf = RandomForestClassifier(
#     n_estimators=80,          # lower trees
#     max_depth=10,             # restrict depth
#     n_jobs=-1,                # use all CPU cores
#     random_state=42
# )

from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)
print("Random Forest:")
print(classification_report(y_test, rf_pred))

# xgboost
from xgboost import XGBClassifier

xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='logloss'
)

xgb.fit(X_train, y_train)

xgb_pred = xgb.predict(X_test)
print("XGBoost:")
print(classification_report(y_test, xgb_pred))

import os
os.makedirs("models", exist_ok=True)


import joblib
joblib.dump(xgb, "models/fraud_model_xgb.pkl")
joblib.dump(rf, "models/fraud_model_rf.pkl")
model = joblib.load("models/fraud_model_rf.pkl")

new = {
    "V1": -1.23,
    "V2": 0.45,
    "V3": -0.67,
    "V4": 0.12,
    "V5": -0.33,
    "V6": 1.02,
    "V7": -0.89,
    "V8": 0.54,
    "V9": -0.21,
    "V10": 0.77,
    "V11": -0.44,
    "V12": 0.30,
    "V13": -0.10,
    "V14": 0.92,
    "V15": -0.58,
    "V16": 0.66,
    "V17": -0.47,
    "V18": 0.39,
    "V19": -0.95,
    "V20": 0.84,
    "V21": -0.22,
    "V22": 0.55,
    "V23": -0.48,
    "V24": 0.29,
    "V25": -0.66,
    "V26": 0.41,
    "V27": -0.77,
    "V28": -0.67,
    "Amount": 1000,
    "Hour": 14
}
import pandas as pd
new_df = pd.DataFrame([new])
new_df = new_df[X_train.columns]
prediction = model.predict(new_df)[0]
print("Fraud" if prediction == 1 else "Normal")

