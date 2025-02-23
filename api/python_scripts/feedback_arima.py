import sys
import pandas as pd
import numpy as np
import mysql.connector
from statsmodels.tsa.arima.model import ARIMA
import json
from datetime import datetime, timedelta


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  
    database="airline_dss_db"
)
cursor = conn.cursor()

query = """
    SELECT mg.tarih, mg.geri_bildirim, gk.aciklama
    FROM musteri_gorusleri mg
    JOIN geri_bildirim_kategorileri gk ON mg.geri_bildirim = gk.kod
"""
cursor.execute(query)
data = cursor.fetchall()

columns = ["tarih", "geri_bildirim", "aciklama"]
df = pd.DataFrame(data, columns=columns)
df["tarih"] = pd.to_datetime(df["tarih"])

complaints = df[df["geri_bildirim"].astype(str).str.startswith("0")]
suggestions = df[df["geri_bildirim"].astype(str).str.startswith("1")]

def train_arima(data):
    if len(data) < 10:
        return None 
    
    data = data.resample("ME").count()
    model = ARIMA(data.iloc[:, 0], order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=6)
    return forecast

forecast_results = []
for category, group in df.groupby("aciklama"):
    group.set_index("tarih", inplace=True)
    prediction = train_arima(group)
    
    if prediction is not None:
        trend = prediction.pct_change().mean()
        forecast_results.append({
            "kategori": category,
            "tahmin": prediction.tolist(),
            "trend": trend
        })

forecast_results.sort(key=lambda x: x["trend"], reverse=True)
top_5_categories = forecast_results[:5]

print(json.dumps(top_5_categories, default=str))

cursor.close()
conn.close()
