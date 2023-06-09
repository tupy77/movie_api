from models.movie import Movie as MovieModel

class MovieService():
    def __init__(self, db) -> None:
        self.db = db

    def get_movies(self):
        result = self.db.query(MovieModel).all()
        return result

    def get_movie(self, id: int):
        result = self.db.query(MovieModel).filter(MovieModel.id == id).first()
        return result
    
    def get_movies_by_category(self, category: str):
        result = self.db.query(MovieModel).filter(MovieModel.category == category).all()
        return result
    
    def create_movie(self, movie: MovieModel):
        self.db.add(movie)
        self.db.commit()
        return True
    
    def update_movie(self, id: int, movie: MovieModel):
        result = self.db.query(MovieModel).filter(MovieModel.id == id).first()
        if not result:
            return False
        result.title = movie.title
        result.overview = movie.overview
        result.year = movie.year
        result.rating = movie.rating
        result.category = movie.category
        self.db.commit()
        return True
    
    def delete_movie(self, id: int):
        result = self.db.query(MovieModel).filter(MovieModel.id == id).first()
        if not result:
            return False
        self.db.delete(result)
        self.db.commit()
        return True