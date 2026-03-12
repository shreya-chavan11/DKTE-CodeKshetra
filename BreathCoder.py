import matplotlib
matplotlib.use('Agg') # Required for generating images without a GUI
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, url_for
import pandas as pd
import numpy as np
import os
import csv
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.neural_network import MLPClassifier
from matplotlib.collections import LineCollection

app = Flask(__name__)

# --- 1. CORE MODEL SETUP & TRAINING ---
def load_and_train():
    # Load your local dataset - Ensure Breath2.csv is in your GitHub root folder
    df = pd.read_csv('Breath2.csv')
    
    # Create target label based on clinical standards
    df['COPD_Label'] = (df['FEV1_FVC_Ratio'] < 0.70).astype(int)
    
    # Encoding Categorical Data
    le_gender = LabelEncoder()
    df['Gender_Enc'] = le_gender.fit_transform(df['Gender'])
    
    le_asthma = LabelEncoder()
    df['Asthma_Enc'] = le_asthma.fit_transform(df.get('Asthma_History', df['COPD_Label'])) 

    # Define features
    features = ['Age', 'Gender_Enc', 'BMI', 'Smoking_Pack_Years', 'Asthma_Enc', 'FEF_25_75_L_s', 'Concavity_Index']
    
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(df[features])
    
    # Neural Network Model
    model = MLPClassifier(hidden_layer_sizes=(32, 16), activation='relu', solver='lbfgs', random_state=42)
    model.fit(X_scaled, df['COPD_Label'])
    
    return model, scaler, features

# Initialize variables on startup
model, scaler, feature_cols = load_and_train()

# --- 2. NAVIGATION ROUTES ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
        else:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

        if name or message:
            with open('messages.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([name, email, message])

        return jsonify({"status": "success", "message": "Sent successfully"})
    
    return render_template('contact.html')

@app.route('/copd')
def copd():
    return render_template('copd.html')

# --- 3. AI PREDICTION & XAI VISUALIZATION ---
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    duration = float(data.get('duration', 0))
    age = float(data.get('age', 30))
    smoking = float(data.get('smoking', 0))
    gender = data.get('gender', 'Male')

    calc_ratio = max(0.40, 0.92 - (duration * 0.045))
    calc_fef = max(0.4, 5.0 / (1 + (duration * 0.3)))
    calc_concavity = min(0.98, 0.02 + (duration * 0.11))
    
    g_enc = 1 if gender == "Male" else 0

    input_vals = pd.DataFrame([[age, g_enc, 24.0, smoking, 0, calc_fef, calc_concavity]], columns=feature_cols)
    raw_prob = model.predict_proba(scaler.transform(input_vals))[0][1]

    if duration < 2.5:
        final_display_prob = raw_prob * 0.5
    elif 2.5 <= duration <= 5.5:
        final_display_prob = 0.25 + ((duration - 2.5) * 0.15)
    else:
        final_display_prob = min(0.99, 0.75 + ((duration - 5.5) * 0.05))
    
    risk_percent = final_display_prob * 100

    # Heatmap Generation
    t = np.linspace(0, 1, 100)
    flow = (1 - t) * (1 + 0.15 * (calc_fef / 5)) * (1 - (calc_concavity * 0.85) * np.sin(np.pi * t))
    flow = np.maximum(flow, 0)

    fig, ax = plt.subplots(figsize=(6, 4))
    pts = np.array([t, flow]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)

    if risk_percent < 20: cmap = 'Greens'
    elif risk_percent < 40: cmap = 'Blues'
    elif risk_percent < 75: cmap = 'YlOrBr'
    else: cmap = 'Reds'

    lc = LineCollection(segs, cmap=cmap, linewidth=10)
    lc.set_array(0.3 + (np.sin(np.pi * t) * final_display_prob))
    ax.add_collection(lc)
    
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.3)
    ax.set_axis_off()
    fig.patch.set_facecolor('#0f172a') 

    if not os.path.exists('static'):
        os.makedirs('static')
        
    graph_path = os.path.join('static', 'output_viz.png')
    fig.savefig(graph_path, bbox_inches='tight', transparent=True)
    plt.close(fig)

    if risk_percent < 30:
        status_note = "Optimal lung morphology detected."
        xai_detail = "Healthy profile with low airway resistance."
    elif risk_percent < 70:
        status_note = "Mild airflow limitation observed."
        xai_detail = "Slight 'scooped' concavity detected."
    else:
        status_note = "Significant obstruction detected."
        xai_detail = "Deep 'scooped' morphology indicates obstructive conditions."

    return jsonify({
        "risk": round(risk_percent, 1),
        "viz_url": url_for('static', filename='output_viz.png') + "?t=" + str(np.random.randint(1000)),
        "ratio": round(calc_ratio, 2),
        "fef": round(calc_fef, 2),
        "note": status_note,
        "xai_text": xai_detail
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 