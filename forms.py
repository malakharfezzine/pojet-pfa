from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, EntrepriseProfile, EncadrantProfile, OffreStage, Candidature, Stage

class LoginForm(forms.Form):
    username = forms.CharField(label='Nom d\'utilisateur')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(label='Prénom')
    last_name = forms.CharField(label='Nom')
    email = forms.EmailField(label='Email')
    cne = forms.CharField(label='CNE')
    filiere = forms.CharField(label='Filière')
    niveau = forms.ChoiceField(choices=StudentProfile.NIVEAU_CHOICES, label='Niveau')
    telephone = forms.CharField(label='Téléphone', required=False)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'ETUDIANT'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(user=user, cne=self.cleaned_data['cne'],
                filiere=self.cleaned_data['filiere'], niveau=self.cleaned_data['niveau'],
                telephone=self.cleaned_data.get('telephone',''))
        return user

class EntrepriseSignUpForm(UserCreationForm):
    first_name = forms.CharField(label='Prénom contact')
    last_name = forms.CharField(label='Nom contact')
    email = forms.EmailField()
    nom_entreprise = forms.CharField(label='Nom de l\'entreprise')
    secteur = forms.CharField(label='Secteur d\'activité')
    adresse = forms.CharField(label='Adresse', widget=forms.Textarea(attrs={'rows':3}))
    telephone = forms.CharField(label='Téléphone', required=False)
    site_web = forms.URLField(label='Site web', required=False)
    ice = forms.CharField(label='ICE')
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'ENTREPRISE'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            EntrepriseProfile.objects.create(user=user, nom_entreprise=self.cleaned_data['nom_entreprise'],
                secteur=self.cleaned_data['secteur'], adresse=self.cleaned_data['adresse'],
                telephone=self.cleaned_data.get('telephone',''), site_web=self.cleaned_data.get('site_web',''),
                ice=self.cleaned_data['ice'], valide=False)
        return user

class EncadrantSignUpForm(UserCreationForm):
    first_name = forms.CharField(label='Prénom')
    last_name = forms.CharField(label='Nom')
    email = forms.EmailField()
    matricule = forms.CharField(label='Matricule')
    specialite = forms.CharField(label='Spécialité')
    bureau = forms.CharField(label='Bureau', required=False)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'ENCADRANT'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            EncadrantProfile.objects.create(user=user, matricule=self.cleaned_data['matricule'],
                specialite=self.cleaned_data['specialite'], bureau=self.cleaned_data.get('bureau',''))
        return user

class OffreStageForm(forms.ModelForm):
    date_limite = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='Date limite')
    class Meta:
        model = OffreStage
        fields = ['titre','description','type_stage','domaine','competences','duree','remuneration','date_limite']
        widgets = {'description':forms.Textarea(attrs={'rows':5}),'competences':forms.Textarea(attrs={'rows':3})}

class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['lettre_motivation']
        widgets = {'lettre_motivation':forms.Textarea(attrs={'rows':8,'placeholder':'Rédigez votre lettre de motivation...'})}

class TraiterCandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['statut','commentaire']
        widgets = {'commentaire':forms.Textarea(attrs={'rows':4})}

class EvaluerStageForm(forms.ModelForm):
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False, label='Date de fin')
    class Meta:
        model = Stage
        fields = ['statut','date_fin','note','observation']
        widgets = {'observation':forms.Textarea(attrs={'rows':4}),'note':forms.NumberInput(attrs={'min':0,'max':20,'step':0.25})}

class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['cv','telephone','filiere','niveau']
        widgets = {'cv':forms.FileInput(attrs={'accept':'.pdf,.doc,.docx'})}
        labels = {'cv':'CV (PDF ou Word)'}
