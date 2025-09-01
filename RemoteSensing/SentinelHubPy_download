import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

# Importamos solo lo necesario para CONSTRUIR la petición
from sentinelhub import (
    DataCollection, MimeType, BBox, CRS, MosaickingOrder,
    SentinelHubRequest
)

# ===================================================================
# PASO 1: CREAR UNA SESIÓN AUTENTICADA (El método fiable)
# ===================================================================
CLIENT_ID = "sh-140573ad-defa-41d4-96e9-eb114e38379a"
CLIENT_SECRET = "wacmrBkcZmRNRwDzJjDA4mFYrLTVSoBV"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

client = BackendApplicationClient(client_id=CLIENT_ID)
oauth_session = OAuth2Session(client=client)
oauth_session.fetch_token(token_url=TOKEN_URL, client_secret=CLIENT_SECRET)
print("Sesión autenticada creada con éxito.")

# ===================================================================
# PASO 2: USAR SENTINELHUB-PY SOLO PARA CONSTRUIR EL PAYLOAD
# ===================================================================
# ... (Aquí va tu código para pedir fechas y el geojson) ...
geojson_path = r"G:/Shared drives/LL - Delivery - team Iberia/01.1 Projects Spain & Portugal/03. Drone&GIS/7. Cartographic analysis/Mawan/GIS/References_geojsons/surface_water_study.geojson"
start_date_str = input("Introduce la fecha de inicio (formato AAAA-MM-DD): ")
end_date_str = input("Introduce la fecha de fin (formato AAAA-MM-DD): ")
time_interval = (start_date_str, end_date_str)

def get_bbox_from_geojson(geojson_path):
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    coords = geojson_data['features'][0]['geometry']['coordinates']
    flat_coords = np.squeeze(coords)
    min_lon, min_lat = flat_coords.min(axis=0)
    max_lon, max_lat = flat_coords.max(axis=0)
    return [min_lon, min_lat, max_lon, max_lat]

bbox_coords = get_bbox_from_geojson(geojson_path)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
print(f"Usando Bounding Box del archivo: {bbox_coords}")

evalscript = """
//VERSION=3
function setup() {
  return { input:["B02","B03","B04","B08"], output:{ id:"default", bands:4 } };
}
function evaluatePixel(s){
  return [2.5*s.B04, 2.5*s.B03, 2.5*s.B02, 2.5*s.B08];
}
"""

request_builder = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=time_interval,
            mosaicking_order=MosaickingOrder.LEAST_CC
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=(1024, 1024)
)

# Extraemos el diccionario JSON (el "payload") de la petición
payload = request_builder.download_list[0].post_values # <-- LÍNEA CORREGIDA

# ===================================================================
# PASO 3: ENVIAR LA PETICIÓN MANUALMENTE A LA URL CORRECTA
# ===================================================================
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

print(f"\nEnviando petición a: {PROCESS_URL}")
response = oauth_session.post(PROCESS_URL, json=payload)
response.raise_for_status()
print("¡Petición completada con éxito!")

# ===================================================================
# PASO 4: GUARDAR Y VISUALIZAR LA IMAGEN
# ===================================================================
img_content = response.content
output_folder = r"C:\Sentinel"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_filename = f"sentinel_image_{start_date_str}_to_{end_date_str}.tif"
output_path = os.path.join(output_folder, output_filename)
with open(output_path, "wb") as f:
    f.write(img_content)
print(f"Imagen guardada en: {output_path}")

'''plt.figure(figsize=(8,8)); plt.axis('off')
plt.imshow(tiff.imread(output_path)); plt.tight_layout()
plt.show()'''
