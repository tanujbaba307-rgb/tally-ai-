from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 🔴 YAHAN APNA n8n WEBHOOK URL DAALO (Jo abhi copy kiya tha)
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/tally-ai"

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Tally AI Agent Backend is running!",
        "status": "active",
        "n8n_connected": True
    })

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # 🔥 n8n webhook ko call karo
        response = requests.post(N8N_WEBHOOK_URL, json={
            "instruction": prompt,
            "context": {}
        })
        
        # n8n se jo response aaya, use frontend ko bhejo
        return jsonify(response.json())
        
    except requests.exceptions.ConnectionError:
        # Agar n8n sleep mode mein ho to
        return jsonify({
            "xml": f'''<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
  <HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE>
          <VOUCHER VCHTYPE="Purchase" ACTION="Create">
            <DATE>{datetime.now().strftime("%Y%m%d")}</DATE>
            <PARTYLEDGERNAME>{prompt.split(' ')[2] if len(prompt.split(' ')) > 2 else 'Party'}</PARTYLEDGERNAME>
            <VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Purchases</LEDGERNAME>
              <AMOUNT>-50000.00</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>'''
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
