from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from .models import User, StudentProfile, EntrepriseProfile, EncadrantProfile, OffreStage, Candidature, Stage, Notification
from .forms import (LoginForm, StudentSignUpForm, EntrepriseSignUpForm, EncadrantSignUpForm,
                    OffreStageForm, CandidatureForm, TraiterCandidatureForm, EvaluerStageForm, StudentProfileUpdateForm)

def notifier(destinataire, type_notif, titre, message, lien=''):
    Notification.objects.create(destinataire=destinataire, type_notif=type_notif, titre=titre, message=message, lien=lien)

def home(request):
    offres = OffreStage.objects.filter(publie=True)[:6]
    stats = {'offres': OffreStage.objects.filter(publie=True).count(),
             'entreprises': EntrepriseProfile.objects.filter(valide=True).count(),
             'etudiants': User.objects.filter(role='ETUDIANT').count()}
    return render(request, 'home.html', {'offres': offres, 'stats': stats})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Identifiants incorrects.')
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def signup_etudiant(request):
    form = StudentSignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Compte créé avec succès !')
        return redirect('dashboard_etudiant')
    return render(request, 'registration/signup_etudiant.html', {'form': form})

def signup_entreprise(request):
    form = EntrepriseSignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Compte créé ! En attente de validation par l\'administration.')
        return redirect('dashboard_entreprise')
    return render(request, 'registration/signup_entreprise.html', {'form': form})

def signup_encadrant(request):
    form = EncadrantSignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Compte encadrant créé !')
        return redirect('dashboard_encadrant')
    return render(request, 'registration/signup_encadrant.html', {'form': form})

def liste_offres(request):
    q = request.GET.get('q','')
    type_f = request.GET.get('type','')
    offres = OffreStage.objects.filter(publie=True)
    if q:
        offres = offres.filter(Q(titre__icontains=q)|Q(domaine__icontains=q)|Q(description__icontains=q))
    if type_f:
        offres = offres.filter(type_stage=type_f)
    return render(request, 'offres/liste.html', {'offres': offres, 'q': q, 'type_f': type_f})

def detail_offre(request, pk):
    offre = get_object_or_404(OffreStage, pk=pk, publie=True)
    deja_postule = False
    if request.user.is_authenticated and request.user.role == 'ETUDIANT':
        deja_postule = Candidature.objects.filter(etudiant=request.user, offre=offre).exists()
    return render(request, 'offres/detail.html', {'offre': offre, 'deja_postule': deja_postule})

@login_required
def postuler(request, offre_pk):
    if request.user.role != 'ETUDIANT':
        return redirect('home')
    offre = get_object_or_404(OffreStage, pk=offre_pk, publie=True)
    if Candidature.objects.filter(etudiant=request.user, offre=offre).exists():
        messages.warning(request, 'Vous avez déjà postulé à cette offre.')
        return redirect('detail_offre', pk=offre_pk)
    form = CandidatureForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.save(commit=False)
        c.etudiant = request.user
        c.offre = offre
        c.save()
        messages.success(request, 'Candidature envoyée avec succès !')
        notifier(offre.entreprise, 'CANDIDATURE_RECUE', f'Nouvelle candidature pour « {offre.titre} »',
                 f'{request.user.get_full_name()} a postulé à votre offre.', f'/offres/{offre.pk}/candidatures/')
        notifier(request.user, 'INFO', 'Candidature envoyée',
                 f'Votre candidature pour « {offre.titre} » a été envoyée.', '/dashboard/etudiant/')
        return redirect('dashboard_etudiant')
    return render(request, 'offres/postuler.html', {'form': form, 'offre': offre})

@login_required
def dashboard_etudiant(request):
    if request.user.role != 'ETUDIANT':
        return redirect('home')
    profile = get_object_or_404(StudentProfile, user=request.user)
    candidatures = Candidature.objects.filter(etudiant=request.user).select_related('offre__entreprise__entreprise_profile')
    offres_suggerees = OffreStage.objects.filter(publie=True).exclude(candidatures__etudiant=request.user)[:4]
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    return render(request, 'dashboards/etudiant.html', {'profile': profile, 'candidatures': candidatures,
                  'offres_suggerees': offres_suggerees, 'nb_notifs': nb_notifs})

@login_required
def dashboard_entreprise(request):
    if request.user.role != 'ENTREPRISE':
        return redirect('home')
    profile = get_object_or_404(EntrepriseProfile, user=request.user)
    offres = OffreStage.objects.filter(entreprise=request.user)
    candidatures_recentes = Candidature.objects.filter(offre__entreprise=request.user).order_by('-date_postulation')[:5]
    stats = {'offres': offres.count(), 'candidatures': Candidature.objects.filter(offre__entreprise=request.user).count(),
             'en_attente': Candidature.objects.filter(offre__entreprise=request.user, statut='CREEE').count()}
    return render(request, 'dashboards/entreprise.html', {'profile': profile, 'offres': offres,
                  'candidatures_recentes': candidatures_recentes, 'stats': stats})

@login_required
def creer_offre(request):
    if request.user.role != 'ENTREPRISE':
        return redirect('home')
    profile = get_object_or_404(EntrepriseProfile, user=request.user)
    if not profile.valide:
        messages.error(request, 'Votre compte n\'est pas encore validé. Vous ne pouvez pas publier d\'offres.')
        return redirect('dashboard_entreprise')
    form = OffreStageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        offre = form.save(commit=False)
        offre.entreprise = request.user
        offre.save()
        messages.success(request, 'Offre publiée avec succès !')
        return redirect('dashboard_entreprise')
    return render(request, 'offres/creer.html', {'form': form})

@login_required
def modifier_offre(request, pk):
    if request.user.role != 'ENTREPRISE':
        return redirect('home')
    offre = get_object_or_404(OffreStage, pk=pk, entreprise=request.user)
    form = OffreStageForm(request.POST or None, instance=offre)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Offre modifiée !')
        return redirect('dashboard_entreprise')
    return render(request, 'offres/creer.html', {'form': form, 'modification': True})

@login_required
def supprimer_offre(request, pk):
    if request.user.role != 'ENTREPRISE':
        return redirect('home')
    offre = get_object_or_404(OffreStage, pk=pk, entreprise=request.user)
    offre.delete()
    messages.success(request, 'Offre supprimée.')
    return redirect('dashboard_entreprise')

@login_required
def candidatures_offre(request, offre_pk):
    if request.user.role != 'ENTREPRISE':
        return redirect('home')
    offre = get_object_or_404(OffreStage, pk=offre_pk, entreprise=request.user)
    candidatures = Candidature.objects.filter(offre=offre).select_related('etudiant__student_profile')
    return render(request, 'offres/candidatures.html', {'offre': offre, 'candidatures': candidatures})

@login_required
def traiter_candidature(request, pk):
    if request.user.role != 'ENTREPRISE':
        return redirect('home')
    candidature = get_object_or_404(Candidature, pk=pk, offre__entreprise=request.user)
    form = TraiterCandidatureForm(request.POST or None, instance=candidature)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Candidature mise à jour !')
        labels = {'EXAMEN':"en cours d'examen",'ACCEPTEE':'acceptée ✅','REFUSEE':'refusée ❌','CREEE':'créée'}
        label = labels.get(candidature.statut, candidature.statut)
        notifier(candidature.etudiant, 'STATUT_CHANGE', f'Candidature {label}',
                 f'Votre candidature pour « {candidature.offre.titre} » est maintenant {label}.',
                 '/dashboard/etudiant/')
        if candidature.statut == 'ACCEPTEE':
            enc = User.objects.filter(role='ENCADRANT').first()
            Stage.objects.get_or_create(candidature=candidature, defaults={
                'encadrant': enc, 'date_debut': candidature.date_postulation.date(), 'statut': 'EN_COURS'})
        return redirect('candidatures_offre', offre_pk=candidature.offre.pk)
    return render(request, 'offres/traiter.html', {'form': form, 'candidature': candidature})

@login_required
def dashboard_encadrant(request):
    if request.user.role != 'ENCADRANT':
        return redirect('home')
    profile = get_object_or_404(EncadrantProfile, user=request.user)
    stages = Stage.objects.filter(encadrant=request.user).select_related('candidature__etudiant__student_profile','candidature__offre')
    stats = {'total': stages.count(), 'en_cours': stages.filter(statut='EN_COURS').count(),
             'termines': stages.filter(statut='TERMINE').count(), 'valides': stages.filter(statut='VALIDE').count()}
    return render(request, 'dashboards/encadrant.html', {'profile': profile, 'stages': stages, 'stats': stats})

@login_required
def evaluer_stage(request, pk):
    if request.user.role != 'ENCADRANT':
        return redirect('home')
    stage = get_object_or_404(Stage, pk=pk, encadrant=request.user)
    form = EvaluerStageForm(request.POST or None, instance=stage)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Évaluation enregistrée !')
        notifier(stage.candidature.etudiant, 'STAGE_EVALUE', 'Votre stage a été évalué',
                 f'Votre encadrant a évalué votre stage.' + (f' Note : {stage.note}/20.' if stage.note else ''),
                 '/dashboard/etudiant/')
        return redirect('dashboard_encadrant')
    return render(request, 'dashboards/evaluer.html', {'form': form, 'stage': stage})

@login_required
def upload_cv(request):
    if request.user.role != 'ETUDIANT':
        return redirect('home')
    profile = get_object_or_404(StudentProfile, user=request.user)
    form = StudentProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profil mis à jour !')
        return redirect('dashboard_etudiant')
    return render(request, 'registration/update_profile.html', {'form': form, 'profile': profile})

# ─── ADMIN ──────────────────────────────────────────────────────────────────
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'ADMIN')

@login_required
def dashboard_admin(request):
    if not is_admin(request.user):
        return redirect('home')
    stats = {
        'etudiants': User.objects.filter(role='ETUDIANT').count(),
        'entreprises': EntrepriseProfile.objects.count(),
        'entreprises_validees': EntrepriseProfile.objects.filter(valide=True).count(),
        'entreprises_attente': EntrepriseProfile.objects.filter(valide=False).count(),
        'encadrants': User.objects.filter(role='ENCADRANT').count(),
        'offres': OffreStage.objects.count(),
        'offres_actives': OffreStage.objects.filter(publie=True).count(),
        'candidatures': Candidature.objects.count(),
        'stages': Stage.objects.count(),
        'stages_en_cours': Stage.objects.filter(statut='EN_COURS').count(),
        'stages_termines': Stage.objects.filter(statut='TERMINE').count(),
    }
    candidatures_recentes = Candidature.objects.select_related('etudiant','offre').order_by('-date_postulation')[:8]
    inscrits_recents = User.objects.order_by('-date_joined')[:8]
    entreprises_attente = EntrepriseProfile.objects.filter(valide=False).select_related('user')
    return render(request, 'dashboards/admin.html', {
        'stats': stats, 'candidatures_recentes': candidatures_recentes,
        'inscrits_recents': inscrits_recents, 'entreprises_attente': entreprises_attente})

@login_required
def admin_entreprises(request):
    if not is_admin(request.user):
        return redirect('home')
    entreprises = EntrepriseProfile.objects.select_related('user').order_by('valide','nom_entreprise')
    return render(request, 'admin_pages/entreprises.html', {'entreprises': entreprises,
                  'nb_en_attente': entreprises.filter(valide=False).count()})

@login_required
def valider_entreprise(request, pk):
    if not is_admin(request.user):
        return redirect('home')
    profile = get_object_or_404(EntrepriseProfile, pk=pk)
    profile.valide = not profile.valide
    profile.save()
    statut = "validée ✅" if profile.valide else "suspendue ❌"
    messages.success(request, f'Entreprise {profile.nom_entreprise} {statut}')
    notifier(profile.user, 'ENTREPRISE_VALIDEE', f'Compte entreprise {statut}',
             f'Votre compte « {profile.nom_entreprise} » a été {statut} par l\'administration.',
             '/dashboard/entreprise/')
    return redirect('admin_entreprises')

@login_required
def admin_utilisateurs(request):
    if not is_admin(request.user):
        return redirect('home')
    users = User.objects.all().order_by('role','last_name')
    return render(request, 'admin_pages/utilisateurs.html', {'users': users})

# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────
@login_required
def notifications_liste(request):
    notifs = Notification.objects.filter(destinataire=request.user)
    notifs.filter(lu=False).update(lu=True)
    return render(request, 'notifications/liste.html', {'notifications': notifs})

@login_required
def notification_lue(request, pk):
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.lu = True
    notif.save()
    return redirect(notif.lien or 'notifications_liste')

@login_required
def notifications_tout_lire(request):
    Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
    return redirect('notifications_liste')
