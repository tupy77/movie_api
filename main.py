from fastapi import Depends, FastAPI, Body, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token

from config.database import Session, engine, Base
from models.movie import Movie as MovieModel

app = FastAPI()
app.title = "Mi aplicación FastAPI" #Título de la documentación
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    # def __init__(self, auto_error: bool = True):
    #     self.auto_error = auto_error
    
    async def __call__(self, request: Request):
      auth = await super().__call__(request)
      data = validate_token(auth.credentials)
      if data['email'] != 'admin@gmail.com':
        raise HTTPException(status_code=403, detail='Invalid credentials')
    
    
    # def __call__(self, request: Request):
    #     token: str = request.headers['Authorization'].split(' ')[1]
    #     try:
    #         payload = validate_token(token=token)
    #         if payload is None:
    #             raise credentials_exception
    #         return payload
    #     except:
    #         raise credentials_exception
    
    # async def __call__(self, request):
    #     token: str = request.headers['Authorization'].split(' ')[1]
    #     try:
    #         payload = validate_token(token=token)
    #         if payload is None:
    #             raise credentials_exception
    #         return payload
    #     except:
    #         raise credentials_exception

class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    # id: int | None
    id: Optional[int] = None #Otra forma de hacerlo
    # title: str = Field(default='Mi pelicula', min_length=1, max_length=15) # default: no es necesario ponerlo si se pone un valor por defecto en el modelo en la clase Config y variable schema_extra
    title: str = Field(min_length=1, max_length=15)
    overview: str = Field(max_length=150)
    year: int = Field(gt=1900, lt=2022) #gt: greater than, lt: less than, ge: greater or equal, le: less or equal
    rating: float
    categories: list
    
    class Config:
        schema_extra = {
            'example': {
                'title': 'Mi pelicula',
                'overview': 'Mi descripción',
                'year': 2021,
                'rating': 5.5,
                'categories': ['Comedy', 'Action']
            }
        }


movies = [
  {
    'id': 1,
    'title': 'The Godfather',
    'overview': 'The story spans ten years from 1945 to 1955 and chronicles the fictional Italian-American Corleone crime family.',
    'year': 1972,
    'rating': 9.2,
    'categories': ['Crime', 'Drama'],
  },
  {
    'id': 2,
    'title': 'The Godfather: Part II',
    'overview': 'The Godfather Part II presents two parallel storylines. One involves Mafia chief Michael Corleone in 1958/1959 after the events of the first movie; the other is a series of flashbacks following his father, Vito Corleone from 1917 to 1925, from his youth in Sicily (1901) to the founding of the Corleone family in New York.',
    'year': 1974,
    'rating': 9.0,
    'categories': ['Crime', 'Drama'],
  },
  {
    'id': 3,
    'title': 'The Dark Knight',
    'overview': 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.',
    'year': 2008,
    'rating': 8.8,
    'categories': ['Action', 'Crime', 'Drama', 'Thriller'],
  }
  ]

@app.get('/', tags=['home'])
def message():
    return HTMLResponse(content='<h1>Hola Mundo</h1>', status_code=200)

  
@app.post('/login', tags=['auth'])
def login(user: User):
      if user.email == 'admin@admin.com' and user.password == 'admin':
          token: str = create_token(user.dict())
          return JSONResponse(content=token, status_code=200)
      return JSONResponse(content={'message': 'Invalid credentials'}, status_code=401)
      
  
@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(content=movies, status_code=200)

  
@app.get('/movies/{movie_id}', tags=['movies'])
def get_movie(movie_id: int = Path(description='The ID of the movie you want to see', gt=0, le=300)):
    movie = next((movie for movie in movies if movie['id'] == movie_id), None)
    if movie == None:
        return JSONResponse(content={'message': 'Movie not found'}, status_code=404)
    return JSONResponse(content=movie)
  
#QUERY PARAMS
@app.get('/movies/', tags=['movies']) #Fijate que en la ruta no se esta pasando el parámetro category, cuando no se pasa parametro FastAPI lo recibe como un query param (PERO SI HAY QUE PONER LA BARRA AL FINAL, SINO SUSTITUIRIA LA RUTA MOVIES ANTERIOR)
def get_movies_by_category(category: str = Query(min_length=4, max_length=20)): #Se pueden poner mas de un parametro
    data = [movie for movie in movies if category in movie['categories']]
    return JSONResponse(content=data)


@app.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie = Body(...)):
    db = Session(bind=engine)
    #new_movie = MovieModel(**movie.dict())
    new_movie = MovieModel(title=movie.title, overview=movie.overview, year=movie.year, rating=movie.rating, categories=movie.categories)
    db.add(new_movie)
    db.commit()
    return JSONResponse(content={'message': 'Movie created'}, status_code=201)
  
# #Otra forma de hacerlo
# @app.post('/movies', tags=['movies'])
# def create_movie(movie: dict):
#     movies.append(movie)
#     return movie


@app.put('/movies/{id}', tags=['movies'], status_code=200)
def update_movie(id: int, movie: Movie):
    item = next((item for item in movies if item['id'] == id), None)
    item['title'] = movie.title
    item['overview'] = movie.overview
    item['year'] = movie.year
    item['rating'] = movie.rating
    item['categories'] = movie.categories
    return JSONResponse(content={'message': 'Movie updated'}, status_code=200)

  
@app.delete('/movies/{id}', tags=['movies'], status_code=200)
def delete_movie(id: int):
    movie = next((movie for movie in movies if movie['id'] == id), None)
    movies.remove(movie)
    return JSONResponse(content={'message': 'Movie deleted'}, status_code=200)