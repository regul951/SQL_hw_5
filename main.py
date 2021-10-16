import sqlalchemy
from pprint import pprint

dbname = input('Введите название базы данных: ')
host = input('Введите host базы данных: ')
user = input('Введите имя пользователя: ')
pswd = input('Введите пароль пользователя: ')
db = f'postgresql://{user}:{pswd}@{host}/{dbname}'
engine = sqlalchemy.create_engine(db)
connection = engine.connect()

# # Очистка таблиц на время тестов
query_restart = 'TRUNCATE TABLE ' \
                'genre, singer, album, singergenre, singeralbum, track, collection, collectiontrack ' \
                'RESTART IDENTITY CASCADE;'
result_restart = connection.execute(query_restart)

# Заполнение таблицы Singer
with open("Singer.txt", "r", encoding='utf-8') as f:
    while True:
        s = (f.readline().rstrip().split(';'))
        if s == ['']:
            break
        query_insert_singer = f'INSERT INTO singer(pseudonym) VALUES(\'{s[0]}\');'
        result_insert_singer = connection.execute(query_insert_singer)

# Заполнение таблицы Genre
with open("Genre.txt", "r", encoding='utf-8') as f:
    while True:
        s = (f.readline().rstrip().split(';'))
        if s == ['']:
            break
        query_insert_genre = f'INSERT INTO genre(title) VALUES(\'{s[0]}\');'
        result_insert_genre = connection.execute(query_insert_genre)

# Заполнение таблицы SingerGenre
with open("SingerGenre.txt", "r", encoding='utf-8') as f:

    singer = connection.execute('SELECT * FROM singer;').fetchall()
    genre = connection.execute('SELECT * FROM genre;').fetchall()

    while True:
        s = (f.readline().rstrip().split(';'))
        if s == ['']:
            break
        for singer_id, pseudonym in singer:
            if pseudonym == s[0]:
                for genre_id, title in genre:
                    if title == s[1]:
                        query_insert_singergenre = f'INSERT INTO singergenre(singer_id, genre_id)' \
                                                   f'VALUES({singer_id}, {genre_id});'
                        result_insert_singergenre = connection.execute(query_insert_singergenre)

# Заполнение таблиц Album, SingerAlbum
with open("Album.txt", "r", encoding='utf-8') as f:
    while True:
        s = (f.readline().rstrip().split(';'))
        if s == ['']:
            break
        query_insert = f'INSERT INTO album(title, year) VALUES(\'{s[0]}\', {s[1]});'
        result_insert = connection.execute(query_insert)

        singer = connection.execute('SELECT * FROM singer;').fetchall()
        album = connection.execute('SELECT * FROM album;').fetchall()

        for key, val in singer:
            if val == s[2]:
                query_insert = f'INSERT INTO singeralbum(singer_id, album_id)' \
                               f'VALUES({key}, {len(album)});'
                result_insert = connection.execute(query_insert)

# Заполнение таблицы Collection
with open("Collection.txt", "r", encoding='utf-8') as f:
    while True:
        s = (f.readline().rstrip().split(';'))
        if s == ['']:
            break
        query_insert = f'INSERT INTO collection(title, duration, year) VALUES(\'{s[0]}\', {s[1]}, {s[2]});'
        result_insert = connection.execute(query_insert)

# Заполнение таблиц Track, CollectionTrack
with open("Track.csv", "r", encoding='utf-8') as f:
    f.readline()

    while True:
        s = (f.readline().rstrip().split(';'))

        if s == ['']:
            break
        album = connection.execute('SELECT id, title FROM album;').fetchall()
        collection = connection.execute('SELECT id, title FROM collection;').fetchall()
        for id_album, title_album in album:
            if title_album == s[2]:
                query_insert = f'INSERT INTO track(title, duration, album_id) ' \
                               f'VALUES(\'{s[4][:40]}\', {s[5]}, {id_album});'
                result_insert = connection.execute(query_insert)

        track = connection.execute('SELECT id, title FROM track;').fetchall()
        for id_coll, title_coll in collection:
            if title_coll == s[6]:
                for id_track, title_track in track:
                    if title_track == s[4]:
                        query_insert = f'INSERT INTO collectiontrack(collection_id, track_id) ' \
                                       f'VALUES({id_coll}, {id_track});'
                        result_insert = connection.execute(query_insert)


# Запросы:
# количество исполнителей в каждом жанре
count_singer = connection.execute('SELECT title, COUNT(singer_id) FROM singergenre '
                                  'JOIN genre ON genre_id = id '
                                  'GROUP BY(title);').fetchall()
pprint(f'1. Количество исполнителей в каждом жанре: {count_singer}')

# количество треков, вошедших в альбомы 2019-2020 годов
count_track = connection.execute('SELECT year, COUNT(track.id) FROM track '
                                 'JOIN album ON  track.album_id = album.id '
                                 'WHERE year = 2019 OR year = 2020 '
                                 'GROUP BY(year);').fetchall()
pprint(f'2. Количество треков, вошедших в альбомы 2019-2020 годов: {count_track}')

# средняя продолжительность треков по каждому альбому
avg_track = connection.execute('SELECT album.title, AVG(track.duration) FROM track '
                               'JOIN album ON  track.album_id = album.id '
                               'GROUP BY(album.title);').fetchall()
pprint(f'3. Средняя продолжительность треков по каждому альбому: {avg_track}')

# все исполнители, которые не выпустили альбомы в 2020 году
not_2020_album = connection.execute('SELECT singer.pseudonym, album.title, album.year FROM singeralbum '
                                    'JOIN album ON  singeralbum.album_id = album.id '
                                    'JOIN singer ON  singeralbum.singer_id = singer.id '
                                    'WHERE NOT year = 2020'
                                    'ORDER BY(year);').fetchall()
pprint(f'4. Все исполнители, которые не выпустили альбомы в 2020 году: {not_2020_album}')

# названия сборников, в которых присутствует конкретный исполнитель (выберите сами):
# Chris Brown , Elvis Presley, Jenny Hval, Mariza, Michael Buble, Paul McCartney, Rod Stewart, Sting
find_singer = 'Jenny Hval'
coll_singer = connection.execute('SELECT DISTINCT c.title FROM collection c '
                                 'JOIN collectiontrack ct ON c.id = ct.collection_id '
                                 'JOIN track t ON ct.track_id = t.id '
                                 'JOIN album a ON t.album_id = a.id '
                                 'JOIN singeralbum sa ON a.id = sa.album_id '
                                 'JOIN singer s ON sa.singer_id = s.id '
                                 f'WHERE s.pseudonym = \'{find_singer}\' '
                                 'ORDER BY(c.title);').fetchall()
pprint(f'5. Названия сборников, в которых присутствует {find_singer}: {coll_singer}')


# название альбомов, в которых присутствуют исполнители более 1 жанра
more_genre = connection.execute('select title, pseudonym, count(genre_id) FROM album a '
                                'JOIN singeralbum sa ON a.id = sa.album_id '
                                'JOIN singer s ON sa.singer_id = s.id '
                                'JOIN singergenre sg ON s.id = sg.singer_id '
                                'group by(a.title, pseudonym) '
                                'having count(genre_id) > 1;').fetchall()
pprint(f'6. Названия сборников, альбомов, в которых присутствуют исполнители более 1 жанра: {more_genre}')

# наименование треков, которые не входят в сборники
not_coll = connection.execute('SELECT track.title FROM track '
                              'LEFT JOIN collectiontrack ON track.id = collectiontrack.track_id '
                              'WHERE collectiontrack.collection_id IS NULL;').fetchall()
pprint(f'7. Наименование треков, которые не входят в сборники: {not_coll}')

# исполнителя(-ей), написавшего самый короткий по продолжительности трек (может быть несколько)
min_duration = connection.execute('SELECT pseudonym, duration FROM track '
                                  'JOIN album a ON track.album_id = a.id '
                                  'JOIN singeralbum sa ON a.id = sa.album_id '
                                  'JOIN singer s ON sa.singer_id = s.id '
                                  'WHERE duration = (SELECT MIN(duration) FROM track);').fetchall()
pprint(f'8. Исполнитель(-и), написавший самый короткий по продолжительности трек: {min_duration}')


# название альбомов, содержащих наименьшее количество треков
min_length_alb = connection.execute(
    'SELECT DISTINCT a.title, min_alb.count_track FROM track '
    'JOIN album a ON track.album_id = a.id '
    'JOIN ('
        'SELECT album_id, count(id) AS count_track '
        'FROM track GROUP BY(album_id)'
        ') AS min_alb ON a.id = min_alb.album_id '
    'WHERE min_alb.count_track = ('
        'SELECT MIN(min_alb.count_track) FROM track '
        'JOIN album a ON track.album_id = a.id '
        'JOIN ('
            'SELECT album_id, count(id) as count_track '
            'FROM track group by(album_id)'
            ') AS min_alb ON a.id = min_alb.album_id);').fetchall()
pprint(f'9. Названия альбомов, содержащих наименьшее количество треков: {min_length_alb}')
