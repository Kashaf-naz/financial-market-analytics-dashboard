# import yfinance as yf
# from datetime import datetime, timedelta
# from statsmodels.tsa.stattools import adfuller
# from sklearn.metrics import median_squared_error, r2_score
# from statsmodels.tsa.arima.model import ARIMA
# import numpy as np
# import pandas as pd
# from sklearn.preprocessing import StandardScaler

# def get_data(ticker):
#     stock_data=yf.downlaod(ticker,start_date, end_date)
#     return stock_data[['Close']]

# def stationary_check(close_price):
#     adf_test = adfuller(close_price)
#     p_value = round(adf_test[1],3)
#     return p_value

# def get_rolling_mean(close_price):
#    rolling_price = close_price.rolling(window=7).mean().dropna()
#    return rolling_price
    
# def get_differencing_order(close_price):
#     p_value = stationary_check(close_price)
#     d=0
#     while True:
#         if p_value >0.05:
#             d +=1
#             close_price = close_price.diff().dropna()
#             p_value = stationary_check(close_price)
#         else:
#             break
#         return d

# def fit_model(data, differencing_order):
#     model = ARIMA(data, order=(30,differencing_order,30))
#     model_fit = model.fit()

#     forecast_step = 30
#     forecast = model_fit.get_forecast(steps = forecast_step)

#     predictions = forecast.prediction_mean
#     return predictions

# def evaluate_model(original_price, differencing_order):
#     train_data, test_data = original_price[:-30], original_price[-30:]
#     predictions = fit_model(train_data,differencing_order)
#     rmse = np.sqrt(mean_squared_error(test_data, predictions))
#     return round(rmse, 2)

# def scaling(close_price):
#     scaler = StandardScaler()
#     scaled_data = scaler.fit_transform(np.array(close_price).reshape(-1,1))
#     return scaled_data, scaler

# def get_forecast(original_price, differencing_order):
#     predictions = fit_model(original_price,differencing_order)
    


