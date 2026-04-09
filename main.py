from flask import Flask, request, jsonify
import logging
import random
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cities = {
    'москва': [
        '1540737/daa6e420d33102bf6947',
        '213044/7df73ae4cc715175059e'
    ],
    'нью-йорк': [
        '1652229/728d5c86707054d4745f',
        '1030494/aca7ed7acefde2606bdc'
    ],
    'париж': [
        '1652229/f77136c2364eb90a3ea8',
        '3450494/aca7ed7acefde22341bdc'
    ]
}

city_synonyms = {
    'москва': ['мск', 'москве', 'столица', 'moscow'],
    'нью-йорк': ['нью йорк', 'нй', 'ny', 'new york', 'big apple'],
    'париж': ['paris', 'париже', 'parij']
}

sessionStorage = {}


def normalize_city_name(city_name):
    if not city_name:
        return None
    city_lower = city_name.lower().strip()
    if city_lower in cities:
        return city_lower
    for city, synonyms in city_synonyms.items():
        if city_lower in synonyms or city_lower == city:
            return city
    return None


@app.route('/post', methods=['POST'])
def main():
    try:
        logging.info(f'Request: {request.json}')
        response = {
            'session': request.json['session'],
            'version': request.json['version'],
            'response': {'end_session': False}
        }
        handle_dialog(response, request.json)
        logging.info(f'Response: {response}')
        return jsonify(response)
    except Exception as e:
        logging.error(f'Error: {e}')
        return jsonify({
            'response': {
                'text': 'Произошла ошибка. Попробуйте еще раз.',
                'end_session': False
            }
        })


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        sessionStorage[user_id] = {'first_name': None}
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я - Алиса. Какой город хочешь увидеть?'
            res['response']['buttons'] = [
                {'title': city.title(), 'hide': True} for city in cities.keys()
            ]
    else:
        city = get_city_from_request(req)
        if city and city in cities:
            res['response']['card'] = {
                'type': 'BigImage',
                'title': f'Город {city.title()}',
                'image_id': random.choice(cities[city])
            }
            res['response']['text'] = 'Красивый город, правда?'
        else:
            res['response']['text'] = 'Первый раз слышу об этом городе. Попробуй еще разок!'


def get_city_from_request(req):
    if 'request' in req and 'nlu' in req['request']:
        for entity in req['request']['nlu']['entities']:
            if entity['type'] == 'YANDEX.GEO':
                city = entity['value'].get('city', None)
                if city:
                    normalized = normalize_city_name(city)
                    if normalized:
                        return normalized
    if 'request' in req and 'original_utterance' in req['request']:
        text = req['request']['original_utterance'].lower()
        for city in cities.keys():
            if city in text:
                return city
        for city, synonyms in city_synonyms.items():
            for synonym in synonyms:
                if synonym in text:
                    return city
    return None


def get_first_name(req):
    if 'request' in req and 'nlu' in req['request']:
        for entity in req['request']['nlu']['entities']:
            if entity['type'] == 'YANDEX.FIO':
                first_name = entity['value'].get('first_name', None)
                if first_name:
                    return first_name
    if 'request' in req and 'original_utterance' in req['request']:
        text = req['request']['original_utterance'].strip()
        if len(text.split()) == 1 and len(text) < 30 and text.isalpha():
            return text
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
