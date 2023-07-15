import json
import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
import openai
import requests

openai.api_key = os.environ['OPEN_API_KEYS']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'GET':
        return render_template('index.html')
    
    input_text = request.form.get('input-text')

    result = translate_by_deepl(input_text, "JA", "EN")

    return render_template('index.html', input_text=input_text, translation=result['translations'][0]['text'])

@app.route('/translation_auto', methods=['POST'])
def translation_auto():
    input_text = request.form.get('input-text')

    base_url = "https://api-free.deepl.com/v2/translate"
    payload = {
        "auth_key": os.environ['DEEPL_API_KEYS'],
        "text": input_text,
        "source_lang": "JA",
        "target_lang": "EN"
    }
    
    response = requests.get(url=base_url, params=payload)
    
    if response.status_code != 200:
        raise Exception("DeepL API request failed with status code: " + str(response.status_code))

    result = json.loads(response.text)
    return jsonify({'translation' : result['translations'][0]['text']})

@app.route('/correction' , methods=['GET', 'POST'])
def correction():
    if request.method == 'GET':
        return redirect(url_for('translate'))

    input_text = request.form.get('input-text')
    translation = request.form.get('translation')
    self_translation = request.form.get('self-translation')

    comparison_result = json.loads(compare_sentence_meanings(translation, self_translation))
    if comparison_result["yes-or-no"] == "no":
        comparison_result['missing-point'] = translate_by_deepl(comparison_result['missing-point'], "EN", "JA")['translations'][0]['text']

    return render_template('index.html', input_text=input_text, translation=translation, self_translation=self_translation, correction=comparison_result['missing-point'])

def compare_sentence_meanings(sentence1, sentence2):
    prompt = f"Are the meanings of the below two sentences the same? \
            ###sentence1 \
            {sentence1} \
            ### \
            ### sentence2 \
            {sentence2} \
            ### \
            Could you reply according to the following conditions? \
            ・Reply in japanese \
            ・Follow below json format \
            ### format \
            {{ \
                \"yes-or-no\" :  answer \"yes\" or \"no\" about result of comparison two sentence. \
                \"missing-point\" : If \"yes-or-no\" is \"no\", tell me the differences briefly in japanese. You must output empty str ('') when \"yes-or-no\" is \"yes\" \
            }} \
            ###"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.get('content')

def translate_by_deepl(input_text, source_lang, target_lang):

    base_url = "https://api-free.deepl.com/v2/translate"
    payload = {
        "auth_key": os.environ['DEEPL_API_KEYS'],
        "text": input_text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    
    response = requests.get(url=base_url, params=payload)
    
    if response.status_code != 200:
        raise Exception("DeepL API request failed with status code: " + str(response.status_code))

    return json.loads(response.text)

if __name__ == "__main__":
    app.run(debug=True)
