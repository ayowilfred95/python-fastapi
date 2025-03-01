from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from dotenv import load_dotenv

load_dotenv()


# Get values from environment
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    is_published: bool = True
    # rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Connected to the database successfully!")
        # Ensure the table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                is_published BOOLEAN DEFAULT TRUE
            );
        """)
        conn.commit()  # Commit changes to the database
        break

    except Exception as error:
        print("Failed to connect to database!")
        print(error)
        time.sleep(2)  # Retry only on failure


my_posts = [
    {
        "id": 1,
        "content": "Here is a good contente",
        "title": "first post"
    },
    {
        "id": 2,
        "title": "How to say hello in italian",
        "content": "Ciao",

    }
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def delete_one_post(id):
    # Iterate over the array
    # Find the index of that specific item
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/posts")
async def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


@app.get("/posts/{id}")
async def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def post_data(post: Post):
    cursor.execute("""INSERT INTO posts(title, content,is_published) VALUES(%s, %s, %s) RETURNING * """,
                   (post.title, post.content, post.is_published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.post("/posts/{id}/delete")
async def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", str((id)),)
    deleted_post = cursor.fetchone
    #Commit the transaction
    conn.commit()
    index = delete_one_post(id)
    if delete_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Post not found')
    return {"message": f"post with id: {id} deleted successfully"}
