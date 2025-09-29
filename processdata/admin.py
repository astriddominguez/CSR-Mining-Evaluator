from django.apps import apps
from django.contrib import admin
from .models import SubSubForm, UserFingerprint, Overview  # els que sí estan definits

class DynamicAdmin(admin.ModelAdmin): 
    def get_list_display(self, request): # Tots els camps de totes les subdimensions són visibles.
        return [field.name for field in self.model._meta.fields]

# Models amb configuració personalitzada
@admin.register(UserFingerprint)
class UserFingerprintAdmin(admin.ModelAdmin):
    list_display = ("fingerprint_id", "first_seen", "last_seen")
    readonly_fields = ("first_seen", "last_seen")

@admin.register(Overview)
class OverviewAdmin(admin.ModelAdmin):
    list_display = ("form", "project_name", "company_name", "mine_ubication", "phase")

# Models dinàmics (hereten de SubSubForm)
for model in apps.get_app_config("processdata").get_models():  
    if issubclass(model, SubSubForm) and model is not SubSubForm:
        try:
            admin.site.register(model, DynamicAdmin)
        except admin.sites.AlreadyRegistered:
            pass
