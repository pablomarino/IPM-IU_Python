import data.tmdbsimple as tmdb
import locale, random, requests, json

_apikey = 'fd7c9991afdb0eae88ab6617508de077'
_config = "https://api.themoviedb.org/3/configuration?api_key="+_apikey
tmdb.API_KEY = _apikey
_response = requests.request("GET", _config, data={}, headers={'content-type': 'application/json'})
_configJSon = json.loads(_response.text)

def getRecommendationsByID(id):
	movie = tmdb.Movies(id)
	movie.similar_movies(language=locale.getdefaultlocale()[0][0:2])
	if hasattr(movie, 'results'):
		_listlen = len(movie.results)
		if (_listlen == 0):
			return {}
		# print("# de recomendaciones : ",_listlen)
		return movie.results[random.randrange(0,_listlen)] # elijo una recomendacion al azar
	else:
		return {}

def _getIdByTitle(title):
	search = tmdb.Search()
	search.movie(query=title)
	if hasattr(search, 'results') and len(search.results)>0:
		return search.results[0]['id'] # devuelvo el primero
	else:
		return -1

def _getTitleById(id):
	movie = tmdb.Movies(id)
	movie.results[0].title

def getRecommendationsByTitle(title):
	id_pelicula = _getIdByTitle(title)
	if(id_pelicula>0):
		return {'recommended':getRecommendationsByID(id_pelicula), 'path': _configJSon['images']['secure_base_url']+_configJSon['images']['poster_sizes'][4]}
