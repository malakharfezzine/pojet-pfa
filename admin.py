from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, EntrepriseProfile, EncadrantProfile, OffreStage, Candidature, Stage, Notification

admin.site.site_header = "PortailStages 2026 — Administration"
admin.site.site_title = "PortailStages Admin"
admin.site.index_title = "Gestion du Portail de Stages"

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','get_full_name','email','role','is_active']
    list_filter = ['role','is_active']
    fieldsets = UserAdmin.fieldsets + (('Rôle', {'fields': ('role',)}),)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user','cne','filiere','niveau']
    list_filter = ['niveau','filiere']

@admin.register(EntrepriseProfile)
class EntrepriseProfileAdmin(admin.ModelAdmin):
    list_display = ['nom_entreprise','secteur','telephone','valide']
    list_filter = ['valide']
    list_editable = ['valide']

@admin.register(EncadrantProfile)
class EncadrantProfileAdmin(admin.ModelAdmin):
    list_display = ['user','matricule','specialite','bureau']

@admin.register(OffreStage)
class OffreStageAdmin(admin.ModelAdmin):
    list_display = ['titre','type_stage','duree','date_limite','publie']
    list_filter = ['type_stage','publie']
    list_editable = ['publie']

@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ['etudiant','offre','statut','date_postulation']
    list_filter = ['statut']
    list_editable = ['statut']

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['candidature','encadrant','statut','note','date_debut']
    list_filter = ['statut']
    list_editable = ['statut']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['destinataire','type_notif','titre','lu','date_creation']
    list_filter = ['lu','type_notif']
