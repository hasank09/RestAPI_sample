from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice
from flask import url_for

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False, default=False)
    has_wifi = db.Column(db.Boolean, nullable=False, default=False)
    has_sockets = db.Column(db.Boolean, nullable=False, default=False)
    can_take_calls = db.Column(db.Boolean, nullable=False, default=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # # Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = choice(all_cafes)

    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = [cafe.to_dict() for cafe in cafes]

    return jsonify(cafes=all_cafes)


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafe:
        all_cafes = [cafe.to_dict() for cafe in cafe]

        return jsonify(cafes=all_cafes)
        # return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_cafe():
    def string_to_bool(answer):
        if isinstance(answer, str):
            if answer.lower() == 'true':
                return True
            else:
                return False
        else:
            return answer

    if request.method == 'POST':
        data = request.form.to_dict()
        print(data)
        print(bool(request.form.get("can_take_calls")))
        # with app.app_context():
        new_cafe = Cafe(name=data['name'], map_url=data['map_url'], img_url=data['img_url'],
                        location=data['location'], seats=data['seats'], has_toilet=string_to_bool(data['has_toilet']),
                        has_wifi=string_to_bool(data['has_wifi']), has_sockets=string_to_bool(data['has_sockets']),
                        can_take_calls=string_to_bool(data['can_take_calls']), coffee_price=data['coffee_price'])
        db.session.add(new_cafe)
        db.session.commit()

        return jsonify(Response={"Success": "Successfully added the new cafe."})

    else:
        return jsonify(Response={"Success": "Sorry, we don't have a cafe at that location."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def coffee_price_update(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = db.session.query(Cafe).filter_by(id=cafe_id).first()

    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(Response={"Success": "Successfully updated Cafe Price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def coffee_delete(cafe_id):
    api_key = request.args.get("api-key")
    cafe_to_delete = db.session.query(Cafe).filter_by(id=cafe_id).first()
    # sample key for delete authentication more mechanism can be created for mulitple keys
    if api_key == '34bef140b3b318b4875685c2a41f586bb373a5889c8325cb4ff4154734ad7c13':

        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(Response={"Success": " Requested Cafe has been successfully  deleted."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(eror="Sorry that's not allowed. Make sure you have correct api-key"), 403


if __name__ == '__main__':
    app.run(debug=True)
