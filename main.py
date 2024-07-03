import json
import os

import google.generativeai as genai
import gspread
import logging

from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, jsonify, request, send_file, send_from_directory

from dotenv import load_dotenv

load_dotenv()
# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = os.getenv('GEMINI_API_KEY')
# GEMINI_MODEL='gemini-1.5-flash'

genai.configure(api_key=API_KEY)

app = Flask(__name__)

def open_worksheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope) 
    client = gspread.authorize(creds)
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1vk7kuDZbI_I9jejQJSZpqNblH07r2Qb1IJLLyo69774/')
    return sheet.worksheet('Retail Sales Dataset_exported.csv')

@app.route("/")
def index():
    return send_file('web/index.html')

@app.route('/manage-data')
def input_data():
    return send_file('web/manage-data.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if API_KEY == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key at
                https://g.co/ai/idxGetGeminiKey and enter it in
                main.py
                '''.replace('\n', '') })
        try:
            worksheet = open_worksheet()
            data = worksheet.get_all_values()
            req_body = request.get_json()
            content = req_body.get("contents")
            model = genai.GenerativeModel(model_name=req_body.get("model"))
            execute_prompt = f'''
anda adalah seorang data analyst expert dan saya adalah seorang sales manajer.

Berdasarkan data berikut 
{data}

dan saya meminta hal berikut
{content}

berikan saya insight yang jelas dan singkat serta akurat. tidak usah berbasa basi
            '''

            response = model.generate_content(execute_prompt, stream=True)
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.text })

            print(stream())
            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({ "error": str(e) })

@app.route('/api/store')
def store_data():
    if request.method != "POST":
        return jsonify({ "error": "Invalid request method" })
    
    req_body = request.get_json()
    date = req_body.get("date")
    product_category = req_body.get("product_category")
    quantity = int(req_body.get("quantity"))
    price = int(req_body.get("price"))
    customer_id = req_body.get("customer_id")
    customer_age = req_body.get("customer_age")
    customer_gender = req_body.get("customer_gender")

    worksheet = open_worksheet()
    total_rows = len(worksheet.col_values(1))

    last_row = worksheet.row_values(total_rows)
    last_index = last_row[0]
    worksheet.append_row([last_index+1, date, customer_id, customer_gender, customer_age, product_category, quantity, price, quantity * price])

    return jsonify({ "success": True })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
