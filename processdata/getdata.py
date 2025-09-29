from .models import Overview, SocioeconomicDimension, EnvironmentDimension
from .data import SOCIOECONOMIC_DIMENSION_QUESTIONS, ENVIRONMENT_DIMENSION_QUESTIONS
from .utils import reverse_geocode, is_child
from django.shortcuts import get_object_or_404
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

def get_overview_data(fingerprint):
    """
    Recupera les dades del formulari Overview associat a un fingerprint.

    Aquesta funció localitza l'objecte `Overview` relacionat amb el fingerprint proporcionat i construeix un
    diccionari amb les dades clau del projecte, incloent el nom, l'empresa, la ubicació i la fase actual.

    :param fingerprint(str): Identificador únic del fingerprint del formulari principal.

    :return (dict): Diccionari amb les dades del projecte. Retorna un diccionari buit si ocorre algun error.
    """
    try:

        overview_subform = get_object_or_404(Overview, form__fingerprint__fingerprint_id = fingerprint)
        
        if overview_subform.mine_ubication:
            try:
                lat_str, lon_str = overview_subform.mine_ubication.split(",")
                location = {
                    "latitude": float(lat_str.strip()),
                    "longitude": float(lon_str.strip())
                }
            except ValueError:
                location = {
                    "latitude": None,
                    "longitude": None
                }
        else:
            location = {
                "latitude": None,
                "longitude": None
            }

        overview_data = {
                        "project_name": overview_subform.project_name,
                        "company_name": overview_subform.company_name,
                        "mine_ubication": location,
                        "phase": overview_subform.phase
                        }
    
        return overview_data
    except Exception as e:
        logger.error(f"Error in get_overview_data({fingerprint}): {e}")
        return {}

def get_socioeconomic_data(fingerprint):
    """
    Recupera les dades de la dimensió socioeconòmica associades a un fingerprint donat.

    Aquesta funció obté l’objecte `SocioeconomicDimension` associat a l’empremta digital proporcionada,
    i processa les respostes mitjançant la funció `get_dimension_data` i les preguntes definides
    en `SOCIOECONOMIC_DIMENSION_QUESTIONS`.

    :param fingerprint (str): Identificador únic del fingerprint del formulari principal.

    :return (dict): Diccionari amb les respostes processades de la dimensió socioeconòmica. Retorna un diccionari buit si ocorre un error.
    """
    try:
        socioeconomic_subform = get_object_or_404(SocioeconomicDimension, form__fingerprint__fingerprint_id = fingerprint)
        socioeconomic_data = get_dimension_data(SOCIOECONOMIC_DIMENSION_QUESTIONS, socioeconomic_subform)
        return socioeconomic_data
    except Exception as e:
        logger.error(f"Error in get_socioeconomic_data({fingerprint}): {e}")
        return {}

def get_environment_data(fingerprint):
    """
    Recupera les dades de la dimensió ambiental associades a un fingerprint donat.

    Aquesta funció obté l’objecte `EnvironmentDimension` vinculat al formulari identificat per `fingerprint`,
    i extreu les respostes corresponents mitjançant la funció `get_dimension_data` i les preguntes definides
    a `ENVIRONMENT_DIMENSION_QUESTIONS`.

    :param fingerprint(str): Identificador únic del fingerprint del formulari principal.

    :return (dict): Diccionari amb les respostes processades de la dimensió ambiental. Retorna un diccionari buit si hi ha un error.
    """
    try:
        environment_subform = get_object_or_404(EnvironmentDimension, form__fingerprint__fingerprint_id = fingerprint)
        environment_data = get_dimension_data(ENVIRONMENT_DIMENSION_QUESTIONS, environment_subform)
        return environment_data
    except Exception as e:
        logger.error(f"Error in get_environment_data({fingerprint}): {e}")
        return {}
    

def get_dimension_data(dimension_questions, dimension_subform):
    """
    Extreu les dades d'una dimensió concreta d’un formulari mitjançant les preguntes i el subformulari corresponent.

    Aquesta funció recorre la llista de preguntes definides per una dimensió (com Socioeconòmica o Ambiental),
    obté el model associat a cada grup de preguntes i recupera les respostes desades en la base de dades,
    utilitzant els noms dels camps especificats com `input_id` o `parent_id` amb fills.

    :param dimension_questions (list(dict)): Llista de diccionaris que descriuen les preguntes associades a una dimensió.

    :param dimension_subform (Model Instance): Instància del subformulari relacionat amb la dimensió (ex: `SocioeconomicDimension` o `EnvironmentDimension`).

    :return (dict): Diccionari amb les dades extretes dels models corresponents, on les claus són els identificadors dels camps i els valors són les respostes desades.
    """
    dimension_data = {}

    for i in range(len(dimension_questions)):
            model_name = dimension_questions[i]['id'] # ID de la subdimensió.    
            Model = apps.get_model("processdata", model_name) # Obtenció del model corresponent a la subdimensió
            instance = Model.objects.get(subform = dimension_subform) # Instància al model
            for question in dimension_questions[i]['questions']:
                if "input_id" in question:
                    field = question["input_id"]
                    value = getattr(instance, field)
                    dimension_data.update({field: value})
                elif "parent_id" in question:
                    for children in question["childrens"]:
                        field = children["input_id"]
                        value = getattr(instance, field)
                        dimension_data.update({field: value})
    return dimension_data

def get_overview_data_for_results(fingerprint):
    """
    Recupera les dades generals d’un projecte per mostrar-les a l’apartat de resultats, amb la ubicació en format text.

    Aquesta funció és molt similar a `get_overview_data`, però està pensada per a l’apartat de resultats,
    on es vol mostrar l’adreça de la mina en format llegible (textual) en comptes de les coordenades.

    Per aconseguir això, utilitza la funció `reverse_geocode` per convertir la latitud i longitud en una adreça textual.
    Si hi ha algun error durant la geocodificació inversa, s’afegeix `mine_address = None`.

    :param fingerprint(str): Identificador únic del fingerprint del formulari principal.

    :return (dict): Diccionari amb les dades del projecte, incloent l’adreça textual (`mine_address`) i la resta d’informació.
             Si no es pot recuperar el formulari Overview, retorna un diccionari buit.
    """

    overview_data = get_overview_data(fingerprint)

    if overview_data == {}:
        return overview_data
    
    try:
        latitude = overview_data['mine_ubication']['latitude']
        longitude = overview_data['mine_ubication']['longitude']
        
        mine_address = reverse_geocode(latitude, longitude)
        overview_data['mine_address'] = mine_address
        del overview_data['mine_ubication']  

    except Exception as e:
        logger.error(f"Error in reverse geocoding for fingerprint {fingerprint}: {e}")
        overview_data['mine_address'] = None

    return overview_data  

def get_results_for_dimension(dimension_questions, dimension_subform, dimension_reference):
    """
    Genera un conjunt de resultats estructurat a partir de les respostes d'una dimensió del formulari, amb identificadors,
    valors i títols de secció, pensat per ser mostrat a la vista de resultats.

    Aquesta funció recorre les preguntes d’una dimensió (Socioeconòmica o Ambiental), accedeix als models
    relacionats i construeix un diccionari amb les respostes donades. També gestiona preguntes amb estructura jeràrquica
    (pare/fills), així com preguntes de selecció múltiple.

    :param dimension_questions (list(dict)): Llista de diccionaris que defineixen la configuració de la dimensió (models, preguntes, seccions).

    :param dimension_subform (Model instance): Instància del subformulari associat a la dimensió.

    :param dimension_reference (str): Identificador de la dimensió per encapsular els resultats (ex: "socioeconomic").

    :return (dict): Diccionari estructurat amb els resultats de cada subdimensió inclosa, agrupats per seccions. 
    """

    results = {dimension_reference: {}}
    
    for i in range(len(dimension_questions)):
        # model_name: nom del model. (ID de la subdimensió)
        # name: Nom que es fa servir per fer referència a aquest a nivell d'interficie d'usuari.
        model_name, name = dimension_questions[i]['id'], dimension_questions[i]['section_name']
        # Inicialitzem la llista on es guardarán les respostes.
        values = []
        # Accés al model i instància a aquest
        Model = apps.get_model("processdata", model_name)  
        instance = Model.objects.get(subform = dimension_subform)
        
        for question in dimension_questions[i]['questions']:
            
            question_id = None # ID de la pregunta
            group_of_childrens = False # Flag que indica si correspón a un grup de fills.

            if "input_id" in question:
                question_id = question["input_id"]
            elif "parent_id" in question: # Cas excepcional -> Qualitat de l'Aire
                group_of_childrens = True  # Un pare -> grup de fills 1, grup de fills 2, etc. Per una única pregunta.
                question_id = question["parent_id"] 
        
            # Revisa si és un fill (ojo, no confondre amb grup de fills)
            is_children, parent = is_child(question_id) 

            if question_id is not None: 
                if group_of_childrens is False: # Cas habitual: no té grups de fills.
                    value = getattr(instance, question_id) # S'extreu el valor emmagatzemat per aquesta pregunta
                    if value is not None: # Només recollim aquells que si tenen resposta
                        if is_children is False: # No és fill. 
                            if question["type"] == "multiple-select": # Multiples opcions seleccionades, s'encadenen amb ,
                                selected_options = []
                                options = question["options"]
                                for option in options:
                                    if option["id"] in value:
                                        selected_options.append(option["name"])
                                value = ", ".join(selected_options)

                            result = {question_id: value} 
                            values.append(result)

                        else: # és fill, vol dir que pertany a un únic conjunt de preguntes.
                            parent_in_values = any(parent in value for value in values)

                            if not parent_in_values: # El pare no es troba registrat, si s'han respós totes les preguntes s'espera que el primer sigui 1.
                                if question_id.endswith('_1'): # si el primer fill no acaba en _1 vol dir que les preguntes anteriors no tenen resposta
                                    result = {parent: {question_id: value}}
                                    values.append(result)
                            else: # El pare ja es troba registrat
                                for d in values:
                                    if parent in d:
                                        d[parent][question_id] = value
                                        break
                    else:
                        if is_children is True: # ún dels fills no ha estat respòs
                            for parents in values: # eliminem els registres que teniem ... 
                                if parents.get(parent):
                                    values.remove(parents)
                                    break
                else: # Excepció per a Air Quality 
                    parent = question["parent_id"]
                    #parent_in_values = any(parent in value for value in values)
                    results2 = []
                    for children in question["childrens"]:
                        question_id = children["input_id"]
                        value = getattr(instance, question_id)
                        results2.append({question_id: value})
                    
                    result = {parent: results2}
                    values.append(result)

        if values != []:
            results[dimension_reference][model_name] = {"answers": values, "title": name}

    return results  
    

def get_results(fingerprint):
    """
    Retorna les respostes del formulari en el format adecuat per ser avaluades per a un usuari concret.

    :param fingerprint: id que identifica a l'usuari a la base de dades.
    """ 
    results = {}
    try:
        # Extracció de les respostes desades per a Dimensió Socioeconòmica i Ambiental
        socioeconomic_subform = get_object_or_404(SocioeconomicDimension, form__fingerprint__fingerprint_id = fingerprint)
        environment_subform = get_object_or_404(EnvironmentDimension, form__fingerprint__fingerprint_id = fingerprint)
        # Processament de les dades per poder ser usades pel càlcul. 
        results = get_results_for_dimension(SOCIOECONOMIC_DIMENSION_QUESTIONS, socioeconomic_subform, 'socioeconomic')
        results.update(get_results_for_dimension(ENVIRONMENT_DIMENSION_QUESTIONS, environment_subform, 'environment'))

        return results
    except Exception as e:
        logger.error(f"Error in get_results({fingerprint}): {e}")


def save_overview_data(fingerprint, data):
    """
    Emmagatzema les dades generals del projecte miner entrades per l'usuari.

    :param fingerprint(str): id que identifica a l'usuari a la base de dades.
    :param data(dict): diccionari amb les dades entrades. 
    """ 
    try:
        # Instància al model Overview 
        overview_subform = get_object_or_404(Overview, form__fingerprint__fingerprint_id = fingerprint)
        # Actualitza les columnes amb les dades entrades, en cas de no haber-hi deixa les que habia previament.
        overview_subform.project_name = data.get("project_name", overview_subform.project_name)
        overview_subform.company_name = data.get("company_name", overview_subform.company_name)

        mine_ubication = data.get("mine_ubication")
    
        if mine_ubication:
            latitude = mine_ubication.get("latitude")
            longitude = mine_ubication.get("longitude")
            if latitude is not None and longitude is not None: 
                overview_subform.mine_ubication = f"{latitude},{longitude}"

        overview_subform.phase = data.get("phase", overview_subform.phase)
        overview_subform.save() # aplica els canvis

        return True

    except Exception as e:
        logger.error(f"Error in save_overview_data(...): {e}")
        return False
    
def save_socioeconomic_data(fingerprint, data):
    """
    Actualitza les dades emmagatzemades a la base de dades que corresponen a la dimensió socioeconomica.

    :param fingerprint(str): id que identifica a l'usuari. 
    :param data(dict): diccionari amb les dades a emmagatzemar.
    """
    # Instància al model SocioeconomicDimension
    socioeconomic_subform = get_object_or_404(SocioeconomicDimension, form__fingerprint__fingerprint_id = fingerprint)
    try:
        save_dimension_data(socioeconomic_subform, data)
        return True
    except Exception as e:
        logger.error(f"Error in save_economic_data(...): {e}")
        return False    

def save_environment_data(fingerprint, data):
    """
    Actualitza les dades emmagatzemades a la base de dades que corresponen a la dimensió ambiental.

    :param fingerprint(str): id que identifica a l'usuari. 
    :param data(dict): diccionari amb les dades a emmagatzemar.
    """
    # Instància al model EnvironmentDimension
    environment_subform = get_object_or_404(EnvironmentDimension, form__fingerprint__fingerprint_id = fingerprint)
    try:
        save_dimension_data(environment_subform, data)
        return True
    except Exception as e:
        logger.error(f"Error in save_environment_data(...): {e}")
        return False    


def save_dimension_data(dimension_subform, data):
    """
    Funció que s'encarrega d'emmagatzemar noves dades per a una dimensió determinada.

    :param dimension_subform: instància del model de la dimensió.
    :param data(dict): dades a emmagatzemar agrupades per subdimensions.
    """
    for model, fields in data.items():
        Model = apps.get_model("processdata", model) 
        subsubform = Model.objects.get(subform = dimension_subform)
        for field, value in fields.items():
            if value != "" and value !=[]: 
                value = True if value == "on" else False if value == "off" else value # Valors si/no s'emmagatzemen en format booleà
                setattr(subsubform, field, value)
            else: # Contingut buit s'emmagatzemma com a None
                setattr(subsubform, field, None)
    
        subsubform.save() # Guardem les dades per la subdimensió