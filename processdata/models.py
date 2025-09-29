from django.db import models
from django.apps import apps
from django.db import transaction
from .data import SOCIOECONOMIC_DIMENSION_QUESTIONS, ENVIRONMENT_DIMENSION_QUESTIONS
import json

class UserFingerprint(models.Model):
    fingerprint_id = models.CharField(max_length = 50, unique = True) # Id únic del visitant 
    first_seen = models.DateTimeField(auto_now_add = True)  # primera visita 
    last_seen = models.DateTimeField(auto_now = True)  # última visita 

    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        super().save(*args, **kwargs)  

        if is_new: 
            try:
                with transaction.atomic(): # totes les consultes s'executen en una sola transacció
                    # Es fan instancies dels models...
                    form = Form.objects.create(fingerprint = self)
                    # OVERVIEW
                    Overview.objects.create(form = form)

                    # Crear SocioeconomicDimension + subformularis
                    socioeconomic_dimension = SocioeconomicDimension.objects.create(form=form)

                    for subdimension in SOCIOECONOMIC_DIMENSION_QUESTIONS:
                        model_name = subdimension["id"]
                        model_class = apps.get_model(self._meta.app_label, model_name)
                        model_class.objects.create(subform=socioeconomic_dimension)

                    # Crear EnvironmentDimension + subformularis
                    environment_dimension = EnvironmentDimension.objects.create(form=form)

                    for subdimension in ENVIRONMENT_DIMENSION_QUESTIONS:
                        model_name = subdimension["id"]
                        model_class = apps.get_model(self._meta.app_label, model_name)
                        model_class.objects.create(subform=environment_dimension)

            except Exception as e:
                print("Error creating form and subforms: ", e)


    def __str__(self):
        return self.fingerprint_id
    
class Form(models.Model):
    fingerprint = models.ForeignKey(UserFingerprint, on_delete = models.CASCADE)  # Relació amb l'usuari  
    created_at = models.DateTimeField(auto_now_add = True)  # Data de creació del formulari

    def __str__(self):
        return f"Form {self.fingerprint.fingerprint_id}"
    
class SubForm(models.Model):
    form = models.OneToOneField(Form, on_delete = models.CASCADE, primary_key = True)  

    def __str__(self):
        return f"SubForm for Form {self.form.fingerprint}"
    
class SubSubForm(models.Model):
    subform = models.OneToOneField(SubForm, on_delete = models.CASCADE, primary_key = True)

    def __str__(self):
        return f"SubSubForm for SubForm {self.subform.form.fingerprint}"
    
#-------------------------------------------------------------------
#                            OVERVIEW
#-------------------------------------------------------------------

class Overview(SubForm):  
    project_name = models.TextField(blank = True, null = True)
    company_name = models.TextField(blank = True, null = True)
    mine_ubication = models.CharField(max_length=100, blank=True, null=True) 
    phase = models.TextField(blank = True, null = True)

    def __str__(self):
        return f"Overview Subform for {self.form.fingerprint}"
    

#---------------------------------------------------------------------------------------
#       FUNCIÓ AUXILIAR PER CREAR LES CEL·LES DE LES SUBDIMENSIONS DINÀMICAMENT
#---------------------------------------------------------------------------------------

def generate_subdimension_fields(questions):
    """
    Genera un diccionari de camps de model Django a partir d'una llista de preguntes.

    Aquesta funció interpreta una llista de preguntes en format JSON, on cada pregunta conté
    informació sobre el tipus d'entrada (`radio`, `number_input`, etc.) i els seus identificadors.
    En funció del tipus, es creen camps corresponents de models Django com BooleanField, 
    FloatField, IntegerField o CharField, amb configuracions adaptades a cada cas. 
    """
    fields = {}
    for question in questions:

        if question["type"] == "radio":
            fields[question["input_id"]] = models.BooleanField(default = False)

        elif question["type"] == "number_input":
            if question["number_type"] == "float":
                fields[question["input_id"]] = models.FloatField(default = None, null = True, blank = True)
            elif question["number_type"] == "int":
                fields[question["input_id"]] = models.IntegerField(default = None, null = True, blank = True)

        elif question["type"] == "multiple-select":
            options = question["options"]
            choices = [(opt["id"], opt["name"]) for opt in options]
            max_choices = [opt["id"] for opt in options]
            as_string = json.dumps(max_choices) # conversió de llista a str, tal i com es guardaria. Màxima longitud = longitud de totes les opcions a la vegada.
            fields[question["input_id"]] = models.CharField(max_length = len(as_string), choices = choices, default = choices[0][0], blank = True, null=True)

        elif question["type"] == "select":
            options = question["options"]
            choices = [(opt, opt) for opt in options]
            max_length = max(len(opt) for opt in options) # Agafa la longitud de la opció més llarga.
            fields[question["input_id"]] = models.CharField(max_length = max_length, choices = choices, null=True)

        elif question["type"] == "one-to-many-numbers":
            for children in question["childrens"]:
                fields[children["input_id"]] = models.FloatField(default = None, null = True, blank = True)

    return fields 

def build_subsubform_model(name, base_class, questions):
    """
    Crea un model Django dinàmicament a partir d'un conjunt de preguntes.

    Aquesta funció genera una classe de model que hereta de `base_class` (normalment SubSubForm),
    i li afegeix camps segons el tipus de preguntes especificades. Cada camp es genera
    utilitzant la funció `generate_subdimension_fields`, que converteix el JSON de preguntes
    en definicions de camps Django.

    :param name: nom de la classe del model. Ex: 'LocalProcurement'
    :param base_class: classe de la qual heretarà el model. Ex: SubSubForm
    :param questions: Llista de preguntes en format JSON.
    """

    fields = generate_subdimension_fields(questions) 
    fields["__module__"] = __name__ # important per indicar que el model pertany al mateix fitxer que esta escribint això. Al models.py d'aquesta app.
    fields["__str__"] = lambda self: f"{name} for {self.subform.form.fingerprint}"
    return type(name, (base_class,), fields) # crea i retorna la clase

# MyClass = type("MyClass", (object,), {"x": 123}) és lo mateix que escriure:
# class MyClass(object):
#   x = 123  
    
#-------------------------------------------------------------------
#                       DIMENSIÓ SOCIOECONOMICA
#-------------------------------------------------------------------
    
class SocioeconomicDimension(SubForm):

    def __str__(self):
        return f"Socioeconomic Dimension for Fingerprint {self.form.fingerprint}"
    
# Creació dinàmica de les subdimensions de la dimensió socioeconòmica
for subdimension in SOCIOECONOMIC_DIMENSION_QUESTIONS:
    reference = subdimension["id"] # ID com a nom del model
    globals()[reference] = build_subsubform_model(reference, SubSubForm, subdimension["questions"])


#-------------------------------------------------------------------
#                       DIMENSIÓ AMBIENTAL
#-------------------------------------------------------------------

class EnvironmentDimension(SubForm):
    def __str__(self):
        return f"Environment Dimension for Fingerprint {self.form.fingerprint}"
    
# Creació dinàmica de les subdimensions de la dimensió ambiental
for subdimension in ENVIRONMENT_DIMENSION_QUESTIONS:
    reference = subdimension["id"] # ID com a nom del model
    globals()[reference] = build_subsubform_model(reference, SubSubForm, subdimension["questions"])