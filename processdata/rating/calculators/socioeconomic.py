import logging
from .utils.helpers import *

logger = logging.getLogger(__name__)

DIM = 0  # Dimensió Socioeconòmica

# -----------------------------------------------------------------
# --------FUNCIONS CALCULADORES DE RATING PER SECCIONS-------------
# -----------------------------------------------------------------

@safe_rating(default=False)
def get_local_procurement_rating(responses):
    """
    Calcula i retorna el rating de Contractació Local a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats.
    """

    table_local_dicts = {
        # Taula 1
        "departments_using_local_suppliers_percentatge": {
            "table": {
                (0, 19.99): 1,
                (20, 39.99): 2,
                (40, 59.99): 3,
                (60, 79.99): 4,
                (80, 100): 5,
            },
            "sentence": "$value$ contractistes locals.",
            "semaphore": POSITIVE_SEMAPHORE
        },
        # Taula 2
        "large_local_contractors_percentatge": {
            "table": {
                (0, 19.99): 1,
                (20, 39.99): 2,
                (80, 100): 3,
                (60, 79.99): 4,
                (40, 59.99): 5,
            },
            "sentence": "$value$ grans contractistes locals.",
            "semaphore": POSITIVE_SEMAPHORE
        },
    }

    return get_ratings_from_percentatge_tables(responses, table_local_dicts, DIM)


@safe_rating(default = False)
def get_local_expediture_rating(responses):
    """
    Calcula i retorna el rating de Cost Local a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Diccionari amb el contingut a mostrar a la vista resultats.
    """

    table_expediture_dicts = {
        # taula 3
        "expediture_structure_local_percentatge": {
            "table": {
                (10, 19.99): 1,
                (20, 39.99): 2,
                (40, 59.99): 3,
                (60, 79.99): 4,
                (80, 100): 5,
            },
            "sentence": "$value$ cost local i regional.",
            "semaphore": POSITIVE_SEMAPHORE
        },
        # taula 4
        "expediture_structure_national_percentatge": {
            "table": {
                (20, 39.99): 1,
                (40, 59.99): 2,
                (60, 100): 3,
            },
            "sentence": "$value$ cost nacional.",
            "semaphore": {1: "RED", 2: "ORANGE", 3: "GREEN"}
        },
        # taula 5
        "employment_quality_percentatge": {
            "table": {
                (0, 19.99): 1,
                (20, 39.99): 2,
                (40, 59.99): 3,
                (60, 79.99): 4,
                (80, 100): 5,
            },
            "sentence": "$value$ empleats locals i regionals.",
            "semaphore": POSITIVE_SEMAPHORE
        },
    }
    return get_ratings_from_percentatge_tables(responses, table_expediture_dicts, DIM)


@safe_rating(default = False)
def get_infraestructure_creation_rating(responses):
    """
    Calcula i retorna el rating de Creació d'Infraestructures a partir de les respostes de l'usuari.

    :param responses (list(dict)): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return int, dict: Retorna el valor de l'índex juntament amb un diccionari, separant la puntuació del contingut informatiu.
    """
    # ID de la secció
    Id = "InfraestructureCreation"

    semaphore = POSITIVE_SEMAPHORE

    # Puntuació i missatges que es mostren a la UI.
    score, extra_messages = 0, []

    # Criteri, on la clau és l'ID de la pregunta i el valor el pes.
    # Si la resposta de l'usuari és afirmativa se li suma el valor esmentat.
    criterion = {
        "consultation": 1, # La comunitat ha estat consultada.
        "benefits-after-close": 3, # Les infraestructures beneficien després del tancament.
        "infraestructures-affected": -3, # S'ha perjudicat a infraestructures existents.
        "infraestructures-upgrades": 1, # Petites millores en camins, accés a aigua potable, ...
        "facilities-for-internal-use": -2, # Instal·lacions únicament per a ús intern de la mina.
        "instalations-for-benefit": 5, # S'han construït hospitals, carreteres, etc.
        "new-local-jobs": 3, # S'ha generat ocupació local.
        "facilities-for-basic-services": 3, # Faciliten l'accés a serveis bàsics.
        "increment-economy": 5, # Ha generat creixement econòmic.
        "means-of-communication": 3, # Millora de les vies de comunicació.
        "maintenance-agreements": 3, # Acords de manteniment.
        "quality-of-life": 5, # Han millorat la qualitat de vida de la població.
        "visible-improvements": 5, # Les millores són visibles.
        "connectivity-changes": 5, # Canvis estructurals en la connectivitat del país.
        "post-mining-use": 3, # Una vegada finalitzat l'activitat minera podran ser utilitzades per altres pròposits.
        "government-agreements": 3, # Acords amb el govern local
        "sustainable-design": 1, # Disseny sostenible
    }

    max_score = sum(value for value in criterion.values() if value >= 0)  # Puntuació màxima
    min_score = max_score / 5  # puntuació necessaria per assolir el nivell 1

    for question, value in iterate_responses(responses):

        if question == "infraestructure-evaluate": # L'usuari no la vol avaluar (és l'únic cas que requereix demanar a l'usuari)
            if value is False:
                return False

        if question == "infraestructure":
            if value is False:  # No s'ha constrüit ni s'ha fet millores
                logger.debug(f"IC - No s'ha construït ni millorat infraestructures. Índex = 1.")
                return create_section_result(Id, 1, DIM, semaphore)
            else:
                # Si s'ha construït o millorat sumem puntuació mínima. Suposem que si s'ha marcat que si com a mínim es tracta d'una petita millora.
                score += min_score

        if question in criterion:
            score += criterion[question] if value is True else 0

        elif question == "infrastructure-type":
            if not "default" in value and len(value) > 0:
                extra_messages.append(("Infraestructures destacades", value))

        elif question == "post-closure-maintenance" and len(value) > 0:
            extra_messages.append(("Responsable del manteniment", value))

    rating = calculate_rating_from_score(score, max_score)
    logger.debug(f"IC - Puntuació: {score}/{max_score}. Índex: {rating}")

    if extra_messages != []:
        return create_section_result(Id, rating, DIM, semaphore, info = get_html_list(extra_messages))
    else:
        return create_section_result(Id, rating, DIM, semaphore)



@safe_rating(default = False)
def get_value_chain_rating(responses):
    """
    Calcula i retorna el rating de Cadena de Valor a partir de les respostes de l'usuari.

    :param responses (list): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return dict: Retorna diccionari amb les dades per a cada secció a mostrar a resultats.
    """

    ratings = {}
    
    for question, value in iterate_responses(responses):
        rating = None
        if question == "type_of_product": 
            product_dicts = {
                "Producte refinat mínim, encara requereix processos addicionals. Procés fet a la mateixa regió o país.": 1,
                "Producte final processat al país, però lluny de la mina, sense paper estratègic clar.": 2,
                "Producte final processat al país, lluny de la mina, i clau per al desenvolupament industrial nacional o supranacional.": 3,
                "Producte final processat a la mateixa regió de la mina, i clau per al desenvolupament industrial nacional o supranacional.": 4,
                "Producte processat a la regió i essencial per al desenvolupament sostenible de la societat.": 5,
            }
            # 1. Tipus de producte i valor afegit
            rating = product_dicts[value]
            ratings[question] = create_card_result(question, {"rating": rating, "out_of": 5}, POSITIVE_SEMAPHORE, DIM)
            logger.debug(f"VC - Tipus de producte, Índex {rating}")
        elif question == "r_and_d":
            # Hem de tenir els tres valors per poder calcular el percentatge.
            rating_table = {
                (0, 19.99): 1,
                (20, 39.99): 2,
                (40, 59.99): 3,
                (60, 79.99): 4,
                (80, 100): 5,
            }

            total_budget, total_inversion = (value["r_and_d_1"], value["r_and_d_2"] + value["r_and_d_3"])

            if (total_budget > 0 and total_inversion > 0):  # Si algún dels dos es 0, no podem realitzar els càlculs.
                pctg = calculate_percentatge(total_inversion, total_budget)
                sentence = f"Inversió del <strong>{pctg}%</strong>"
                logger.debug(f"VC - Inversió I + D: {pctg}%")

                if pctg is not None:
                    if pctg <= 100:
                        rating = get_result_from_percentatge_table(pctg, rating_table)
                    else:
                        rating = 5
                        sentence += """<br><span class="text-danger">**Valor irreal, revisa les dades entrades. **<span>"""

                if rating:
                    ratings[question] = create_card_result(question, {"rating": rating, "out_of": 5}, POSITIVE_SEMAPHORE, DIM)
                    ratings[question]["sentence"] = get_html_sentence(sentence)

    return ratings if ratings != {} else False



@safe_rating(default = False)
def get_rating_economic_disturbance(responses):
    """
        Calcula i retorna el rating de Impacte de les Pertorbacions Econòmiques a partir de les respostes de l'usuari.

        :param responses (list): Llista de diccionaris amb les respostes proporcionades per l’usuari.
        :return int, dict: Retorna el valor de l'índex juntament amb un diccionari, separant la puntuació del contingut informatiu.
    """
      
    Id = "EconomicDisturbance"
    semaphore = NEGATIVE_SEMAPHORE
    extra_messages = []
    pctg, impact_type, long_term, created_jobs = None, None, None, False

    for question, value in iterate_responses(responses):

        if question == "affected-activities":
            if not "default" in value:  # Activitats socioeconòmiques afectades.
                extra_messages.append(("Activitats socioeconòmiques afectades", value))
    
        elif (question == "families_vs_jobs"):  
            families, jobs = value["families_vs_jobs_1"], value["families_vs_jobs_2"]

            if families == 0:
                logger.debug("ED - No hi ha families afectades. No hi ha impacte.")
                return False
            else:
                if (jobs == 0):  # Si hi han families afectades però no s'ha generat cap lloc de treball.
                    extra_messages.append(("Llocs de treball generats", "0 ❌"))
                    logger.debug("ED - No s'han generat ocupacions.")
                    # return create_result_output(Id, 5, DIM, separate, extra_msgs = get_html_list(extra_messages))
                else:
                    created_jobs = True  # Si s'han generat ocupacions
                    pctg = calculate_percentatge(families, jobs)
                    if pctg <= 100:
                        extra_messages.append(("Relació entre afectació i generació de llocs de treball", f"{pctg}%"))
                    else:
                        extra_messages.append(("Relació entre afectació i generació de llocs de treball", f"+100%"))

                    logger.debug(f"ED - Families afectades respecte les ocupacions generades: {pctg}%")

        elif question == "full-impact":
            if value == "No afecta":
                logger.debug("ED - No hi ha cap impacte perquè NO AFECTA.")
                return False
            else:
                impact_type_table = {"Afecta tota la comunitat": "yes", "Afecta només una part": "partial"}
                impact_type = impact_type_table[value]

        elif question == "long-term-impact":
            long_term_table = {
                "Tant durant com després del tancament": "yes",
                "Només durant la vida útil de la mina": "no",
                "No se sap": "unknown",
            }
            long_term = long_term_table[value]

            if impact_type is None:
                # No s'ha especificat el nivell d'impacte, no podem valorar-ho.
                return False

            if created_jobs is False:
                # Si no s'han generat posicions de treball...
                if impact_type == "partial":  # Impacte petit si afecta parcialment
                    return create_section_result(Id, -2, DIM, semaphore, info=get_html_list(extra_messages))
                elif impact_type == "yes":  # Afecta tota la comunitat
                    if long_term != "no":  # A llarg termini o no se sap
                        return create_section_result(Id, -5, DIM, semaphore, info=get_html_list(extra_messages))
                    else:  # Només durant la vida de la mina
                        return create_section_result(Id, -3, DIM, semaphore, info=get_html_list(extra_messages))

            if pctg is None:
                # No s'ha pogut calcular percentatge.
                return False

            if (long_term != "no" and pctg >= 25):  # Si no se sap o afecta tant durant com després de la mina i afecta a més del 25%
                return create_section_result(Id, -5, DIM, semaphore, info=get_html_list(extra_messages))

            # Altres casos durant la vida útil
            if pctg < 25:
                if impact_type == "partial":
                    return create_section_result(Id, -2, DIM, semaphore, info=get_html_list(extra_messages))
                elif impact_type == "yes":
                    return create_section_result(Id, -3, DIM, semaphore, info=get_html_list(extra_messages))
            elif 25 <= pctg <= 50:
                if impact_type == "partial":
                    return create_section_result(Id, -3, DIM, semaphore, info=get_html_list(extra_messages))
                elif impact_type == "yes":
                    return create_section_result(Id, -4, DIM, semaphore, info=get_html_list(extra_messages))
            elif pctg > 50:
                if impact_type == "partial":
                    return create_section_result(Id, -4, DIM, semaphore, info=get_html_list(extra_messages))
                elif impact_type == "yes":
                    return create_section_result(Id, -5, DIM, semaphore, info=get_html_list(extra_messages))

    return False


@safe_rating(default = False)
def get_additional_involvement_rating(responses):
    """
    Calcula i retorna el rating de Impacte de la Participació Adiccional a partir de les respostes de l'usuari.

    :param responses (list): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return int, dict: Retorna el valor de l'índex juntament amb un diccionari, separant la puntuació del contingut informatiu.
    """
    
    Id = "AdditionalInvolvement"
    semaphore = POSITIVE_SEMAPHORE

    score = sum(next(iter(r.values())) for r in responses)

    if score == 0:
        # No hi ha participació adiccional
        logger.debug("AI - No hi ha participació adiccional")
        return False

    rating = max(1, min(5, score))
    logger.debug(f"AI - Puntuació: {score}. Índex: {rating}")

    return create_section_result(Id, rating, DIM, semaphore)


@safe_rating(default = False)
def get_closure_process_rating(responses):
    """
    Calcula i retorna el rating de Impacte de les Condicions Finals al a partir de les respostes de l'usuari.

    :param responses (list): Llista de diccionaris amb les respostes proporcionades per l’usuari.
    :return int, dict: Retorna el valor de l'índex juntament amb un diccionari, separant la puntuació del contingut informatiu.
    """

    Id = "ClosureProcess"
    score, extra_messages = 0, []
  
    for question, value in iterate_responses(responses):
        if question == "added_value_final_conditions_info":
            current_conditions = responses[0]["added_value_final_conditions_info"]  # Condicions actuals del lloc que s'ha de restaurar
            extra_messages.extend([("Condicions actuals del lloc a restaurar", current_conditions)])
        elif question == "added_value_final_conditions":
            if not "added_value_final_conditions_1" in value or not "added_value_final_conditions_2" in value:
                return False # Camps obligatoris, si no no es realitza la puntuació.
            
            # Valoració d'us futur amb sinergia (condició 2)
            usos_sinergics = [
                "Agricultura o ramaderia.",
                "Àrea protegida per conservació.",
                "Infraestructura per energies renovables.",
            ]

            foreseen_future, impact_before_close = (
                value["added_value_final_conditions_1"],
                value["added_value_final_conditions_2"],
            )

            extra_messages.extend(
                [
                    ("Ús futur previst per l'àrea restaurada", foreseen_future),
                    (
                        "Impacte ambiental i social de la mina abans del tancament",
                        impact_before_close,
                    ),
                ]
            )

            # hi ha sinergia amb el territori -> aporta valor afegit a llarg termini.
            if foreseen_future in usos_sinergics:
                score += 1

            # Impacte lleu abans del tancament
            if impact_before_close == "Pocs impactes negatius significatius":
                score += 1

            # Sumem 1 per cada True
            score += sum(list(value.values())[2:])

            # Màxim Score = 11 
            # (Important posar la maxima puntuació així, recordem que si alguna pregunta no ha estat resposa no es processada)
            rating = calculate_rating_from_score(score, 11)

            logger.debug(f"CP - Puntuació: {score}/11. Índex: {rating}")

            return create_section_result(Id, rating, DIM, POSITIVE_SEMAPHORE, info=get_html_list(extra_messages))

    return False
