from django.test import TestCase
from .rating.calculators.environment import * 
from .rating.calculators.socioeconomic import * 

class HelpersTestCase(TestCase):
    def test_result_from_percentatge_table(self):
        table = {(0, 19.99): 1, (20, 39.99): 2, (40, 59.99): 3, (60, 79.99): 4, (80, 100): 5}
        correct_responses = {1: 10, 2: 20, 3: 40, 4: 60, 5: 100}
        for index, pctg in correct_responses.items():
            result = get_result_from_percentatge_table(pctg, table)
            self.assertEqual(result, index)

    def test_normalize_score(self):
        # Cas 1: majoria de puntuacions baixa i amb penalització. Poor Level. 
        max_score = 28
        scores = [3, 2, 2, 1, 3, 2, -2]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 37.67, places=2)
        self.assertEqual(score, 11)

        # Cas 2: puntuacions mitjanament altes amb penalització. Satisfactory Level.
        max_score = 28
        scores = [3, 4, 4, 5, 2, 5, -3]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 70.67, places=2)
        self.assertEqual(score, 20)

        # Cas 3: puntuacions altes. Good Level.
        max_score = 43
        scores = [3, 5, 5, 5, 5, 5, 5, 5, 5]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 100, places=2)
        self.assertEqual(score, 43)

        # Cas 4: puntuacions amb penalització. Weak Level.
        max_score = 15
        scores = [2, 3, 5, -3, -5]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 41.5, places=2)
        self.assertEqual(score, 2)

        # Cas 5: puntuacions sense penalització. Weak Level.
        max_score = 15
        scores = [2, 3, 5]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 58.75, places=2)
        self.assertEqual(score, 10)

        # Cas 6: Tot penalitzacions greus. Very Poor Level.
        max_score = 0
        scores = [-5, -5, -5]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 1.0, places=2)
        self.assertEqual(score, -15)

        # Cas 7: Tot penalitzacions. Weak Level. 
        max_score = 0
        scores = [-1, -2, -5]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 47.2, places=2)
        self.assertEqual(score, -8)

        # Cas 8: puntuacions altes VS amb moltes penalitzacions. Satisfactory Level.
        max_score = 43
        scores = [3, 5, 5, 5, 5, 5, 5, 5, 5, -5, -5, -5, -5, -2]
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 63.08, places=2)
        self.assertEqual(score, 21)

        # Cas 9: No hi ha puntuacions
        max_score = 0
        scores = []
        nscore, score = normalize_likert_score(max_score, scores)
        self.assertAlmostEqual(nscore, 1, places=2)
        self.assertEqual(score, 0)

    # ****************** TEST FORMATADORS I CREADORS DE SORTIDA ********************
    def test_formatted_extra_info(self):
        # Cas 1: secció sense títol específic, bloc únic
        section_id = "EconomicDisturbance"
        rating = 5
        dim = 0  # Socioeconòmica
        result = get_formatted_extra_info(section_id, rating, dim)
        self.assertIn("summary", result)
        self.assertIn("advice", result)
        self.assertNotIn("name", result)
        
        # Cas 2: tarjeta
        card_id = "departments_using_local_suppliers_percentatge"
        result = get_formatted_extra_info(card_id, rating, dim)
        self.assertIn("name", result)
        self.assertIn("summary", result)
        self.assertIn("advice", result)
        self.assertNotIn("messages", result)  # No hem passat extra_msgs

        # Cas 3: targeta amb missatges extres
        extra_msgs = [("Comentari 1", "Valor 1"), ("Comentari 2", "Valor 2")]
        result = get_formatted_extra_info(card_id, rating, dim, extra_msgs)
        self.assertIn("name", result)
        self.assertIn("summary", result)
        self.assertIn("advice", result)
        self.assertIn("messages", result)
        self.assertEqual(len(result["messages"]), 2)

        # Cas 4: secció sense nom amb missatges extres
        extra_msgs_4 = [("Info addicional", "Sí")]
        result = get_formatted_extra_info(section_id, rating, dim, extra_msgs_4)
        self.assertIn("summary", result)
        self.assertIn("advice", result)
        self.assertIn("messages", result)
        self.assertNotIn("name", result)
        self.assertEqual(len(result["messages"]), 1)

    def test_create_card_result(self):
        # Paràmetres d’entrada
        card_id = "departments_using_local_suppliers_percentatge"
        dim = 0  # Socioeconòmica
        sem = POSITIVE_SEMAPHORE
        rdata = {
            "rating": 5,
            "out_of": 5
        }

        result = create_card_result(card_id, rdata, sem, dim)

        # Comprovacions bàsiques
        self.assertEqual(result["rating"], 5)
        self.assertEqual(result["out_of"], 5)
        self.assertEqual(result["semaphore"], "DGREEN")
        self.assertIn("summary", result)
        self.assertIn("advice", result)
        self.assertIn("name", result)

    def test_create_section_result(self):
        section_id = "EconomicDisturbance"
        rating = -4
        dim = 0  # Socioeconòmica
        sem = NEGATIVE_SEMAPHORE
        extra_msgs = [("Comentari", "Impacte alt")]

        # Cas 1: sense missatges extres
        rating_result, view_data = create_section_result(section_id, rating, dim, sem)
        self.assertEqual(rating_result, rating)
        self.assertEqual(view_data["semaphore"], "RED")
        self.assertIn("summary", view_data)
        self.assertIn("advice", view_data)
        self.assertNotIn("name", view_data)  # És un bloc únic
        self.assertNotIn("messages", view_data)

        # Cas 2: amb missatges extres
        rating_result, view_data = create_section_result(section_id, rating, dim, sem, extra_msgs)
        self.assertEqual(rating_result, rating)
        self.assertEqual(view_data["semaphore"], "RED")
        self.assertIn("summary", view_data)
        self.assertIn("advice", view_data)
        self.assertIn("messages", view_data)
        self.assertEqual(len(view_data["messages"]), 1)
        self.assertEqual(view_data["messages"][0][0], "Comentari")

    def test_ratings_from_percentatge_tables(self):
        responses = [{"departments_using_local_suppliers_percentatge": 85}]
        references = {
            "departments_using_local_suppliers_percentatge": {
                "table": {(0, 19): 1, (20, 39): 2, (40, 59): 3, (60, 80): 4, (81, 100): 5},
                "sentence": "$value$ contractistes locals.",
                "semaphore": POSITIVE_SEMAPHORE
            }
        }
        result = get_ratings_from_percentatge_tables(responses, references, dim=0)

        self.assertIsInstance(result, dict)
        self.assertIn("departments_using_local_suppliers_percentatge", result)

        card = result["departments_using_local_suppliers_percentatge"]
        self.assertEqual(card["rating"], 5)
        self.assertEqual(card["out_of"], 5)
        self.assertEqual(card["semaphore"], "DGREEN")
        self.assertEqual(card["name"], "Integració de contractistes locals")
        self.assertIn("Excel·lent", card["summary"])
        self.assertEqual(card["advice"], "Documenta i comparteix l’experiència com a bona pràctica, i garanteix la continuïtat del model.")


# TEST CÀLCULS DIMENSIÓ SOCIOECONOMICA
class SocioeconomicTestCase(TestCase):
    def test_local_procurement_rating(self):
        
        local_suppliers = "departments_using_local_suppliers_percentatge"
        local_contractors = "large_local_contractors_percentatge"

        # TEST MASSIU: Contractació Local
        test_for_index_1, s1 = [0, 1.5, 3, 4.8, 6, 7.2, 10, 12.5, 15, 17.3, 19], "RED"
        test_for_index_2, s2 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39], "ORANGE"
        test_for_index_3, s3 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59], "YELLOW"
        test_for_index_4, s4 = [60, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 79.99], "GREEN"
        test_for_index_5, s5 = [81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "DGREEN"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{local_suppliers: t}]
                result = get_local_procurement_rating(responses)
                self.assertEqual(result[local_suppliers]["rating"], test["index"])
                self.assertEqual(result[local_suppliers]["semaphore"], test["color"])
                self.assertNotIn(local_contractors, result)

        # TEST MASSIU: Grans Contractistes Locals
        test_for_index_1, s1 = [0, 1.5, 3, 4.8, 6, 7.2, 10, 12.5, 15, 17.3, 19], "RED" # < 20%
        test_for_index_2, s2 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39], "ORANGE" # 20-40%
        test_for_index_3, s3 = [81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "YELLOW" # +80%
        test_for_index_4, s4 = [60, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 79.99], "GREEN" # 60-80%
        test_for_index_5, s5 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59], "DGREEN" # 40-60%

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{local_contractors: t}]
                result = get_local_procurement_rating(responses)
                self.assertEqual(result[local_contractors]["rating"], test["index"])
                self.assertEqual(result[local_contractors]["semaphore"], test["color"])
                self.assertNotIn(local_suppliers, result)

        # COMBINACIONS:
        # C1: les dues seccions han estat resposes per l'usuari.
        responses = [{"departments_using_local_suppliers_percentatge": 20}, {"large_local_contractors_percentatge": 40}]
        result = get_local_procurement_rating(responses)
        self.assertEqual(result["departments_using_local_suppliers_percentatge"]["rating"], 2)
        self.assertEqual(result["departments_using_local_suppliers_percentatge"]["semaphore"], "ORANGE")
        self.assertEqual(result["large_local_contractors_percentatge"]["rating"], 5)
        self.assertEqual(result["large_local_contractors_percentatge"]["semaphore"], "DGREEN")
        

    def test_local_expediture_rating(self):

        local_expediture = "expediture_structure_local_percentatge"
        national_expediture = "expediture_structure_national_percentatge"
        employment_quality = "employment_quality_percentatge"

        # TEST MASSIU: Cost Local
        test_for_index_1, s1 = [10, 12.5, 15, 17.3, 19], "RED" # 10-20%
        test_for_index_2, s2 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39], "ORANGE" # 20-40%
        test_for_index_3, s3 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59], "YELLOW" # 40-60%
        test_for_index_4, s4 = [60, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 79.99], "GREEN" # 60-80%
        test_for_index_5, s5 = [81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "DGREEN" # +80%

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{local_expediture: t}]
                result = get_local_expediture_rating(responses)
                self.assertEqual(result[local_expediture]["rating"], test["index"])
                self.assertEqual(result[local_expediture]["semaphore"], test["color"])
                self.assertNotIn(national_expediture, result)
                self.assertNotIn(employment_quality, result)

        # TEST MASSIU: Cost Nacional
        test_for_index_1, s1 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39], "RED" # 20-40%
        test_for_index_2, s2 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59.99], "ORANGE" # 40-60%
        test_for_index_3, s3 = [61, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 80, 81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "GREEN" # +60%

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3}
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{national_expediture: t}]
                result = get_local_expediture_rating(responses)
                self.assertEqual(result[national_expediture]["rating"], test["index"])
                self.assertEqual(result[national_expediture]["semaphore"], test["color"])
                self.assertNotIn(local_expediture, result)
                self.assertNotIn(employment_quality, result)


        # TEST MASSIU: Qualitat d'empleament
        test_for_index_1, s1 = [0, 1.5, 3, 4.8, 6, 7.2, 10, 12.5, 15, 17.3, 19], "RED" # 0-20%
        test_for_index_2, s2 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39], "ORANGE" # 20-40%
        test_for_index_3, s3 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59], "YELLOW" # 40-60%
        test_for_index_4, s4 = [60, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 79.99], "GREEN" # 60-80%
        test_for_index_5, s5 = [81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "DGREEN" # +80%

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{employment_quality: t}]
                result = get_local_expediture_rating(responses)
                self.assertEqual(result[employment_quality]["rating"], test["index"])
                self.assertEqual(result[employment_quality]["semaphore"], test["color"])
                self.assertNotIn(national_expediture, result)
                self.assertNotIn(local_expediture, result)

        # COMBINACIONS:

        # C1: l'usuari ha respós totes les seccions.
        responses = [
            {"expediture_structure_local_percentatge": 45},
            {"expediture_structure_national_percentatge": 50},
            {"employment_quality_percentatge": 60}
        ]
        result = get_local_expediture_rating(responses)
        self.assertEqual(result["expediture_structure_local_percentatge"]["rating"], 3)
        self.assertEqual(result["expediture_structure_local_percentatge"]["semaphore"], "YELLOW")
        self.assertEqual(result["expediture_structure_national_percentatge"]["rating"], 2)
        self.assertEqual(result["expediture_structure_national_percentatge"]["semaphore"], "ORANGE")
        self.assertEqual(result["employment_quality_percentatge"]["rating"], 4)
        self.assertEqual(result["employment_quality_percentatge"]["semaphore"], "GREEN")

        # C2: l'usuari únicament ha respos les dues primeres seccions.
        responses = [
            {"expediture_structure_local_percentatge": 10},
            {"expediture_structure_national_percentatge": 25}
        ]
        result = get_local_expediture_rating(responses)
        self.assertEqual(result["expediture_structure_local_percentatge"]["rating"], 1)
        self.assertEqual(result["expediture_structure_local_percentatge"]["semaphore"], "RED")
        self.assertEqual(result["expediture_structure_national_percentatge"]["rating"], 1)
        self.assertEqual(result["expediture_structure_national_percentatge"]["semaphore"], "RED")
        self.assertNotIn("employment_quality_percentatge", result)

        # C3: l'usuari únicament ha respós la segona i última secció.
        responses = [
            {"expediture_structure_national_percentatge": 80},
            {"employment_quality_percentatge": 95}
        ]
        result = get_local_expediture_rating(responses)
        self.assertNotIn("expediture_structure_local_percentatge", result)
        self.assertEqual(result["expediture_structure_national_percentatge"]["rating"], 3)
        self.assertEqual(result["expediture_structure_national_percentatge"]["semaphore"], "GREEN")
        self.assertEqual(result["employment_quality_percentatge"]["rating"], 5)
        self.assertEqual(result["employment_quality_percentatge"]["semaphore"], "DGREEN")

        # C4: l'usuari únicament ha respós la primera i l'última secció.
        responses = [
            {"expediture_structure_local_percentatge": 90},
            {"employment_quality_percentatge": 95}
        ]
        result = get_local_expediture_rating(responses)
        self.assertEqual(result["expediture_structure_local_percentatge"]["rating"], 5)
        self.assertEqual(result["expediture_structure_local_percentatge"]["semaphore"], "DGREEN")
        self.assertNotIn("expediture_structure_national_percentatge", result)
        self.assertEqual(result["employment_quality_percentatge"]["rating"], 5)
        self.assertEqual(result["employment_quality_percentatge"]["semaphore"], "DGREEN")

    
    def test_infraestructure_creation(self):
        # Cas 1: No hi ha hagut millora
        responses = [{"infraestructure": False}]
        result = get_infraestructure_creation_rating(responses)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1]["semaphore"], "RED")

        # Cas 2: La millora és pràcticament irrellevant
        responses = [
            {"infraestructure": True},
            {"consultation": False},
            {"benefits-after-close": False},
            {"infraestructures-upgrades": True},
            {"facilities-for-internal-use": False},
            {"instalations-for-benefit": False},
            {"new-local-jobs": False},
            {"facilities-for-basic-services": True},
            {"increment-economy": False},
            {"means-of-communication": False},
            {"maintenance-agreements": False},
            {"quality-of-life": False},
            {"visible-improvements": False},
            {"connectivity-changes": False},
            {"post-mining-use": False},
            {"government-agreements": False},
            {"sustainable-design": False}
        ]
        result = get_infraestructure_creation_rating(responses)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1]["semaphore"], "RED")

        # Cas 3: Hi ha una millora lleugera
        responses = [
            {"infraestructure": True},
            {"consultation": False},
            {"benefits-after-close": False},
            {"infraestructures-upgrades": True},
            {"facilities-for-internal-use": False},
            {"instalations-for-benefit": False},
            {"new-local-jobs": False},
            {"facilities-for-basic-services": True},
            {"increment-economy": False},
            {"means-of-communication": False},
            {"maintenance-agreements": False},
            {"quality-of-life": True},
            {"visible-improvements": False},
            {"connectivity-changes": False},
            {"post-mining-use": True},
            {"government-agreements": False},
            {"sustainable-design": False}
        ]
        result = get_infraestructure_creation_rating(responses)
        self.assertEqual(result[0], 2)
        self.assertEqual(result[1]["semaphore"], "ORANGE")

        # Cas 4: Hi ha una millora moderada
        responses = [
            {"infraestructure": True},
            {"consultation": False},
            {"benefits-after-close": False},
            {"infraestructures-upgrades": True},
            {"facilities-for-internal-use": False},
            {"instalations-for-benefit": False},
            {"new-local-jobs": False},
            {"facilities-for-basic-services": True},
            {"increment-economy": False},
            {"means-of-communication": True},
            {"maintenance-agreements": True},
            {"quality-of-life": True},
            {"visible-improvements": False},
            {"connectivity-changes": False},
            {"post-mining-use": True},
            {"government-agreements": True},
            {"sustainable-design": True}
        ]
        result = get_infraestructure_creation_rating(responses)
        self.assertEqual(result[0], 3)
        self.assertEqual(result[1]["semaphore"], "YELLOW")

        # Cas 5: Hi ha una millora notable però encara hi han aspectes a millorar
        responses = [
            {"infraestructure": True},
            {"consultation": True},
            {"benefits-after-close": False},
            {"infraestructures-upgrades": True},
            {"facilities-for-internal-use": False},
            {"instalations-for-benefit": True},
            {"new-local-jobs": False},
            {"facilities-for-basic-services": True},
            {"increment-economy": False},
            {"means-of-communication": True},
            {"maintenance-agreements": True},
            {"quality-of-life": True},
            {"visible-improvements": True},
            {"connectivity-changes": False},
            {"post-mining-use": True},
            {"government-agreements": True},
            {"sustainable-design": True}
        ]
        result = get_infraestructure_creation_rating(responses)
        self.assertEqual(result[0], 4)
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # Cas 6: Hi ha una gran millora visible
        responses = [
            {"infraestructure": True},
            {"consultation": True},
            {"benefits-after-close": True},
            {"infraestructures-upgrades": True},
            {"facilities-for-internal-use": False},
            {"instalations-for-benefit": True},
            {"new-local-jobs": True},
            {"facilities-for-basic-services": True},
            {"increment-economy": True},
            {"means-of-communication": True},
            {"maintenance-agreements": True},
            {"quality-of-life": True},
            {"visible-improvements": True},
            {"connectivity-changes": True},
            {"post-mining-use": True},
            {"government-agreements": True},
            {"sustainable-design": True}
        ]
        result = get_infraestructure_creation_rating(responses)
        self.assertEqual(result[0], 5)
        self.assertEqual(result[1]["semaphore"], "DGREEN")

    def test_value_chain_rating(self):
        # TEST MASSIU: Tipus de producte i valor afegit
        responses_and_index = {
            "Producte refinat mínim, encara requereix processos addicionals. Procés fet a la mateixa regió o país.": (1, "RED"),
            "Producte final processat al país, però lluny de la mina, sense paper estratègic clar.": (2, "ORANGE"),
            "Producte final processat al país, lluny de la mina, i clau per al desenvolupament industrial nacional o supranacional.": (3, "YELLOW"),
            "Producte final processat a la mateixa regió de la mina, i clau per al desenvolupament industrial nacional o supranacional.": (4, "GREEN"),
            "Producte processat a la regió i essencial per al desenvolupament sostenible de la societat.": (5, "DGREEN")
        }
        for response, output in responses_and_index.items():
            responses = [{"type_of_product": response}]
            result = get_value_chain_rating(responses)
            self.assertEqual(result["type_of_product"]["rating"], output[0])
            self.assertEqual(result["type_of_product"]["semaphore"], output[1])

        # TEST MASSIU: Cadena de Valor
        total = 12500 # euros
        pctgs = {
            (1, "RED"): [0.25, 1, 5.5, 10, 19.5],
            (2, "ORANGE"): [21.2, 25.5, 30, 31, 35.75],
            (3, "YELLOW"): [41, 46.7, 50, 52.2, 59.9],
            (4, "GREEN"): [61, 62.5, 71.5, 79.99, 79.99],
            (5, "DGREEN"): [80.65, 83, 90, 100, 130] 
        }
        # Funció anònima que càlcula l'inversió total a partir d'un percentatge desitjar i el total de pressupost.
        # p: percentatge inversió I&D; t: total de pressupost. 
        ti = lambda p, t: (p * t)/100
        for index, lp in pctgs.items():
            for p in lp:
                inversions = ti(p, total)
                i1 = i2 = inversions / 2
                responses = [{"r_and_d": {"r_and_d_1": total, "r_and_d_2": i1, "r_and_d_3": i2}}]
                result = get_value_chain_rating(responses)
                self.assertEqual(result["r_and_d"]["rating"], index[0])
                self.assertEqual(result["r_and_d"]["semaphore"], index[1])

        # Combinacions i Excepcions:
        # C1: 60% s'inversió I+D + Tipus de producte amb valor màxim (5) 
        responses = [{"r_and_d": {"r_and_d_1": 4000, "r_and_d_2": 1400, "r_and_d_3": 1000}}, {"type_of_product": "Producte processat a la regió i essencial per al desenvolupament sostenible de la societat."}]
        result = get_value_chain_rating(responses)
        self.assertEqual(result["type_of_product"]["rating"], 5)
        self.assertEqual(result["type_of_product"]["semaphore"], "DGREEN")

        # C2: Tipus de producte amb valor 2 + Pressupost I&D sense inversió
        responses = [{"type_of_product": "Producte final processat al país, però lluny de la mina, sense paper estratègic clar."}, {"r_and_d": {"r_and_d_1": 1000, "r_and_d_2": 0, "r_and_d_3": 0}}]
        result = get_value_chain_rating(responses)
        self.assertEqual(result["type_of_product"]["rating"], 2)
        self.assertEqual(result["type_of_product"]["semaphore"], "ORANGE")
        self.assertNotIn("r_and_d", result)

        # C3: I+D amb 0 de pressupost → ha de retornar False
        responses = [{"r_and_d": {"r_and_d_1": 0, "r_and_d_2": 1000, "r_and_d_3": 1000}}]
        result = get_value_chain_rating(responses)
        self.assertFalse(result)

        # C4: Tot a 0 → ha de retornar False
        responses = [{"r_and_d": {"r_and_d_1": 0, "r_and_d_2": 0, "r_and_d_3": 0}}]
        result = get_value_chain_rating(responses)
        self.assertFalse(result)

        # C5: Amb pressupost pero sense inversió → ha de retornar False
        responses = [{"r_and_d": {"r_and_d_1": 34593.54, "r_and_d_2": 0, "r_and_d_3": 0}}]
        result = get_value_chain_rating(responses)
        self.assertFalse(result)

        # C6: I+D amb >100% d’inversió → ha de donar rating 5 amb advertència
        responses = [{"r_and_d": {"r_and_d_1": 1000, "r_and_d_2": 4000, "r_and_d_3": 2000}}]
        result = get_value_chain_rating(responses)
        self.assertEqual(result["r_and_d"]["rating"], 5)
        self.assertEqual(result["r_and_d"]["semaphore"], "DGREEN")
        self.assertIn("**Valor irreal", result["r_and_d"]["sentence"])

    def test_economic_disturbance(self):
        # TEST MASSIU:
        # T1: Impacte petit. Families afectades és > al 25% de l'ocupació local. Afectació parcial i només durant la vida de la mina. 
        values = [(5, 30), (100, 2000), (100, 500)] # 16,6%, 5% i 20%
        for value in values:
            responses = [
                {"families_vs_jobs": {"families_vs_jobs_1": value[0], "families_vs_jobs_2": value[1]}},  
                {"full-impact": "Afecta només una part"},
                {"long-term-impact": "Només durant la vida útil de la mina"}
            ]
            result = get_rating_economic_disturbance(responses)
            self.assertEqual(result[0], -2)
            self.assertEqual(result[1]["semaphore"], "YELLOW")

        # T2: Impacte mitja. Menys del 25% però afecta de forma completa.
        values = [(5, 30), (100, 2000), (100, 500)] # 16,6%, 5% i 20%
        for value in values:
            responses = [
                {"families_vs_jobs": {"families_vs_jobs_1": value[0], "families_vs_jobs_2": value[1]}},  
                {"full-impact": "Afecta tota la comunitat"},
                {"long-term-impact": "Només durant la vida útil de la mina"}
            ]
            result = get_rating_economic_disturbance(responses)
            self.assertEqual(result[0], -3)
            self.assertEqual(result[1]["semaphore"], "ORANGE")
        
        # T3: Impacte mitjà. Afecta entre el 25-50% però parcialment.
        values = [(12, 40), (10, 40), (10, 20)] # 30%, 25%, 50% 
        for value in values:
            responses = [
                {"families_vs_jobs": {"families_vs_jobs_1": value[0], "families_vs_jobs_2": value[1]}},  
                {"full-impact": "Afecta només una part"},
                {"long-term-impact": "Només durant la vida útil de la mina"}
            ]
            result = get_rating_economic_disturbance(responses)
            self.assertEqual(result[0], -3)
            self.assertEqual(result[1]["semaphore"], "ORANGE")

        # T4: Impacte gran, entre 25–50% i afecta totalment.
        values = [(12, 40), (10, 40), (10, 20)] # 30%, 25%, 50% 
        for value in values:
            responses = [
                {"families_vs_jobs": {"families_vs_jobs_1": value[0], "families_vs_jobs_2": value[1]}},  
                {"full-impact": "Afecta tota la comunitat"},
                {"long-term-impact": "Només durant la vida útil de la mina"}
            ]
            result = get_rating_economic_disturbance(responses)
            self.assertEqual(result[0], -4)
            self.assertEqual(result[1]["semaphore"], "RED")

        # T5: Impacte molt gran, +25% i a llarg termini
        values = [
            (13, 50),   # 26%
            (15, 50),   # 30%
            (20, 50),   # 40%
            (25, 50),   # 50%
            (30, 50),   # 60%
            (40, 50),   # 80%
            (45, 50),   # 90%
            (50, 50),   # 100%
            (60, 60),   # 100%
            (100, 100), # 100%
        ]
        for value in values:
            responses = [
                {"families_vs_jobs": {"families_vs_jobs_1": value[0], "families_vs_jobs_2": value[1]}},  
                {"full-impact": "Afecta tota la comunitat"},
                {"long-term-impact": "Tant durant com després del tancament"}
            ]
            result = get_rating_economic_disturbance(responses)
            self.assertEqual(result[0], -5)
            self.assertEqual(result[1]["semaphore"], "DRED")

        # EXCEPCIONS
        # E1-1: Incomplet
        responses = [{"families_vs_jobs": {"families_vs_jobs_1": 200, "families_vs_jobs_2": 10}}]
        result = get_rating_economic_disturbance(responses)
        self.assertFalse(result)
        # E1-2: Incomplet. 
        responses = [{"families_vs_jobs": {"families_vs_jobs_1": 100, "families_vs_jobs_2": 0}}, {"full-impact": "Afecta tota la comunitat"}]
        result = get_rating_economic_disturbance(responses)
        self.assertFalse(result)
        
        # E2: No hi ha famílies afectades. No penalitza.
        responses = [
                        {"families_vs_jobs": {"families_vs_jobs_1": 0, "families_vs_jobs_2": 10}},  
                        {"full-impact": "Afecta només una part"}, 
                        {"long-term-impact": "Només durant la vida útil de la mina"}
                    ]
        result = get_rating_economic_disturbance(responses)
        self.assertFalse(result)

        # E3: Families afectades però no s'ha generat cap ocupació i a més afecta parcialment de forma temporal.
        responses = [{"families_vs_jobs": {"families_vs_jobs_1": 100, "families_vs_jobs_2": 0}}, {"full-impact": "Afecta només una part"},
            {"long-term-impact": "Només durant la vida útil de la mina"}]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -2)
        self.assertEqual(result[1]["semaphore"], "YELLOW")

        # E4: Families afectades però no s'ha generat cap ocupació i a més afecta a tota la comunitat.
        responses = [{"families_vs_jobs": {"families_vs_jobs_1": 100, "families_vs_jobs_2": 0}}, {"full-impact": "Afecta tota la comunitat"},
            {"long-term-impact": "Només durant la vida útil de la mina"}]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -3)
        self.assertEqual(result[1]["semaphore"], "ORANGE")

        # E5: Families afectades però no s'ha generat cap ocupació, afecta a tota la comunitat i a llarg termini.
        responses = [{"families_vs_jobs": {"families_vs_jobs_1": 100, "families_vs_jobs_2": 0}}, {"full-impact": "Afecta tota la comunitat"},
            {"long-term-impact": "Tant durant com després del tancament"}]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # E6: Families afectades però no s'ha generat cap ocupació, afecta a tota la comunitat i no se sap quant temps afectará. 
        responses = [{"families_vs_jobs": {"families_vs_jobs_1": 100, "families_vs_jobs_2": 0}}, {"full-impact": "Afecta tota la comunitat"},
            {"long-term-impact": "No se sap"}]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # E7: No hi ha impacte (resposta explícita)
        responses = [{"full-impact": "No afecta"}]
        result = get_rating_economic_disturbance(responses)
        self.assertFalse(result)

        # CASOS LÍMIT
        
        # CL1: exactament 25%, parcial i només durant la mina
        responses = [
            {"families_vs_jobs": {"families_vs_jobs_1": 5, "families_vs_jobs_2": 20}},  # 25%
            {"full-impact": "Afecta només una part"},
            {"long-term-impact": "Només durant la vida útil de la mina"}
        ]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -3)
        self.assertEqual(result[1]["semaphore"], "ORANGE")

        # CL2: exactament 50%, total i només durant la mina
        responses = [
            {"families_vs_jobs": {"families_vs_jobs_1": 10, "families_vs_jobs_2": 20}},  # 50%
            {"full-impact": "Afecta tota la comunitat"},
            {"long-term-impact": "Només durant la vida útil de la mina"}
        ]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -4)
        self.assertEqual(result[1]["semaphore"], "RED")

        # CL3: +50% però afectació parcial
        responses = [
            {"families_vs_jobs": {"families_vs_jobs_1": 60, "families_vs_jobs_2": 100}},  # 60%
            {"full-impact": "Afecta només una part"},
            {"long-term-impact": "Només durant la vida útil de la mina"}
        ]
        result = get_rating_economic_disturbance(responses)
        self.assertEqual(result[0], -4)
        self.assertEqual(result[1]["semaphore"], "RED")


    def test_additional_involvement_rating(self):
        # Cas 1: Només una afirmativa → ha de retornar 1
        responses = [
            {"economic-participation": False},
            {"acquiring-shares": False},
            {"program-environment-control": False},
            {"heritage-protection": False},
            {"decisions-comunity": True},  # únic True
            {"emergency-assistence": False},
            {"employers-volunteer": False},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1]["semaphore"], "RED")

        # Cas 2: Participació parcial (2 de 7 afirmatives)
        responses = [
            {"economic-participation": True},
            {"acquiring-shares": False},
            {"program-environment-control": False},
            {"heritage-protection": False},
            {"decisions-comunity": False},
            {"emergency-assistence": False},
            {"employers-volunteer": True},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertEqual(result[0], 2)
        self.assertEqual(result[1]["semaphore"], "ORANGE")

        # Cas 3: Només 3 afirmarives → ha de retornar 3
        responses = [
            {"economic-participation": False},
            {"acquiring-shares": True},
            {"program-environment-control": True},
            {"heritage-protection": False},
            {"decisions-comunity": True},  
            {"emergency-assistence": False},
            {"employers-volunteer": False},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertEqual(result[0], 3)
        self.assertEqual(result[1]["semaphore"], "YELLOW")

        # Cas 4: Només 3 afirmatives + 1 extra → ha de retornar 4
        responses = [
            {"economic-participation": False},
            {"acquiring-shares": True},
            {"program-environment-control": True},
            {"heritage-protection": False},
            {"decisions-comunity": True},  
            {"emergency-assistence": False},
            {"employers-volunteer": False},
            {"additional-others": 1},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertEqual(result[0], 4)
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # Cas 5: Participació completa (7 de 7 afirmatives)
        responses = [
            {"economic-participation": True},
            {"acquiring-shares": True},
            {"program-environment-control": True},
            {"heritage-protection": True},
            {"decisions-comunity": True},
            {"emergency-assistence": True},
            {"employers-volunteer": True},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertEqual(result[0], 5)
        self.assertEqual(result[1]["semaphore"], "DGREEN")

        # Cas 6: Sense participació
        responses = [
            {"economic-participation": False},
            {"acquiring-shares": False},
            {"program-environment-control": False},
            {"heritage-protection": False},
            {"decisions-comunity": False},
            {"emergency-assistence": False},
            {"employers-volunteer": False},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertFalse(result)

        # Cas 7: Només 3 afirmatives + 6 extra → ha de retornar 5
        responses = [
            {"economic-participation": False},
            {"acquiring-shares": True},
            {"program-environment-control": True},
            {"heritage-protection": False},
            {"decisions-comunity": True},  
            {"emergency-assistence": False},
            {"employers-volunteer": False},
            {"additional-others": 6},
        ]
        result = get_additional_involvement_rating(responses)
        self.assertEqual(result[0], 5)
        self.assertEqual(result[1]["semaphore"], "DGREEN")

    def test_closure_process_rating(self):
        # Cas 1: Valor afegit a llarg termini lleu
        responses = [
            {
                "added_value_final_conditions": {
                    "added_value_final_conditions_1": "Infraestructura per energies renovables.",
                    "added_value_final_conditions_2": "Greu impacte ambiental",
                    "added_value_final_conditions_3": True,
                    "added_value_final_conditions_4": False,
                    "added_value_final_conditions_5": False,
                    "added_value_final_conditions_6": False,
                    "added_value_final_conditions_7": False,
                    "added_value_final_conditions_8": False,
                    "added_value_final_conditions_9": False,
                    "added_value_final_conditions_10": False,
                    "added_value_final_conditions_11": False
                }
            },
        ]
        result = get_closure_process_rating(responses)
        self.assertEqual(result[0], 1) 
        self.assertEqual(result[1]["semaphore"], "RED")

        # Cas 2: Valor afegit a llarg termini moderat
        responses = [
            {"added_value_final_conditions_info": "Contaminació del sòl i l'aigua present."},
            {
                "added_value_final_conditions": {
                    "added_value_final_conditions_1": "Altres usos econòmics o socials",
                    "added_value_final_conditions_2": "Pèrdua d'ocupació massiva a la regió",
                    "added_value_final_conditions_3": False,
                    "added_value_final_conditions_4": False,
                    "added_value_final_conditions_5": False,
                    "added_value_final_conditions_6": True,
                    "added_value_final_conditions_7": False,
                    "added_value_final_conditions_8": True,
                    "added_value_final_conditions_9": True,
                    "added_value_final_conditions_10": False,
                    "added_value_final_conditions_11": True
                }
            },
        ]

        result = get_closure_process_rating(responses)
        self.assertEqual(result[0], 2)  
        self.assertEqual(result[1]["semaphore"], "ORANGE")

        # Cas 3: Valor afegit a llarg termini alt
        responses = [
            {
                "added_value_final_conditions": {
                    "added_value_final_conditions_1": "Altres usos econòmics o socials",
                    "added_value_final_conditions_2": "Pèrdua d'ocupació massiva a la regió",
                    "added_value_final_conditions_3": True,
                    "added_value_final_conditions_4": True,
                    "added_value_final_conditions_5": True,
                    "added_value_final_conditions_6": True,
                    "added_value_final_conditions_7": False,
                    "added_value_final_conditions_8": True,
                    "added_value_final_conditions_9": False,
                    "added_value_final_conditions_10": False,
                    "added_value_final_conditions_11": True
                }
            },
        ]
        result = get_closure_process_rating(responses)
        self.assertEqual(result[0], 3)  
        self.assertEqual(result[1]["semaphore"], "YELLOW")

        # Cas 4: Valor afegit a llarg termini alt, amb una sinergia parcial amb el context social, econòmic i ambiental específic
        responses = [
            {
                "added_value_final_conditions": {
                    "added_value_final_conditions_1": "Agricultura o ramaderia.",
                    "added_value_final_conditions_2": "Pocs impactes negatius significatius",
                    "added_value_final_conditions_3": True,
                    "added_value_final_conditions_4": True,
                    "added_value_final_conditions_5": True,
                    "added_value_final_conditions_6": True,
                    "added_value_final_conditions_7": False,
                    "added_value_final_conditions_8": True,
                    "added_value_final_conditions_9": False,
                    "added_value_final_conditions_10": False,
                    "added_value_final_conditions_11": True
                }
            },
        ]
        result = get_closure_process_rating(responses)
        self.assertEqual(result[0], 4)  
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # Cas 5: Valor afegit a llarg termini alt, amb una sinergia important amb el context social, econòmic i ambiental específic
        responses = [
            {"added_value_final_conditions_info": "Degradació de la biodiversitat i ecosistemes."},
            {
                "added_value_final_conditions": {
                    "added_value_final_conditions_1": "Àrea protegida per conservació.",
                    "added_value_final_conditions_2": "Pocs impactes negatius significatius",
                    "added_value_final_conditions_3": True,
                    "added_value_final_conditions_4": True,
                    "added_value_final_conditions_5": True,
                    "added_value_final_conditions_6": True,
                    "added_value_final_conditions_7": True,
                    "added_value_final_conditions_8": True,
                    "added_value_final_conditions_9": True,
                    "added_value_final_conditions_10": True,
                    "added_value_final_conditions_11": True
                }
            },
        ]
        result = get_closure_process_rating(responses)
        self.assertEqual(result[0], 5)  
        self.assertEqual(result[1]["semaphore"], "DGREEN")   

        # Cas 6: Incomplet. 
        responses = [
            {
                "added_value_final_conditions": {
                    "added_value_final_conditions_1": "Infraestructura per energies renovables.",
                    "added_value_final_conditions_3": True,
                    "added_value_final_conditions_4": False,
                    "added_value_final_conditions_5": False,
                    "added_value_final_conditions_6": False,
                    "added_value_final_conditions_7": False,
                    "added_value_final_conditions_8": False,
                    "added_value_final_conditions_9": False,
                    "added_value_final_conditions_10": False,
                    "added_value_final_conditions_11": False
                }
            },
        ]
        result = get_closure_process_rating(responses)
        self.assertEqual(result, False)


# TEST CÀLCULS DIMENSIÓ AMBIENTAL
class EnvironmentTestCase(TestCase):
    def test_energy_rating(self):
        # TEST MASSIU: 
        # - Tècniques energètiques eficients.
        # - Energia renovable instal·lada.
        # - Maquinària electrificada.

        test_for_index_1, s1 = [0, 1.5, 3, 4.8, 6, 7.2, 10, 12.5, 15, 17.3, 19, 19.99], "RED"
        test_for_index_2, s2 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39, 39.99], "ORANGE"
        test_for_index_3, s3 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59, 59.99], "YELLOW"
        test_for_index_4, s4 = [60, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 79.99], "GREEN"
        test_for_index_5, s5 = [81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "DGREEN"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{"ghg_reduction": t}, {"green_energy_sources": t}, {"green_energy_fleet": t}]
                result = get_energy_rating(responses)
                self.assertEqual(result["ghg_reduction"]["rating"], test["index"])
                self.assertEqual(result["green_energy_sources"]["rating"], test["index"])
                self.assertEqual(result["green_energy_fleet"]["rating"], test["index"])
                self.assertEqual(result["ghg_reduction"]["semaphore"], test["color"])
                self.assertEqual(result["green_energy_sources"]["semaphore"], test["color"])
                self.assertEqual(result["green_energy_fleet"]["semaphore"], test["color"])

        # Combinacions
        # C1: 
        responses = [{"ghg_reduction": 25}, {"green_energy_sources": 80}]
        result = get_energy_rating(responses)
        self.assertEqual(result["ghg_reduction"]["rating"], 2)
        self.assertEqual(result["green_energy_sources"]["rating"], 5)
        self.assertNotIn("green_energy_fleet", result)
        self.assertEqual(result["ghg_reduction"]["semaphore"], "ORANGE")
        self.assertEqual(result["green_energy_sources"]["semaphore"], "DGREEN")
        # C2: 
        responses = [{"ghg_reduction": 25}, {"green_energy_fleet": 80}]
        result = get_energy_rating(responses)
        self.assertEqual(result["ghg_reduction"]["rating"], 2)
        self.assertEqual(result["green_energy_fleet"]["rating"], 5)
        self.assertNotIn("green_energy_sources", result)
        self.assertEqual(result["ghg_reduction"]["semaphore"], "ORANGE")
        self.assertEqual(result["green_energy_fleet"]["semaphore"], "DGREEN")
        # C3: 
        responses = [{"green_energy_fleet": 25}, {"green_energy_sources": 80}]
        result = get_energy_rating(responses)
        self.assertEqual(result["green_energy_fleet"]["rating"], 2)
        self.assertEqual(result["green_energy_sources"]["rating"], 5)
        self.assertNotIn("ghg_reduction", result)
        self.assertEqual(result["green_energy_fleet"]["semaphore"], "ORANGE")
        self.assertEqual(result["green_energy_sources"]["semaphore"], "DGREEN")
        # C4:
        responses = [{"green_energy_fleet": 25}]
        result = get_energy_rating(responses)
        self.assertEqual(result["green_energy_fleet"]["rating"], 2)
        self.assertNotIn("green_energy_sources", result)
        self.assertNotIn("ghg_reduction", result)
        self.assertEqual(result["green_energy_fleet"]["semaphore"], "ORANGE")
        # C5: 
        responses = [{"green_energy_sources": 25}]
        result = get_energy_rating(responses)
        self.assertEqual(result["green_energy_sources"]["rating"], 2)
        self.assertNotIn("green_energy_fleet", result)
        self.assertNotIn("ghg_reduction", result)
        self.assertEqual(result["green_energy_sources"]["semaphore"], "ORANGE")
        # C6: 
        responses = [{"ghg_reduction": 25}]
        result = get_energy_rating(responses)
        self.assertEqual(result["ghg_reduction"]["rating"], 2)
        self.assertNotIn("green_energy_sources", result)
        self.assertNotIn("green_energy_fleet", result)
        self.assertEqual(result["ghg_reduction"]["semaphore"], "ORANGE")
    
    def test_tailing_rating(self):
        # TEST MASSIU: Recuperabilitat dels minerals en els residus de la mina.
        responses_price_increase = {
            "8-10 vegades més alt": (1, "RED"),
            "6-8 vegades més alt": (2, "ORANGE"),
            "4-6 vegades més alt": (3, "YELLOW"),
            "2-4 vegades més alt": (4, "GREEN"),
            "Fins a 2 vegades més alt":  (5, "DGREEN")
        }
        for response, output in responses_price_increase.items():
            responses = [{"price_increase": response}]
            result = get_tailings_rating(responses)
            self.assertEqual(result["price_increase"]["rating"], output[0])
            self.assertEqual(result["price_increase"]["semaphore"], output[1])

        # TEST MASSIU: Reutilització dels residus com a material de construcció o farciment.
        test_for_index_1, s1 = [0, 1.5, 3, 4.8, 6, 7.2, 9.99], "RED"
        test_for_index_2, s2 = [10, 11.5, 13.4, 15, 19.99], "ORANGE"
        test_for_index_3, s3 = [20, 21.2, 22, 25, 29.99, 34, 34.99], "YELLOW"
        test_for_index_4, s4 = [35, 36.5, 37, 38.6, 40, 49.99], "GREEN"
        test_for_index_5, s5 = [50, 51.2, 60, 75, 81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "DGREEN"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{"other_tailing_usage": t}]
                result = get_tailings_rating(responses)
                self.assertEqual(result["other_tailing_usage"]["rating"], test["index"])
                self.assertEqual(result["other_tailing_usage"]["semaphore"], test["color"])

        
        # TEST MASSIU: Recuperació d’aigua dels residus de la mina.
        test_for_index_1, s1 = [0, 1.5, 3, 4.8, 6, 7.2, 9.99, 10, 11.5, 13.4, 15, 19.99], "RED"
        test_for_index_2, s2 = [20, 21.2, 22, 25, 29.99, 34, 34.99, 39.99], "ORANGE"
        test_for_index_3, s3 = [40, 46.5, 47, 48.6, 50, 59.99], "YELLOW"
        test_for_index_4, s4 = [60, 61.2, 65, 70, 75.5, 79.99], "GREEN"
        test_for_index_5, s5 = [80, 81.2, 90, 99, 99.99, 100], "DGREEN"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{"water_recovery_from_tailings": t}]
                result = get_tailings_rating(responses)
                self.assertEqual(result["water_recovery_from_tailings"]["rating"], test["index"])
                self.assertEqual(result["water_recovery_from_tailings"]["semaphore"], test["color"])
    
        # Combinacions
        # C1:
        responses = [{"price_increase": "4-6 vegades més alt"}, {"other_tailing_usage": 30}]
        result = get_tailings_rating(responses)
        self.assertEqual(result["price_increase"]["rating"], 3)
        self.assertEqual(result["other_tailing_usage"]["rating"], 3)
        self.assertNotIn("water_recovery_from_tailings", result)
        self.assertEqual(result["price_increase"]["semaphore"], "YELLOW")
        self.assertEqual(result["other_tailing_usage"]["semaphore"], "YELLOW")
        # C2:
        responses = [{"other_tailing_usage": 90}, {"water_recovery_from_tailings": 90}]
        result = get_tailings_rating(responses)
        self.assertNotIn("price_increase", result)
        self.assertEqual(result["other_tailing_usage"]["rating"], 5)
        self.assertEqual(result["water_recovery_from_tailings"]["rating"], 5)
        self.assertEqual(result["other_tailing_usage"]["semaphore"], "DGREEN")
        self.assertEqual(result["water_recovery_from_tailings"]["semaphore"], "DGREEN")
        # C3:
        responses = [{"price_increase": "2-4 vegades més alt"}, {"water_recovery_from_tailings": 85}]
        result = get_tailings_rating(responses)
        self.assertEqual(result["price_increase"]["rating"], 4)
        self.assertEqual(result["price_increase"]["semaphore"], "GREEN")
        self.assertEqual(result["water_recovery_from_tailings"]["rating"], 5)
        self.assertEqual(result["water_recovery_from_tailings"]["semaphore"], "DGREEN")
        self.assertNotIn("other_tailing_usage", result)

    def test_waste_rating(self):
        # TEST MASSIU:
        mean_industry_waste = 81.25 # Percentatge mitjà de residus generats en la industria.
        mine_waste = lambda p, m: ((p*m)/100) + m

        test_for_index_1, s1, s1i = [1.5, 3, 4.8, 6, 7.2, 9.99, 10, 11.5, 13.4, 15, 19.99], "RED", "GREEN" 
        test_for_index_2, s2, s2i = [20, 21.2, 22, 25, 29.99, 34, 34.99, 39.99], "ORANGE", "YELLOW"
        test_for_index_3, s3, s3i = [40, 46.5, 47, 48.6, 50, 59.99], "YELLOW", "ORANGE"
        test_for_index_4, s4, s4i = [60, 61.2, 65, 70, 75.5, 79.99], "GREEN", "RED"
        test_for_index_5, s5, s5i = [80, 81.2, 90, 99, 99.99, 100], "DGREEN", "DRED"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1, "color_i": s1i},
            {"testers": test_for_index_2, "index": 2, "color": s2, "color_i": s2i},
            {"testers": test_for_index_3, "index": 3, "color": s3, "color_i": s3i},
            {"testers": test_for_index_4, "index": 4, "color": s4, "color_i": s4i},
            {"testers": test_for_index_5, "index": 5, "color": s5, "color_i": s5i},
        ]

        for test in testers:
            for t in test["testers"]:
                wr2 = mean_industry_waste
                # Reducció de residus
                wr1 = mine_waste(-t, mean_industry_waste)
                responses =  [{"waste_ratio": {"waste_ratio_1": wr1, "waste_ratio_2": wr2}}]
                result = get_waste_rating(responses)
                self.assertEqual(result[0]["lower_waste_ratio"]["rating"], test["index"])
                self.assertEqual(result[0]["lower_waste_ratio"]["semaphore"], test["color"])
                # Excés de residus
                wr1 = mine_waste(t, mean_industry_waste)
                responses =  [{"waste_ratio": {"waste_ratio_1": wr1, "waste_ratio_2": wr2}}]
                result = get_waste_rating(responses)
                self.assertEqual(result[0]["higher_waste_ratio"]["rating"], -test["index"])
                self.assertEqual(result[0]["higher_waste_ratio"]["semaphore"], test["color_i"])
                # Proporció de residus reutilitzats com a farciment o material de construcció.
                responses =  [{"waste_reuse": t}]
                result = get_waste_rating(responses)
                self.assertEqual(result[0]["waste_reuse"]["rating"], test["index"])
                self.assertEqual(result[0]["waste_reuse"]["semaphore"], test["color"])

        # COMBINACIONS I EXCEPCIONS:

        # C1: reducció de residus del 33,33% i reutilització del 20% dels residus
        responses = [{"waste_ratio": {"waste_ratio_1": 20, "waste_ratio_2": 30}}, {"waste_reuse": 20}]
        result = get_waste_rating(responses)
        self.assertEqual(result[0]["lower_waste_ratio"]["rating"], 2) 
        self.assertEqual(result[0]["lower_waste_ratio"]["semaphore"], "ORANGE")
        self.assertEqual(result[0]["waste_reuse"]["rating"], 2)
        self.assertEqual(result[0]["waste_reuse"]["semaphore"], "ORANGE")     

        # C2: increment del 17,48% i reutilització del 41.23% dels residus
        responses = [{"waste_ratio": {"waste_ratio_1": 45.7, "waste_ratio_2": 38.9}}, {"waste_reuse": 41.23}]
        result = get_waste_rating(responses)
        self.assertEqual(result[0]["higher_waste_ratio"]["rating"], -1)
        self.assertEqual(result[0]["higher_waste_ratio"]["semaphore"], "GREEN")
        self.assertEqual(result[0]["waste_reuse"]["rating"], 3)
        self.assertEqual(result[0]["waste_reuse"]["semaphore"], "YELLOW")

        # E1: no hi ha reducció ni increment. No hi ha penalització ni puntuació positiva.
        responses = [{"waste_ratio": {"waste_ratio_1": 0.1, "waste_ratio_2": 0.1}}]
        result = get_waste_rating(responses)
        self.assertEqual(result, False)

        # E2: s'ha reduit al 100% els residus. 
        responses = [{"waste_ratio": {"waste_ratio_1": 0, "waste_ratio_2": 0.1}}]
        result = get_waste_rating(responses)
        self.assertEqual(result[0]["lower_waste_ratio"]["rating"], 5)
        self.assertEqual(result[0]["lower_waste_ratio"]["semaphore"], "DGREEN")

        # E3: A pasat de no generar residus a generar-los.
        responses = [{"waste_ratio": {"waste_ratio_1": 0.1, "waste_ratio_2": 0}}]
        result = get_waste_rating(responses)
        self.assertEqual(result[0]["higher_waste_ratio"]["rating"], -5)
        self.assertEqual(result[0]["higher_waste_ratio"]["semaphore"], "DRED")


    def test_water_rating(self):
        # TEST MASSIU: Variació de la qualitat de l'aigua

        # Concentració abans de l'explotació (mg/L)
        wqv1 = 120
        wqv2 = lambda p, b: ((p*b)/100) + b

        test_for_index_1, s1 = [1.5, 3, 4.8, 6, 7.2, 9.99], "GREEN" 
        test_for_index_2, s2 = [10, 11.5, 13.4, 15, 19.99], "YELLOW"
        test_for_index_3, s3 = [20, 21.2, 22, 25, 29.99], "ORANGE"
        test_for_index_4, s4 = [30, 35.6, 41, 60, 61.2, 65, 70, 75.5, 79.99, 80, 81.2, 90, 99, 99.99, 100], "RED"

        testers = [
            {"testers": test_for_index_1, "index": -1, "color": s1},
            {"testers": test_for_index_2, "index": -2, "color": s2},
            {"testers": test_for_index_3, "index": -3, "color": s3},
            {"testers": test_for_index_4, "index": -4, "color": s4},
        ]

        for test in testers:
            for t in test["testers"]:
                # La concentració de contaminants ha incrementat
                w2 = wqv2(t, wqv1)
                responses =  [{"water_quality_variation": {"water_quality_variation_1": wqv1, "water_quality_variation_2": w2}}]
                result = get_water_rating(responses)
                self.assertEqual(result["water_quality_variation"]["rating"], test["index"])
                self.assertEqual(result["water_quality_variation"]["semaphore"], test["color"])
                # La concentració de contaminants s'ha reduit.
                w2 = wqv2(-t, wqv1)
                responses =  [{"water_quality_variation": {"water_quality_variation_1": wqv1, "water_quality_variation_2": w2}}]
                result = get_water_rating(responses)
                self.assertEqual(result["water_quality_variation"]["rating"], test["index"])
                self.assertEqual(result["water_quality_variation"]["semaphore"], test["color"])

        # EXCEPCIONS:
        # E1: No hi ha variació de l'aigua. No penalitza. 
        responses = [{"water_quality_variation": {"water_quality_variation_1": 100, "water_quality_variation_2": 100}}]
        result = get_water_rating(responses)
        self.assertEqual(result, False) 
        # E2: A pasat de no tenir contaminants a tenir-ne. 
        responses = [{"water_quality_variation": {"water_quality_variation_1": 0, "water_quality_variation_2": 100}}]
        result = get_water_rating(responses)
        self.assertEqual(result["water_quality_variation"]["rating"], -4)
        self.assertEqual(result["water_quality_variation"]["semaphore"], "RED")
        # E3: Pasa de tenir-ne a no tenir. Segons l'article, qualsevol variació representa un impacte negatiu.
        responses = [{"water_quality_variation": {"water_quality_variation_1": 100, "water_quality_variation_2": 0}}]
        result = get_water_rating(responses)
        self.assertEqual(result["water_quality_variation"]["rating"], -4)
        self.assertEqual(result["water_quality_variation"]["semaphore"], "RED")

        # TEST MASSIU: Reutilització de l’aigua. 
        test_for_index_1, s1 = [1.5, 3, 4.8, 6, 7.2, 9.99, 10, 11.5, 13.4, 15, 19.99], "RED"
        test_for_index_2, s2 = [20, 21.2, 22, 25, 29.99, 34, 34.99, 39.99], "ORANGE"
        test_for_index_3, s3 = [40, 46.5, 47, 48.6, 50, 59.99], "YELLOW"
        test_for_index_4, s4 = [60, 61.2, 65, 70, 75.5, 79.99], "GREEN"
        test_for_index_5, s5 = [80, 81.2, 90, 99, 99.99, 100], "DGREEN"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{"water_reuse": t}]
                result = get_water_rating(responses)
                self.assertEqual(result["water_reuse"]["rating"], test["index"])
                self.assertEqual(result["water_reuse"]["semaphore"], test["color"])

        # TEST MASSIU: Reducció/Increment del cabal d’aigua.
        q1 = 200
        q2_func = lambda p, b: ((p*b)/100) + b

        test_for_index_1, s1 = [60, 61.2, 65, 70, 75.5, 79.99, 80, 81.2, 90, 99, 99.99, 100], "RED"
        test_for_index_2, s2 = [35, 39.99, 40, 46.5, 47, 48.6, 50, 59.99], "ORANGE"
        test_for_index_3, s3 = [20, 21.2, 22, 25, 29.99, 34, 34.99], "YELLOW"
        test_for_index_4, s4 = [10, 11.5, 13.4, 15, 19.99], "GREEN"
        test_for_index_5, s5 = [0, 1.5, 3, 4.8, 6, 7.2, 9.99], "DGREEN"

        testers = [
            {"testers": test_for_index_1, "index": 1, "color": s1},
            {"testers": test_for_index_2, "index": 2, "color": s2},
            {"testers": test_for_index_3, "index": 3, "color": s3},
            {"testers": test_for_index_4, "index": 4, "color": s4},
            {"testers": test_for_index_5, "index": 5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                # La concentració de contaminants ha incrementat
                q2 = q2_func(-t, q1)
                responses =  [{"waterflow_reduction": {"waterflow_reduction_1": q1, "waterflow_reduction_2": q2}}]
                result = get_water_rating(responses)
                self.assertEqual(result["waterflow_reduction"]["rating"], test["index"])
                self.assertEqual(result["waterflow_reduction"]["semaphore"], test["color"])
                # La concentració de contaminants s'ha reduit.
                if t!=0:
                    q2 = q2_func(t, q1)
                    responses =  [{"waterflow_reduction": {"waterflow_reduction_1": q1, "waterflow_reduction_2": q2}}]
                    result = get_water_rating(responses)
                    self.assertEqual(result["waterflow_increment"]["rating"], test["index"])
                    self.assertEqual(result["waterflow_increment"]["semaphore"], test["color"])


        # Combinacions:
        # C1: variació de la qualitat de l'aigua del 7% + reutilització del 40% de l'aigua + reducció del 8% del caudal
        responses = [
                        {"water_quality_variation": {"water_quality_variation_1": 100, "water_quality_variation_2": 107}}, 
                        {"water_reuse": 40}, 
                        {"waterflow_reduction": {"waterflow_reduction_1": 100, "waterflow_reduction_2": 92}}
                    ]
        result = get_water_rating(responses)
        self.assertEqual(result["water_quality_variation"]["rating"], -1)
        self.assertEqual(result["water_quality_variation"]["semaphore"], "GREEN")
        self.assertEqual(result["water_reuse"]["rating"], 3)
        self.assertEqual(result["water_reuse"]["semaphore"], "YELLOW")
        self.assertEqual(result["waterflow_reduction"]["rating"], 5)
        self.assertEqual(result["waterflow_reduction"]["semaphore"], "DGREEN")

        # C2: variació de la qualitat de l'aigua del 15% amb reutilització del 90% de l'aigua 
        responses = [{"water_quality_variation": {"water_quality_variation_1": 80, "water_quality_variation_2": 92}}, {"water_reuse": 90}]
        result = get_water_rating(responses)
        self.assertEqual(result["water_quality_variation"]["rating"], -2)
        self.assertEqual(result["water_quality_variation"]["semaphore"], "YELLOW")
        self.assertEqual(result["water_reuse"]["rating"], 5)
        self.assertEqual(result["water_reuse"]["semaphore"], "DGREEN")
        
        # C3: variació de la qualitat de l'aigua del 25% + reducció del 30% del caudal
        responses = [{"water_quality_variation": {"water_quality_variation_1": 50, "water_quality_variation_2": 62.5}}, {"waterflow_reduction": {"waterflow_reduction_1": 50, "waterflow_reduction_2": 35}}]
        result = get_water_rating(responses)
        self.assertEqual(result["water_quality_variation"]["rating"], -3)
        self.assertEqual(result["water_quality_variation"]["semaphore"], "ORANGE")
        self.assertEqual(result["waterflow_reduction"]["rating"], 3)
        self.assertEqual(result["waterflow_reduction"]["semaphore"], "YELLOW")

    def test_air_rating(self):
        from .rating.calculators.utils.html_content import get_html_table
        def create_content(color, name, value_before, value_after, unit, limit, impacte, rating):
            return [ 
                    color,
                    name,
                    f"{value_before}  <small>({unit})</small>",
                    f"{value_after} <small>({unit})</small>",
                    f"{limit} <small>({unit})</small>",
                    f"{impacte}%",
                    f"-{rating}",
                ]
        
        headers = ["Contaminant", "Valor previ", "Valor mesurat", "Límit admissible", "% Increment relatiu", "Índex"]

        # TEST 1: casos habituals s'empitjora o es manté.
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 40}, {"toxic_2": 20}, {"toxic_3": 75}, {"toxic_6": 51}, {"toxic_7": 51}]},  # PM10, PM2.5, TSP, CO2, O3
            {"toxics_after_explotation": [{"toxic_1": 60}, {"toxic_2": 30}, {"toxic_3": 81.25}, {"toxic_6": 71.58}, {"toxic_7": 51}]},
            {"limit": [{"limit_1": 100}, {"limit_2": 50}, {"limit_3": 150}, {"limit_6": 100}, {"limit_7": 100}]}
        ]

        table = [
            create_content("table-light", "PM10", 40, 60, "µg/m³", 100, 33.33, 2), # Increment del 33,33%
            create_content("table-light", "PM2.5", 20, 30, "µg/m³", 50, 33.33, 2), # Increment del 33,33%
            create_content("table-light", "TSP", 75, 81.25, "µg/m³", 150, 8.33, 1), # Increment del 8,33%
            create_content("table-danger", "CO2", 51, 71.58, "mg/m³", 100, 42.0, 3), # Increment del 42%
            create_content("table-light", "O3", 51, 51, "µg/m³", 100, 0, 1) # Es manté. Increment de 0%
        ]

        result = get_air_rating(responses)
        self.assertEqual(result[1]['messages'], get_html_table(headers, table))
        self.assertEqual(result[0], -3) # Pitjor dels casos.
        self.assertEqual(result[1]["semaphore"], "ORANGE")

        # -----------------------------------------------------------------------------------------------
        # TEST 2: Casos excepcionals on ja es trobava o havia superat el límit.
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 100}, {"toxic_2": 110}]},  # PM10, PM2.5
            {"toxics_after_explotation": [{"toxic_1": 100}, {"toxic_2": 110}]},
            {"limit": [{"limit_1": 100}, {"limit_2": 100}]}
        ]

        table = [
            create_content("table-light", "PM10", 100, 100, "µg/m³", 100, 0, 1), # Es trobava al límit i es manté. El projecte miner no ha empitjorat la situació.
            create_content("table-light", "PM2.5", 110, 110, "µg/m³", 100, 0, 1), # Havia superat el límit però es manté. Mateixa conclusió, la situació no s'ha empitjorat.
        ]

        result = get_air_rating(responses)
        self.maxDiff = None
        self.assertEqual(result[1]['messages'], get_html_table(headers, table))
        self.assertEqual(result[0], -1) 
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # ----------------------------------------------------------------------------------------------------------------------
        # TEST 3: Casos massius i habituals, on la situació empitjora respecte la situació anterior però sense superar el límit.

        responses = [
            {"toxics_before_explotation": [
                {"toxic_1": 40.0}, 
                {"toxic_2": 20.0}, 
                {"toxic_3": 152.0}, 
                {"toxic_4": 151.0},
                {"toxic_5": 130.0},
                {"toxic_6": 150.0},
                {"toxic_7": 95.0},
                {"toxic_8": 0.7},
                {"toxic_9": 0.03},
                {"toxic_10": 0.02},
                {"toxic_11": 1.0},
                {"toxic_12": 0.8},
                {"toxic_13": 10.0},
                {"toxic_14": 0.3}
            ]},
            {"toxics_after_explotation": [
                {"toxic_1": 48.0},
                {"toxic_2": 24.0},
                {"toxic_3": 220.0},
                {"toxic_4": 180.0},
                {"toxic_5": 160.0},
                {"toxic_6": 220.0},
                {"toxic_7": 120.0},
                {"toxic_8": 1.2},
                {"toxic_9": 0.06},
                {"toxic_10": 0.3},
                {"toxic_11": 2.5},
                {"toxic_12": 2.5},
                {"toxic_13": 15.0},
                {"toxic_14": 0.6}
            ]},
            {"limit": [
                {"limit_1": 50.0},
                {"limit_2": 25.0},
                {"limit_3": 250.0},
                {"limit_4": 200.0},
                {"limit_5": 200.0},
                {"limit_6": 300.0},
                {"limit_7": 180.0},
                {"limit_8": 10.0},
                {"limit_9": 0.1},
                {"limit_10": 0.5},
                {"limit_11": 6.0},
                {"limit_12": 5.0},
                {"limit_13": 20.0},
                {"limit_14": 1.0}
            ]}
        ]

        table = [
            create_content("table-danger", "PM10", 40.0, 48.0, "µg/m³", 50.0, 80.0, 5),
            create_content("table-danger", "PM2.5", 20.0, 24.0, "µg/m³", 25.0, 80.0, 5),
            create_content("table-danger", "TSP", 152.0, 220.0, "µg/m³", 250.0, 69.39, 4),
            create_content("table-danger", "NO2", 151.0, 180.0, "µg/m³", 200.0, 59.18, 3),
            create_content("table-danger", "SO2", 130.0, 160.0, "µg/m³", 200.0, 42.86, 3),
            create_content("table-danger", "CO2", 150.0, 220.0, "mg/m³", 300.0, 46.67, 3),
            create_content("table-light", "O3", 95.0, 120.0, "µg/m³", 180.0, 29.41, 2),
            create_content("table-light", "CO", 0.7, 1.2, "mg/m³", 10.0, 5.38, 1),
            create_content("table-danger", "Dioxines", 0.03, 0.06, "ng/Nm³", 0.1, 42.86, 3),
            create_content("table-danger", "Pb", 0.02, 0.3, "µg/m³", 0.5, 58.33, 3),
            create_content("table-light", "As", 1.0, 2.5, "ng/m³", 6.0, 30.0, 2),
            create_content("table-danger", "Cd", 0.8, 2.5, "ng/m³", 5.0, 40.48, 3),
            create_content("table-danger", "Ni", 10.0, 15.0, "ng/m³", 20.0, 50.0, 3),
            create_content("table-danger", "B(a)P", 0.3, 0.6, "ng/m³", 1.0, 42.86, 3),
        ]


        result = get_air_rating(responses)
        self.assertEqual(result[1]['messages'], get_html_table(headers, table))
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # ----------------------------------------------------------------------------------
        # TEST 4: casos expecionals.

        responses = [
            {"toxics_before_explotation": [
                {"toxic_1": 70}, {"toxic_2": 10}, {"toxic_3": 100}, {"toxic_4": 190},
                {"toxic_5": 80}, {"toxic_6": 400}, {"toxic_7": 100}, {"toxic_8": 5},
                {"toxic_9": 0.2}, {"toxic_10": 0.1}, {"toxic_11": 10}, {"toxic_12": 1},
                {"toxic_13": 50}, {"toxic_14": 1.5}
            ]},
            {"toxics_after_explotation": [
                {"toxic_1": 45}, {"toxic_2": 22}, {"toxic_3": 270}, {"toxic_4": 160},
                {"toxic_5": 200}, {"toxic_6": 290}, {"toxic_7": 98}, {"toxic_8": 4},
                {"toxic_9": 0.09}, {"toxic_10": 0.05}, {"toxic_11": 6}, {"toxic_12": 4},
                {"toxic_13": 22}, {"toxic_14": 0.8}
            ]},
            {"limit": [
                {"limit_1": 50.0}, {"limit_2": 25.0}, {"limit_3": 250.0}, {"limit_4": 200.0},
                {"limit_5": 200.0}, {"limit_6": 300.0}, {"limit_7": 180.0}, {"limit_8": 10.0},
                {"limit_9": 0.1}, {"limit_10": 0.5}, {"limit_11": 6.0}, {"limit_12": 5.0},
                {"limit_13": 20.0}, {"limit_14": 1.0}
            ]}
        ]

        table = [
            create_content("table-light", "PM10", 70, 45, "µg/m³", 50.0, 125.0, 1), # Es superaba el límit i ha millorat.
            create_content("table-danger", "PM2.5", 10, 22, "µg/m³", 25.0, 80.0, 5), # La situació ha empitjorat respecte el valor previ.
            create_content("table-danger", "TSP", 100, 270, "µg/m³", 250.0, 113.33, 5), # Igual que el cas anterior, i a més es supera el límit.
            create_content("table-light", "NO2", 190, 160, "µg/m³", 200.0, -300.0, 1), # La situació ha millorat.
            create_content("table-danger", "SO2", 80, 200, "µg/m³", 200.0, 100.0, 5), # Ha empitjorat i està en el límit.
            create_content("table-light", "CO2", 400, 290, "mg/m³", 300.0, 110.0, 1), # Ha millorat.
            create_content("table-light", "O3", 100, 98, "µg/m³", 180.0, -2.5, 1), # Ha millorat.
            create_content("table-light", "CO", 5, 4, "mg/m³", 10.0, -20.0, 1), # Ha millorat.
            create_content("table-light", "Dioxines", 0.2, 0.09, "ng/Nm³", 0.1, 110.0, 1), # Ha millorat
            create_content("table-light", "Pb", 0.1, 0.05, "µg/m³", 0.5, -12.5, 1), # Ha millorat. 
            create_content("table-light", "As", 10, 6, "ng/m³", 6.0, 100.0, 1), # Anteriorment es superaba el límit, ara a millorat.
            create_content("table-danger", "Cd", 1, 4, "ng/m³", 5.0, 75.0, 4), # Ha empitjorat
            create_content("table-light", "Ni", 50, 22, "ng/m³", 20.0, 93.33, 1), # Ha millorat
            create_content("table-light", "B(a)P", 1.5, 0.8, "ng/m³", 1.0, 140.0, 1), # Ha millorat
        ]

        result = get_air_rating(responses)
        self.assertEqual(result[1]['messages'], get_html_table(headers, table))
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # Cas 2: impacte alt 
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 10}]},      # PM10
            {"toxics_after_explotation": [{"toxic_1": 50}]},
            {"limit": [{"limit_1": 40}]}  # marge = 30, increment = 40 → 133.33%
        ]

        result = get_air_rating(responses)
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # Cas 3: sense marge i ha empitjorat
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 40}]},      # PM10
            {"toxics_after_explotation": [{"toxic_1": 60}]},
            {"limit": [{"limit_1": 40}]}  # marge = 0
        ]
        result = get_air_rating(responses)
        self.assertEqual(result[0], -1)
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # Cas 4: cap tòxic supera el 20% (revisar)
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 40}, {"toxic_2": 30}]},
            {"toxics_after_explotation": [{"toxic_1": 44}, {"toxic_2": 32}]},
            {"limit": [{"limit_1": 60}, {"limit_2": 50}]}  # increments del 4 i 2 → variació <10%
        ]
        result = get_air_rating(responses)
        self.assertEqual(result[0], -2)
        self.assertEqual(result[1]["semaphore"], "YELLOW")

        # Cas 5: un amb poc impacte amb altre amb gran impacte
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 40}, {"toxic_2": 10}]},
            {"toxics_after_explotation": [{"toxic_1": 44}, {"toxic_2": 50}]},
            {"limit": [{"limit_1": 80}, {"limit_2": 30}]}  # PM10: variació 6.6% (rating 1), PM2.5: 133% (rating 5)
        ]
        result = get_air_rating(responses)
        self.assertEqual(result[0], -5) # Cas més greu
        self.assertEqual(result[1]["semaphore"], "DRED")

        # Cas 6: valors incomplets
        responses = [
            {"toxics_before_explotation": [{"toxic_1": None}]},
            {"toxics_after_explotation": [{"toxic_1": 60}]},
            {"limit": [{"limit_1": 100}]}
        ]
        result = get_air_rating(responses)
        self.assertEqual(result, False)

        # Cas excepcional 1: no hi ha marge ni variació
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 60}]},
            {"toxics_after_explotation": [{"toxic_1": 60}]},
            {"limit": [{"limit_1": 60}]}
        ]
        result = get_air_rating(responses)
        self.assertEqual(result[0], -1) # Impacte nul
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # Cas excepcional 2: el marge és negatiu, es a dir, la concentració de tòxics abans superaba el límit però ha millorat
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 60}]},
            {"toxics_after_explotation": [{"toxic_1": 50}]},
            {"limit": [{"limit_1": 60}]}
        ]
        result = get_air_rating(responses)
        self.assertEqual(result[0], -1) # No hi ha hagut increment, per tant impacte petit o nul.
        self.assertEqual(result[1]["semaphore"], "GREEN")

        # Cas excepcional 3: el marge és negatiu, es a dir, la concentració de tòxics abans superaba el límit i a més a empitjorat
        responses = [
            {"toxics_before_explotation": [{"toxic_1": 60}]},
            {"toxics_after_explotation": [{"toxic_1": 61}]},
            {"limit": [{"limit_1": 20}]}
        ]
        result = get_air_rating(responses)
        self.assertEqual(result[0], -5) # La situació és pitjor que l'anterior, que ja era dolenta 
        self.assertEqual(result[1]["semaphore"], "DRED")

    def test_landform_change_rating(self):
        # TEST MASSIU: Impacte petit. Afecta a menys del 20% del terreny i es reversible.
        affected_area = [0.5, 1, 2, 5, 10.15, 15.5, 19.99]
        for a in affected_area:
            responses = [{"area_alterada": a}, {"reversible_modification": True}]
            result = get_landform_changes_rating(responses)
            self.assertEqual(result[0], -1)
            self.assertEqual(result[1]["semaphore"], "GREEN")

        # TEST MASSIU: Impacte mitjà. Es modifica entre el 20%-40% i es reversible.
        affected_area = [20, 21.4, 25, 26.7, 30, 30.5, 39.99]
        for a in affected_area:
            responses = [{"area_alterada": a}, {"reversible_modification": True}]
            result = get_landform_changes_rating(responses)
            self.assertEqual(result[0], -2)
            self.assertEqual(result[1]["semaphore"], "YELLOW")

        # TEST MASSIU: Impacte important. Es modifica +40% del terreny i es reversible
        affected_area = [40, 41.2, 45, 46.7, 50, 51.9, 56, 59.99]
        for a in affected_area:
            responses = [{"area_alterada": a}, {"reversible_modification": True}]
            result = get_landform_changes_rating(responses)
            self.assertEqual(result[0], -3)
            self.assertEqual(result[1]["semaphore"], "ORANGE")

        # TEST MASSIU: Impacte molt important. Es modifica +60% del terreny i es reversible
        affected_area = [60, 61.2, 65, 71, 75.5, 80, 90, 95, 99.99, 100]
        for a in affected_area:
            responses = [{"area_alterada": a}, {"reversible_modification": True}]
            result = get_landform_changes_rating(responses)
            self.assertEqual(result[0], -4)
            self.assertEqual(result[1]["semaphore"], "RED")

        # TEST MASSIU: Impacte extrem. Es modifica +60% del terreny i NO es reversible
        affected_area = [60, 61.2, 65, 71, 75.5, 80, 90, 95, 99.99, 100]
        for a in affected_area:
            responses = [{"area_alterada": a}, {"reversible_modification": False}]
            result = get_landform_changes_rating(responses)
            self.assertEqual(result[0], -5)
            self.assertEqual(result[1]["semaphore"], "DRED")

        # EXCEPCIONS:
        
        # E1: Impacte extrem, s'ha afectat 20% del terreny però NO es reversible (Aqui la NO reversibilitat predomina)
        responses = [{"area_alterada": 20}, {"reversible_modification": False}]
        result = get_landform_changes_rating(responses)
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # E2: falta el percentatge no es pot fer la valoració.
        responses = [{"reversible_modification": True}]
        result = get_landform_changes_rating(responses)
        self.assertEqual(result, False) 


    def test_biodiversity_rating(self):
        # Cas 1: No s'ha entrat la biodiversitat afectada
        responses = [{"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": True}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result, False)

        # Cas 2: No hi ha biodiversitat afectada és 0%
        responses = [{"biodiversity_affected": 0}, {"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": True}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result, False) 

        # Cas 3: L'impacte és molt lleu i recuperable.
        responses = [{"biodiversity_affected": 5}, {"endangered_species": False}, {"critic_habitat": False}, {"complete_recovery": True}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -1)
        self.assertEqual(result[1]["semaphore"], "GREEN")  

        # Cas 4: Afecta a una petita part de la biodiversitat, la zona es critica pero es recupera al 100%
        responses = [{"biodiversity_affected": 5}, {"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": True}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -1)
        self.assertEqual(result[1]["semaphore"], "GREEN")   

        # Cas 5: Afecta a una petita part de la biodiversitat, la zona es critica i a més no es recupera completament.
        responses = [{"biodiversity_affected": 5}, {"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": False}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -3) 
        self.assertEqual(result[1]["semaphore"], "ORANGE")  

        # Cas 6: Afecta a una part moderada biodiversitat, la zona es critica i a més no es recupera completament.
        responses = [{"biodiversity_affected": 30}, {"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": False}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -4) 
        self.assertEqual(result[1]["semaphore"], "RED")  

        # Cas 7: Afecta a la meitat biodiversitat, la zona es critica i a més no es recupera completament.
        responses = [{"biodiversity_affected": 50}, {"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": False}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")   

        # Cas 8: Afecta a tota la biodiversitat, la zona es critica i a més no es recupera completament.
        responses = [{"biodiversity_affected": 100}, {"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": False}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -5) 
        self.assertEqual(result[1]["semaphore"], "DRED")  

        # Cas 9: Afecta a tota la biodiversitat, però no afecta a zones critiques i es preveu complet recuperament
        responses = [{"biodiversity_affected": 100}, {"endangered_species": False}, {"critic_habitat": False}, {"complete_recovery": True}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -3)
        self.assertEqual(result[1]["semaphore"], "ORANGE")   

        # Cas 10: Afecta a una petita part però hi han especies en extinció i a mes no es preveu una recuperació completa
        responses = [{"biodiversity_affected": 10}, {"endangered_species": True}, {"critic_habitat": False}, {"complete_recovery": False}]
        result = get_biodiversity_rating(responses)

        self.assertEqual(result[0], -2)
        self.assertEqual(result[1]["semaphore"], "YELLOW")   

        # Cas 11: Impacte mitjà (40%) sobre la biodiversitat, però amb recuperació completa i sense afectació a espècies en perill ni hàbitats crítics.
        responses = [{"biodiversity_affected": 40}, {"endangered_species": False}, {"critic_habitat": False}, {"complete_recovery": True}]
        self.assertEqual(get_biodiversity_rating(responses)[0], -1)

        # Cas 12: No s’ha indicat el valor de biodiversitat afectada.
        responses = [{"endangered_species": True}, {"critic_habitat": True}, {"complete_recovery": False}]
        self.assertEqual(get_biodiversity_rating(responses), False)

        # Casos 13 (intervals límit)
        for v in [20, 40, 60, 80]:
            with self.subTest(biodiversity_affected=v):
                responses = [{"biodiversity_affected": v}, {"endangered_species": False}, {"critic_habitat": False}, {"complete_recovery": False}]
                result = get_biodiversity_rating(responses)
                self.assertIsInstance(result, tuple)  # S'hauria de retornar una tupla amb índex vàlid

    def test_subsidence_rating(self):
        # Cas 1: No hi ha subsidència
        responses = [{"subsidence_detected": False}]
        result = get_subsidence_rating(responses)

        self.assertEqual(result, False)

        # Cas 2: La subsidència és incompatible
        responses = [{"subsidence_detected": True}, {"sub_compatible_impact": False}]
        result = get_subsidence_rating(responses) 

        self.assertEqual(result[0], -5) # Subsidència incomptatible
        self.assertEqual(result[1]["semaphore"], "DRED")  

        # Cas 3: Hi ha risc de col·lapse
        responses = [{"subsidence_detected": True}, {"sub_compatible_impact": False}, {"sub_risk_of_collapse": True}]
        result = get_subsidence_rating(responses) 

        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")  

        # Cas 4: S'han detectat 3 impactes 'lleus'
        responses = [{"subsidence_detected": True}, {"sub_compatible_impact": True}, {"sub_risk_of_collapse": False}, {"sub_collapses_detected": True}, {"sub_affected_water_quality": True}, {"sub_alterations_in_rivers": True}]
        result = get_subsidence_rating(responses) 

        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")  

        # Cas 5: S'han detectat 2 impactes 'lleus'
        responses = [{"subsidence_detected": True}, {"sub_compatible_impact": True}, {"sub_risk_of_collapse": False}, {"sub_collapses_detected": True}, {"sub_affected_water_quality": True}, {"sub_alterations_in_rivers": False}]
        result = get_subsidence_rating(responses) 

        self.assertEqual(result, False) # No són prous impactes com per penalitzar

        # Cas 6: Només risc de col·lapse
        responses = [{"subsidence_detected": True}, {"sub_risk_of_collapse": True}]
        result = get_subsidence_rating(responses)
        self.assertEqual(result[0], -5)
        self.assertEqual(result[1]["semaphore"], "DRED")

        # Cas 7: Només subsidència detectada, cap altre paràmetre
        responses = [{"subsidence_detected": True}]
        self.assertEqual(get_subsidence_rating(responses), False)

        # Cas 8: 2 impactes reals + 1 False
        responses = [{"subsidence_detected": True}, {"sub_collapses_detected": True}, {"sub_affected_water_quality": True}, {"sub_alterations_in_rivers": False}]
        self.assertEqual(get_subsidence_rating(responses), False)

        # Cas 9: subsidència = False però altres valors True
        responses = [{"subsidence_detected": False}, {"sub_collapses_detected": True}, {"sub_affected_water_quality": True}, {"sub_alterations_in_rivers": True}]
        self.assertEqual(get_subsidence_rating(responses), False)


    def test_positive_environmental_rating(self):
        # Cas 1: millor dels casos
        responses = [
            {"env_soil_quality_improved":  True},
            {"env_water_regeneration": True},
            {"env_reforestation_projects": True},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  100},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation":  True}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 5)
        self.assertEquals(result[1]["semaphore"], "DGREEN")

        # Cas 2: millora notable tot i que no s'ha millorat la qualitat del sòl 
        responses = [
            {"env_soil_quality_improved":  False},
            {"env_water_regeneration": True},
            {"env_reforestation_projects": True},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  80},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation":  True}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 4)
        self.assertEquals(result[1]["semaphore"], "GREEN")

        # Cas 3: millora moderada ja que no s'ha millorat la qualitat del sòl ni s'ha descontaminat l'aigua
        responses = [
            {"env_soil_quality_improved":  False},
            {"env_water_regeneration": False},
            {"env_reforestation_projects": True},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  100},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation":  True}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 3)
        self.assertEquals(result[1]["semaphore"], "YELLOW")

        # Cas 4: millora ambiental important gràcies a la restauració de sòl i aigua,
        # tot i que només s’ha restaurat un 10% de la superfície afectada.

        responses = [
            {"env_soil_quality_improved":  True},
            {"env_water_regeneration": True},
            {"env_reforestation_projects": True},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  10},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation":  True}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 4)
        self.assertEquals(result[1]["semaphore"], "GREEN")

        # Cas 5: es constata una millora ambiental moderada. 
        # S’ha millorat la qualitat del sòl i s’han dut a terme accions com la reforestació i la reintroducció d’espècies natives, 
        # amb una restauració del 50% de la superfície afectada. 
        # No obstant això, no hi ha evidència de regeneració d’aigües, ni d’increment en la biodiversitat ni creació d’hàbitats.
        responses = [
            {"env_soil_quality_improved":  True},
            {"env_water_regeneration": False},
            {"env_reforestation_projects": True},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  50},
            {"env_biodiversity_increase": False},
            {"env_habitat_creation":  False}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 3)
        self.assertEquals(result[1]["semaphore"], "YELLOW")

        # Cas 6: millora ambiental molt limitada. No s’ha millorat ni el sòl ni l’aigua, 
        # no s’han dut a terme reforestacions ni s’han creat hàbitats, i només s’ha restaurat un 25% de la superfície. 
        # L’única acció positiva és la reintroducció d’espècies vegetals natives. → Rating esperat: 1

        responses = [
            {"env_soil_quality_improved":  False},
            {"env_water_regeneration": False},
            {"env_reforestation_projects": False},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  25},
            {"env_biodiversity_increase": False},
            {"env_habitat_creation":  False}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 1)
        self.assertEquals(result[1]["semaphore"], "RED")

        # Cas 7: millora ambiental parcial. Tot i que no s’han millorat ni el sòl ni l’aigua ni s’ha fet reforestació, 
        # s’ha restaurat un 45% de la superfície afectada i s’han introduït espècies natives, amb un augment de la biodiversitat i creació d’hàbitats. 
        # El resultat reflecteix un impacte positiu moderat però amb mancances en els aspectes més crítics. → Rating esperat: 2

        responses = [
            {"env_soil_quality_improved":  False},
            {"env_water_regeneration": False},
            {"env_reforestation_projects": False},
            {"env_native_species_restoration":  True},
            {"env_restored_area_percentage":  45},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation":  True}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result[0], 2)
        self.assertEquals(result[1]["semaphore"], "ORANGE")

        # Cas 8: el percentatge d'area restaurada no s'ha entrat.
        responses = [
            {"env_soil_quality_improved":  False},
            {"env_water_regeneration": False},
            {"env_reforestation_projects": False},
            {"env_native_species_restoration":  True},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation":  True}
        ]
        result = get_positive_environmental_rating(responses)

        self.assertEquals(result, False)

        # Cas 9: Només es proporciona el percentatge de restauració (100%) i cap altra acció positiva.
        # La puntuació total és 5 sobre 17 → rating 1 (millora ambiental molt limitada).
        responses = [{"env_restored_area_percentage": 100}]
        result = get_positive_environmental_rating(responses)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1]["semaphore"], "RED")

        # Cas 10: Restauració mínima (1%) i cap altra acció positiva.
        responses0 = [{"env_restored_area_percentage": 1}]
        result0 = get_positive_environmental_rating(responses0)
        self.assertEqual(result0[0], 1)  # Score = 1 → impacte positiu molt limitat
        self.assertEqual(result0[1]["semaphore"], "RED")

        # Cas 11: S'ha indicat env_restored_area_percentage = 0 i s’ha millorat el sòl.
        # Tot i que la restauració és nul·la (no suma), s’activa la puntuació gràcies a la millora del sòl (+4 punts).
        # Score = 4/17 → rating = 1
        responses1 = [{"env_restored_area_percentage": 0}, {"env_soil_quality_improved": True}]
        result1 = get_positive_environmental_rating(responses1)
        self.assertEqual(result1[0], 1)
        self.assertEqual(result1[1]["semaphore"], "RED")


        # Cas 12: Totes les accions positives marcades, però env_restored_area_percentage = 0.
        # Tot i que no s’ha restaurat àrea, el fet d’indicar el valor fa que es consideri “completat”.
        # La resta d’accions sumen un total de 13 punts sobre 17 → rating = 4
        responses2 = [
            {"env_soil_quality_improved": True},
            {"env_water_regeneration": True},
            {"env_reforestation_projects": True},
            {"env_native_species_restoration": True},
            {"env_biodiversity_increase": True},
            {"env_habitat_creation": True},
            {"env_restored_area_percentage": 0}
        ]
        result2 = get_positive_environmental_rating(responses2)
        self.assertEqual(result2[0], 4)
        self.assertEqual(result2[1]["semaphore"], "GREEN")

    def test_liability_impact_rating(self):
        # TEST MASSIU: Extensió dels passius ambientals. 
        test_for_index_1, s1 = [1.5, 3, 4.8, 6, 7.2, 10, 12.5, 15, 17.3, 19], "GREEN" # 0-20%
        test_for_index_2, s2 = [20, 21.5, 24, 26.7, 29, 30.5, 33, 35.8, 38, 39], "YELLOW" # 20-40%
        test_for_index_3, s3 = [40, 42.3, 45, 47.5, 50, 52.8, 55, 57.6, 59], "ORANGE" # 40-60%
        test_for_index_4, s4 = [60, 62.5, 65, 67.7, 70, 72.2, 75, 77.9, 79.99], "RED" # 60-80%
        test_for_index_5, s5 = [81, 82.4, 85, 87.6, 90, 92.1, 95, 97.8, 100], "DRED" # +80%

        testers = [
            {"testers": test_for_index_1, "index": -1, "color": s1},
            {"testers": test_for_index_2, "index": -2, "color": s2},
            {"testers": test_for_index_3, "index": -3, "color": s3},
            {"testers": test_for_index_4, "index": -4, "color": s4},
            {"testers": test_for_index_5, "index": -5, "color": s5},
        ]

        for test in testers:
            for t in test["testers"]:
                responses = [{"extension": {"extension_1": t}}]
                results = get_liability_impact_rating(responses)
                self.assertEqual(results["ExtensionLiabilities"]["rating"], test["index"])
                self.assertEqual(results["ExtensionLiabilities"]["semaphore"], test["color"])

        # Excepció: l'area afectada és exactament 0, no penalitza
        responses = [{"extension": {"extension_1": 0}}]
        results = get_liability_impact_rating(responses)
        self.assertFalse(results)

        # TEST MASSIU: Impacte dels passius ambientals.

        # Cas 1: Impacte petit i molt bona gestió
        # Només hi ha un impacte lleu (impact_3 = "Baix") i tots els ítems de gestió estan en True.
        # El score total és baix i es compensa amb bona gestió → rating = -1, semàfor verd.
        responses = [
            {"impact": {
                "impact_1": False,
                "impact_2": False,
                "impact_3": "Baix",
                "impact_4": False,
                "impact_5": False
            }},
            {"management": {
                "management_1": True,
                "management_2": True,
                "management_3": True,
                "management_4": True
            }}
        ]
        results = get_liability_impact_rating(responses)
        self.assertEqual(results["LiabilityImpact"]["rating"], -1)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "GREEN")

        # Cas 2: Impacte moderat i gestió parcial
        # Diversos impactes detectats (impact_1, impact_3 = "Moderat", impact_4) però només una gestió correcta.
        # Score net = 3 - 1 = 2 ➜ rating = -2, semàfor taronja.
        responses = [
            {"impact": {
                "impact_1": True,
                "impact_2": False,
                "impact_3": "Moderat",
                "impact_4": True,
                "impact_5": False
            }},
            {"management": {
                "management_1": True,
                "management_2": False,
                "management_3": False,
                "management_4": False
            }}
        ]
        results = get_liability_impact_rating(responses)
        self.assertEqual(results["LiabilityImpact"]["rating"], -2)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "YELLOW")

        # Cas X: Impacte moderat amb diversos factors actius i gestió neutra
        # S'activen impact_1 (+2), impact_3 = "Moderat" (+2) i impact_5 (+2) ➜ total = 6
        # Gestió neutra (2 respostes True) ➜ no suma ni resta
        # Score final = 6 ➜ rating = -3 (sobre 16) → semàfor ORANGE

        responses = [
            {"impact": {
                "impact_1": True,        # +2
                "impact_2": True,       # +0
                "impact_3": "Alt",   # +2
                "impact_4": False,       # +0
                "impact_5": True         # +2
            }},
            {"management": {
                "management_1": True,    # 2 True (no canvia el score)
                "management_2": False,
                "management_3": True,
                "management_4": False
            }}
        ]

        results = get_liability_impact_rating(responses)
        self.assertEqual(results["LiabilityImpact"]["rating"], -3)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "ORANGE")


        # Cas 3: Impacte alt i gestió dolenta
        # Tots els impactes estan actius, i impact_3 és "Alt". Cap acció de gestió és positiva.
        # Score molt elevat ➜ rating = -4, semàfor vermell.
        responses = [
            {"impact": {
                "impact_1": True,
                "impact_2": True,
                "impact_3": "Alt",
                "impact_4": True,
                "impact_5": True
            }},
            {"management": {
                "management_1": False,
                "management_2": False,
                "management_3": False,
                "management_4": False
            }}
        ]
        results = get_liability_impact_rating(responses)
        self.assertEqual(results["LiabilityImpact"]["rating"], -4)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "RED")

        # Cas 4: Impacte extrem i sense gestió
        # Tots els impactes actius i impact_3 és "Extrem", sense cap mesura de gestió aplicada.
        # Score màxim ➜ rating = -5, semàfor vermell fosc.
        responses = [
            {"impact": {
                "impact_1": True,
                "impact_2": True,
                "impact_3": "Molt alt",
                "impact_4": True,
                "impact_5": True
            }},
            {"management": {
                "management_1": False,
                "management_2": False,
                "management_3": False,
                "management_4": False
            }}
        ]
        results = get_liability_impact_rating(responses)
        self.assertEqual(results["LiabilityImpact"]["rating"], -5)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "DRED")

        # Cas 5: Sense impactes ni gestió. No s'ha especificat impact_3.
        # No s’ha detectat cap impacte i totes les accions de gestió són falses.
        # El càlcul no s’hauria d’activar ➜ s’espera False.
        responses = [
            {"impact": {
                "impact_1": False,
                "impact_2": False,
                "impact_4": False,
                "impact_5": False
            }},
            {"management": {
                "management_1": False,
                "management_2": False,
                "management_3": False,
                "management_4": False
            }}
        ]
        results = get_liability_impact_rating(responses)
        self.assertEqual(results, False)

        # COMBINACIONS

        # C1:
        responses = [
            {"extension": {"extension_1": 90}},
            {"impact": {"impact_1": True, "impact_2":  True, "impact_3":  "Molt alt",  "impact_4":  True, "impact_5":  True}},
            {"management": {"management_1":  False, "management_2":  False, "management_3":  False, "management_4":  False}}
        ]

        results = get_liability_impact_rating(responses)
        self.assertEqual(results["ExtensionLiabilities"]["rating"], -5)
        self.assertEqual(results["ExtensionLiabilities"]["semaphore"], "DRED")
        self.assertEqual(results["LiabilityImpact"]["rating"], -5)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "DRED")

        # C2:
        responses = [
            {"extension": {"extension_1": 0}},
            {"impact": {"impact_1": True, "impact_2":  True, "impact_3":  "Molt alt",  "impact_4":  True, "impact_5":  True}},
            {"management": {"management_1":  False, "management_2":  False, "management_3":  False, "management_4":  False}}
        ]

        results = get_liability_impact_rating(responses)
        self.assertNotIn("ExtensionLiabilities", results)
        self.assertEqual(results["LiabilityImpact"]["rating"], -5)
        self.assertEqual(results["LiabilityImpact"]["semaphore"], "DRED")

# command: python3 manage.py test
