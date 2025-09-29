import logging
from .calculators.utils.helpers import *
from .calculators.socioeconomic import *
from .calculators.environment import *

logger = logging.getLogger(__name__)

# Configuració per defecte de l'estructura del contingut:
indicators_handlers = {
        "socioeconomic": { # ID pregunta: funció calculadora de índex
            "LocalProcurement": get_local_procurement_rating,
            "LocalExpediture": get_local_expediture_rating,
            "InfraestructureCreation": get_infraestructure_creation_rating,
            "ValueChain": get_value_chain_rating,
            "EconomicDisturbance": get_rating_economic_disturbance,
            "AdditionalInvolvement": get_additional_involvement_rating,
            "ClosureProcess": get_closure_process_rating,

        },
        "environment": {
            "Energy": get_energy_rating,
            "Tailings": get_tailings_rating,
            "Waste": get_waste_rating,
            "Water": get_water_rating,
            "Air": get_air_rating,
            "LandformChanges": get_landform_changes_rating,
            "Biodiversity": get_biodiversity_rating,
            "Subsidence": get_subsidence_rating,
            "PositiveEnvironmental": get_positive_environmental_rating,
            "EnvironmentalLiabilities": get_liability_impact_rating
        }
    }

def create_section_dict(title, rating, section_result, info = None):
    """
    Crea tota la estructura de resultat per a una secció en concret amb el seu nom de referència, puntuació total, resultat per subseccions i informació addicional si en té.

    :param title(str): títol de la secció.
    :param rating(int): índex total de la secció.
    :param section_result(list(dict)): resultat per a cada subsecció (si hi han). 
    :param info(dict): diccionari amb 'summary i 'advice' com a claus. 
    """
    if info is not None:
        return {"name": title, "rating_total": f"{rating}", "subsection_results": section_result, **info}
    return {"name": title, "rating_total": f"{rating}", "subsection_results": section_result}


def calculate_rating(form_answers): 
    """
    Calcula el resultat de l'índex CSR a partir de les respostes del formulari.

    Aquest càlcul inclou:
      - El valor total agregat de totes les dimensions.
      - El valor de cada dimensió i subdimensió (secció).
      - Informació HTML o contextual associada a cada resultat.

    Args:
        form_answers (dict): Diccionari estructurat per dimensions i seccions.
            Format:
            {
                "ambiental": {
                    "energia": {
                        "answers": [...],
                        "title": "Eficiència energètica"
                    },
                    ...
                },
                ...
            }

    Returns:
        dict: Diccionari amb tota l'estructura de resultats:
            {
                "ambiental": {
                    "result": {
                        "energia": {
                            "title": ...,
                            "rating_total": ...,
                            "data": ...,
                            "info": ...
                        },
                        ...
                    },
                    "rating_total": "X/Y"
                },
                ...
                "rating_total": "TOTAL_X/TOTAL_Y"
            }
    """
    
    if not isinstance(form_answers, dict):
        logger.error("form_answers no és un diccionari.")
        return {}
 
    calculation_result = {}

    all_rating_total = []
    all_out_of_total = 0

    for dimension, sections in form_answers.items():
        # Inicialitzem resultat per la dimensió
        calculation_result[dimension] = {"result": {}}
        # Inicialitzem total acumulat de totes les subdimensions(o seccions) de la dimensió
        section_rating_total, out_of_total = [], 0

        for section, data in sections.items():
            # Recollim respostes i títol
            form_answers, title = data["answers"], data["title"]
            # Accedim a la funció que calcula l'índex per aquesta secció
            rating_func = indicators_handlers[dimension][section]
            # Inicialitzem resultat per la secció
            section_result = []

            logger.debug(f"CALC - Resultats per la secció: {title}\n")
            
            # Obtenim el resultat de calcular l'Índex i obtenir la informació a mostrar a la vista de resultats.
            result = rating_func(form_answers)

            if isinstance(result, tuple):
                # 2 respostes: valor + info o diccionari + info
                res_ratings, extra_info = result
            else:
                # 1 resposta: diccionari (cas habitual per a tarjetes)
                res_ratings, extra_info = result, None

            if not isinstance(res_ratings, bool):  # False quan no hi han valors de resposta

                # Emmagatzemem resultat de la subdimensió
                section_result.append({section: res_ratings})
                
                if isinstance(res_ratings, dict): # Tarjetes (diccionari)
                    # Puntuació total de les tarjetes
                    ratings, out_of = [], 0
                    for _, content in res_ratings.items():
                        rating = content["rating"]
                        ratings.append(rating)
                        out_of += content["out_of"]

                    # Emmagatzemem les puntuacions al total de puntuacions de la dimensió
                    section_rating_total.extend(ratings)
                    # Total de puntuació
                    all_ratings = sum(ratings) 
                    rating_total = f"{all_ratings}/{out_of}"
                    
                else: # Bloc únic (tupla)
                    section_rating_total.append(res_ratings)
                    if res_ratings >= 0: # Positius
                        out_of = 5
                    else: # Negatius
                        out_of = 0
                    rating_total = f"{res_ratings}/{out_of}" 
                
                # Emmagatzemem el resultat complet per a la secció d'aquesta dimensió
                calculation_result[dimension]["result"][section] = create_section_dict(title, rating_total, section_result, info = extra_info)
                out_of_total += out_of

    
        # Puntuació total per a la dimensió        
        s_rating_total = sum(section_rating_total)
        calculation_result[dimension]["rating_total"] = f"{s_rating_total}/{out_of_total}"

        # Emmagatzemem tots els resultats obtinguts per a la dimensió.
        all_rating_total.extend(section_rating_total)
        all_out_of_total += out_of_total
    

    n_csr_rating_total, csr_rating_total = normalize_likert_score(all_out_of_total, all_rating_total)
    calculation_result["rating_total"] = f"{csr_rating_total}/{all_out_of_total}"
    calculation_result["nrating_total"] = f"{n_csr_rating_total}/100"

    return calculation_result
