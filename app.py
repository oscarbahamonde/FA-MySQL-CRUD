from os import getcwd
from fastapi import FastAPI, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from uvicorn import run
from sqlmodel import SQLModel, create_engine, Field, Session
from pydantic import EmailStr
from uuid import uuid4, UUID
from typing import List
from starlette.staticfiles import StaticFiles
from shutil  import copyfileobj


class User(SQLModel):
   id : UUID = Field(uuid4(), primary_key=True)
   username : str = Field(nullable=False)
   email : EmailStr = Field(nullable=False)
   password: str = Field(nullable=False)

class Product(SQLModel):
    id : UUID = Field(uuid4(), primary_key=True)
    name : str = Field(nullable=False)
    price : float = Field(nullable=False)
    description : str = Field(nullable=False)
    image : str = Field(default='https://penmadsidrap.com/uploads/blog_image/default.jpg')
    category: str = Field(nullable=False)
    
class Cart(SQLModel):
    id : UUID = Field(uuid4(), primary_key=True)
    user_id : UUID = Field(nullable=False)
    products_id : List[UUID] = Field(nullable=True)
 
class Post(SQLModel):
    id: UUID = Field(uuid4(), primary_key=True)
    title: str = Field(nullable=False)
    summary: str = Field(nullable=False)
    content: str = Field(nullable=False)
    category: str = Field(nullable=True)
    image: str = Field(default='https://penmadsidrap.com/uploads/blog_image/default.jpg')
    icon: str = Field(default='mdi mdi-file-document-outline')

db = create_engine("mysql+pymysql://user:secret@localhost:3306/db")

SQLModel.metadata.create_all(db)

app = FastAPI()

app.mount('/uploads', StaticFiles(directory='uploads'), name='static')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.get("/")
async def index():
    return RedirectResponse(url='/docs')
@app.get("/products")
async def products():
    with Session(db) as session:
        products = session.query(Product).all()
        return products

@app.post("/products")
async def add_product(product: Product):
    with Session(db) as session:
        session.add(product)
        return product

@app.get("/cart/{id}")
async def cart(id: UUID):
    with Session(db) as session:
        cart = session.query(Cart).filter_by(user_id=id).first()
        return cart

@app.post("/cart/{id}")
async def cart(id: UUID, products_id: List[UUID]):
    with Session(db) as session:
        cart = session.query(Cart).filter_by(user_id=id).first()
        if cart:
            cart.products_id = products_id
        else:
            cart = Cart(user_id=id, products_id=products_id)
            session.add(cart)
        session.commit()
        return cart

@app.get("/posts")
async def posts():
    with Session(db) as session:
        posts = session.query(Post).all()
        return posts

@app.get("/posts")
async def posts():
    with Session(db) as session:
        posts = session.query(Post).all()
        return posts

@app.post("/posts")
async def add_post(post: Post):
    with Session(db) as session:
        session.add(post)
        return post

@app.post("/uploadfile")
def upload_file(file: UploadFile = File(...)):
    with open(getcwd()+'/uploads/'+file.filename, 'wb+') as buffer:
        try:
            copyfileobj(file.file, buffer)
        except Exception as e:
            print(e)
        buffer.close() 
    return buffer.name

if __name__ == "__main__":
    run(app, host='0.0.0.0', port=8000, debug=True)