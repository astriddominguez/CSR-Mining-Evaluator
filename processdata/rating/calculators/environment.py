import logging
from .utils.helpers import *

logger = logging.getLogger(__name__)

DIM = 1  # Dimensió Ambiental

@safe_rating(default = False)
def get_energy_rating(responses):
    """
    Calcula i retorna el rating d'Energia a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats.
    """

    # TAULA PER DEFECTE (Taula 12, 13 i 14)
    default_energy_table = {
        (0, 19.99): 1,
        (20, 39.99): 2,
        (40, 59.99): 3,
        (60, 79.99): 4,
        (80, 100): 5,
    }

    table_energy_dicts = {
        "ghg_reduction": {
            "table": default_energy_table, 
            "sentence": "$value$ tècniques d’estalvi energètic implementades.",
            "semaphore": POSITIVE_SEMAPHORE
        },
        "green_energy_sources": {
            "table": default_energy_table, 
            "sentence": "$value$ energia renovable utilitzada.",
            "semaphore": POSITIVE_SEMAPHORE
        },
        "green_energy_fleet": {
            "table": default_energy_table, 
            "sentence": "$value$ flota amb energia verda.",
            "semaphore": POSITIVE_SEMAPHORE
        },
    }

    return get_ratings_from_percentatge_tables(responses, table_energy_dicts, DIM)


@safe_rating(default = False)
def get_tailings_rating(responses):  
    """
    Calcula i retorna el rating de Residus de Processos a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats.
    """

    table_tailings_dicts = {
        "price_increase": {
            "table": {
                "8-10 vegades més alt": 1,
                "6-8 vegades més alt": 2,
                "4-6 vegades més alt": 3,
                "2-4 vegades més alt": 4,
                "Fins a 2 vegades més alt":  5
            },
            "semaphore": POSITIVE_SEMAPHORE 
        },
        "other_tailing_usage" : {
            "table": {
                (0, 9.99): 1,
                (10, 19.99): 2,
                (20, 34.99): 3,
                (35, 49.99): 4,
                (50, 100): 5,
            },
            "sentence": "$value$ reutilització de residus miners",
            "semaphore": POSITIVE_SEMAPHORE
        },
        "water_recovery_from_tailings": {
            "table": {
                (0, 19.99): 1,
                (20, 39.99): 2,
                (40, 59.99): 3,
                (60, 79.99): 4,
                (80, 100): 5,
            },
            "sentence": "$value$ recuperació d’aigua dels residus",
            "semaphore": POSITIVE_SEMAPHORE
        }
    }

    ratings = {}

    first_element = responses[0]
    first_id = "price_increase" # aquest en cas de ser present sempre estaria en el primer de la llista

    if first_id in first_element:
        option = first_element[first_id]
        rating = table_tailings_dicts[first_id]["table"][option]
        semaphore = table_tailings_dicts[first_id]["semaphore"]
        logger.debug(f"TAILINGS - Opció: {option}. Índex: {rating}")
        ratings[first_id] = create_card_result(first_id, {"rating": rating, "out_of": 5}, semaphore, DIM)
        del table_tailings_dicts[first_id]
        responses.pop(0) # s'elimina per poder processar la resta amb la funció auxiliar 

    if len(responses) > 0:
        ratings.update(get_ratings_from_percentatge_tables(responses, table_tailings_dicts, DIM))

    return ratings


@safe_rating(default = False)
def get_waste_rating(responses): 
    """
    Calcula i retorna el rating de Gestió de Residus a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats.
    """
  
    ratings, extra_messages = {}, []

    default_waste_table = {(0, 19.99): 1, (20, 39.99): 2, (40, 59.99): 3, (60, 79.99): 4, (80, 100): 5}

    table_waste_dicts = {
        "higher_waste_ratio": {"table": default_waste_table, "sentence": "$value$ excés de residus"},
        "lower_waste_ratio": {"table": default_waste_table,  "sentence": "$value$ reducció de residus"},
        "waste_reuse": {"table": default_waste_table, "sentence": "$value$ residus reutilitzats"},
    }

    for question, value in iterate_responses(responses):
        if question == "waste_ratio_info":
            extra_messages.append(("Tipus de mineria", value))
        elif question == "waste_advanced_techniques":
            title = "Tècniques avançades aplicades"
            if value is True:
                extra_messages.append((title, "Sí ✅"))
            else:
                extra_messages.append((title, "No ❌"))
        elif question == "waste_mesures":
            extra_messages.append(("Mesures ambientals", value))
        elif question == "waste_reuse_uses":
            extra_messages.append(("Reutilització de residus per a", value)) 
        elif question == "waste_ratio":
            values = value   
            # Mirem que tenim els dos percentatges, per poder calcular la diferència
            mine_waste, industry_waste = values["waste_ratio_1"], values["waste_ratio_2"] 
            diff_waste = mine_waste - industry_waste 

            if diff_waste != 0: # Casos on hi ha hagut increment o decrement
                
                if industry_waste != 0: # Cas habitual 
                    diff_pctg = calculate_percentatge(diff_waste, industry_waste) 
                else: # Si la mitjana és 0 i ara hi ha excés de residus considerem el pitjor dels casos.
                    diff_pctg = 100

                logger.debug(f"WASTE - Ràtio de residus: {diff_pctg}%")

                if diff_pctg > 0: # increment de residus
                    ref = "higher_waste_ratio"
                    out_of = 0
                    sem = NEGATIVE_SEMAPHORE
                else: # reducció de residus
                    ref = "lower_waste_ratio"
                    out_of = 5
                    sem = POSITIVE_SEMAPHORE

                if diff_pctg > 100: # Si supera el 100%
                    rating = 5
                else: # Pel rang (0% - 100%)
                    rating = get_result_from_percentatge_table(abs(diff_pctg), table_waste_dicts[ref]["table"])
                
                if ref == "higher_waste_ratio": # Penalització
                    rating = -rating

                sentence = table_waste_dicts[ref]["sentence"].replace("$value$", f"<strong>{diff_pctg}%</strong>")

                ratings[ref] = create_card_result(ref, {"rating": rating, "out_of": out_of}, sem, DIM)
                ratings[ref]["sentence"] = get_html_sentence(sentence)

        elif question == "waste_reuse":
            logger.debug(f"WASTE - Reutilització de residus: {value}%")
            rating = get_result_from_percentatge_table(value, table_waste_dicts["waste_reuse"]["table"])        
            ratings["waste_reuse"] = create_card_result("waste_reuse", {"rating": rating, "out_of": 5}, POSITIVE_SEMAPHORE, DIM)
            ratings["waste_reuse"]["sentence"] = get_html_sentence(table_waste_dicts["waste_reuse"]["sentence"].replace("$value$", f"<strong>{value}%</strong>"))

    if ratings != {}: # Retorna contingut de la tarjeta per una banda, i per l'altre el contingut que va a fora de les tarjetes (és un cas excepcional)
        return ratings, {"list": get_html_list(extra_messages)}
    else:
        return False
    
  

@safe_rating(default = False)
def get_water_rating(responses):
    """
    Calcula i retorna el rating de Gestió de l'aigua a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats.
    """
    ratings = {}

    table_water_dicts = {
        "water_quality_variation": {
            "table": {
                (30, 100): -4, # > 30%
                (20, 29.99): -3, # 20% - 30%
                (10, 19.99): -2, # 10% - 20%
                (0, 9.99): -1 # < 10% 
            }
        },
        "water_reuse": {
            "table": {
                (0, 19.99): 1,
                (20, 39.99): 2,
                (40, 59.99): 3,
                (60, 79.99): 4,
                (80, 100): 5,
            }
        },
        "waterflow_reduction": {
            "table": {
                (60, 100): 1,
                (35, 59.99): 2,
                (20, 34.99): 3,
                (10, 19.99): 4,
                (0, 9.99): 5,
            }
        } 
    }

    for question, value in iterate_responses(responses):
        if isinstance(value, dict):
            if question == "water_quality_variation":
                # Variació de la qualitat de l'aigua
                # Variació (%) = (([Concentració actual] - [Concentració inicial]) / [Concentració inicial]) × 100    
                current_concentration = value["water_quality_variation_2"]
                initial_concentration = value["water_quality_variation_1"]
                
                diff = current_concentration - initial_concentration

                if diff != 0: 
                    # Si no hi ha variació de la qualitat de l'aigua no s'aplica penalització (diff == 0).
                    # Si la variació és None, per defecte agafem 100. Que indica un canvi brusc. Ex: pasa de no tenir-ne contaminants a tenir-ne.
                    variation_pctg = calculate_percentatge(abs(diff), initial_concentration) or 100

                    if variation_pctg > 100: # variació superior al 100%
                        rating = -4 # índex màxim
                        sentence = f"<strong>+100%</strong> variació qualitat de l'aigua"
                    else: # Variació inferior a 100%
                        sentence = f"<strong>{variation_pctg}%</strong> variació qualitat de l'aigua"
                        rating = get_result_from_percentatge_table(abs(variation_pctg), table_water_dicts[question]["table"])
                    
                    logger.debug(f"WATER - Variació qualitat de l'aigua: {variation_pctg}%. Índex {rating}") 

                    ratings[question] = create_card_result(question, {"rating": rating, "out_of": 0}, NEGATIVE_SEMAPHORE, DIM)
                    ratings[question]["sentence"] = get_html_sentence(sentence)

            else:
                # Reducció del cabal d'aigua
                # Reducció (%) = (([Cabal inicial] - [Cabal actual]) / [Cabal inicial]) × 100
                initial_cabal = value["waterflow_reduction_1"]
                current_cabal = value["waterflow_reduction_2"]

                diff = initial_cabal - current_cabal

                logger.debug(f"WATER - Diferència de cabal: {diff}")
                sentence = None

                if diff != 0:
                    flow_pctg = calculate_percentatge(abs(diff), initial_cabal)
                    rating = get_result_from_percentatge_table(flow_pctg, table_water_dicts[question]["table"])
                    if diff > 0: # Reducció del cabal (Més habitual)
                        question = "waterflow_reduction" 
                        sentence = f"<strong>{flow_pctg}%</strong> reducció del cabal"
                        logger.debug(f"WATER - Reducció del cabal: {flow_pctg}%. Índex {rating}") 
                    else: # Increment del cabal (Cas menys habitual)
                        question = "waterflow_increment" 
                        sentence = f"<strong>{flow_pctg}%</strong> increment del cabal"
                        logger.debug(f"WATER - Increment del cabal: {flow_pctg}%. Índex {rating}") 

                else: # No ha hagut variació, s'aplica la millor puntuació.
                    question = "waterflow_reduction" 
                    rating = 5
                    sentence = "El cabal no ha variat"
                    logger.debug(f"WATER - El cabal no ha variat") 

                ratings[question] = create_card_result(question, {"rating": rating, "out_of": 5} , POSITIVE_SEMAPHORE, DIM)
                if sentence:
                    ratings[question]["sentence"] = get_html_sentence(sentence)
        else:
            # Reutilització de l'aigua
            rating = get_result_from_percentatge_table(value, table_water_dicts[question]["table"])
            logger.debug(f"WATER - Es reutilitza {value}% de l'aigua. - Índex {rating}")
            ratings[question] = create_card_result(question, {"rating": rating, "out_of": 5}, POSITIVE_SEMAPHORE, DIM)
            ratings[question]["sentence"] = get_html_sentence(f"<strong>{value}%</strong> aigua reutilitzada")
    
    if ratings != {}:
        return ratings
    else:
        return False
        


@safe_rating(default = False)
def get_air_rating(responses):
    """
    Calcula i retorna el rating de la Qualitat de l'Aire a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats. 
    """

    Id = "air_quality"
    semaphore = NEGATIVE_SEMAPHORE

    # clau: index de l'identificador esperat. Ex: <id>_1
    # valors: nom i unitat del tòxic.
    emission_standards = { 
        "1": {"name": "PM10", "unit": "µg/m³"},              
        "2": {"name": "PM2.5", "unit": "µg/m³"},
        "3": {"name": "TSP", "unit": "µg/m³"},            
        "4": {"name": "NO2", "unit": "µg/m³"},             
        "5": {"name": "SO2", "unit": "µg/m³"},
        "6": {"name": "CO2", "unit": "mg/m³"},                        
        "7": {"name": "O3", "unit": "µg/m³"},
        "8": {"name": "CO", "unit": "mg/m³"},
        "9": {"name": "Dioxines", "unit": "ng/Nm³"},
        "10": {"name": "Pb", "unit": "µg/m³"},             
        "11": {"name": "As", "unit": "ng/m³"},               
        "12": {"name": "Cd", "unit": "ng/m³"},            
        "13": {"name": "Ni", "unit": "ng/m³"},           
        "14": {"name": "B(a)P", "unit": "ng/m³"}   
    }

    # Les unitats associades a cada contaminant atmosfèric (ex: µg/m³, mg/m³, ng/Nm³) 
    # s’han assignat seguint els estàndards oficials de qualitat de l’aire establerts per la Unió Europea:
    # https://environment.ec.europa.eu/topics/air/air-quality/eu-air-quality-standards_en
    # entre d’altres fonts on es defineixen aquests tòxics com a indicadors clau de contaminació.


    air_quality_table = {
        (0, 19.99): 1, (20, 39.99): 2, (40, 59.99): 3, (60, 79.99): 4, (80, 100): 5
    }

    toxics_before_explotation = responses[0]['toxics_before_explotation']
    toxics_after_explotation = responses[1]['toxics_after_explotation']
    toxics_limit = responses[2]['limit']
    
    toxics_results = {}
    headers = ["Contaminant", "Valor previ", "Valor mesurat", "Límit admissible", "% Increment relatiu", "Índex"]
    table = []

    for i in range(0, len(toxics_before_explotation)):

        toxic_before, toxic_after, toxic_limit = toxics_before_explotation[i], toxics_after_explotation[i], toxics_limit[i]
        id_before, id_after, id_toxic = next(iter(toxic_before)), next(iter(toxic_after)), next(iter(toxic_limit))
        num_before, num_after, num_limit = get_number_children(id_before), get_number_children(id_after), get_number_children(id_toxic)
        
        if num_before == num_after == num_limit:

            value_before, value_after, limit = toxic_before[id_before], toxic_after[id_after], toxic_limit[id_toxic] 
            
            if value_after and value_before and limit:

                unit = emission_standards[num_before]["unit"]
                
                # marge d'increment 
                margin = limit - value_before
                # increment 
                increment = value_after - value_before
                # relació de quant a incrementat respecte el marge que es tenia
                impacte = calculate_percentatge(increment, margin) or 0  
                
                rating = None 

                # cas excepcional, ja s'habia sobrepasat el límit
                if value_before > limit:
                    if value_after <= value_before: # Ha millorat o es manté igual.
                        rating = 1 # Penalització mínima de -1
                    else: # Ha empitjorat
                        rating = 5 # Penalització màxima de -5

                if not rating:
                    if impacte > 100: # penalització màxima
                        rating = 5
                    else:
                        if margin == 0 and increment == 0: # No hi ha marge ni variació
                            rating = 1
                        else:  
                            rating = get_result_from_percentatge_table(impacte, air_quality_table)

                # Afegim valoració a la taula

                # Es marca en vermell si cap rating iguala o supera el 3.
                color = "table-danger" if rating >= 3 else "table-light"

                content_table = [ 
                    color,
                    emission_standards[num_before]["name"],
                    f"{value_before}  <small>({unit})</small>",
                    f"{value_after} <small>({unit})</small>",
                    f"{limit} <small>({unit})</small>",
                    f"{impacte}%",
                    f"-{rating}",
                ]

                table.append(content_table)

                toxics_results[emission_standards[num_before]["name"]] = rating

                logger.debug(f"AIR - Marge: {margin}; Increment: {increment}")
                logger.debug(f"AIR - Impacte(%): {impacte}%; Índex: {rating}")
    
    if toxics_results != {}: # Considerem l'índex més gran, 1 tòxic que supera el límit ja es molt greu.
        return create_section_result(Id, -max(toxics_results.values()), DIM, semaphore, info = get_html_table(headers, table))
    else:
        return False


@safe_rating(default = False)
def get_landform_changes_rating(responses):
    """
    Calcula i retorna el rating de Canvis de la Morfologia del Terreny a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats. 
    """

    Id = "LandformChanges"
    semaphore = NEGATIVE_SEMAPHORE
    
    # Inicialització índex 
    rating = None  
    # Llistat de missatges i missatge d'advertència
    list_msgs=[]
    warning_msg = ""
    # Inicialment no s'han aplicat mesures de restauració ni es compta amb un pla de rehabilitació
    restauration_mesures = False
    rehab_plan = False
    # Flag que indica si totes les preguntes necessaries per obtenir la valoració han estat resposes.
    completed = False        

    for id, value in iterate_responses(responses):
        if id == "modifications_type":
            list_msgs.append(("Tipus de modificació", value))
        elif id == "area_alterada":
            if value == 0: # Si el percentatge és 0 no hi ha cap impacte.
                return False
            completed = True
            list_msgs.append(("Àrea afectada", f"{value} %"))
            landform_table = {(0, 19.99): -1, (20, 39.99): -2, (40, 59.99): -3, (60, 100): -4}
            rating = get_result_from_percentatge_table(value, landform_table)
            logger.debug(f"LC - Percentatge àrea alterada {value}%")
        elif id == "reversible_modification": 
            if value is False and completed is True: # Si els canvis no són reversibles -> impacte extremadament greu
                return create_section_result(Id, -5, DIM, semaphore, info = get_html_list(list_msgs))
        elif id == "recovery_time":
            if value <= 10:
                list_msgs.append(("Temps previst de recuperació", f"{value} anys (recuperació ràpida)"))
            elif value <= 50:
                list_msgs.append(("Temps previst de recuperació", f"{value} anys (recuperació a mig termini)"))
            else:
                list_msgs.append(("Temps previst de recuperació", f"{value} anys (recuperació molt lenta)"))
        elif id == "restauration_mesures":
            restauration_mesures = value 
        elif id == "rehab_plan":
            rehab_plan = value
    
    # Missatge d'advertencia
    if restauration_mesures is False and rehab_plan is False: 
        warning_msg = "No s’han aplicat mesures de restauració ni existeix un pla de rehabilitació definit. Aquesta doble absència redueix les garanties de recuperació del terreny i pot comportar impactes a llarg termini sobre el medi ambient i el paisatge."
    elif restauration_mesures is False:
        warning_msg = "No s’han aplicat mesures de restauració per recuperar la morfologia o minimitzar l’impacte. Aquesta manca d’actuació pot agreujar la degradació del terreny i dificultar la seva recuperació futura."
    elif rehab_plan is False:
        warning_msg = "No existeix cap pla de rehabilitació definit per restablir la topografia i la coberta vegetal. Aquesta absència suposa una manca de garanties sobre la restauració futura i pot augmentar el risc de deixar impactes permanents en el paisatge."

    if len(warning_msg) > 0: 
        extra_info = get_html_list(list_msgs) + get_html_warning(warning_msg)
    else:
        extra_info = get_html_list(list_msgs)

    if rating is None:
        logger.debug("LC - Falta introduir el percentatge de l'àrea total alterada.")
        return False
    
    logger.debug(f"LC - Índex: {rating}")

    return create_section_result(Id, rating, DIM, semaphore, info = extra_info)

@safe_rating(default = False)
def get_biodiversity_rating(responses): 
    """
    Calcula i retorna el rating de Biodiversitat i Ecosistemes a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats. 
    """
    
    Id = "Biodiversity"
    semaphore = NEGATIVE_SEMAPHORE

    score, list_msg = 0, []
    completed = False 
    warnings = []

    for id, value in iterate_responses(responses):
        if id == "biodiversity_affected":
            completed = True
            if value == 0:
                return False
            # taula no especificada al PDF
            biodiversity_table = {(1, 19.99): 1, (20, 39.99): 2, (40, 59.99): 3, (60, 79.99): 4, (80, 100): 5}     
            score = get_result_from_percentatge_table(value, biodiversity_table)
            logger.debug(f"BE: Biodiversitat afectada: {value}%; índex: {score}") 
            list_msg.append(("Biodiversitat afectada", f"{value}%"))

        elif id == "endangered_species" or id == "critic_habitat":
            if value is True:
                score += 1
        elif id == "complete_recovery":
            if value is True:
                score -= 2
        elif id == "protected_habitat":
            if value is True:
                warnings.append("hàbitats protegits")
        elif id == "fragmented_habitat":
            if value is True:
                warnings.append("fragmentació del territori")
        elif id == "water_ecosistems":
            if value is True:
                warnings.append("alteració d’ecosistemes aquàtics")
        elif id == "estandarized_plan":
            if value is False:
                list_msg.append(("Pla de restauració ambiental", "No consta cap pla aprovat ni auditable ❌"))
            else:
                list_msg.append(("Pla de restauració ambiental", "Existeix i està aprovat ✅"))

    if completed is True:
        info = get_html_list(list_msg)
        if len(warnings) > 0:
            warning_msg = "S’han detectat afectacions en "
            for i in range(len(warnings)):
                if i == 0:
                    warning_msg += warnings[i]
                elif i == (len(warnings) - 1):
                    warning_msg += f" i {warnings[i]}"
                else:
                    warning_msg += f", {warnings[i]}"
            info += get_html_warning(warning_msg)
        # Limitem entre 1 i 5 
        rating = -round(min(max(score, 1), 5))
        logger.debug(f"BE - Puntuació {score}. Índex: {rating}")

        return create_section_result(Id, rating, DIM, semaphore, info = info)
    else:
        return False

@safe_rating(default = False)
def get_subsidence_rating(responses):
    """
    Calcula i retorna el rating de la Subsidència a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats. 
    """
     
    Id, impacts = "Subsidence", 0
    semaphore = NEGATIVE_SEMAPHORE

    for id, value in iterate_responses(responses):
        if id == "subsidence_detected":
            if value is False:
                logger.debug("SUB - No s'ha detectat subsidència. Penalització: 0.")
                return False
        elif id == "sub_compatible_impact":
            logger.debug("SUB - Impacte de la subsidència és incompatible. Penalització: -5")
            if value is False:
                return create_section_result(Id, -5, DIM, semaphore)
        elif id == "sub_risk_of_collapse":
            if value is True:
                logger.debug("SUB - Hi ha risc de col·lapse. Penalització: -5")
                return create_section_result(Id, -5, DIM, semaphore)
        else:
            if value is True:
                impacts += 1

    if impacts >= 3:
        logger.debug("SUB - 3 o més impactes. Puntuació: -5")
        return create_section_result(Id, -5, DIM, semaphore)
    else:
        logger.debug("SUB - Menys de 3 impactes. Puntuació: 0")
        return False
    
 
@safe_rating(default = False)
def get_positive_environmental_rating(responses):
    """
    Calcula i retorna el rating de Efectes ambientals positius a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats. 
    """
     
    Id = "PositiveEnvironmental"
    semaphore = POSITIVE_SEMAPHORE

    score, list_msg = 0, []
    # Qualitat del sòl i Descontaminació d'aïgues -> impacte gran. La resta suma 1 punt.
    criterion = {"env_soil_quality_improved": 4 , "env_water_regeneration": 4}
    
    completed = False
    
    for id, value in iterate_responses(responses):
        if id == "env_restored_area_percentage":
            # taula creada sota el meu criteri (No s'especifica res al PDF)
            restored_area_table = {(0, 19.99): 1, (20, 39.99): 2, (40, 59.99): 3, (60, 79.99): 4, (80, 100): 5}
            if value != 0:
                score += get_result_from_percentatge_table(value, restored_area_table)
            list_msg.append(("Àrea restaurada", f"{value}%"))
            logger.debug(f"IPE - Àrea restaurada: {value}%")
            completed = True
        else:
            if id in criterion:
                if value is True:
                    score += criterion[id] 
            # La resta de preguntes si s'han respòs que Sí són positives.
            else:
                if value is True:
                    score += 1

    if completed is True:
        # 4 + 4 + 5 + 4*1 = 17
        max_score = 17
        rating = calculate_rating_from_score(score, max_score)
        logger.debug(f"IPE - Puntuació: {score}/17. Índex: {rating}")
        return create_section_result(Id, rating, DIM, semaphore, info = get_html_list(list_msg))
    else:
        return False 
        

# PASSIUS AMBIENTALS
@safe_rating(default = False)
def get_liability_impact_rating(responses):
    """
    Calcula i retorna el rating de Passius Ambientals a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats. 
    """
     
    ratings, impact_score = {}, 0
    impact_completed = False
    for parent, children in iterate_responses(responses):
        if parent == "extension": 
            # 1. EXTENSIÓ DELS PASSIUS AMBIENTALS 
            Id, extension_table = "ExtensionLiabilities", {(0, 19.99): 1, (20, 39.99): 2, (40, 59.99): 3, (60, 79.99): 4, (80, 100): 5} # Taula 28
            
            affected_area = children["extension_1"] # Percentatge de l'àrea afectada

            if affected_area != 0: # Si es exactament 0 no penalitza
                rating = get_result_from_percentatge_table(affected_area, extension_table)
    
                ratings[Id] = create_card_result(Id, {"rating": -rating, "out_of": 0}, NEGATIVE_SEMAPHORE, DIM)

                # Afegim la frase extra informativa dins de la tarjeta resultant.
                ratings[Id]["sentence"] = get_html_sentence(f"Àrea afectada: <strong>{affected_area}%</strong>")
                logger.debug(f"LI - Àrea afectada: {affected_area}%. Índex: {rating}")

        elif parent == "impact":
            # 2. IMPACTE DELS PASSIUS AMBIENTALS
            # Les Si/No sempre entrarán, no cal mirar-les.
            # Criteri d'impacte
            impact_criterion = {"impact_1": 2, "impact_2": 4, "impact_4": 2, "impact_5": 2}

            for child, value in children.items():
                if child != "impact_3": 
                    if value is True:
                        impact_score += impact_criterion[child]
                else: # Cost
                    
                    impact_completed = True 

                    if value == "Baix":
                        impact_score += 1
                    elif value == "Moderat":
                        impact_score += 2
                    elif value == "Alt":
                        impact_score += 3 
                    elif value == "Molt alt":
                        impact_score += 5
                    elif value == "No restaurable":
                        ratings["LiabilityImpact"] = create_card_result("LiabilityImpact", {"rating": -5, "out_of": 0}, NEGATIVE_SEMAPHORE, DIM)
                        return ratings
            
            logger.debug(f"LI - Impacte. Puntuació {impact_score}")
            
        elif parent == "management":
            # es valora la gestió i suma o resta punts a la puntuació
            # Si la resposta és Sí és positiu
            trues = sum(children.values())
            if trues == 0: # Mala gestió
                impact_score += 1
            elif trues > 2: # Bona gestió, li resta un punt a l'impacte negatiu
                impact_score -= 1

            logger.debug(f"LI - Impacte + Gestió. Puntuació {impact_score}/16")  
    
    if impact_completed is True:
        rating = calculate_rating_from_score(impact_score, 16)      
        ratings["LiabilityImpact"] = create_card_result("LiabilityImpact", {"rating": -rating, "out_of": 0}, NEGATIVE_SEMAPHORE, DIM)

    return ratings if ratings != {} else False
