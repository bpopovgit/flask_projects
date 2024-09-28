import enum
from datetime import datetime
from marshmallow_enum import EnumField
from marshmallow import Schema, fields, validate, ValidationError, validates
from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column
from password_strength import PasswordPolicy
from werkzeug.security import generate_password_hash

app = Flask(__name__)

db_user = config('DB_USER')
db_pass = config('DB_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@localhost:5432/clothes'

db = SQLAlchemy(app)
api = Api(app)
migrate = Migrate(app, db)

policy = PasswordPolicy.from_names(
    uppercase=1,
    numbers=1,
    special=1,
    nonletters=1,
)


def validate_password(value):
    errors = policy.test(value)
    if errors:
        raise ValidationError(f"Not a valid password.")


class BaseUserSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(required=True)

    @validates("full_name")
    def validate_name(self, value):
        try:
            first_name, last_name = value.split()
        except ValueError:
            raise ValidationError("Full name should consist of first and last name at least.")
        if len(first_name) < 3 and len(last_name) < 3:
            raise ValueError("Name should be at least 3 characters")


class UserSignInSchema(BaseUserSchema):
    password = fields.String(
        required=True,
        validate=validate.And(
            validate.Length(min=8, max=20),
            validate_password
        )
    )


class SignUp(Resource):
    def post(self):
        data = request.get_json()
        schema = UserSignInSchema()
        errors = schema.validate(data)

        if not errors:
            data["password"] = generate_password_hash(data["password"], method='pbkdf2:sha256')
            user = User(**data)
            db.session.add(user)
            try:
                db.session.commit()
                response_schema = UserOutSchema()
                response_data = response_schema.dump(user)
                return response_data, 201
            except IntegrityError as ex:
                return {"message": "Email already exists, please sign in instead!"}

        else:
            return errors, 400


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


class Clothes(db.Model):
    __tablename__ = 'clothes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    color: Mapped[ColorEnum] = mapped_column(
        db.Enum(ColorEnum),
        default=ColorEnum.white,
        nullable=False
    )
    size: Mapped[SizeEnum] = mapped_column(
        db.Enum(SizeEnum),
        default=SizeEnum.s,
        nullable=False
    )
    photo: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())


class SingleClothSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    color = EnumField(ColorEnum, by_value=True)
    size = EnumField(SizeEnum, by_value=True)
    created_on = fields.DateTime()
    updated_on = fields.DateTime()


class UserOutSchema(BaseUserSchema):
    id = fields.Integer()
    full_name = fields.String()
    clothes = fields.List(fields.Nested(SingleClothSchema), many=True)


class UserResource(Resource):
    def get(self, pk):
        user = db.session.execute(db.select(User).filter_by(id=pk)).scalar_one()
        return UserOutSchema().dump(user)


api.add_resource(SignUp, '/register/')
api.add_resource(UserResource, '/users/<int:pk>/')
