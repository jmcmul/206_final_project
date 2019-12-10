from bs4 import BeautifulSoup
import requests
import json
import deezer
import wikipedia
import requests
import sqlite3
import plotly.graph_objects as go

url = "https://deezerdevs-deezer.p.rapidapi.com/playlist/3453772742"

headers = {
    'x-rapidapi-host': "deezerdevs-deezer.p.rapidapi.com",
    'x-rapidapi-key': "9656d1afc2mshda91478167cbde4p1bb07fjsn87d7f12066e8"
    }

response = requests.request("GET", url, headers=headers)

top_tracks = []
top_artists = []
duration_times = []
r = json.loads(response.text)
tracks = r['tracks']
for song in tracks['data'][0:50]:
    top_tracks.append(song['title'])
    duration_times.append(song['duration'])
    top_artists.append(song['artist']['name'])
list_of_urls = []
for (x,y) in zip(top_tracks,top_artists):
    search = "{} {}".format(x,y)
    results = wikipedia.search(search, results=2)
    searched = wikipedia.page(results[0])
    list_of_urls.append(searched.url)
genres = []
for url in list_of_urls:
    soup = BeautifulSoup(requests.get(url).text,'html.parser')
    table = soup.find('table', {'class': 'infobox'})
    list_of_genres1 = table.find('td', {'class': 'category hlist'})
    if list_of_genres1 != None:
        if list_of_genres1.find('a') != None:
            genre = list_of_genres1.find('a')
            genres.append(genre.text)
            print(genre.text)
        else:
            list_of_genres2 = list_of_genres1.find('div', {'class': 'hlist hlist-separated'})
            li = list_of_genres1.find('ul')
            genre = li.find('a')
            genres.append(genre.text)
            print(genre.text)
    else:
        genre = "unknown"
        genres.append(genre)
        print(genre)



id = 0
finish = 0
for (title, artist, duration, genre) in zip(top_tracks, top_artists, duration_times, genres):
    if finish == 20:
        break
    try:
        sqliteConnection = sqlite3.connect('track_db.sqlite')
        cursor = sqliteConnection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS deezerTracks(
                        id integer PRIMARY KEY,
                        Trackid integer ALTERNATE KEY,
                        duration integer,
                        Trackname text NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS deezerArtists(
                        id integer PRIMARY KEY,
                        Artistid integer ALTERNATE KEY,
                        Artistname text NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS deezerGenres(
                        id integer PRIMARY KEY,
                        Genreid integer ALTERNATE KEY,
                        Genrename text NOT NULL)''')
        print("Successfully Connected to SQLite")
        title.replace("'", '\'')
        artist.replace("'", '\'')
        genre.replace("'", '\'')
        sqlite_insert_query1 = """INSERT INTO `deezerTracks` (id, Trackid, duration, Trackname) VALUES ({}, {},{},"{}")""".format(id, id, duration, title)
        sqlite_insert_query2 = """INSERT INTO `deezerArtists` (id, Artistid, Artistname) VALUES ({}, {},"{}")""".format(id, id, artist)
        sqlite_insert_query3 = """INSERT INTO `deezerGenres` (id, Genreid, Genrename) VALUES ({}, {},"{}")""".format(id, id, genre)

        count1 = cursor.execute(sqlite_insert_query1)
        count2 = cursor.execute(sqlite_insert_query2)
        count3 = cursor.execute(sqlite_insert_query3)
        sqliteConnection.commit()
        print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
        finish += 1
        cursor.close()
        

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
         if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")

    id += 1
    if id == 50:
        sqliteConnection = sqlite3.connect('track_db.sqlite')
        cursor = sqliteConnection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS myResults AS SELECT Trackname, Artistname
                        FROM  deezerTracks JOIN  deezerArtists
                        ON Trackid = Artistid
                        WHERE deezerTracks.id = deezerArtists.id''')
        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()




genreDict ={}
for genre in genres:
    if genre in genreDict:
        genreDict[genre] += 1
    else:
        genreDict[genre] = 1


genre_list = []
genre_values = []
for key in genreDict.keys(): 
    genre_list.append(key) 
          
for value in genreDict.values():
    genre_values.append(value)



fig = go.Figure(data=[go.Pie(labels=genre_list,
                             values=genre_values)])
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=10,
                  marker=dict(line=dict(color='#000000', width=2)))

fig.update_layout(title_text="Deezer 2017")
#fig.show()
exit()


