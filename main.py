import json
import os

import google.generativeai as genai
import gspread
import logging

from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, jsonify, request, send_file, send_from_directory

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'AIzaSyBU-kvhibDf-Cy_vncrq-PcTS5VyXY8Vp0'
# GEMINI_MODEL='gemini-1.5-flash'

genai.configure(api_key=API_KEY)

app = Flask(__name__)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope) 
client = gspread.authorize(creds)

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
            # setup google sheet
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope) 
            client = gspread.authorize(creds)
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1jplp8qtv4uFD4YQitLf7dn-NUuYdMIDvIpJPq8Qb7-A/')
            worksheet = sheet.worksheet('Retail Sales Dataset_exported.csv')
            data = worksheet.get_all_values()

            req_body = request.get_json()
            content = req_body.get("contents")
            model = genai.GenerativeModel(model_name=req_body.get("model"))
            execute_prompt = f'''
anda adalah seorang data analyst expert dan saya adalah seorang salas manajer, saya sedang berhadapan dengan client saya.

Berdasarkan data berikut 
{data}

dan client saya meminta hal berikut
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


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
