from flask import Flask, jsonify, render_template, request
import joblib
import pandas as pd

# Load saved model and preprocessing objects
loaded_model = joblib.load('model/gradient_boosting_model.pkl')  # Model
loaded_scaler = joblib.load('model/minmax_scaler.pkl')  # Scaler
loaded_label_encoders = joblib.load('model/label_encoders.pkl')  # Dictionary of label encoders
loaded_onehot_encoder = joblib.load('model/onehot_encoder.pkl')  # OneHotEncoder for categorical features


app = Flask(__name__)

# Feature definitions
# numerical_features = [
#     'income_annum', 'loan_amount', 'loan_term',
#     'cibil_score', 'residential_assets_value',
#     'commercial_assets_value', 'luxury_assets_value',
#     'bank_asset_value', 'no_of_dependents'
# ]
# categorical_features = ['education', 'self_employed']


@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/predict", methods=["POST"])
def predict():
        # Collect data from the form
        data = pd.DataFrame([{
            'Gender': request.form["Gender"],
            'Age': int(request.form["Age"]),
            'Married': request.form["Married"],
            'Number_of_Referrals': int(request.form["Number_of_Referrals"]),
            'Tenure_in_Months': int(request.form["Tenure_in_Months"]),
            'Phone_Service': request.form["Phone_Service"],
            'Multiple_Lines': request.form["Multiple_Lines"],
            'Internet_Type': request.form["Internet_Type"],
            'Online_Security': request.form["Online_Security"],
            'Online_Backup': request.form["Online_Backup"],
            'Device_Protection_Plan': request.form["Device_Protection_Plan"],
            'Premium_Support': request.form["Premium_Support"],
            'Streaming_TV': request.form["Streaming_TV"],
            'Streaming_Movies': request.form["Streaming_Movies"],
            'Streaming_Music': request.form["Streaming_Music"],
            'Unlimited_Data': request.form["Unlimited_Data"],
            'Contract': request.form["Contract"],
            'Paperless_Billing': request.form["Paperless_Billing"],
            'Payment_Method': request.form["Payment_Method"],
            'Monthly_Charge': float(request.form["Monthly_Charge"]),
            'Total_Charges': float(request.form["Total_Charges"]),
            'Total_Refunds': float(request.form["Total_Refunds"]),
            'Total_Extra_Data_Charges': float(request.form["Total_Extra_Data_Charges"]),
            'Total_Long_Distance_Charges': float(request.form["Total_Long_Distance_Charges"]),
            'Total_Revenue': float(request.form["Total_Revenue"]),
            'State': request.form["State"]
        }])

        # Step 1: Apply label encoding to categorical columns
        for col, le in loaded_label_encoders.items():
            if col in data.columns:
                data[col] = le.transform(data[col])

        # Step 2: Apply one-hot encoding to the 'State' column
        state_encoded = loaded_onehot_encoder.transform(data[['State']])
        state_encoded_df = pd.DataFrame(state_encoded, columns=loaded_onehot_encoder.get_feature_names_out(['State']))
        data = pd.concat([data.drop('State', axis=1), state_encoded_df], axis=1)

        # Step 3: Ensure all features required by the scaler are present
        for feature in loaded_scaler.feature_names_in_:
            if feature not in data.columns:
                data[feature] = 0  # Add missing columns with default values

        # Reorder columns to match scaler input
        data = data[loaded_scaler.feature_names_in_]

        # Step 4: Scale the data
        scaled_data = loaded_scaler.transform(data)

        # Step 5: Make predictions
        predictions = loaded_model.predict(scaled_data)  # 0--> Stayed, 1--> Churned

        if predictions == 1:
            status = "Churned"
        elif predictions == 0:
            status = "Stayed"
            
        # Step 6: Get prediction probabilities (optional)
        prediction_probs = loaded_model.predict_proba(scaled_data)

        # Return prediction result
        return render_template("home.html", predictions=status)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        response = {
            'status': 'success',
            'message': 'Form submitted successfully!',
            'data': {
                'name': name,
                'email': email,
                'message': message
            }
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
