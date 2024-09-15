from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

app = Flask(__name__)

db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST')
db_port = config('DB_PORT')
db_name = config('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)
api = Api(app)
migrate = Migrate(app, db)


class BookModel(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=True)

    reader: Mapped['ReaderModel'] = relationship(back_populates='books')

    def __repr__(self):
        return f"<{self.pk}> {self.title} from {self.author}"

    def as_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}


class ReaderModel(db.Model):
    __tablename__ = 'readers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    books: Mapped[list['BookModel']] = relationship(back_populates='reader')


class BooksResource(Resource):
    def get(self):
        # books = BookModel.query.all() # version 2
        books = db.session.execute(db.select(BookModel)).scalars()  # version 3
        return [b.as_dict() for b in books]

    def post(self):
        data = request.get_json()
        book = BookModel(**data)
        db.session.add(book)
        db.session.commit()
        return book.as_dict(), 201


class BookResource(Resource):
    def get(self, id):
        book = BookModel.query.get(id)
        if book is None:
            return {"message": "Book not found"}, 404
        return book.as_dict()

    def put(self, id):
        book = BookModel.query.get(id)
        if book is None:
            return {"message": "Book not found"}, 404

        data = request.get_json()
        if "title" in data:
            book.title = data["title"]
        if "author" in data:
            book.author = data["author"]

        db.session.commit()
        return book.as_dict(), 200

    def delete(self, id):
        book = BookModel.query.get(id)
        if book is None:
            return {"message": "Book not found"}, 404

        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}, 200

# TODO Homework - add the Bookresource to respective binding url
api.add_resource(BooksResource, "/books")
api.add_resource(BookResource, "/books/<int:id>")

