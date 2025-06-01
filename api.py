from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
	uid = db.Column(db.Integer, primary_key=True)
	uname = db.Column(db.String(80), nullable=False)
	email = db.Column(db.String(80), nullable=False)

	def __repr__(self):
		return f"User(name = {self.name}, email = {self.email})"

user_args = reqparse.RequestParser()
user_args.add_argument('uname', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

user_fields = {'uid':fields.Integer, 'uname':fields.String, 'email':fields.String} # Response in JSON format

class Users(Resource):
	@marshal_with(user_fields) # Decorating/Marshalling/Serializing our JSON data
	def get(self):
		users = UserModel.query.all()
		return users
	@marshal_with(user_fields)
	def post(self):
		args = user_args.parse_args()
		user = UserModel(uname=args["uname"], email=args["email"])
		db.session.add(user)
		db.session.commit()
		users = UserModel.query.all()
		return users, 201

class single_user(Resource):
	@marshal_with(user_fields)
	def get(self, uid):
		user = UserModel.query.filter_by(uid=uid).first()
		if not user:
			abort(404, "User not found")
		return user
	@marshal_with(user_fields)
	def patch(self, uid):
		args = user_args.parse_args()
		user = UserModel.query.filter_by(uid=uid).first()
		if not user:
			abort(404, "User not found")
		user.uname = args["uname"]
		user.email = args["email"]
		db.session.commit()
		return user
	@marshal_with(user_fields)
	def delete(self, uid):
		user = UserModel.query.filter_by(uid=uid).first()
		if not user:
			abort(404, "User not found")
		db.session.delete(user)
		db.session.commit()
		users = UserModel.query.all()
		return users

api.add_resource(Users, '/api/users/') # Return all users from the database at this URL
api.add_resource(single_user, '/api/users/<int:uid>') # Return the user with specified integer ID from the database at this URL, else abort with 404 error and "User not found"

@app.route('/')
def home():
	return "<h1>Flask + REST API</h1>"

if __name__ == '__main__':
	app.run(debug=True)
