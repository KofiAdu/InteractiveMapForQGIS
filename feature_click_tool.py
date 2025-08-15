from qgis.gui import QgsMapToolIdentifyFeature
from qgis.PyQt.QtWidgets import QMessageBox

##click interactivity
class FeatureClickTool(QgsMapToolIdentifyFeature):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas

    def featureIdentified(self, feature):
        attrs = feature.attributes()
        fields = feature.fields()
        info = "\n".join(f"{fields[i].name()}: {attrs[i]}" for i in range(len(attrs)))
        QMessageBox.information(None, "Feature Info", info)