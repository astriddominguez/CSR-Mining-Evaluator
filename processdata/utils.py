import re
import os
import json
from django.conf import settings
import requests

def load_json(filename):
    """
    Carrega un fitxer JSON des de processdata/config/ i el retorna en format JSON.

    :param filename(str): nom del fitxer JSON a carregar.  
    """
    file_path = os.path.join(settings.JSON_DIR,  filename) # path del fitxer
    with open(file_path, "r", encoding = "utf-8") as file:
        return json.load(file)
    
def reverse_geocode(lat, lon):
    """
    Retorna l'adreça en format de text donades latitud i longitud.

    :param lat(float): latitud 
    :param lon(float): longitud
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 18, # 0-18; 18: building -> la ubicació més completa
        "addressdetails": 0 # 0 or 1. No necessitem l'adreça desglosada. 
    }
    headers = {
        "User-Agent": "tfg-app-astrid/1.0 (astriddominguez@estudiantat.upc.edu)" 
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status() # Si el codi és 404, 500, etc. Llança error
        data = response.json()
        return data.get("display_name") 
    except requests.RequestException as e:
        print("Error obtenint l’adreça:", e)
        return None
    
def is_child(question_id):
    """
    Rep un identificador corresponent a una pregunta del formulari i retorna True si aquest identificador correspon a una
    preguna "filla" i el ID del pare, en cas que sigui pregunta "pare" o única retornará False i un None.

    :param question_id (str): identificador de la pregunta. SEMPRE acabará en _ i un número que indica el seu nivell.

    Exemple: 
    question_id = r_and_d_1
    retornará True i el seu pare amb r_and_d. 
    """
    if re.search(r"_\d+$", question_id):
        tail_p = question_id.rfind('_')
        return True, question_id[0:tail_p] 
    else:
        return False, None