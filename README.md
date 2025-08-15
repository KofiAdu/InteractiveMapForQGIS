# Interactive Map – QGIS Plugin

Turn any QGIS vector layers into a polished, interactive **web map** powered by your choice of **Leaflet**, **OpenLayers**, or **Mapbox**. Load a basemap, add one or more vector layers (SHP, GeoJSON, KML/KMZ, GPKG, GDB), tweak layer names (in the QGIS Layers Panel) for friendly popups, and **export** a self‑contained web map—no coding required.

---

## Features
- **Basemaps in QGIS**: One‑click access to built‑in basemaps (hard‑coded list). Add your **custom basemap URLs** as well (Optional).
- **Flexible data input**: Load multiple vector layers via the plugin: **Shapefile (SHP), GeoJSON, KML/KMZ, GeoPackage (GPKG), Geodatabase (GDB)**.
- **Readable layer names**: Rename layers / set field aliases in QGIS so popups and layer lists use clean, human‑friendly titles.
- **Export to the web**:
  - **Leaflet** or **OpenLayers** with a basemap switcher and layer toggles.
  - **Mapbox** (requires an access token) including support for your **Mapbox Studio** custom styles.
- **Interactive UI**: Click points/lines/polygons for attribute **popups**; toggle layers on/off; switch basemaps.
- **Multi‑layer exports**: Include as many layers as you like—**only layers loaded via the plugin** are exported.

> **Important design note:** Only **vector layers loaded via the plugin** are included in exports. To remove a layer from an export, restart the plugin (or QGIS) and reload only the layers you want.

---

## Install

> Not published to the official QGIS Plugins Repository (yet). Install manually:

### Option 1: Manual Installation
1. Download/clone this repository folder into your QGIS plugins directory.

**Windows**
```
C:\Users\<your_username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

**Linux/macOS**
```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

2. Restart QGIS.
3. Enable from **Plugins ▸ Manage and Install Plugins**.

### Option 2: Plugin Manager (if/when published)
1. Open **QGIS**
2. **Plugins ▸ Manage and Install Plugins**
3. Search for **Interactive Map**
4. Click **Install**

---

## Requirements
- **QGIS 3.x**
- Internet connection for basemaps and web assets
- **Mapbox** exports: a **Mapbox access token** (free account at mapbox.com)

---

## How to Use

1. **Open the plugin**  
   *Plugins ▸ Interactive Map ▸ Open*

2. **(Optional) Load a basemap in QGIS**  
   Pick from the built‑ins, or paste a **custom XYZ/Tile URL**. Your chosen basemap will also be available in the exported web map’s basemap switcher.

3. **Load vector layers (via the plugin)**  
   Use the plugin’s loader to add any number of layers (SHP, GeoJSON, KML/KMZ, GPKG, GDB).  
   > *Only layers added through the plugin are included in export.*

4. **Tidy names for the web**  
   In QGIS, rename layers and set field aliases so your **popup titles and attribute labels** look good in the web map.

5. **Choose your web map library**  
   - **Leaflet/OpenLayers**: pick any basemap from the list.
   - **Mapbox**: paste your **Mapbox token**. Select a Mapbox basemap or paste a **Mapbox Studio style URL** to use your own custom map.

6. **Export**  
   Choose an output folder. The plugin generates a ready‑to‑open **`index.html`** with required assets and your data.

7. **Open & explore**  
   Open `{maplibrary}.html` in a browser. Toggle layers, switch basemaps, and click features for popups.

---

## Output Structure (typical)
```
output/
├─ `{maplibrary}.html`
└─ data/              #Exported vector layers (e.g., GeoJSON)
```

---

## Notes & Tips
- Works best if your data is in **WGS84 (EPSG:4326)** for web mapping. (The plugin handles reprojection where possible.)
- Rename layers/fields in QGIS for clean popup labels.
- **Mapbox**: keep your token private; don’t commit it to public repos.
- If the map doesn’t load when double‑clicking `{maplibrary}.html`, run a simple local web server (some browsers block local file access to JSON):
  ```bash
  # Python 3
  python -m http.server 8000
  # then visit http://localhost:8000 in your browser
  ```

---

## Troubleshooting
- **“My layer isn’t in the export.”**  
  Ensure you loaded it **through the plugin**. To remove layers from an export, **restart the plugin/QGIS** and reload only the layers you want.

- **Layer Removal/Deletion**

- **“Basemap not showing.”**  
  Check your internet connection and, for **Mapbox**, confirm your access token. For custom XYZ URLs, verify the template.

- **“Popups show ugly field names.”**  
  Set field **aliases** or rename fields in QGIS before export.

- **“Projection looks off.”**  
  Reproject layers to **EPSG:4326** in QGIS before export.

---

## Roadmap
- Publish to the **QGIS Plugin Repository**
- WMS/WMTS basemap support
- Style/theme options for web maps (dark mode, print layouts)
- More popup configuration (media, links, formatting)

---

## Contributing
Pull requests and issues welcome! If you add a new basemap or library option, include a short description and test data if possible.

---

## About
**Interactive Map** is built for GIS users and developers who want fast, clean web maps from QGIS—without writing JavaScript.

---

## License
Add a license (e.g., **MIT**) to the repository’s root as `LICENSE`.

