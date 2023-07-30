#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, User, Review, Game

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "Index for Game/Review/User API"


@app.route("/games")
def games():
    games = []
    for game in Game.query.all():
        game_dict = {
            "title": game.title,
            "genre": game.genre,
            "platform": game.platform,
            "price": game.price,
        }
        games.append(game_dict)

    response = make_response(games, 200)

    return response


@app.route("/games/<int:id>")
def game_by_id(id):
    game = Game.query.filter(Game.id == id).first()

    game_dict = game.to_dict()

    response = make_response(game_dict, 200)

    return response


@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    if request.method == "GET":
        reviews = []
        for review in Review.query.all():
            review_dict = review.to_dict()
            reviews.append(review_dict)
        response = make_response(reviews, 200)
        return response
    elif request.method == "POST":
        data = request.json
        if "user_id" not in data or "game_id" not in data or "comment" not in data:
            return (
                {"error": "You must include include comment, game id and user id"},
                422,
            )
        else:
            review = Review()
            # score=data.score,comment=data.comment,created_at=db.func.now(),game_id=data.game_id,user_id=data.user_id
            try:
                for attr in data:
                    setattr(review, attr, data[attr])
                db.session.add(review)
                db.session.commit()
                return review.to_dict(), 201
            except (IntegrityError, ValueError) as ie:
                return {"error": ie.args}, 422


@app.route("/users")
def users():
    users = []
    for user in User.query.all():
        user_dict = user.to_dict()
        users.append(user_dict)

    response = make_response(users, 200)

    return response


@app.route("/reviews/<int:id>", methods=["GET", "PATCH", "DELETE"])
def deview_by_id(id):
    review = Review.query.filter(Review.id == id).first()

    if request.method == "GET":
        response = make_response(review.to_dict(), 200)
        return response
    elif request.method == "DELETE":
        db.session.delete(review)
        db.session.commit()
        return {}, 204
    elif request.method == "PATCH":
        data = request.json
        review = Review.query.filter(Review.id == id).first()
        for attr in data:
            setattr(review, attr, data[attr])
        review.updated_at = db.func.now()
        db.session.commit()
        return review.to_dict()


if __name__ == "__main__":
    app.run(port=5555, debug=True)
