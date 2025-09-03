from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt

CLIENT_ID = "sh-140573ad-defa-41d4-96e9-eb114e38379a"
CLIENT_SECRET = "wacmrBkcZmRNRwDzJjDA4mFYrLTVSoBV"

# set up credentials
client = BackendApplicationClient(client_id=CLIENT_ID)
oauth = OAuth2Session(client=client)

# get an authentication token
token = oauth.fetch_token(
    token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
    client_secret=CLIENT_SECRET,
    include_client_id=True
)

bbox = [-87.72171, 17.11848, -87.342682, 17.481674]
start_date = "2020-06-01"
end_date = "2020-08-31"
collection_id = "sentinel-2-l2a"

# evalscript
evalscript = """
//VERSION=3

function setup() {
  return {
    input: ["B02", "B03", "B04"],
    output: { id: 'default',
              bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
}
"""

# request body/payload
json_request = {
    'input': {
        'bounds': {
            'bbox': bbox,
            'properties': {
                'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
            }
        },
        'data': [
            {
                'type': 'S2L2A',
                'dataFilter': {
                    'timeRange': {
                        'from': f'{start_date}T00:00:00Z',
                        'to': f'{end_date}T23:59:59Z'
                    },
                    'mosaickingOrder': 'leastCC',
                },
            }
        ]
    },
    'output': {
        'width': 1024,
        'height': 1024,
        'responses': [
            {
                'identifier': 'default',
                'format': {
                    'type': 'image/tiff',
                }
            }
        ]
    },
    'evalscript': evalscript
}

url_request = "https://sh.dataspace.copernicus.eu/api/v1/process"
headers_request = {
    "Authorization": f"Bearer {token['access_token']}"
}

# Send the request
print("Enviando petición para obtener la imagen...")
response = oauth.post(url_request, headers=headers_request, json=json_request)
response.raise_for_status() # Lanza un error si la petición falló
print("¡Respuesta recibida!")

# --- AÑADIR ESTAS LÍNEAS PARA DESCARGAR LA IMAGEN ---
# Define el nombre del archivo de salida
nombre_archivo = "C:/Sentinel/imagen_sentinel.tif"

# Abre el archivo en modo 'write binary' (wb) y guarda el contenido
with open(nombre_archivo, "wb") as f:
    f.write(response.content)

print(f"Imagen descargada y guardada como '{nombre_archivo}'")
# ---------------------------------------------------

# read the image as numpy array for plotting
image_arr = np.array(Image.open(io.BytesIO(response.content)))

# plot the image for visualization
plt.figure(figsize=(16,16))
plt.axis('off')
plt.tight_layout()
plt.imshow(image_arr)
plt.show()
