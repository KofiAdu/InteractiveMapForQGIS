# exporter.py

import os, tempfile, json, shutil
from qgis.core import (
        QgsProject, QgsVectorLayer,
        QgsVectorFileWriter, QgsCoordinateReferenceSystem, 
        QgsCoordinateTransform, QgsWkbTypes
    )


def normalize_style_id(s: str) -> str:
        s = (s or "").strip()
        if not s:
            return ""
        #accept any of these forms and return "username/styleid"
        prefixes = [
            "mapbox://styles/",
            "https://api.mapbox.com/styles/v1/",
            "http://api.mapbox.com/styles/v1/",
        ]
        for p in prefixes:
            if s.startswith(p):
                s = s[len(p):]
                break
        s = s.split("?", 1)[0]
        return s  #expected: "mapboxname/xxxxxxxxxxxxxxxxxxx"

class Exporter:
    def __init__(self, iface, plugin_dir, loaded_vector_layers):
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.loaded_vector_layers = loaded_vector_layers

    def export_to_web_map(self, settings):
        print("Starting export with settings:", settings)

      
        engine = settings["engine"]  #Leaflet, Openlayer or Mapbox
        tpl_path = os.path.join(self.plugin_dir, "templates", f"{engine.lower()}_template.html")
        if not os.path.exists(tpl_path):
            self.iface.messageBar().pushCritical("Export Error", f"Missing template: {tpl_path}")
            return
        template = open(tpl_path, "r", encoding="utf-8").read()

        basemap_url = self.get_basemap_url(settings)

        file_url_mode = bool(settings.get("file_url_mode", True))  

        #cap size for leaflet 
        LEAFLET_MAX_MB_DEFAULT = 350
        leaflet_max_mb = int(settings.get("leaflet_max_mb", LEAFLET_MAX_MB_DEFAULT))
        leaflet_max_bytes = leaflet_max_mb * 1024 * 1024

        
        MAX_JS_WRAP_MB_DEFAULT = 250  
        max_js_wrap_mb = int(settings.get("max_js_wrap_mb", MAX_JS_WRAP_MB_DEFAULT))
        max_js_wrap_bytes = max_js_wrap_mb * 1024 * 1024

        #output folders
        out_dir = (settings.get("output_folder") or "").strip() or os.path.join(os.path.expanduser("~"), "InteractiveMap_Export")
        data_dir = os.path.join(out_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        #crs conversion setup
        dest_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        ctx = QgsProject.instance().transformContext()

        manifest = {"layers": []}
        exported_any = False
        preload_scripts = [] 
        skipped_large = []   
        skipped_offline = []  

        #export each vector layer
        for layer in QgsProject.instance().mapLayers().values():
            if not isinstance(layer, QgsVectorLayer) or not layer.isValid():
                continue

            safe = self._safe_name(layer.name())
            print("→ exporting", layer.name(), "→", safe)

            # temp GeoJSON in EPSG:4326 (RFC7946-friendly)
            tmp_path = os.path.join(tempfile.gettempdir(), f"{layer.id()}.geojson")

            opt = QgsVectorFileWriter.SaveVectorOptions()
            opt.driverName   = "GeoJSON"
            opt.fileEncoding = "UTF-8"
            opt.ct           = QgsCoordinateTransform(layer.crs(), dest_crs, ctx)
            opt.layerOptions = ["RFC7946=YES", "WRITE_BBOX=NO", "COORDINATE_PRECISION=6"]

            err_code, err_msg = QgsVectorFileWriter.writeAsVectorFormatV2(layer, tmp_path, ctx, opt)
            print("writer-return →", layer.name(), err_code, err_msg)
            if err_code != QgsVectorFileWriter.NoError:
                print("⚠️  write error, skipped:", layer.name(), "| reason:", err_msg)
                continue

            size_bytes = os.path.getsize(tmp_path)

            if engine == "Leaflet" and size_bytes > leaflet_max_bytes:
                skipped_large.append((layer.name(), size_bytes))
                print(f"⏭️  Skipping '{layer.name()}' – {size_bytes/1024/1024:.1f} MB exceeds Leaflet limit ({leaflet_max_mb} MB).")
                continue

            if file_url_mode and size_bytes > max_js_wrap_bytes:
                skipped_offline.append((layer.name(), size_bytes))
                print(f"⏭️  Skipping '{layer.name()}' – {size_bytes/1024/1024:.1f} MB exceeds offline JS-wrap limit ({max_js_wrap_mb} MB).")
                continue

            out_geojson = os.path.join(data_dir, f"{safe}.geojson")
            shutil.copyfile(tmp_path, out_geojson)

            # layer metadata
            ext = layer.extent()
            bounds = [ext.xMinimum(), ext.yMinimum(), ext.xMaximum(), ext.yMaximum()]
            gtype = QgsWkbTypes.displayString(layer.wkbType())

            manifest["layers"].append({
                "id": layer.id(),
                "key": safe,
                "name": layer.name(),
                "type": "geojson",
                "path": f"data/{safe}.geojson",
                "geometryType": gtype,
                "bounds": bounds
            })
            exported_any = True

            if file_url_mode:
                js_path = os.path.join(data_dir, f"{safe}.js")
                with open(out_geojson, "r", encoding="utf-8") as f:
                    gj = f.read()
                with open(js_path, "w", encoding="utf-8") as jf:
                    jf.write(
                        f'window.__layers = window.__layers || {{}}; '
                        f'window.__layers["{safe}"] = {gj};'
                    )
                preload_scripts.append(f'<script src="data/{safe}.js"></script>')

        def _fmt_mb(n): return f"{n/1024/1024:.1f} MB"

        if skipped_large:
            msg = "Skipped (too large for Leaflet): " + ", ".join([f"{n} ({_fmt_mb(b)})" for n,b in skipped_large])
            self.iface.messageBar().pushWarning("Leaflet limit", msg)

        if skipped_offline:
            msg = ("Skipped for offline (double-click) mode: " +
                ", ".join([f"{n} ({_fmt_mb(b)})" for n,b in skipped_offline]) +
                f". Tip: switch engine (OpenLayers/Mapbox) or lower size, or serve via http.")
            self.iface.messageBar().pushInfo("Offline limit", msg)

        if not exported_any:
            self.iface.messageBar().pushCritical(
                "Export stopped",
                (f"No layers exported. Leaflet cap: {leaflet_max_mb} MB; "
                f"offline JS-wrap cap: {max_js_wrap_mb} MB.")
            )
            return

        manifest_url = "data/manifest.json"
        if file_url_mode:
            with open(os.path.join(data_dir, "manifest.js"), "w", encoding="utf-8") as jf:
                jf.write("window.__manifest = " + json.dumps(manifest, ensure_ascii=False) + ";")
            preload_scripts.insert(0, '<script src="data/manifest.js"></script>')
        else:
            with open(os.path.join(data_dir, "manifest.json"), "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, ensure_ascii=False, indent=2)

        style_url = self.get_mapbox_style_url(settings)
        token = settings.get("token", "")
        html = (template
            .replace("{{BASEMAP_URL}}", basemap_url or "")
            .replace("{{MANIFEST_URL}}", manifest_url)
            .replace("{{PRELOAD_SCRIPTS}}", "\n  ".join(preload_scripts))
            .replace("{{MAPBOX_TOKEN}}", token)
            .replace("{{MAPBOX_STYLE}}", style_url or ""))

        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{engine.lower()}_map.html")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            self.iface.messageBar().pushSuccess("Export Complete", f"Map saved: {out_path}")
            print("Exported HTML map:", out_path)
        except Exception as e:
            self.iface.messageBar().pushCritical("Export Failed", str(e))
            print("Failed to write HTML:", e)


    def _safe_name(self, s: str) -> str:
        keep = "abcdefghijklmnopqrstuvwxyz0123456789_-"
        s2 = "".join(ch if ch.lower() in keep else "-" for ch in s.lower())
        while "--" in s2: s2 = s2.replace("--","-")
        return s2.strip("-") or "layer"


    def get_mapbox_style_url(self, settings):
        basemap = settings["basemap"]
        if basemap == "Mapbox Standard":
            return "mapbox://styles/mapbox/standard"  
        if basemap == "Custom Mapbox Style":
            cid = normalize_style_id(settings.get("custom_style_id"))
            if cid:
                return f"mapbox://styles/{cid}"
        return "" 


    def get_basemap_url(self, settings):
        engine = settings["engine"]
        basemap = settings["basemap"]

        if engine == "Mapbox":
            token = settings["token"] or ""
            if basemap == "Custom Mapbox Style":
                style_id = normalize_style_id(settings.get("custom_style_id")) or "mapbox/streets-v11"
            elif basemap == "Mapbox Streets":
                style_id = "mapbox/streets-v11"
            elif basemap == "Mapbox Satellite":
                style_id = "mapbox/satellite-v9"
            elif basemap == "Mapbox Light":
                style_id = "mapbox/light-v10"
            elif basemap == "Mapbox Dark":
                style_id = "mapbox/dark-v10"
            elif basemap == "Mapbox Standard":
                return ""
            else:
                style_id = "mapbox/streets-v11"

            return f"https://api.mapbox.com/styles/v1/{style_id}/tiles/{{z}}/{{x}}/{{y}}?access_token={token}"

        urls = {
            "OpenStreetMap": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Carto Light": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
            "Carto Dark": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
            "Stamen Toner": "http://tile.stamen.com/toner/{z}/{x}/{y}.png",
            "Esri Satellite": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "Custom XYZ": settings.get("custom_url", "https://tile.openstreetmap.org/{z}/{x}/{y}.png")
        }
        return urls.get(basemap, urls["OpenStreetMap"])
