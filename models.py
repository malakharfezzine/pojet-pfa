from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [('ETUDIANT','Étudiant'),('ENTREPRISE','Entreprise'),('ENCADRANT','Encadrant'),('ADMIN','Admin')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ETUDIANT')

class StudentProfile(models.Model):
    NIVEAU_CHOICES = [('1','1ère année'),('2','2ème année'),('3','3ème année')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    cne = models.CharField(max_length=20, unique=True)
    filiere = models.CharField(max_length=100)
    niveau = models.CharField(max_length=5, choices=NIVEAU_CHOICES, default='2')
    telephone = models.CharField(max_length=15, blank=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)

class EntrepriseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='entreprise_profile')
    nom_entreprise = models.CharField(max_length=200)
    secteur = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15, blank=True)
    site_web = models.URLField(blank=True)
    ice = models.CharField(max_length=20, unique=True)
    valide = models.BooleanField(default=False)

class EncadrantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='encadrant_profile')
    matricule = models.CharField(max_length=20, unique=True)
    specialite = models.CharField(max_length=100)
    bureau = models.CharField(max_length=20, blank=True)

class OffreStage(models.Model):
    TYPE_CHOICES = [('INITIATION',"Stage d'initiation"),('PERFECTIONNEMENT','Stage de perfectionnement'),('PFA','PFA'),('PFE','PFE')]
    entreprise = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offres')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_stage = models.CharField(max_length=20, choices=TYPE_CHOICES)
    domaine = models.CharField(max_length=100)
    competences = models.TextField(blank=True)
    duree = models.IntegerField()
    remuneration = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    date_limite = models.DateField()
    publie = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date_creation']

class Candidature(models.Model):
    STATUT_CHOICES = [('CREEE','Créée'),('EXAMEN','En examen'),('ACCEPTEE','Acceptée'),('REFUSEE','Refusée')]
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidatures')
    offre = models.ForeignKey(OffreStage, on_delete=models.CASCADE, related_name='candidatures')
    lettre_motivation = models.TextField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='CREEE')
    commentaire = models.TextField(blank=True)
    date_postulation = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('etudiant','offre')
        ordering = ['-date_postulation']

class Stage(models.Model):
    STATUT_CHOICES = [('EN_COURS','En cours'),('TERMINE','Terminé'),('VALIDE','Validé')]
    candidature = models.OneToOneField(Candidature, on_delete=models.CASCADE, related_name='stage')
    encadrant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stages_encadres')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='EN_COURS')
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    observation = models.TextField(blank=True)

class Notification(models.Model):
    TYPE_CHOICES = [
        ('CANDIDATURE_RECUE','Candidature reçue'),('STATUT_CHANGE','Statut mis à jour'),
        ('STAGE_EVALUE','Stage évalué'),('ENTREPRISE_VALIDEE','Entreprise validée'),('INFO','Information'),
    ]
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type_notif = models.CharField(max_length=30, choices=TYPE_CHOICES, default='INFO')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=200, blank=True)
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date_creation']
