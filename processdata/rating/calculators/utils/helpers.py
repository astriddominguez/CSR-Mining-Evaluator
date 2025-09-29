from ....data import SOCIOECONOMIC_DIMENSION_RESULTS as SR, ENVIRONMENT_DIMENSION_RESULTS as ER
from .html_content import *
import statistics
import logging 

logger = logging.getLogger(__name__)

DIM_CRITERION = {0: SR, 1: ER}

#----------------------------------------------------------------
#---------------------------- SEMÀFORS---------------------------
#----------------------------------------------------------------

POSITIVE_SEMAPHORE = {1: "RED", 2: "ORANGE", 3: "YELLOW", 4: "GREEN", 5: "DGREEN"}
NEGATIVE_SEMAPHORE = {-1: "GREEN", -2: "YELLOW", -3: "ORANGE", -4: "RED", -5: "DRED"}

# --------------------------------------------------------------
# -------------------FUNCIONS AUXILIARS-------------------------
#---------------------------------------------------------------

def iterate_responses(responses):
    """
    Itera sobre una llista de diccionaris amb les respostes de l'usuari. 
    """
    for response in responses:
        key = next(iter(response))
        val = response[key]
        yield key, val

def safe_rating(default = False):
    """
    Decorador per capturar excepcions en funcions de càlcul de ratings.
    Si hi ha un error, mostra'l per logger i retorna el valor per defecte.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__module__)
                logger.error(f"Error in {func.__name__}(...): {e}")
                return default
        return wrapper
    return decorator

def get_number_children(children):
    """
    Obté i retorna el número del final d'un id fill.

    :param children (str): id del fill. Normalment: '<nom_pare>_<numero>'.
    """
    return children.split('_')[-1]


#---------------------------------------------------------------------
#--------------- FORMATADORS I CREADORS DE SORTIDA--------------------
#---------------------------------------------------------------------

def get_formatted_extra_info(id, rating, dim, extra_msgs = None):
    """
    Recupera i formata la informació complementària (resum i consell) associada a una secció i nivell de puntuació donat.

    Aquesta funció consulta els diccionaris de referència (DIM_CRITERION) per obtenir el `summary` i `advice` 
    corresponents a una puntuació (`rating`) per a una secció identificada per `id` dins d'una dimensió (`dim`).

    També pot afegir missatges addicionals (`extra_msgs`) si es proporcionen.

    :param id (str): Identificador de la secció (ex. "Waste", "InfraestructureCreation").
    :param rating (int or str): Puntuació de l'índex (es converteix a str internament per accedir al diccionari).
    :param dim (int): Dimensió a la qual pertany la secció (0 = socioeconòmica, 1 = ambiental).
    :param extra_msgs (list, optional): Missatges addicionals en format [("títol", valor), ...] per afegir a la resposta.
    """

    criterion = DIM_CRITERION[dim]  # criteri respecte la dimensió
    rating = str(abs(rating))
    extra_data = criterion[id] 
    # Resum i Consell segons la puntuació resultant
    summary, advice = get_html_summary(extra_data["summaries"][rating]), extra_data["advices"][rating]
    
    if "name" in extra_data: # Cada tarjeta té el seu propi títol. 
        title = extra_data["name"]
        if not extra_msgs:
            return {"name": title, "summary": summary, "advice": advice}
        else: 
            return {"name": title, "summary": summary, "advice": advice, "messages": extra_msgs}
    if not extra_msgs: # Bloc únic. Recordem: bloc únic el títol és el de la pròpia subdimensió.
        return {"summary": summary, "advice": advice}
    else: 
        return {"summary": summary, "advice": advice, "messages": extra_msgs}
    
def create_card_result(id, rdata, sem, dim):
    """
    Retorna un diccionari amb les dades formatades per mostrar dins d'una targeta de resultat.

    :param id (str): Identificador de la subsecció.
    :param rdata (dict): Diccionari amb les dades del rating, esperant com a mínim les claus:
        - 'rating' (int): valor de l'índex (1 a 5)
        - 'out_of' (int): valor màxim de l'índex (normalment 5)
    :param sem (str): Color del semàfor per la targeta (ex. "RED", "ORANGE", "GREEN", "NEUTRAL").
    :param dim (int): Índex de dimensió (0 = socioeconòmica, 1 = ambiental), per accedir al diccionari de contingut.
    """
    view_data = get_formatted_extra_info(id, rdata['rating'], dim)
    return {
        **rdata,
        "semaphore": sem[rdata['rating']],
        **view_data
    }

def create_section_result(id, rating, dim, sem, info = None):
    """
    Crea el resultat formatat d'una secció sencera de l'índex CSR (ex. "Energia", "Aigua", "Contractació Local").

    Si es proporciona informació addicional (`info`), aquesta s'afegeix com a missatges complementaris.

    :param id (str): Identificador de la secció (ex. "Energy", "Water", "LocalProcurement").
    :param rating (int): Valor del rating obtingut (entre 1 i 5).
    :param dim (int): Dimensió a la qual pertany la secció (0 = socioeconòmica, 1 = ambiental).
    :param info (list, optional): Llista de missatges addicionals (tipus [("títol", valor), ...]) a mostrar com a detalls. 
    """
    view_data = get_formatted_extra_info(id, rating, dim, extra_msgs = info)
    return rating, {"semaphore": sem[rating], **view_data}


def get_ratings_from_percentatge_tables(responses, references, dim):
    """
    Calcula el rating per cada percentatge i ho retorna en un diccionari.

    :param responses (list):  llista de diccionaris, on la clau de cadascun d'ells és li'ID de la pregunta i el valor el percentatge (%).
    :param references (dict): diccionari on la clau és l'ID de la pregunta, i el valor és un altre diccionari que conté con a claus una tupla
                              amb l'interval de percentatges i el valor és el rating que li pertoca.
    :param dim (int): pot ser 0 (Socioeconomic) o 1 (Environmental). Indica per a quina dimensió s'esta realitzant el càlcul.  

    :returns dict: retorna un diccionari on la clau és l'ID de la pregunta i el valor el rating resultant.
    :returns bool: False si les preguntes no han estat resposes.
    """

    ratings = {}
    
    for key, pctg in iterate_responses(responses):
        if pctg is not None:
            
            refs = references[key]
            pctg_table = refs["table"]

            rating = get_result_from_percentatge_table(pctg, pctg_table)
    
            info = DIM_CRITERION[dim][key]
            name, summary, advice = info["name"], info["summaries"][str(rating)], info["advices"][str(rating)]
            sentence = refs["sentence"].replace("$value$", f"<strong>{pctg}%</strong>")
            color = refs['semaphore'][rating]

            ratings[key] = {
                "rating": rating,
                "out_of": max(pctg_table.values()),
                "semaphore": color,
                "name": name, 
                "summary": create_html_sentence_with_summary(sentence, summary),
                "advice": advice
            }
    
    return ratings if ratings != {} else False


#---------------------------------------------------------------------
#---------------------------CALCULADORES------------------------------
#---------------------------------------------------------------------


def get_result_from_percentatge_table(percentatge, table):
    """
    Retorna el valor de rating comprovant la referència de la taula.

    :param percentatge(float): valor de percentatge pel qual s'ha de trobar la correspondència de rating a la taula.
    :table(dict): diccionari amb tuples per clau amb valor mínim i máxim amb la seva correspondència de rating. Ex: {(0, 20): 1, (20, 40): 2, (40, 60): 3, (60, 80): 4, (80, 100): 5}
    """
    for (min_val, max_val), rating in table.items():
        if min_val <= percentatge <= max_val:
            return rating
    return 1 

def calculate_percentatge(dividend, divisor):
    """
    Calcula un percentatge donat un dividend i divisor. Si no pot calcular el percentatge retorna None.

    :param dividend(float): número que es divideix
    :param divisor(float): número pel qual es divideix el dividend. 
    """
    if divisor == 0 or dividend == 0:
        return None
    return round(dividend / divisor * 100, 2)

def calculate_average(values):
    """
    Calcula la mitjana aritmètica d'una llista de valors numèrics. 
    :param values (list of float or int): Llista de valors numèrics sobre els quals es vol calcular la mitjana.
    """
    return statistics.mean(values)

def calculate_rating_from_score(score, max_score):
    """
    Converteix una puntuació numèrica total (`score`) en un índex de sostenibilitat de l'1 al 5.

    :param score (float or int): Puntuació total obtinguda per una secció segons els criteris aplicats.
    :param max_score (float or int): Puntuació màxima possible que es pot obtenir.
    """
    rating = round((score / max_score) * 5)
    rating = max(1, min(5, rating))
    return rating

def normalize_likert_score(max_score, scores, scale=(1, 100)):
    """
    Normalitza el resultat del total obtingut a una escala del 1 al 100. Tenint en compte que cadascuna de les puntuacions és 
    en base a l'escala de Likert. Retorna tant el valor normalitzat com el valor brut.

    :param max_score(int): màxima puntuació possible.
    :param scores(list(int)): llista de puntuacions obtingudes.  
    :param scale(tuple(int)): escala númerica. Per defecte, de l'1 al 100.
    """

    a, b = scale[0], scale[1] 
    
    if len(scores) == 0: # Si no hi ha puntuacions retorna valor mínim de l'escala + 0 de la global 
        return a, 0
    
    min_score = 0
    total_score = 0
    for score in scores:
        # Si la puntuació és positiva - Escala: 1-5. On 1, és la puntuació mínima.
        # Si la puntuació és negative - Escala: (-5)-(-1). On -5, és la puntuació mínima.
        min_score+=1 if score > 0 else -5
        total_score+=score

    nscore = a + ((total_score - min_score)*(b-a))/(max_score - min_score)
    return round(nscore, 2), total_score 
        

