import pandas as pd
import glob
import os

# Ruta donde tienes los archivos CSV
ruta_archivos = 'I:/My Drive/GEE/NDVI_EarthEngine_Exports' # Cambia esto a donde estén tus CSVs
archivos_csv = glob.glob(os.path.join(ruta_archivos, '*.csv'))

# Lista para ir guardando los DataFrames
dataframes = []

for idx, archivo in enumerate(archivos_csv):
    if idx == 0:
        # El primer archivo lo leemos completo (incluye cabeceras)
        df = pd.read_csv(archivo)
    else:
        # Los demás archivos los leemos saltando la cabecera
        df = pd.read_csv(archivo, skiprows=1, header=None)
        # Usamos las cabeceras del primer archivo
        df.columns = dataframes[0].columns if dataframes else pd.read_csv(archivos_csv[0]).columns
    dataframes.append(df)

# Concatenamos todos los DataFrames
df_final = pd.concat(dataframes, ignore_index=True)

# Guardamos el resultado en un nuevo archivo
df_final.to_csv('I:/My Drive/GEE/NDVI_EarthEngine_Exports/archivo_final.csv', index=False)

print('¡Archivos combinados exitosamente!')
