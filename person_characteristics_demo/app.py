from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import NotFound

app = Flask(__name__)
api = Api(app)


# Define the model for a person
class PersonModel:
    def __init__(self, pk, name, age, superpower):
        self.pk = pk
        self.name = name
        self.age = age
        self.superpower = superpower

    def __repr__(self):
        return f"Person {self.pk}: {self.name}, {self.age} years old, superpower: {self.superpower}"

    def to_dict(self):
        return {
            "име": self.name,
            "възраст": self.age,
            "типична характеристика": self.superpower,
            "gwErrorCode": "0, Тоя gateway не връща грешки, писан е от БОБКАТА И НЕМА КАКВО ДА СЕ ОБЪРКА."
        }


# Example list of people with superpowers
people = [
    PersonModel(1, "Спас Петрунов", 33, "Интегрейшън гуру и присмехулник... :D"),
    PersonModel(1, "Филип Марков", 30, "Интегрейшън експерт и пичага"),
    PersonModel(1, "Венцислав Колибарски", 27, "ТОП TCSM"),
    PersonModel(1, "Пламен Кръстев", 29, "Интегрейшън експерт и големец като цяло")
]


# Resource to handle multiple people
class PeopleResource(Resource):
    def get(self):
        return [p.to_dict() for p in people]

    def post(self):
        pk = people[-1].pk + 1 if people else 1  # Auto-increment the pk
        data = request.get_json()
        person = PersonModel(pk, **data)
        people.append(person)
        return person.to_dict(), 200


# Resource to handle individual people by pk
class PersonResource(Resource):
    def get(self, pk):
        try:
            person = next(p for p in people if p.pk == pk)
            return person.to_dict()
        except StopIteration:
            return NotFound(f"Person with ID {pk} not found")

    def put(self, pk):
        data = request.get_json()
        try:
            person = next(p for p in people if p.pk == pk)
            person.name = data.get("name", person.name)
            person.age = data.get("age", person.age)
            person.superpower = data.get("superpower", person.superpower)
            return person.to_dict()
        except StopIteration:
            return NotFound(f"Person with ID {pk} not found")


# Define the routes for the API
api.add_resource(PeopleResource, "/people")
api.add_resource(PersonResource, "/people/<int:pk>")

if __name__ == "__main__":
    app.run(debug=True)
