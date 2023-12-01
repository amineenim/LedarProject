"""
Created on Thu Sep 21 17:45:24 2023

@author: filippi_j
On a repris le code de Monsieur filippi_j pour faire l'extraction des images raster
"""
import contextily as cx
import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import box
from fiona.crs import from_epsg
from rasterio.mask import mask
from pyproj import Transformer
import pycrs
import json
import os.path



def webMapsToTif(west, south, east, north, outF, providerSRC=cx.providers.GeoportailFrance.orthos, zoomLevel=19):
    tempOUT = outF + "_temp.tif"

    cx.bounds2raster(west, south, east, north,
                     ll=True,
                     path=tempOUT,
                     zoom=zoomLevel,
                     source=cx.providers.GeoportailFrance.orthos

                     )

    data = rasterio.open(tempOUT)

    bbox = box(west, south, east, north)

    geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))
    geo = geo.to_crs(crs=data.crs.data)

    coords = [json.loads(geo.to_json())['features'][0]['geometry']]

    out_img, out_transform = mask(data, shapes=coords, crop=True)
    epsg_code = int(data.crs.data['init'][5:])
    out_meta = data.meta.copy()
    print(out_meta)

    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform,
                     "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
                    )

    with rasterio.open(outF, "w", **out_meta) as dest:
        dest.write(out_img)

    print("Extracted image from contextily bounds:", west, south, east, north, " zoom ", zoomLevel, " out files ", outF,
          " and temporary ", tempOUT)

########################### Question 1#####################################################################
'''
 Pour cette partie nous avons essayé d faire une extraction des données lidar.laz en donnant les même cordonnées que ceux des images raster
le but ici était d'avoir les nuages de points des images ratser qu'on a extrait, cependant le code nous donne en output le lien de ign
j'ai essayé de chercher mais je n'ai trouvé aucun moyen pour extraire des nuages de point à partir d'une longitude latitude
Ma question est comment assurer la cohérence entre les données raster et les données laz
'''
########################### Question 2#####################################################################
'''
##https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/KR/LHD_FXX_0655_6232_PTS_C_LAMB93_IGN69.copc.laz
#J'ai aussi trouvé cette source de données, mais en lisant la documentation de IGN, la corse est découpe en 5 blocs a savoir (US,VS,UT,VT,VU)
# et si on suit toujours la documentation (page 17) tous ces blocs doivent avoir un code IGNF altitude = IGN78C
# Alors que les données que j'ai trouvé concernant les 5 blocs Corse ont un code IGN69 ? est-ce que c'est normal
#Est ce que je peux prendre les données que me propose ce lien ??
'''
def findfileToDownload(west, south, east, north, lidarCRS=2154, step=1,
                       prefix="URL: https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/KR/LHD_FXX_0655_6232_PTS_C_LAMB93_IGN69.copc.laz"):
    points = []
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:%d" % lidarCRS)


    x_ne, y_ne = transformer.transform(north, east)
    x_sw, y_sw = transformer.transform(south, west)

    for x in np.arange(x_sw - step, x_ne + step, step):
        for y in np.arange(y_sw, y_ne, step):
            points.append((int(x / 1000), int(y / 1000)))
    filenames = []
    for x, y in points:
        x_str = str(int(x))
        y_str = str(int(y))
        filename = f"{prefix}{x_str}_{y_str}-2022/file/LIDARHD_1-0_LAZ_IP-{x_str}_{y_str}-2022.laz"
        filenames.append(filename)

    print("\n".join(filenames))

def list_laz_files(directory_path):
    laz_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.laz'):
                full_path = os.path.join(root, file)
                laz_files.append(full_path)

    return laz_files

dirout = "C:/Users/Lenovo/Desktop/out"

orthoTIF = "%sortho.tif"%dirout
lat_sw, lon_sw = 42.007884 , 9.327366
lat_ne, lon_ne = 42.008428 ,  9.328064

west, south, east, north = lon_sw,lat_sw, lon_ne,lat_ne
findfileToDownload(west, south, east, north,lidarCRS=2154, step=1,prefix="https://geoservices.ign.fr/lidarhd#telechargement")
webMapsToTif(west, south, east, north, orthoTIF, zoomLevel=18)


