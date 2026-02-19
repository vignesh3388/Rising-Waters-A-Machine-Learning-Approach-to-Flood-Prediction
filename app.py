from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from joblib import load

app = Flask(__name__)

# Load model and scaler
model = load('floods.save')
scaler = load('transform.save')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Cloud Cover, ANNUAL, Jan-Feb, Mar-May, Jun-Sep
        try:
            cloud_cover = float(request.form['cloud_cover'])
            annual = float(request.form['annual'])
            jan_feb = float(request.form['jan_feb'])
            mar_may = float(request.form['mar_may'])
            jun_sep = float(request.form['jun_sep'])

            features = np.array([[cloud_cover, annual, jan_feb, mar_may, jun_sep]])
            features_scaled = scaler.transform(features)
            
            # Get probability and prediction
            probability = model.predict_proba(features_scaled)[0][1] * 100
            prediction = model.predict(features_scaled)
            
            # Determine Flood Level and Precautions
            if probability < 10:
                level = "Very Low"
                alert_class = "success"
                precautions = [
                    "Stay informed about weather updates.",
                    "No immediate action required."
                ]
            elif 10 <= probability < 30:
                level = "Low"
                alert_class = "info"
                precautions = [
                    "Monitor local news and weather reports.",
                    "Keep an emergency contact list ready.",
                    "Ensure gutters and drains are clear."
                ]
            elif 30 <= probability < 60:
                level = "Medium"
                alert_class = "warning"
                precautions = [
                    "Prepare an emergency kit (food, water, medicine).",
                    "Move valuables and electrical items to higher ground.",
                    "Identify safe evacuation routes."
                ]
            else:
                level = "High"
                alert_class = "danger"
                precautions = [
                    "Evacuate if advised by local authorities.",
                    "Turn off utilities (gas, electricity, water).",
                    "Avoid walking or driving through floodwaters.",
                    "Stay on higher ground."
                ]

            result = f"Flood Risk: {level} ({probability:.2f}%)"
            accuracy = 97.0  # From notebook evaluation
                
            return render_template('home.html', 
                                 prediction_text=result, 
                                 alert_class=alert_class, 
                                 probability=probability,
                                 flood_level=level,
                                 precautions=precautions,
                                 model_accuracy=accuracy)
        except Exception as e:
            return render_template('home.html', prediction_text=f"Error: {str(e)}", alert_class="warning")

if __name__ == "__main__":
    app.run(debug=True)
