from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode

import os

# Se crea la aplicacion
app = Flask(__name__)

# Se agregan a la configuracion las variables de entorno
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)

# Se crean las tablas del modelo asociado
class Artista(db.Model):
    # name, age
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    age = db.Column(db.Integer)
    albums = db.Column(db.Text)
    tracks = db.Column(db.Text)
    self_ = db.Column("self", db.Text)
    
    def __init__(self, id, name, age, albums, tracks, self_):
        self.id = id
        self.name = name
        self.age = age
        self.albums = albums
        self.tracks = tracks
        self.self_ = self_
    
    
class Album(db.Model):
    # name, genre
    id = db.Column(db.Text, primary_key=True)
    artist_id = db.Column(db.Text, db.ForeignKey("artista.id", ondelete="CASCADE"))
    name = db.Column(db.Text)
    genre = db.Column(db.Text)
    artist = db.Column(db.Text)
    tracks = db.Column(db.Text)
    self_ = db.Column("self", db.Text)
    
    def __init__(self,id, artist_id, name, genre, artist, tracks, self_):
        self.id = id
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.artist = artist
        self.tracks = tracks
        self.self_ = self_
    

class Cancion(db.Model):
    # name, duration
    id = db.Column(db.Text, primary_key=True)
    album_id = db.Column(db.Text, db.ForeignKey("album.id", ondelete="CASCADE"))
    name = db.Column(db.Text)
    duration = db.Column(db.Float)
    times_played = db.Column(db.Integer)
    artist = db.Column(db.Text)
    album = db.Column(db.Text)
    self_ = db.Column("self", db.Text)

    def __init__(self, id, album_id, name, duration, times_played, artist, album, self_):
        self.id = id
        self.album_id = album_id
        self.name = name
        self.duration = duration
        self.times_played = times_played
        self.artist = artist
        self.album = album
        self.self_ = self_
    
 
# Se crean las rutas ligadas al modelo
@app.route("/artists", methods=['POST', 'GET'])
def artists():
    if request.method == "POST":
        body = request.json
        # Analiza si tiene name y age
        nombre = [nombre for nombre in body]
        if ("name" in nombre) and ("age" in nombre):
            # Se crea el nuevo artista dado que los datos son los correctos
            id = b64encode(body["name"].encode()).decode('utf-8')[:22]
            # Se ve si existe el artista
            existe = db.session.query(Artista).filter(Artista.id == id).all()   # Para hacer una consulta y retorna una lista
            if len(existe)>0:
                respuesta = jsonify({
                    "id": existe[0].id,
                    "name": existe[0].name,
                    "age": existe[0].age,
                    "albums": existe[0].albums,
                    "tracks": existe[0].tracks,
                    "self": existe[0].self_
                })
                respuesta.status_code = 409
                return respuesta
            # Acá es porque el artista no existe y se debe crear
            else:
                albums_url = f"{os.environ.get('TAREA_URL')}artists/{id}/albums"
                tracks_url = f"{os.environ.get('TAREA_URL')}albums/{id}/tracks"
                self_url = f"{os.environ.get('TAREA_URL')}artists/{id}"
                artista = Artista(id, body["name"], body["age"], albums_url, tracks_url, self_url)
                db.session.add(artista)
                db.session.commit()
                
                respuesta = jsonify({
                    "id": artista.id,
                    "name": artista.name,
                    "age": artista.age,
                    "albums": artista.albums,
                    "tracks": artista.tracks,
                    "self": artista.self_
                })
                respuesta.status_code = 201
                return respuesta
        else:
            # Se levanta un error que dice que los datos entregados no son los correctos
            respuesta = jsonify({})
            respuesta.status_code = 400
            return respuesta
    
    elif request.method == "GET":
        consulta_artistas = db.session.query(Artista).all()
        respuesta = []
        for artista in consulta_artistas:
            respuesta.append({
                "id": artista.id,
                "name": artista.name,
                "age": artista.age,
                "albums": artista.albums,
                "tracks": artista.tracks,
                "self": artista.self_
            })
        estatus = jsonify(respuesta)
        estatus.status_code = 200
        return estatus
    
    else:
        # En caso de que no exista el metodo del request
        respuesta = jsonify({})
        respuesta.status_code = 405
        return respuesta



@app.route("/artists/<string:artist_id>", methods=['GET'])
def artists_artist_id(artist_id):
    if request.method == "GET":
        consulta_por_artista = db.session.query(Artista).filter(Artista.id == artist_id).all()
        #El artista existe
        if len(consulta_por_artista) > 0:
            estatus = jsonify({
                "id": artist_id,
                "name": consulta_por_artista[0].name,
                "age": consulta_por_artista[0].age,
                "albums": consulta_por_artista[0].albums,
                "tracks": consulta_por_artista[0].tracks,
                "self": consulta_por_artista[0].self_
                })
            estatus.status_code = 200
            return estatus
        #El artista no existe
        else:
            respuesta = jsonify({})
            respuesta.status_code = 404
            return respuesta
    else:
        # En caso de que no exista el metodo del request
        respuesta = jsonify({})
        respuesta.status_code = 405
        return respuesta



@app.route("/artists/<string:artist_id>/albums", methods=['POST'])
def artists_artists_id_albums(artist_id):
    #Analizo si el método existe
    if request.method == "POST":
        body = request.json
        nombre = [nombre for nombre in body]
        #Analizo si es que los datos entregados son los correctos
        if ("name" in nombre) and ("genre" in nombre):
            aux = body["name"]+":"+artist_id
            id = b64encode(aux.encode()).decode('utf-8')[:22]
            existe = db.session.query(Artista).filter(Artista.id == artist_id).all()   # Para hacer una consulta y retorna una lista
            #Si el artista existe, entonces puedo crear la album
            if len(existe)>0:
                existe_2 = db.session.query(Album).filter(Album.id == id).all()
                #Si el album ya existe, entonces arrojo el error
                if len(existe_2)>0:
                    respuesta = jsonify({
                        "id": existe_2[0].id,
                        "artist_id": artist_id,
                        "name": existe_2[0].name,
                        "genre": existe_2[0].genre,
                        "artist": existe_2[0].artist,
                        "tracks": existe_2[0].tracks,
                        "self": existe_2[0].self_
                    })
                    respuesta.status_code = 409
                    return respuesta
                #Si el album no existe, la creo y la muestro
                else:
                    album = Album(id, artist_id, body["name"], body["genre"], f"{os.environ.get('TAREA_URL')}artists/{id}", f"{os.environ.get('TAREA_URL')}albums/{id}/tracks", f"{os.environ.get('TAREA_URL')}albums/{id}")
                    db.session.add(album)
                    db.session.commit()
                    respuesta = jsonify({
                        "id": album.id,
                        "artist_id": artist_id,
                        "name": album.name,
                        "genre": album.genre,
                        "artist": album.artist,
                        "tracks": album.tracks,
                        "self": album.self_
                    })
                    respuesta.status_code = 201
                    return respuesta
            #Si no existe, arrojo error
            else:
                respuesta = jsonify({})
                respuesta.status_code = 422
                return respuesta
        else:
            # Se levanta un error que dice que los datos entregados no son los correctos
            respuesta = jsonify({})
            respuesta.status_code = 400
            return respuesta

    else:
        # En caso de que no exista el metodo del request
        respuesta = jsonify({})
        respuesta.status_code = 405
        return respuesta


@app.route("/albums", methods=['GET'])
def albums():
    if request.method == "GET":
        consulta_albums = db.session.query(Album).all()
        respuesta = []
        for album in consulta_albums:
            respuesta.append({
                "id": album.id,
                "artist_id": album.artist_id,
                "name": album.name,
                "genre": album.genre,
                "artist": album.artist,
                "tracks": album.tracks,
                "self": album.self_
            })
        estatus = jsonify(respuesta)
        estatus.status_code = 200
        return estatus

    else:
        # En caso de que no exista el metodo del request
        respuesta = jsonify({})
        respuesta.status_code = 405
        return respuesta
        


@app.route("/albums/<string:album_id>/tracks", methods=['POST'])
def albums_album_id_tracks(album_id):
    #Analizo si el método existe
    if request.method == "POST":
        body = request.json
        nombre = [nombre for nombre in body]
        #Analizo si es que los datos entregados son los correctos
        if ("name" in nombre) and ("duration" in nombre):
            aux = body["name"]+":"+album_id
            id = b64encode(aux.encode()).decode('utf-8')[:22]
            existe = db.session.query(Album).filter(Album.id == album_id).all()   # Para hacer una consulta y retorna una lista
            #Si el album existe, entonces puedo crear la canción
            if len(existe)>0:
                existe_2 = db.session.query(Cancion).filter(Cancion.id == id).all()
                #Si existe la canción, arrojo el error
                if len(existe_2)>0:
                    respuesta = jsonify({
                        "id": existe_2[0].id,
                        "album_id": album_id,
                        "name": existe_2[0].name,
                        "duration": existe_2[0].duration,
                        "times_played": existe_2[0].times_played,
                        "artist": existe_2[0].artist,
                        "album": existe_2[0].album,
                        "self": existe_2[0].self_
                    })
                    respuesta.status_code = 409
                    return respuesta
                #Si no existe la canción, la creo
                else:
                    cancion = Cancion(id, album_id, body["name"], body["duration"], 0, f"{os.environ.get('TAREA_URL')}artists/{existe[0].artist_id}", f"{os.environ.get('TAREA_URL')}albums/{album_id}", f"{os.environ.get('TAREA_URL')}tracks/{id}")
                    db.session.add(cancion)
                    db.session.commit()
                    respuesta = jsonify({
                        "id": cancion.id,
                        "album_id": album_id,
                        "name": cancion.name,
                        "duration": cancion.duration,
                        "times_played": 0,
                        "artist": cancion.artist,
                        "album": cancion.album,
                        "self": cancion.self_
                    })
                    respuesta.status_code = 201
                    return respuesta
            #Acá es porque el album ya existe
            else:
                respuesta = jsonify({})
                respuesta.status_code = 422
                return respuesta
        else:
            # Se levanta un error que dice que los datos entregados no son los correctos
            respuesta = jsonify({})
            respuesta.status_code = 400
            return respuesta
    
    else:
        # En caso de que no exista el metodo del request
        respuesta = jsonify({})
        respuesta.status_code = 405
        return respuesta


@app.route("/tracks", methods=['GET'])
def tracks():
    if request.method == "GET":
        consulta_canciones = db.session.query(Cancion).all()
        respuesta = []
        for cancion in consulta_canciones:
            respuesta.append({
                "id": cancion.id,
                "album_id": cancion.album_id,
                "name": cancion.name,
                "duration": cancion.duration,
                "times_played": cancion.artist,
                "artist": cancion.artist,
                "album": cancion.album,
                "self": cancion.self_
            })
        estatus = jsonify(respuesta)
        estatus.status_code = 200
        return estatus
    
    else:
        # En caso de que no exista el metodo del request
        respuesta = jsonify({})
        respuesta.status_code = 405
        return respuesta



if __name__ == '__main__':
    #Se activa la aplicación para que empiece a correr en el servidor
    app.run(debug=True, port=8000) 
    