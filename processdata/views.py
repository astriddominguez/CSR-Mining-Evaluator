from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from .models import UserFingerprint
from django.middleware.csrf import get_token
from .data import OVERVIEW_QUESTIONS, SOCIOECONOMIC_DIMENSION_QUESTIONS, ENVIRONMENT_DIMENSION_QUESTIONS
import json
from .rating.calculate import calculate_rating
from .getdata import *

#-----------------------------------------------------------------------
#----------------------------- VISTES-----------------------------------
#-----------------------------------------------------------------------

# VISTA PRINCIPAL
def index(request):
    return render(request, template_name = 'index.html')

# VISTA DEL FORMULARI
def evaluator(request):
    step, fingerprint = False, False
    step = request.GET.get("last") # Si es True es prové de la vista resultats.
    fingerprint = request.GET.get("fingerprintId") # únicament necessari si es prové de resultats.

    return render(request, "pages/evaluator.html", {"overview_questions": OVERVIEW_QUESTIONS, "socio_economic_questions": SOCIOECONOMIC_DIMENSION_QUESTIONS, "environment_questions": ENVIRONMENT_DIMENSION_QUESTIONS, "LastStep": step, "fingerprintId": fingerprint})  

# VISTA DE RESULTATS
def results(request):
    fingerprint_id = request.GET.get("fingerprintId") 
    results = get_results(fingerprint_id) # s'obté respostes del formulari per l'usuari a partir del seu identificador.
    ratings = calculate_rating(results) # a partir de les anteriors respostes es fa el càlcul i s'obté l'estructura de dades a mostrar.

    return render(request, 'pages/results.html', {
        "fingerprint": fingerprint_id, 
        "project_data": get_overview_data_for_results(fingerprint_id),
        "ratings": ratings
    })

# VISTA DE TUTORIAL
def tutorial(request): 
    return render(request, template_name = 'pages/tutorial.html')

#------------------------------------------------------------------------------
#-------------PETICIONS DE RECEPCIÓ/ENVIAMENT CLIENT-SERVIDOR------------------
#------------------------------------------------------------------------------

def get_csrf_token(request):
    """
    Retorna el token CSRF i ho estableix com a cookie en la resposta.

    Aquesta funció genera un token CSRF utilitzant el sistema de protecció de
    Django i el retorna dins d'una resposta JSON.  A més, estableix aquest
    token com una cookie al navegador del client. 

    :param request (HttpRequest): petició HTTP rebuda.
    """
    response = JsonResponse({"csrftoken": get_token(request)})
    # samesite = "Lax": no permet enviar cookies en peticions automátiques de tipus POST fetes desde altre lloc web (evita CSRF).
    # secure = False. Permet enviar la cookie per HTTP normal, sense xifrar. A producció ha d'estar a True.
    response.set_cookie("csrftoken", get_token(request), samesite = "Lax", secure = False)
    return response


@csrf_protect 
def check_fingerprint_and_send_form(request): 
    """
    Revisa si el fingerprint (ID de l'usuari existeix), i si ja existeix es retorna les dades contingudes del formulari
    per mostrar-les novament a la pàgina. 
    
    :param request (HttpRequest): petició HTTP rebuda.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        fingerprint_id = data.get("fingerprint_id")

        if fingerprint_id:
            
            # Si afecta alguna columna l'usuari existeix i actualitza l'última vegada que aquest s'ha connectat
            updated_rows = UserFingerprint.objects.filter(fingerprint_id = fingerprint_id).update(last_seen = now())
            user_exists = updated_rows > 0

            if user_exists: # Si l'usuari existeix retornem les respostes del formulari emmagatzemades 
                overview_data = get_overview_data(fingerprint_id)
                socioeconomic_data = get_socioeconomic_data(fingerprint_id)
                environment_data = get_environment_data(fingerprint_id)
                
                form_data = {
                    "overview": overview_data,
                    "socioeconomic_dimension": socioeconomic_data,
                    "environment_dimension": environment_data
                }
                
                return JsonResponse({"message": "Searched if fingerprint is registered", "registered": user_exists, "form": form_data})
            else:
                return JsonResponse({"message": "Searched if fingerprint is registered", "registered": user_exists})

    return JsonResponse({"error": "Method Not Allowed"}, status = 405)

@csrf_protect
def save_fingerprint(request):
    """
    Emmagatzema el Fingerprint a la base de dades per primera vegada i actualitza la última connexió del usuari.
    S'ha de tenir en compte que en registrar-lo, internament també s'inicialitzarán tots els models corresponents al formulari.
    
    :param request (HttpRequest): petició HTTP rebuda.
    """ 
    if request.method == "POST":
        data = json.loads(request.body)
        fingerprint_id = data.get("fingerprint_id")

        if fingerprint_id:
            user, created = UserFingerprint.objects.get_or_create(fingerprint_id = fingerprint_id)

            user.last_seen = now() # última connexió 
            user.save(update_fields = ['last_seen'])

            return JsonResponse({"message": "Fingerprint saved", "new": created}) 

    return JsonResponse({"error": "Method Not Allowed"}, status = 405)

@csrf_protect 
def update_overview(request):
    """
    Crida a la funció encarregada d'actualitzar la base de dades amb el formulari de dades generals del projecte
    per a un usuari en concret.
    
    :param request (HttpRequest): petició HTTP rebuda.
    """ 
    if request.method == "POST":
        data = json.loads(request.body)
        fingerprint = data.get("fingerprint")

        if not fingerprint:
            return JsonResponse({"error": "Fingerprint is required"}, status = 400)
        
        del data["fingerprint"] 
        if save_overview_data(fingerprint, data):
            return JsonResponse({"message": "Overview updated successfully"}, status = 200)
        else:
            return JsonResponse({"error": "Failed to save overview data"}, status = 500)

    return JsonResponse({"error": "Method Not Allowed"}, status = 405)

@csrf_protect 
def update_socioeconomic_dimension(request):
    """
    Crida a la funció encarregada d'actualitzar la base de dades amb el formulari de dimensió socioeconòmica per a un usuari concret.
    
    :param request (HttpRequest): petició HTTP rebuda.
    """ 
    if request.method == "POST":
        data = json.loads(request.body)
        fingerprint = data.get("fingerprint")

        if not fingerprint:
            return JsonResponse({"error": "Fingerprint is required"}, status = 400)

        del data["fingerprint"] 
        if save_socioeconomic_data(fingerprint, data):
            return JsonResponse({"message": "Socioeconomic Dimension updated"}, status = 200) 
        else:
            return JsonResponse({"error": "Failed to update Socioeconomic Dimension"}, status = 500)

    return JsonResponse({"error": "Method Not Allowed"}, status = 405)

@csrf_protect 
def update_environment_dimension(request):
    """
    Crida a la funció encarregada d'actualitzar la base de dades amb el formulari de dimensió ambiental per a un usuari concret.
    
    :param request (HttpRequest): petició HTTP rebuda.
    """ 
    if request.method == "POST":
        data = json.loads(request.body)
        fingerprint = data.get("fingerprint")

        if not fingerprint:
            return JsonResponse({"error": "Fingerprint is required"}, status = 400)
        
        del data["fingerprint"]
        if save_environment_data(fingerprint, data):
            return JsonResponse({"message": "Environment Dimension updated"}, status = 200) 
        else:
            return JsonResponse({"error": "Failed to update Environment Dimension"}, status = 500)

    return JsonResponse({"error": "Method Not Allowed"}, status = 405)



