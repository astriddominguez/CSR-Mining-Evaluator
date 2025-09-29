import sys
import os
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Configurem Django perquè aquest script és una funcionalitat externa
# i s'executa fora del seu entorn habitual (com un script independent).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  
django.setup()

from django.apps import apps
from datetime import timedelta
from django.utils import timezone

def clean_bd():
    """
    Elimina tots els registres de la base de dades corresponent a un usuari on la seva última
    connexió amb la pàgina web va ser fa 7 dies. 
    """
    # Accedim al model UserFingerprint
    Model = apps.get_model('processdata', 'UserFingerprint')  
    limit_date = timezone.now() - timedelta(days=7)  
    # __lt: less than. 
    deleted_count, _ = Model.objects.filter(last_seen__lt=limit_date).delete()
    print(f"S'han eliminat {deleted_count} registres antics.")

if __name__ == "__main__":
    clean_bd()
