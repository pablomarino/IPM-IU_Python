import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import data.Tmdb
from gi.repository import Gtk
from gi.repository import Gio
import requests
from io import BytesIO
from data.Films import Films
import threading

# recomendaciones desaparecer cuando no hay recomendaciones
# aparecer cuando hay
# botonera desactivar cuando solo hay un recomendacion

class UIHandler():
	# almaceno pelis vistas
	_f=Films()
	_listWidget=None
	_listViewedWidget=None
	_listPendingWidget=None
	_flist=None
	_fpending=Gtk.ListStore(str, str, str, str)
	_fviewed=Gtk.ListStore(str, str, str, str)
	_titles=[]
	_rec_actual = 0
	_builder = None
	_threads = list()

	##############################
	# METODOS GENERALES
	##############################
	def on_window_main_realize(self,w):
		UIHandler.hideRecommendationBox()
		UIHandler.showRecommendationBox()

	def __init__(self,builder):
		UIHandler._builder = builder
		UIHandler.retrieveRecommendations(self)
		UIHandler._listWidget=builder.get_object("treeview")
		UIHandler._listViewedWidget=builder.get_object("treeview1")
		UIHandler._listPendingWidget=builder.get_object("treeview2")
		UIHandler.updateLists()

		self.years= list(range(2016,1916,-1))
		self.sYears = UIHandler._builder.get_object("storeYears")
		for year in self.years:
			self.sYears.append([year])

	def updateLists():
		UIHandler._listWidget.set_model(UIHandler._flist)
		UIHandler._listViewedWidget.set_model(UIHandler._fviewed)
		UIHandler._listPendingWidget.set_model(UIHandler._fpending)

	def onDeleteWindow(self, *args):
		UIHandler._builder.get_object("window_main").set_sensitive(True)
		Gtk.main_quit(*args)

	##############################
	# METODOS WINDOW_MAIN
	##############################

	def onAdd(self, button):
		UIHandler._builder.get_object("window_main").set_sensitive(False)
		dialogo = UIHandler._builder.get_object("modal_input_add")

		UIHandler._builder.get_object("cboxYears").set_active(0)
		# Muestro la botonera de añadir
		UIHandler._builder.get_object("add_button_accept").show()
		UIHandler._builder.get_object("add_button_cancel").show()
		# Oculto la botonera de editar
		UIHandler._builder.get_object("edit_button_accept").hide()
		UIHandler._builder.get_object("edit_button_cancel").hide()
		dialogo.run()

	def onRemove(self, button):
		UIHandler._builder.get_object("window_main").set_sensitive(False)
		selection = UIHandler._listWidget.get_selection()
		data, row = selection.get_selected_rows()
		if row == []:
			UIHandler._builder.get_object("window_main").set_sensitive(False)
			dialogo = UIHandler._builder.get_object("modal_error")
			dialogo.run()
		else:
			UIHandler._builder.get_object("window_main").set_sensitive(False)
			dialogo = UIHandler._builder.get_object("modal_warning")
			dialogo.run()

	def onEdit(self, button):
		selection = UIHandler._listWidget.get_selection()
		data, row = selection.get_selected_rows()
		if row == []:
			# no hay seleccion
			UIHandler._builder.get_object("window_main").set_sensitive(False)
			dialogo = UIHandler._builder.get_object("modal_error")
			dialogo.run()
		else:
			# Muestro la botonera de editar
			UIHandler._builder.get_object("edit_button_accept").show()
			UIHandler._builder.get_object("edit_button_cancel").show()
			# Oculto la botonera de añadir
			UIHandler._builder.get_object("add_button_accept").hide()
			UIHandler._builder.get_object("add_button_cancel").hide()
			UIHandler._builder.get_object("window_main").set_sensitive(False)
			# obtengo los datos del registro seleccionado
			iter = data.get_iter(row[0])
			title = data.get_value(iter, 1)
			year = data.get_value(iter, 2)
			rating = data.get_value(iter, 3)
			vista = data.get_value(iter, 4)
			# los muestro en los campos
			UIHandler._builder.get_object("add_input_title").set_text(title)
			posYear = self.years.index(int(year))
			UIHandler._builder.get_object("cboxYears").set_active(posYear)
			UIHandler._builder.get_object("spinRating").set_value(float(rating))
			UIHandler._builder.get_object("cbox").set_active(int(vista))
			dialogo = UIHandler._builder.get_object("modal_input_add")
			dialogo.run()

	##############################
	# METODOS MODAL_INPUT_ADD
	##############################

	def onAcceptAdd(self, button):
		title = UIHandler._builder.get_object("add_input_title").get_text()
		posYear = UIHandler._builder.get_object("cboxYears").get_active()
		year = self.years[posYear]
		rating = UIHandler._builder.get_object("spinRating").get_value()
		vista = UIHandler._builder.get_object("cbox").get_active()
		if title != "" and year > 1900 and year < 2018 and rating !="":
			# remplazo la entrada en la base de datos y actualizo la ventana
			UIHandler._f.addFilm(title,str(year),str(rating),str(vista))
			UIHandler.retrieveRecommendations(self)
			UIHandler.updateLists()
			# Limpio las entradas de texto
			UIHandler._builder.get_object("add_input_title").set_text("")
			# Cierro el dialogo
			dialogo = UIHandler._builder.get_object("modal_input_add")
			dialogo.hide()
			UIHandler._builder.get_object("window_main").set_sensitive(True)

	def onCloseAdd(self, button):
		# Limpio las entradas de texto
		UIHandler._builder.get_object("add_input_title").set_text("")
		# Oculto el dialogo
		UIHandler._builder.get_object("modal_input_add").hide()
		# Devuelvo el foco a la ventana principal
		UIHandler._builder.get_object("window_main").set_sensitive(True)

	##############################
	# METODOS MODAL_INPUT_EDIT
	##############################

	def onAcceptModify(self, button):
		title = UIHandler._builder.get_object("add_input_title").get_text()
		posYear = UIHandler._builder.get_object("cboxYears").get_active()
		year = self.years[posYear]
		rating = UIHandler._builder.get_object("spinRating").get_value()
		vista = UIHandler._builder.get_object("cbox").get_active()
		if title != "" and year != "" and rating != "":
			data, row = UIHandler._listWidget.get_selection().get_selected_rows()
			iter = data.get_iter(row[0])
			id = data.get_value(iter, 0)
			# remplazo la entrada en la base de datos y actualizo la ventana
			UIHandler._f.editFilm(id,title, year, rating, vista)
			UIHandler.retrieveRecommendations(self)
			UIHandler.updateLists()
			# Limpio las entradas de texto
			UIHandler._builder.get_object("add_input_title").set_text("")
			# Cierro el dialogo
			dialogo = UIHandler._builder.get_object("modal_input_add")
			dialogo.hide()
			UIHandler._builder.get_object("window_main").set_sensitive(True)

	def onCloseModify(self, button):
		# Limpio las entradas de texto
		UIHandler._builder.get_object("add_input_title").set_text("")
		# Oculto el dialogo
		UIHandler._builder.get_object("modal_input_add").hide()
		# Devuelvo el foco a la ventana principal
		UIHandler._builder.get_object("window_main").set_sensitive(True)

	##############################
	# METODOS MODAL_WARNING
	##############################

	def onCloseQuestion(self, button):
		dialogo = UIHandler._builder.get_object("modal_warning")
		dialogo.hide()
		UIHandler._builder.get_object("window_main").set_sensitive(True)

	def onContinue(self, button):
		selection = UIHandler._builder.get_object("treeview").get_selection()
		data, row = selection.get_selected_rows()
		iter = data.get_iter(row[0])
		id = data.get_value(iter, 0)
		# Elimino el registro
		UIHandler._f.removeFilm(id)
		UIHandler.retrieveRecommendations(self)
		UIHandler.updateLists()
		# Oculto aviso eliminacion
		dialogo = UIHandler._builder.get_object("modal_warning")
		dialogo.hide()
		# Devuelvo el foco a la ventana principal
		UIHandler._builder.get_object("window_main").set_sensitive(True)

	##############################
	# METODOS MODAL_ERROR
	##############################

	def onAcceptError(self, button):
		UIHandler._builder.get_object("window_main").set_sensitive(True)
		dialogo = UIHandler._builder.get_object("modal_error")
		dialogo.hide()

	##############################
	# RECOMENDACIONES
	##############################

	def posterResize(self, window, rectangle):
		allocation = UIHandler._builder.get_object("overlay_recommendation").get_allocation()
		h = UIHandler._builder.get_object("overlay_recommendation").size_request()
		try:
			_pb_width = self.pixbuf.get_width()
			_pb_height = self.pixbuf.get_height()
			if(_pb_width>=_pb_height) and _pb_width!=0:
				self.temp_height = allocation.width*(_pb_height/_pb_width)
				self.temp_width = allocation.width
			else:
				self.temp_height=allocation.height
				self.temp_width= allocation.height*(_pb_width/_pb_height)
			self.p = self.pixbuf.scale_simple(self.temp_width, self.temp_height,  GdkPixbuf.InterpType.BILINEAR)#GdkPixbuf.InterpType.NEAREST)
			UIHandler._builder.get_object("poster").set_from_pixbuf(self.p)
		except:
			pass

	def previousPoster(self,button):
		anterior = UIHandler._rec_actual-1;
		if(anterior>=0):
			UIHandler._rec_actual=UIHandler._rec_actual-1
		else:
			UIHandler._rec_actual=len(UIHandler._titles)-1
		posterShow(self,UIHandler._titles,UIHandler._rec_actual)
		self.posterResize(None,None)
		print('::: recomendacion anterior', UIHandler._rec_actual)

	def nextPoster(self,button):
		print('::: recomendacion siguiente')
		siguiente = UIHandler._rec_actual+1;
		if(siguiente<len(UIHandler._titles)):
			UIHandler._rec_actual=UIHandler._rec_actual+1
		else:
			UIHandler._rec_actual=1
		posterShow(self,UIHandler._titles,UIHandler._rec_actual)
		self.posterResize(None,None)

	def retrieveRecommendations(self):
		UIHandler._flist=UIHandler._f.getFilms()
		UIHandler._fpending=Gtk.ListStore(str, str, str, str)
		UIHandler._fviewed=Gtk.ListStore(str, str, str, str)
		for i in UIHandler._flist:
			if(i[4]=='1'):
				print('::: Añado pelicula vista',i[1])
				UIHandler._fviewed.append([i[0],i[1],i[2],i[3]])
				UIHandler._titles.append(i[1])
			else:
				UIHandler._fpending.append([i[0],i[1],i[2],i[3]])
		if(len(UIHandler._fviewed)>0):
			posterShow(self,UIHandler._titles,UIHandler._rec_actual)
			UIHandler.showRecommendationBox()
		else:
			UIHandler.hideRecommendationBox()
			print('::: No hay peliculas vistas')

	def showRecommendationBox():
		_box=UIHandler._builder.get_object("box_recommend")
		if not _box.props.visible and (len(UIHandler._fviewed)>0):
			print('::: Show Recommendation Box')
			_box.show()
			UIHandler._builder.get_object("separator").show()

	def hideRecommendationBox():
		_box=UIHandler._builder.get_object("box_recommend")
		if _box.props.visible and (len(UIHandler._fviewed)==0):
			print('::: hide Recommendation Box')
			_box.hide()
			UIHandler._builder.get_object("separator").hide()

def _download_images(url, path='.'):
	r = requests.get(url, stream=True)
	filetype = r.headers['content-type'].split('/')[-1]
	with open('tmp/poster.jpeg','wb') as w:
		w.write(r.content)

def _showPreloader():
	UIHandler._builder.get_object("spinner").start()
	UIHandler._builder.get_object("poster").hide()

def _hidePreloder():
	UIHandler._builder.get_object("spinner").stop()
	UIHandler._builder.get_object("poster").show()



def posterShow(self,_titles,actual):
	t = threading.Thread(target=threadGetRecommendationsByTitle, args=(self,_titles,actual))
	t.setDaemon(True)
	t.start()
	UIHandler._threads.append(t)
	_showPreloader()

def threadGetRecommendationsByTitle(self,_titles,actual):
	print('::: Muestro posters recomendados por',_titles[actual])
	_recommendations = data.Tmdb.getRecommendationsByTitle(_titles[actual])
	doPosterShow(self,_titles,actual,_recommendations)

def doPosterShow(self,_titles,actual,_recommendations):
	if _recommendations['recommended']=={}:
		print("::: No hay recomendaciones para "+_titles[actual]+" lo elimino ")
		del(_titles[actual])
		if (actual<=len(_titles)):
			print('::: Cargo el siguiente')
			posterShow(self,_titles,actual)
		else:
			print('::: No hay ninguna pelicula en la lista, acabo')
			return
	else:
		_download_images(str(_recommendations['path'])+str(_recommendations['recommended']['poster_path']))
		UIHandler._builder.get_object("poster").set_from_file('tmp/poster.jpeg')
		try:
			self.pixbuf = UIHandler._builder.get_object("poster").get_pixbuf()
			self.temp_height = self.pixbuf.get_height()
			self.temp_width = self.pixbuf.get_width()
			UIHandler._builder.get_object("label_recommendation_Info").set_text(_recommendations['recommended']['title'])
			UIHandler._builder.get_object("label_viewed").set_text(_titles[actual])
		except Exception as e:
			pass
	_hidePreloder()
