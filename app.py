import json
import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'GET':
        return render_template('index.html')

    base_url = "https://api-free.deepl.com/v2/translate"
    payload = {
        "auth_key": os.environ['DEEPL_API_KEYS'],
        "text": request.form.get('input-text'),
        "source_lang": "JA",
        "target_lang": "EN"
    }
    
    response = requests.get(url=base_url, params=payload)
    
    if response.status_code != 200:
        raise Exception("DeepL API request failed with status code: " + str(response.status_code))

    result = json.loads(response.text)
    return render_template('index.html', translation=result['translations'][0]['text'])

if __name__ == "__main__":
    app.run(debug=True)
