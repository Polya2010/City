from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

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

sessionStorage = {}


@app.route("/post", methods=["POST"])
def main():
    logging.info(f"Request: {request.json!r}")
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {"end_session": False},
    }

    handle_dialog(request.json, response)

    logging.info(f"Response: {response!r}")

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req["session"]["user_id"]

    if req["session"]["new"]:
        sessionStorage[user_id] = {"first_name": None}
        res["response"]["text"] = "Привет! Назови свое имя!"
        return

    if sessionStorage[user_id]["first_name"] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res["response"]["text"] = "Не расслышала имя. Повтори, пожалуйста!"
        else:
            sessionStorage[user_id]["first_name"] = first_name
            res["response"]["text"] = f"Приятно познакомиться, {first_name.title()}. Я - Алиса. Какой город хочешь увидеть?"
            res["response"]["buttons"] = [
                {"title": city.title(), "hide": True} for city in cities.keys()
            ]
    else:
        city = get_city(req)
        if city and city in cities:
            res["response"]["card"] = {
                "type": "BigImage",
                "title": f"Город {city.title()}",
                "image_id": random.choice(cities[city])
            }
            res["response"]["text"] = "Красивый город, правда?"
        else:
            res["response"]["text"] = "Первый раз слышу об этом городе. Попробуй еще разок!"


def get_city(req):
    if "request" in req and "nlu" in req["request"]:
        for entity in req["request"]["nlu"]["entities"]:
            if entity["type"] == "YANDEX.GEO":
                return entity["value"].get("city", None)
    return None


def get_first_name(req):
    if "request" in req and "nlu" in req["request"]:
        for entity in req["request"]["nlu"]["entities"]:
            if entity["type"] == "YANDEX.FIO":
                return entity["value"].get("first_name", None)
    return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
