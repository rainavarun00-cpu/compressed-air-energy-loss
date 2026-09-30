import sqlite3
import joblib
import pandas as pd


DATABASE = "data/sensor_data.db"
MODEL = "air_leak_model.pkl"


def detect_latest():

    model = joblib.load(MODEL)

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query("""
        SELECT *
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 1
    """, conn)

    conn.close()


    if df.empty:

        return {
            "status": "NO DATA",
            "score": 0
        }


    features = [
        "pressure_bar",
        "flow_lpm",
        "temperature_c",
        "power_kw"
    ]


    X = df[features]


    prediction = model.predict(X)[0]

    score = model.decision_function(X)[0]


    if prediction == -1:

        status = "POSSIBLE AIR LEAK"

    else:

        status = "NORMAL"


    return {
        "status": status,
        "score": round(float(score), 4),
        "data": df.iloc[0].to_dict()
    }


if __name__ == "__main__":

    result = detect_latest()

    print(result)