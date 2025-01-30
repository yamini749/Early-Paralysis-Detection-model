from flask import Flask, request, jsonify
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import pandas as pd
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained model and scaler
model = load_model('Paralysis_model.h5')
scaler = StandardScaler()
scaler.fit(pd.read_csv('data2.xls').iloc[:, [0, 1, 2, 3]])

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse the input data
        data = request.json
        ecg = data.get('ecg')
        acc_x = data.get('acc_x')
        acc_y = data.get('acc_y')
        acc_z = data.get('acc_z')

        # Validate input data
        if None in [ecg, acc_x, acc_y, acc_z]:
            return jsonify({'error': 'Invalid input data'}), 400

        # Check if all values are below the threshold (200)
        if all(value < 200 for value in [ecg, acc_x, acc_y, acc_z]):
            return jsonify({'status': 'Paralyzed'})

        # Prepare input data for the model
        input_data = np.array([[ecg, acc_x, acc_y, acc_z]])
        input_data = scaler.transform(input_data)

        # Make prediction using the trained model
        prediction = model.predict(input_data)[0][0]

        # Determine the result based on prediction
        result = 'Paralyzed' if prediction >= 0.5 else 'Not Paralyzed'
        return jsonify({'status': result})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
