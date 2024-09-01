import sys
import io
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import folium
from folium import plugins
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

class WazeLikeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initMap()
        self.initGraph()

    def initUI(self):
        self.setWindowTitle('Optimización de Rutas - Perú')
        self.setGeometry(100, 100, 1200, 800)

        layout = QHBoxLayout()

        # Sidebar
        sidebar = QVBoxLayout()
        self.origin_input = QLineEdit()
        self.origin_input.setPlaceholderText("Origen")
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Destino")
        self.search_button = QPushButton("Buscar Ruta")
        self.search_button.clicked.connect(self.searchRoute)

        sidebar.addWidget(QLabel("Origen:"))
        sidebar.addWidget(self.origin_input)
        sidebar.addWidget(QLabel("Destino:"))
        sidebar.addWidget(self.destination_input)
        sidebar.addWidget(self.search_button)
        sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(300)

        # Map view
        self.web_view = QWebEngineView()
        
        layout.addWidget(sidebar_widget)
        layout.addWidget(self.web_view)

        self.setLayout(layout)

    def initMap(self):
        m = folium.Map(location=[-9.1900, -75.0152], zoom_start=6)
        plugins.Fullscreen().add_to(m)
        plugins.MousePosition().add_to(m)
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())

    def initGraph(self):
        self.G = nx.Graph()
        self.ciudades = {
            "Lima": (-12.0464, -77.0428),
            "Arequipa": (-16.4090, -71.5375),
            "Trujillo": (-8.1116, -79.0289),
            "Chiclayo": (-6.7764, -79.8443),
            "Cusco": (-13.5319, -71.9675),
            "Iquitos": (-3.7491, -73.2538),
            "Piura": (-5.1945, -80.6328),
            "Huancayo": (-12.0651, -75.2049),
            "Tacna": (-18.0146, -70.2536),
            "Pucallpa": (-8.3791, -74.5539)
        }
        for ciudad, coords in self.ciudades.items():
            self.G.add_node(ciudad, pos=coords)

        rutas = [
            ("Lima", "Arequipa"), ("Lima", "Trujillo"), ("Lima", "Huancayo"),
            ("Arequipa", "Cusco"), ("Arequipa", "Tacna"),
            ("Trujillo", "Chiclayo"), ("Chiclayo", "Piura"),
            ("Cusco", "Pucallpa"), ("Pucallpa", "Iquitos")
        ]
        self.G.add_edges_from(rutas)

    def searchRoute(self):
        origin = self.origin_input.text()
        destination = self.destination_input.text()

        origin_coords = self.geocode(origin)
        destination_coords = self.geocode(destination)

        if origin_coords and destination_coords:
            self.showRoute(origin_coords, destination_coords)
        else:
            print("No se pudo encontrar una o ambas ubicaciones.")

    def geocode(self, address):
        geolocator = Nominatim(user_agent="waze_like_app")
        try:
            location = geolocator.geocode(address + ", Peru")
            if location:
                return location.latitude, location.longitude
            else:
                return None
        except (GeocoderTimedOut, GeocoderUnavailable):
            return None

    def showRoute(self, origin, destination):
        m = folium.Map(location=origin, zoom_start=10)
        folium.Marker(origin, popup="Origen").add_to(m)
        folium.Marker(destination, popup="Destino").add_to(m)

        # Aquí iría la lógica para encontrar la ruta óptima
        # Por ahora, solo dibujamos una línea recta entre origen y destino
        folium.PolyLine([origin, destination], color="red", weight=2.5, opacity=0.8).add_to(m)

        plugins.Fullscreen().add_to(m)
        plugins.MousePosition().add_to(m)
        
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WazeLikeApp()
    ex.show()
    sys.exit(app.exec_())