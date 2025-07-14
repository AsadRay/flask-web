import requests
from flask import current_app
from flask_babel import _


def translate(text, source_language='', dest_language='bn'):
    if not current_app.config.get('MS_TRANSLATOR_KEY'):
        return _('Error: the translation service is not configured.')

    headers = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region':current_app.config['MS_TRANSLATOR_REGION'],
        'Content-type': 'application/json'
    }

    # Build URL; omit 'from=' if source_language is empty (auto-detect)
    url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    if source_language:
        url += f'&from={source_language}'
    url += f'&to={dest_language}'

    try:
        response = requests.post(url, headers=headers, json=[{'Text': text}])
        response.raise_for_status()
        result = response.json()
        print("Azure translate response:", result)  # Debug print
        return result[0]['translations'][0]['text']
    except requests.RequestException as e:
        print("Translation request failed:", e)
    return _('Error: the translation service failed.')
