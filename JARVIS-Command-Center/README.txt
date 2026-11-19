J.A.R.V.I.S. COMMAND CENTER
===========================

A browser-based dashboard featuring your supplied Hologram.glb model and the visual palette cues extracted from materials.json.

RUN IT
------
1. Extract the ZIP to a normal folder.
2. Make sure Python 3 is installed.
3. Double-click START-JARVIS.bat.
4. Open http://localhost:8000 when the browser does not open automatically.

A local web server is required because browsers block loading local GLB/JSON assets from file:// pages.

FEATURES
--------
- Interactive 3D hologram: drag to rotate, scroll to zoom.
- Rotation toggle, view reset, custom GLB upload and intensity slider.
- Overview, activity, directives, hardware and memory views.
- Add and complete sample directives.
- Command dock with working demo commands.
- Responsive desktop and mobile layouts.

ASSET / MATERIAL NOTES
----------------------
The original Hologram.glb is included unchanged. The browser renderer recreates the key visual cues present in materials.json: electric-blue emission, amber view-angle highlights, blue secondary tint, transparent body and animated scanline/noise detail. Blender shader nodes are not directly executable in Three.js, so this is a real-time browser approximation rather than a literal node-for-node conversion.

IMPORTANT
---------
This is a front-end prototype. CPU, RAM, temperature, network and device states are illustrative demo values, not live readings from your computer. No external accounts or services are connected. Three.js and the selected fonts are loaded from CDNs, so an internet connection is required on first load.
