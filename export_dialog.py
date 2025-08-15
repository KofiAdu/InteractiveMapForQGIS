from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5 import uic
import os

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "export_dialog.ui")
        uic.loadUi(ui_path, self)

        ##connect ok and cancel
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        ##hide advanced mapbox fields by default
        self.apiTokenLineEdit.hide()
        self.customStyleLineEdit.hide()
        self.label_3.hide()
        self.label_customStyle.hide()

        ##format options / types of map libraries
        self.formatComboBox.addItems(["Leaflet", "OpenLayers", "Mapbox"])
        self.update_basemaps("Leaflet")

        ##connect signals
        self.formatComboBox.currentTextChanged.connect(self.update_visibility)
        self.browseButton.clicked.connect(self.pick_folder)
        

    def update_visibility(self):
        selected = self.formatComboBox.currentText()

        ##show/hide Mapbox inputs
        is_mapbox = selected == "Mapbox"
        self.apiTokenLineEdit.setVisible(is_mapbox)
        self.customStyleLineEdit.setVisible(is_mapbox)
        self.label_3.setVisible(is_mapbox)
        self.label_customStyle.setVisible(is_mapbox)

        ##update basemaps
        self.update_basemaps(selected)

    def update_basemaps(self, engine):
        self.basemapComboBox.clear()

        if engine == "Mapbox":
            self.basemapComboBox.addItems([
                "Mapbox Standard",
                "Mapbox Streets",
                "Mapbox Satellite",
                "Mapbox Light",
                "Mapbox Dark",
                "Custom Mapbox Style"
            ])
        else:
            self.basemapComboBox.addItems([
                "OpenStreetMap",
                "Carto Light",
                "Carto Dark",
                "Stamen Toner",
                "Esri Satellite",
                "Custom XYZ"
            ])

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self.folderLineEdit.setText(folder)

    def get_settings(self):
        return {
            "engine": self.formatComboBox.currentText(),
            "basemap": self.basemapComboBox.currentText(),
            "token": self.apiTokenLineEdit.text(),
            "custom_style_id": self.customStyleLineEdit.text(),
            "output_folder": self.folderLineEdit.text(),
        }
