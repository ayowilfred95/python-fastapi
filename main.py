from fastapi import FastAPI, Response,status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    is_published: bool = True
    rating: Optional[int] = None


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
    return {"posts": my_posts}


@app.get("/posts/{id}")
async def get_post(id: int, response:Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id:{id} not found" )
         #response.status_code = status.HTTP_404_NOT_FOUND
         #return {"message": f"post with id:{id} not found"}
    # print(post)
    return {"post": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def post_data(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 100)
    my_posts.append(post_dict)

    return {"data": post_dict}


@app.post("/posts/{id}/delete")
async def delete_post(id: int):
    index = delete_one_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'Post not found')
    my_posts.pop(index)
    return {"message": f"post with id: {id} deleted successfully"}
