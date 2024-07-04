#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)

    # Create a patch instance method to handle updating of a plant object records in the database.
    def patch(self, id):
        plant_record = Plant.query.filter(Plant.id == id).first()
        for attr in request.form:
            setattr(plant_record, attr, request.form[attr])
        db.session.add(plant_record)
        db.session.commit()
        response_dict = plant_record.to_dict()
        response_dict['is_in_stock'] = False  # Update is_in_stock to False after updating the record.
        response = make_response(response_dict, 200)
        return response
    # Create a delete instance method to handle delete an object from the database.
    def delete(self, id):
        plant_record = Plant.query.filter(Plant.id == id).first()
        db.session.delete(plant_record)
        db.session.commit()
        response_dict = {
            "message": "Plant record deleted successfully"
        }
        response = make_response(response_dict, 204)
        return response
api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
