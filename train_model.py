import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

data = pd.DataFrame({
    "temp": [24,25,26,27,28,29,30,31,25,26,27,80,90,-5,100],
    "hum":  [45,48,50,52,55,57,60,62,49,51,53,10,5,95,3],
})

model = IsolationForest(contamination=0.2, random_state=42)
model.fit(data)

joblib.dump(model, "isolation_model.pkl")
print("_Isolation Forest model saved")

