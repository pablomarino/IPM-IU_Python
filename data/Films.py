import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import json



class Films():
    _file = 'json/films.json'
    _dataFile =''
    _films =''
    _activeid=0

    def __init__(self):
        self._dataFile = open(self._file, "r",-1,'UTF-8')
        self._films = json.loads(self._dataFile.read())
        self._dataFile.close()

    def getFilms(self):
        list = Gtk.ListStore(str, str, str, str, str)
        # creo id's unicos y consecutivos para cada entrada
        for i in range(len(self._films['data'])):
            self._films['data'][i]['id']=str(i)
        datafile = open(self._file, "w+", -1, 'UTF-8')
        datafile.write(json.dumps(self._films))
        datafile.close()
        for record in self._films['data']:
            list.append([record['id'],record['title'],record['year'],record['rating'],record['vista']])
        return list

    '''
    def getViewFilms(self,view):
        list = Gtk.ListStore(str, str, str, str,str)
        # creo id's unicos y consecutivos para cada entrada
        for i in range(len(self._films['data'])):
            self._films['data'][i]['id']=str(i)
        datafile = open(self._file, "w+", -1, 'UTF-8')
        datafile.write(json.dumps(self._films))
        datafile.close()
        for record in self._films['data']:
            if record["vista"] == str(view):
                list.append([record['id'],record['title'],record['year'],record['rating'],record['vista']])
        return list
    '''

    def addFilm(self,title,year,rating,vista):
        print('ADDFILM')
        self._films['data'].append({"title": title, "year": year, "rating": rating, "vista": vista})
        outfile = open(self._file, "w", -1, 'UTF-8')
        outfile.write(json.dumps(self._films))
        outfile.close()

    def editFilm(self,id,title,year,rating,vista):
        for i in range(len(self._films['data'])):
            if self._films['data'][i]['id'] == id:
                self._films['data'][i]['title'] = str(title)
                self._films['data'][i]['year'] = str(year)
                self._films['data'][i]['rating'] = str(rating)
                self._films['data'][i]['vista'] = str(vista)
                outfile = open(self._file, "w", -1, 'UTF-8')
                outfile.write(json.dumps(self._films))
                outfile.close()
                break

    def removeFilm(self,id):
        for i in range(len(self._films['data'])):
            if self._films['data'][i]['id'] == id:
                self._films['data'].pop(i)
                outfile = open(self._file, "w", -1, 'UTF-8')
                outfile.write(json.dumps(self._films))
                outfile.close()
                break

    def getFile(self):
        return self._file
