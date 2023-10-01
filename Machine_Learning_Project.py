# -*- coding: utf-8 -*-
"""FinalTask_Kalbe_DS_Silvia Astri Rahmaningrum.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18qzalggLMKy8MKLGLia9kQZYiuUW-dP_

# Regression Time Series

## Import Library
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pmdarima as pm

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
from yellowbrick.cluster import KElbowVisualizer

import warnings
warnings.filterwarnings('ignore')

!pip install pmdarima

"""## Import Data"""

df_customer = pd.read_csv('Customer.csv', sep=';')
df_product = pd.read_csv('Product.csv', sep=';')
df_store = pd.read_csv('Store.csv', sep=';')
df_transaction = pd.read_csv('Transaction.csv', sep=';')

"""## Data Preparation"""

df_customer.shape, df_product.shape, df_store.shape, df_transaction.shape

df_customer.info()

df_customer.head()

df_customer[df_customer['Marital Status'].isnull()]

#convert type object to float
df_customer['Income'] = df_customer['Income'].str.replace(',', '.').astype(float)

#fill missing values
df_customer.isna().sum()
df_customer.fillna(method='ffill', inplace=True)

df_product.info()

df_store.info()

df_transaction.info()

df_transaction.head()

#convert Date to datetime
df_transaction['Date'] = pd.to_datetime(df_transaction['Date'], format='%d/%m/%Y')

#merge df
merged_df = pd.merge(df_transaction, df_product, on='ProductID', how='left')
merged_df = pd.merge(merged_df, df_store, on='StoreID', how='left')
merged_df = pd.merge(merged_df, df_customer, on='CustomerID', how='left')
merged_df.head()

merged_df.info()

(merged_df['Price_x']/merged_df['Price_y']).value_counts()

"""Column Price_x and Price_y have a same value in each column, so one of the column can be drop"""

merged_df.drop(columns = 'Price_y', inplace=True)

data = merged_df
data.head()

data.info()

#change data type from object to float
data['Longitude'] = data['Longitude'].apply(lambda x: x.replace(',','.')).astype(float)
data['Latitude'] = data['Latitude'].apply(lambda x: x.replace(',','.')).astype(float)

data.info()

df_reg = data.groupby('Date').agg({'Qty':'sum'})
df_reg

# plot qty sales in a year
df_reg.plot(figsize=(12,8), title='Daily Sales', xlabel='Date', ylabel='Total Qty', legend=False)

#Split Data Training and Testing
print(df_reg.shape)
test_size = round(df_reg.shape[0] * 0.15)
train = df_reg.iloc[:-1*(test_size)]
test = df_reg.iloc[-1*(test_size):]
print(train.shape, test.shape)

plt.figure(figsize=(12,5))
sns.lineplot(data=train, x=train.index, y=train['Qty'])
sns.lineplot(data=test, x=test.index, y=test['Qty'])
plt.show()

"""## Data Stationary Check"""

def adf_test(dataset):
    df_test = adfuller(dataset, autolag = 'AIC')
    print("1. ADF : ", df_test[0])
    print("2. P-Value : ", df_test[1])
    print("3. Num Of Lags : ", df_test[2])
    print("4. Num Of Observations Used For ADF Regression : ", df_test[3])
    print("5. Critical Values : ")
    for key, val in df_test[4].items():
      print("\t",key, ": ", val)
adf_test(df_reg)

"""P-Value (0.00) < Alpha (0.05) shows that the data is stationary and can be used in time series analysis with ARIMA"""

# ACF and PACF plots
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(df_reg.diff().dropna(), lags=40, ax=ax[0])
plot_pacf(df_reg.diff().dropna(), lags=40, ax=ax[1])
plt.show()

"""## Modelling"""

#auto-fit ARIMA
auto_arima = pm.auto_arima(train, stepwise=False, seasonal=False)
auto_arima

"""### Hyperparameter Tuning"""

from itertools import product

p = range(0, 4)
d = range(0, 4)
q = range(0, 4)

pdq = list(product(p, d, q))
print(pdq)

aic_scores = []
for param in pdq:
  model = ARIMA(df_reg, order=param)
  model_fit = model.fit()
  aic_scores.append({'par': param, 'aic': model_fit.aic})

best_aic = min(aic_scores, key=lambda x: x['aic'])
print(best_aic)

#hyperparameter tuning
model_hyper = ARIMA(train, order=best_aic['par'])
model_fit_hyper = model_hyper.fit()

"""### Manual Hyperparameter Tuning"""

#Trial and error tuning (40,2,9)
model_manual = ARIMA(train, order=(30,1,9))
model_fit_manual = model_manual.fit()

"""### Plot Forecasting"""

forecast_manual = model_fit_manual.forecast(len(test))
forecast_hyper = model_fit_hyper.forecast(len(test))
forecast_auto = auto_arima.predict(len(test))

df_plot = df_reg.iloc[-100:]

df_plot['forecast_manual'] = [None]*(len(df_plot)-len(forecast_manual)) + list(forecast_manual)
df_plot['forecast_hyper'] = [None]*(len(df_plot)-len(forecast_hyper)) + list(forecast_hyper)
df_plot['forecast_auto'] = [None]*(len(df_plot)-len(forecast_auto)) + list(forecast_auto)

df_plot.plot()
plt.show()

"""## Metrics Evaluation"""

#Manual parameter tuning metrics 10.9 , 0.24 , 14.07
mae_manual = mean_absolute_error(test, forecast_manual)
mape_manual = mean_absolute_percentage_error(test, forecast_manual)
rmse_manual = np.sqrt(mean_squared_error(test, forecast_manual))

print(f'mae_manual : {round(mae_manual,3)}')
print(f'mape_manual : {round(mape_manual,3)}')
print(f'rmse_manual : {round(rmse_manual,3)}')

#Hyperparameter parameter tuning metrics
mae_hyper = mean_absolute_error(test, forecast_hyper)
mape_hyper = mean_absolute_percentage_error(test, forecast_hyper)
rmse_hyper = np.sqrt(mean_squared_error(test, forecast_hyper))

print(f'mae_hyper : {round(mae_hyper,3)}')
print(f'mape_hyper : {round(mape_hyper,3)}')
print(f'rmse_mhyper : {round(rmse_hyper,3)}')

#Auto-fit ARIMA metrics
mae_auto = mean_absolute_error(test, forecast_auto)
mape_auto = mean_absolute_percentage_error(test, forecast_auto)
rmse_auto = np.sqrt(mean_squared_error(test, forecast_auto))

print(f'mae_auto : {round(mae_auto,3)}')
print(f'mape_auto : {round(mape_auto,3)}')
print(f'rmse_auto : {round(rmse_auto,3)}')

"""The best evaluation metrics with Manual Hyperparameter Tuning with order (30,1,9)"""

## Apply model with "Manual Hyperparameter Tuning" to forecast data

model = ARIMA(df_reg, order=(30,1,9))
model_fit = model.fit()
forecast = model_fit.forecast(steps=31)

forecast

# Visualize Predictions
plt.figure(figsize=(12,5))
plt.plot(df_reg, color='blue')
plt.plot(forecast, color='green')
plt.title('Quantity Sales Forecasting')
plt.ylabel('Qty')
plt.xlabel('Date')
plt.show()

forecast.describe()

"""# Clustering"""

merged_df.head()

merged_df.corr()

df_cluster = merged_df.groupby('CustomerID').agg({'TransactionID':'count',
                                                  'Qty':'sum',
                                                  'TotalAmount' : 'sum'
                                                  }).reset_index().rename(columns={
                                                  'TransactionID' : 'count_transaction',
                                                  'Qty' : 'total_qty'
                                                  })
df_cluster

#drop CustomerID
df_cluster = df_cluster.drop(columns = ['CustomerID'])
df_cluster.head()

df_cluster.info()

df_cluster.isna().sum()

# scale data into same range
scaler = StandardScaler()
scaled_df = scaler.fit_transform(df_cluster[['count_transaction', 'total_qty', 'TotalAmount']])
scaled_df = pd.DataFrame(scaled_df, columns=['count_transaction', 'total_qty', 'TotalAmount'])
scaled_df.head()

# finding optimal number of clusters
inertia = []
max_clusters = 11
for n_cluster in range(1, max_clusters):
    kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=n_cluster)
    kmeans.fit(df_cluster)
    inertia.append(kmeans.inertia_)

plt.figure(figsize=(10,8))
plt.plot(np.arange(1, max_clusters), inertia, marker='o')
plt.xlabel('Number of cluster')
plt.ylabel('Inertia')
plt.xticks(np.arange(1, max_clusters))
plt.show()

# create cluster
n_cluster = 4
kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=n_cluster)
kmeans.fit(df_cluster)
df_cluster['cluster'] = kmeans.labels_

#
df_cluster['cluster'] = kmeans.labels_
df_cluster.head()

plt.figure(figsize=(6,6))
sns.pairplot(data=df_cluster,hue='cluster',palette='Set1')
plt.show()

df_cluster_mean = df_cluster.groupby('cluster').agg({'count_transaction':'mean','total_qty':'mean','TotalAmount':'mean'})
df_cluster_mean.sort_values('cluster', ascending = False)

data.info()

from google.colab import drive
drive.mount('/content/drive')

# Save the DataFrame to a CSV file
data.to_csv('/content/drive/MyDrive/Rakamin/data_join.csv', index=False, header=True)

