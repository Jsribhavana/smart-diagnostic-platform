from __future__ import annotations
import joblib
from flask import Flask, request, jsonify
from pathlib import Path
import pandas as pd
import re
from io import BytesIO
import os
import requests
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:
    pdfminer_extract_text = None
# Ensure we can run as a script without package context
# Set project ROOT to parent of this file's directory (diabetes_stacking_model)
ROOT = Path(__file__).resolve().parents[1]

app = Flask(__name__)

# Basic CORS headers to allow frontend (localhost:3000) to call the API
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

MODEL_PATH = ROOT / 'models' / 'stacking_model.pkl'
SCALER_PATH = ROOT / 'models' / 'scaler.pkl'
FOOD_PATH = ROOT / 'data' / 'indian_food.csv'
PRODUCTS_PATH = ROOT.parents[0] / 'madhumeha-app' / 'src' / 'dataset' / 'products_with_links.csv'
HOSPITALS_PATH = ROOT.parents[0] / 'madhumeha-app' / 'src' / 'dataset' / 'remaining_hospitals.csv'
HOSPITALS_EXCEL_PATH = ROOT / 'data' / 'hospitals_lat_long.xlsx'

model = None
scaler = None
food_df = None

def load_artifacts():
    global model, scaler, food_df
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
    if SCALER_PATH.exists():
        scaler = joblib.load(SCALER_PATH)
    if FOOD_PATH.exists():
        food_df = pd.read_csv(FOOD_PATH)

load_artifacts()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model_loaded': model is not None})

@app.route('/products', methods=['GET'])
def products():
    try:
        if not PRODUCTS_PATH.exists():
            return jsonify({'error': 'Products dataset not found'}), 404
        df = pd.read_csv(PRODUCTS_PATH)
        # Normalize text columns
        for c in ['name', 'ingredients', 'flavor_profile', 'course', 'Amazon_Link', 'Flipkart_Link']:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str)
        # Exclude obvious sweets/desserts
        sweet_mask = df['flavor_profile'].str.lower().str.contains('sweet') if 'flavor_profile' in df.columns else False
        dessert_mask = df['course'].str.lower().str.contains('dessert') if 'course' in df.columns else False
        dessert_words = ['laddu','jalebi','gulab','halwa','barfi','kheer','rasgulla','sandesh','peda','mithai','cake','cookie','ice cream','pithe','petha','rabri','modak','shrikhand']
        name_has_dessert = df['name'].str.lower().apply(lambda x: any(w in x for w in dessert_words)) if 'name' in df.columns else False
        exclude = sweet_mask | dessert_mask | name_has_dessert
        # Include explicit diabetes-friendly signals
        allow_words = [
            'diabetic','diabetes','sugar-free','no sugar','unsweetened','whole','multigrain','brown rice','oats','quinoa','whole wheat',
            'low glycemic','low gi','stevia','monk fruit','erythritol','protein','fiber'
        ]
        def has_allow(row):
            doc = (' '.join([str(row.get('name','')), str(row.get('ingredients','')), str(row.get('Amazon_Link','')), str(row.get('Flipkart_Link',''))])).lower()
            return any(w in doc for w in allow_words)
        df['allow_hit'] = df.apply(has_allow, axis=1)
        # Friendly: allow signal OR not excluded sweets/desserts
        friendly = df['allow_hit'] | (~exclude)
        df_f = df[friendly]
        cols = [c for c in ['name', 'Amazon_Link', 'Flipkart_Link'] if c in df_f.columns]
        items = df_f[cols].dropna(how='all').head(60).to_dict(orient='records')
        return jsonify({'items': items, 'count': len(items)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hospitals', methods=['GET'])
def hospitals():
    try:
        # Try to load from Excel file first (has lat/long), fallback to CSV
        df = None
        if HOSPITALS_EXCEL_PATH.exists():
            try:
                df = pd.read_excel(HOSPITALS_EXCEL_PATH, engine='openpyxl')
            except ImportError:
                # openpyxl not installed, will fallback to CSV
                pass
            except Exception as e:
                # Other errors reading Excel, log and fallback
                print(f"Warning: Could not read Excel file: {e}")
                pass
        if df is None and HOSPITALS_PATH.exists():
            df = pd.read_csv(HOSPITALS_PATH)
        if df is None:
            return jsonify({'error': 'Hospitals dataset not found'}), 404
        
        pincode = str(request.args.get('pincode', '') or '').strip()
        city = str(request.args.get('city', '') or '').strip().lower()
        state = str(request.args.get('state', '') or '').strip().lower()
        near = str(request.args.get('near', '') or '').strip()
        
        # Normalize column names (case-insensitive matching)
        col_map = {}
        for c in df.columns:
            c_lower = c.lower().strip()
            if 'hospital' in c_lower or 'name' in c_lower:
                col_map[c] = 'Hospital'
            elif 'city' in c_lower:
                col_map[c] = 'City'
            elif 'state' in c_lower:
                col_map[c] = 'State'
            elif 'address' in c_lower or 'local' in c_lower:
                col_map[c] = 'LocalAddress'
            elif 'pincode' in c_lower or 'pin' in c_lower:
                col_map[c] = 'Pincode'
            elif 'latitude' in c_lower or 'lat' in c_lower:
                col_map[c] = 'Latitude'
            elif 'longitude' in c_lower or 'long' in c_lower or 'lng' in c_lower or 'lon' in c_lower:
                col_map[c] = 'Longitude'
        df = df.rename(columns=col_map)
        
        # Normalize Pincode to 6-digit strings
        if 'Pincode' in df.columns:
            def norm_pin(v):
                try:
                    s = str(v).strip()
                    if s.endswith('.0'):
                        s = s[:-2]
                    return s
                except Exception:
                    return ''
            df['Pincode'] = df['Pincode'].apply(norm_pin)
        if 'City' in df.columns:
            df['City'] = df['City'].fillna('').astype(str)
        if 'State' in df.columns:
            df['State'] = df['State'].fillna('').astype(str)
        
        # Filter by pincode if provided
        if pincode:
            df = df[df['Pincode'] == pincode]
        # Filter by city/state if provided
        if city:
            df = df[df['City'].str.lower() == city]
        if state:
            df = df[df['State'].str.lower() == state]
        # Near option: if set and no filters present, return top entries
        if near in ('1','true','yes') and not any([pincode, city, state]):
            pass
        
        # Select columns including lat/long if available
        cols = [c for c in ['Hospital','City','State','LocalAddress','Pincode','Latitude','Longitude'] if c in df.columns]
        items = df[cols].dropna(how='all').head(50).to_dict(orient='records')
        
        # Convert lat/long to float if present
        for item in items:
            if 'Latitude' in item and item['Latitude'] is not None:
                try:
                    item['Latitude'] = float(item['Latitude'])
                except (ValueError, TypeError):
                    item['Latitude'] = None
            if 'Longitude' in item and item['Longitude'] is not None:
                try:
                    item['Longitude'] = float(item['Longitude'])
                except (ValueError, TypeError):
                    item['Longitude'] = None
        
        return jsonify({'items': items, 'count': len(items)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 204)
    payload = request.get_json(force=True)
    # Expected fields
    fields = [
        'hba1c', 'glucose', 'blood_pressure', 'skin_thickness', 'insulin',
        'nju', 'age', 'smoker', 'physicalactivity', 'bmi_category'
    ]
    missing = [f for f in fields if f not in payload]
    if missing:
        return jsonify({'error': f'Missing fields: {missing}'}), 400

    if model is None or scaler is None:
        return jsonify({'error': 'Model not loaded. Train and save artifacts first.'}), 500

    # Assemble single-row input
    X = pd.DataFrame([payload], columns=fields)
    X_proc = scaler.transform(X)  # ColumnTransformer handles numeric+categorical
    current_proba = float(model.predict_proba(X_proc)[:, 1][0])
    current_pred = int(current_proba >= 0.5)

    # Compute future risk using simple heuristic over lifestyle and clinical factors
    age = float(payload.get('age', 0) or 0)
    smoker = int(payload.get('smoker', 0) or 0)
    pa = float(payload.get('physicalactivity', 0) or 0)  # 0–3 scale expected
    bp = float(payload.get('blood_pressure', 0) or 0)
    hba1c = float(payload.get('hba1c', 0) or 0)
    bmi_cat = str(payload.get('bmi_category', '') or '').lower()

    risk_points = 0.0
    if age >= 60:
        risk_points += 3
    elif age >= 45:
        risk_points += 2
    if smoker == 1:
        risk_points += 2
    if pa <= 0:
        risk_points += 2
    elif pa == 1:
        risk_points += 1
    elif pa >= 3:
        risk_points -= 1
    if 'obese' in bmi_cat or 'overweight' in bmi_cat:
        risk_points += 2
    if bp >= 130:
        risk_points += 1
    if 5.7 <= hba1c < 6.5:
        risk_points += 2

    import math
    future_proba = 1 / (1 + math.exp(-(-2 + 0.8 * current_proba + 0.5 * risk_points)))

    def risk_label(p: float) -> str:
        return 'High' if p >= 0.7 else ('Moderate' if p >= 0.4 else 'Low')

    current_risk = risk_label(current_proba)
    future_risk = risk_label(future_proba)

    suggestions = {'recommended': [], 'avoid': []}
    explanation_parts = []
    if hba1c >= 6.5:
        explanation_parts.append('Elevated HbA1c indicates current diabetes range, strongly increasing present risk.')
    elif hba1c >= 5.7:
        explanation_parts.append('HbA1c in prediabetes range raises future risk if lifestyle is not improved.')
    if bp >= 130:
        explanation_parts.append('Higher blood pressure contributes to long-term cardiovascular and diabetes risk.')
    if smoker == 1:
        explanation_parts.append('Smoking elevates insulin resistance and future diabetes risk.')
    if pa <= 1:
        explanation_parts.append('Lower physical activity increases insulin resistance and weight gain risk.')
    if 'obese' in bmi_cat or 'overweight' in bmi_cat:
        explanation_parts.append('Weight category suggests higher insulin resistance and future risk.')

    explanation = (
        f"Your present risk is {current_proba:.2%} ({current_risk}), and your projected future risk is {future_proba:.2%} ({future_risk}). "
        + " ".join(explanation_parts or [
            'Your biometrics and lifestyle inputs collectively determine these probabilities, with HbA1c and glucose driving present risk, and age, activity, BMI, and smoking status shaping future risk.'
        ]) + " Based on your risk profile, we recommend focusing on Indian foods with lower glycemic index and minimizing refined, high-GI items."
    )

    if food_df is not None:
        low_gi = food_df[food_df['glycemic_index'] <= 55]
        high_gi = food_df[food_df['glycemic_index'] >= 70]
        suggestions['recommended'] = (
            low_gi.head(12)[['food', 'recommendation_notes']].to_dict(orient='records')
        )
        suggestions['avoid'] = (
            high_gi.head(10)[['food', 'recommendation_notes']].to_dict(orient='records')
        )

    return jsonify({
        'current_prediction': current_pred,
        'current_probability': current_proba,
        'current_risk_level': current_risk,
        'future_probability': future_proba,
        'future_risk_level': future_risk,
        'diet_recommendations': suggestions,
        'explanation': explanation
    })

def _infer_bmi_category(bmi: float) -> str:
    if bmi <= 0:
        return 'Normal'
    if bmi < 25:
        return 'Normal'
    if bmi < 30:
        return 'Overweight'
    return 'Obese'

def _extract_values_from_text(text: str) -> dict:
    vals = {}
    def num(s):
        try:
            return float(s)
        except Exception:
            return None
    m = re.search(r'(Hb\s*A1c|A1c|Glycated\s+Hemoglobin|HbA1c)[^\d]*([0-9]+(?:\.[0-9]+)?)\s*%?', text, flags=re.IGNORECASE)
    if m:
        vals['hba1c'] = num(m.group(2))
    m = re.search(r'(Fasting Plasma Glucose|Fasting Glucose|FPG|FBG)[^\d]*([0-9]{2,3})\s*mg/?dL?', text, flags=re.IGNORECASE)
    if m:
        vals['glucose'] = num(m.group(2))
    m = re.search(r'(Postprandial|Post[- ]meal|PPG|PPBS|PBG|PLBS|Random Glucose|RBS)[^\d]*([0-9]{2,3})\s*mg/?dL?', text, flags=re.IGNORECASE)
    if m:
        vals['skin_thickness'] = num(m.group(2))
    m = re.search(r'(Blood Pressure|BP)[^\d]*([0-9]{2,3})(?:\s*/\s*([0-9]{2,3}))?', text, flags=re.IGNORECASE)
    if m:
        vals['blood_pressure'] = num(m.group(1))
    m = re.search(r'Insulin[^\d]*([0-9]+(?:\.[0-9]+)?)', text, flags=re.IGNORECASE)
    if m:
        vals['insulin'] = num(m.group(1))
    m = re.search(r'Age[^\d]*([0-9]{1,3})', text, flags=re.IGNORECASE)
    if m:
        vals['age'] = num(m.group(1))
    m = re.search(r'BMI[^\d]*([0-9]+(?:\.[0-9]+)?)', text, flags=re.IGNORECASE)
    if m:
        bmi = num(m.group(1)) or 0.0
        vals['bmi_category'] = _infer_bmi_category(bmi)
    return vals

def _ocr_image_bytes(data: bytes) -> str:
    try:
        from PIL import Image as _Img
        import pytesseract as _tess
    except Exception:
        return ''
    try:
        img = _Img.open(BytesIO(data))
        return _tess.image_to_string(img) or ''
    except Exception:
        return ''

def _ocr_pdf_bytes_with_fitz(data: bytes) -> str:
    try:
        import fitz  # PyMuPDF
        from PIL import Image as _Img
        import pytesseract as _tess
    except Exception:
        return ''
    text = ''
    try:
        doc = fitz.open(stream=data, filetype='pdf')
        for page in doc:
            pix = page.get_pixmap(alpha=False)
            img = _Img.frombytes('RGB', [pix.width, pix.height], pix.samples)
            t = _tess.image_to_string(img) or ''
            text += '\n' + t
    except Exception:
        return ''
    return text

@app.route('/extract-report', methods=['POST'])
def extract_report():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file provided'}), 400
    text = ''
    ct = (f.content_type or '').lower()
    data = f.read()
    bio = BytesIO(data)
    method = 'none'
    if PdfReader is not None and ('pdf' in ct or f.filename.lower().endswith('.pdf')):
        try:
            reader = PdfReader(bio)
            for page in reader.pages:
                t = page.extract_text() or ''
                text += '\n' + t
            if text:
                method = 'pypdf2'
        except Exception:
            pass
    if not text and ('pdf' in ct or f.filename.lower().endswith('.pdf')):
        ocr_text = _ocr_pdf_bytes_with_fitz(data)
        if ocr_text:
            text = ocr_text
            method = 'pymupdf+ocr'
    # Fallback to pdfminer if text not extracted via PyPDF2
    if not text and ('pdf' in ct or f.filename.lower().endswith('.pdf')) and 'pdfminer_extract_text' in globals() and pdfminer_extract_text is not None:
        try:
            text = pdfminer_extract_text(bio) or ''
            if text:
                method = 'pdfminer'
        except Exception:
            text = ''
    if not text:
        try:
            text = data.decode('utf-8', errors='ignore')
            if text:
                method = 'utf8'
        except Exception:
            text = ''
    if not text and ('image' in ct or f.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))):
        ocr_text = _ocr_image_bytes(data)
        if ocr_text:
            text = ocr_text
            method = 'image+ocr'
    extracted = _extract_values_from_text(text)
    fields = ['hba1c','glucose','blood_pressure','skin_thickness','insulin','nju','age','smoker','physicalactivity','bmi_category']
    present = [k for k in fields if k in extracted]
    resp = {k: extracted.get(k, None) for k in fields}
    # Detect OCR availability status
    ocr_available = True
    try:
        import pytesseract as _t
        import PIL
    except Exception:
        ocr_available = False
    return jsonify({'fields': resp, 'present': present, 'missing': [k for k in fields if k not in present], 'filename': f.filename, 'text_length': len(text), 'method': method, 'ocr_available': ocr_available})

@app.route('/route', methods=['POST', 'OPTIONS'])
def get_route():
    """Proxy endpoint for OpenRouteService API to avoid CORS issues"""
    if request.method == 'OPTIONS':
        return ('', 204)
    
    try:
        data = request.get_json(force=True)
        
        # Get API key from environment variable
        api_key = os.getenv('OPENROUTESERVICE_API_KEY', '')
        if not api_key:
            return jsonify({'error': 'OpenRouteService API key not configured on server'}), 500
        
        # Validate required fields
        if 'start' not in data or 'end' not in data:
            return jsonify({'error': 'Missing start or end coordinates'}), 400
        
        start = data['start']
        end = data['end']
        
        # Validate coordinate format
        if not isinstance(start, dict) or 'latitude' not in start or 'longitude' not in start:
            return jsonify({'error': 'Invalid start coordinates format'}), 400
        if not isinstance(end, dict) or 'latitude' not in end or 'longitude' not in end:
            return jsonify({'error': 'Invalid end coordinates format'}), 400
        
        # Prepare request to OpenRouteService
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        body = {
            'coordinates': [
                [start['longitude'], start['latitude']],
                [end['longitude'], end['latitude']]
            ],
            'format': 'geojson',
            'instructions': False,
            'geometry': True,
            'units': 'km'
        }
        
        # Make request to OpenRouteService
        response = requests.post(url, json=body, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_text = response.text
            return jsonify({
                'error': f'OpenRouteService API error: {error_text}',
                'status_code': response.status_code
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)