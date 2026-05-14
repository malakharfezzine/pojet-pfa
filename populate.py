from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from gestion_stage.models import *

class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de démonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Création des données...')

        # ADMIN
        if not User.objects.filter(username='superadmin').exists():
            u = User.objects.create_superuser('superadmin', 'admin@portailstages.ma', 'Admin@2026!')
            u.role = 'ADMIN'; u.first_name = 'Super'; u.last_name = 'Admin'; u.save()

        # ENTREPRISES (5)
        entreprises_data = [
            ('techwave', 'Karim', 'Benjelloun', 'TechWave Maroc', 'Développement Web & Mobile', 'Techwave@2026', 'ICE001234', True),
            ('datamaroc', 'Fatima', 'Chraibi', 'DataMaroc Solutions', 'Intelligence Artificielle', 'Data@Maroc26', 'ICE002345', True),
            ('cloudsys', 'Youssef', 'Alaoui', 'CloudSys Casablanca', 'Cloud & DevOps', 'Cloud@Sys26', 'ICE003456', True),
            ('securenet', 'Nadia', 'Tazi', 'SecureNet Maroc', 'Cybersécurité', 'Secure@Net26', 'ICE004567', False),
            ('innova', 'Hassan', 'Moussaoui', 'InnovaGroup', 'Conseil IT', 'Innova@2026', 'ICE005678', True),
        ]
        ent_users = []
        for username, fn, ln, nom, secteur, pwd, ice, valide in entreprises_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@exemple.ma', pwd)
                u.role = 'ENTREPRISE'; u.first_name = fn; u.last_name = ln; u.save()
                EntrepriseProfile.objects.create(user=u, nom_entreprise=nom, secteur=secteur,
                    adresse=f'Boulevard Mohammed V, Casablanca', telephone=f'0522{ice[-3:]}000',
                    ice=ice, valide=valide)
            ent_users.append(User.objects.get(username=username))

        # ENCADRANTS (5)
        encadrants_data = [
            ('pr.lamrani', 'Mustapha', 'Lamrani', 'ENC001', 'Génie Logiciel', 'B201', 'Lamrani@Enc26'),
            ('pr.bennani', 'Houda', 'Bennani', 'ENC002', 'Intelligence Artificielle', 'A104', 'Bennani@Enc26'),
            ('pr.zaki', 'Omar', 'Zaki', 'ENC003', 'Réseaux & Cybersécurité', 'C305', 'Zaki@Enc26'),
            ('pr.rafik', 'Sanaa', 'Rafik', 'ENC004', 'Big Data & Cloud', 'B110', 'Rafik@Enc26'),
            ('pr.idrissi', 'Mehdi', 'Idrissi', 'ENC005', 'Développement Web', 'A207', 'Idrissi@Enc26'),
        ]
        enc_users = []
        for username, fn, ln, mat, spec, bureau, pwd in encadrants_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@ecole.ma', pwd)
                u.role = 'ENCADRANT'; u.first_name = fn; u.last_name = ln; u.save()
                EncadrantProfile.objects.create(user=u, matricule=mat, specialite=spec, bureau=bureau)
            enc_users.append(User.objects.get(username=username))

        # ÉTUDIANTS (5)
        etudiants_data = [
            ('sara.mansouri', 'Sara', 'Mansouri', 'CNE2021001', 'Génie Informatique', '3', '0612111111', 'Sara@Etu26'),
            ('amine.berrada', 'Amine', 'Berrada', 'CNE2021002', 'Génie Logiciel', '3', '0612222222', 'Amine@Etu26'),
            ('leila.ouali', 'Leila', 'Ouali', 'CNE2022001', 'Big Data & IA', '2', '0612333333', 'Leila@Etu26'),
            ('khalid.tahiri', 'Khalid', 'Tahiri', 'CNE2022002', 'Réseaux & Télécom', '2', '0612444444', 'Khalid@Etu26'),
            ('imane.cherkaoui', 'Imane', 'Cherkaoui', 'CNE2023001', 'Génie Informatique', '1', '0612555555', 'Imane@Etu26'),
        ]
        etu_users = []
        for username, fn, ln, cne, filiere, niveau, tel, pwd in etudiants_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@etudiant.ma', pwd)
                u.role = 'ETUDIANT'; u.first_name = fn; u.last_name = ln; u.save()
                StudentProfile.objects.create(user=u, cne=cne, filiere=filiere, niveau=niveau, telephone=tel)
            etu_users.append(User.objects.get(username=username))

        # OFFRES (8)
        offres_data = [
            (ent_users[0], 'Développement Application React/Django', 'Développez une application web complète en React et Django REST Framework. Vous travaillerez au sein d\'une équipe agile.', 'PERFECTIONNEMENT', 'Développement Web', 'React, Django, Python, REST API', 3, 2000, 45),
            (ent_users[0], 'Stage DevOps & CI/CD', 'Mise en place de pipelines CI/CD avec Jenkins et Docker. Automatisation du déploiement sur AWS.', 'PFE', 'DevOps', 'Docker, Jenkins, AWS, Linux', 6, 3000, 60),
            (ent_users[1], 'Machine Learning & Analyse de Données', 'Développement de modèles de machine learning pour la prédiction des comportements clients.', 'PFE', 'Intelligence Artificielle', 'Python, Scikit-learn, TensorFlow, Pandas', 6, 2500, 30),
            (ent_users[1], 'NLP & Chatbot IA', 'Création d\'un chatbot intelligent basé sur les LLMs pour le service client.', 'PFA', 'Intelligence Artificielle', 'Python, NLP, Transformers, FastAPI', 4, 2000, 20),
            (ent_users[2], 'Infrastructure Cloud Azure', 'Migration d\'infrastructure on-premise vers Microsoft Azure. Gestion des ressources cloud.', 'PERFECTIONNEMENT', 'Cloud Computing', 'Azure, Terraform, PowerShell, Docker', 3, 1500, 15),
            (ent_users[2], 'Administration Système Linux', 'Stage d\'initiation à l\'administration des systèmes Linux et aux outils DevOps.', 'INITIATION', 'Systèmes & Réseaux', 'Linux, Bash, Ansible', 2, 0, 30),
            (ent_users[4], 'Développement Mobile Flutter', 'Développement d\'une application mobile cross-platform avec Flutter/Dart.', 'PFA', 'Développement Mobile', 'Flutter, Dart, Firebase, REST API', 4, 1800, 25),
            (ent_users[4], 'Sécurité des Applications Web', 'Audit de sécurité et tests de pénétration sur des applications web. Rédaction de rapports.', 'PERFECTIONNEMENT', 'Cybersécurité', 'OWASP, Burp Suite, Python', 3, 2200, 10),
        ]
        offres = []
        for ent, titre, desc, type_s, domaine, comp, duree, rem, jours in offres_data:
            o, created = OffreStage.objects.get_or_create(titre=titre, entreprise=ent, defaults={
                'description': desc, 'type_stage': type_s, 'domaine': domaine, 'competences': comp,
                'duree': duree, 'remuneration': rem, 'date_limite': date.today() + timedelta(days=jours), 'publie': True})
            offres.append(o)

        # CANDIDATURES & STAGES
        cand_data = [
            (etu_users[0], offres[0], 'ACCEPTEE', 'Je suis très motivée par ce poste et maîtrise React et Django.'),
            (etu_users[0], offres[2], 'EXAMEN', 'Passionnée par le ML, j\'ai réalisé plusieurs projets en Python.'),
            (etu_users[1], offres[0], 'EXAMEN', 'Développeur web avec expérience en React et DRF.'),
            (etu_users[1], offres[1], 'ACCEPTEE', 'DevOps enthousiaste, j\'ai pratiqué Docker et Jenkins.'),
            (etu_users[2], offres[2], 'ACCEPTEE', 'Big Data & IA est ma spécialité, maîtrise de TensorFlow.'),
            (etu_users[2], offres[3], 'CREEE', 'Intéressée par le NLP, j\'ai réalisé un projet chatbot.'),
            (etu_users[3], offres[5], 'EXAMEN', 'Je souhaite débuter en administration système Linux.'),
            (etu_users[3], offres[7], 'CREEE', 'La cybersécurité est ma passion depuis 2 ans.'),
            (etu_users[4], offres[4], 'CREEE', 'Intéressée par le Cloud Azure pour ma 1ère expérience.'),
            (etu_users[4], offres[6], 'ACCEPTEE', 'Flutter est mon framework de prédilection depuis 1 an.'),
        ]
        candidatures = []
        for etu, offre, statut, lettre in cand_data:
            c, _ = Candidature.objects.get_or_create(etudiant=etu, offre=offre, defaults={
                'lettre_motivation': lettre, 'statut': statut})
            if c.statut != statut:
                c.statut = statut; c.save()
            candidatures.append(c)

        # STAGES pour les candidatures ACCEPTEE
        stages_data = [
            (candidatures[0], enc_users[4], date(2026,3,1), None, 'EN_COURS', None),
            (candidatures[3], enc_users[2], date(2026,2,15), date(2026,5,15), 'TERMINE', 17.5),
            (candidatures[4], enc_users[1], date(2026,3,10), None, 'EN_COURS', None),
            (candidatures[9], enc_users[0], date(2026,4,1), date(2026,5,31), 'VALIDE', 19.0),
        ]
        for cand, enc, debut, fin, statut, note in stages_data:
            s, _ = Stage.objects.get_or_create(candidature=cand, defaults={
                'encadrant': enc, 'date_debut': debut, 'date_fin': fin, 'statut': statut, 'note': note})

        # NOTIFICATIONS de démonstration
        for etu in etu_users[:3]:
            Notification.objects.get_or_create(
                destinataire=etu, titre='Bienvenue sur PortailStages !',
                defaults={'type_notif': 'INFO', 'message': 'Découvrez les offres disponibles et postulez dès maintenant.',
                          'lien': '/offres/', 'lu': False})
        for ent in ent_users[:3]:
            Notification.objects.get_or_create(
                destinataire=ent, titre='Nouvelle candidature reçue',
                defaults={'type_notif': 'CANDIDATURE_RECUE', 'message': 'Un étudiant a postulé à l\'une de vos offres.',
                          'lien': '/dashboard/entreprise/', 'lu': False})

        self.stdout.write(self.style.SUCCESS('''
========================================================
  BASE DE DONNÉES CRÉÉE AVEC SUCCÈS !
========================================================

  ADMIN
  Username : superadmin       | Mot de passe : Admin@2026!

  ÉTUDIANTS
  Username : sara.mansouri    | Mot de passe : Sara@Etu26
  Username : amine.berrada    | Mot de passe : Amine@Etu26
  Username : leila.ouali      | Mot de passe : Leila@Etu26
  Username : khalid.tahiri    | Mot de passe : Khalid@Etu26
  Username : imane.cherkaoui  | Mot de passe : Imane@Etu26

  ENTREPRISES
  Username : techwave         | Mot de passe : Techwave@2026
  Username : datamaroc        | Mot de passe : Data@Maroc26
  Username : cloudsys         | Mot de passe : Cloud@Sys26
  Username : securenet        | Mot de passe : Secure@Net26  (non validée)
  Username : innova           | Mot de passe : Innova@2026

  ENCADRANTS
  Username : pr.lamrani       | Mot de passe : Lamrani@Enc26
  Username : pr.bennani       | Mot de passe : Bennani@Enc26
  Username : pr.zaki          | Mot de passe : Zaki@Enc26
  Username : pr.rafik         | Mot de passe : Rafik@Enc26
  Username : pr.idrissi       | Mot de passe : Idrissi@Enc26

========================================================
'''))
