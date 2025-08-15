from qgis.core import QgsRasterLayer, QgsProject

class BasemapManager:
    def __init__(self):
        self.current_basemap_layer = None

        ##predefined basemaps url
        self.basemaps = {
            "OpenStreetMap": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "CartoDB Light": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            "CartoDB Dark": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            "Stamen Toner": "http://tile.stamen.com/toner/{z}/{x}/{y}.png",
            "Esri Satellite": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        }

    #add a custom basemap to the internal list
    def add_custom_basemap(self, name, url):
        if "{s}" in url:
            url = url.replace("{s}", "a")
        self.basemaps[name] = url
    
    def add_basemap(self, name):
        ##adds a basemap from the internal basemap dictionary by name
        if name not in self.basemaps:
            raise ValueError(f"Unknown basemap: {name}")
        
        url = self.basemaps[name]
        
        #optional: handle subdomains
        if "{s}" in url:
            url = url.replace("{s}", "a")  

        layer = QgsRasterLayer(f"type=xyz&url={url}", name, "wms")

        if not layer.isValid():
            raise RuntimeError(f"Failed to load basemap: {name}")
        
        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        root.insertLayer(0, layer)

        if self.current_basemap_layer and self.current_basemap_layer != layer:
            QgsProject.instance().removeMapLayer(self.current_basemap_layer)

        self.current_basemap_layer = layer
