import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
from io import BytesIO
import pickle as pkl
import joblib
import tensorflow as tf
import base64
import time

# Connexion à la base de données SQLite
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Création de la table pour les informations personnelles
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, email TEXT, phone TEXT, contry TEXT, province TEXT, region INTEGER, language TEXT, religion TEXT, password TEXT, profile_pic IMAGE)''')
conn.commit()

# Ajouter la colonne profile_pic à la table users si elle n'existe pas déjà
try:
    c.execute('ALTER TABLE users ADD COLUMN profile_pic BLOB')
except sqlite3.OperationalError:
    pass

# Création de la table pour les informations personnelles
c.execute('''CREATE TABLE IF NOT EXISTS user_info (username TEXT, age INTEGER, gender TEXT, marital_status TEXT, children INTEGER, education_level TEXT, salary REAL, wakeup_time TEXT, partners INTEGER, hobbies TEXT, prefered_color TEXT)''')
conn.commit()

# Fonction pour ajouter un nouvel utilisateur
def add_user(username, email, phone, country, province, region, language, religion, password, profile_pic):
    c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (username, email, phone, country, province, region, language, religion, password, profile_pic))
    conn.commit()

# Fonction pour vérifier les informations de connexion
def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    return c.fetchone()

# Fonction pour ajouter des informations personnelles
def add_user_info(username, age, gender, marital_status, children, education_level, salary, wakeup_time, partners, hobbies, prefered_color):
    c.execute('INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
              (username, age, gender, marital_status, children, education_level, salary, wakeup_time, partners, hobbies, prefered_color))
    conn.commit()

# Fonction pour vérifier si l'utilisateur a déjà renseigné ses informations personnelles
def check_user_info(username):
    c.execute('SELECT * FROM user_info WHERE username = ?', (username,))
    return c.fetchone()

# Fonction pour récupérer la photo de profil de l'utilisateur
def get_profile_pic(username):
    c.execute('SELECT profile_pic FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    return result[0] if result else None

# Fonction pour mettre à jour les informations personnelles de l'utilisateur
def update_user_info(username, age, gender, marital_status, children, education_level, salary, wakeup_time, partners, hobbies, prefered_color, profile_pic=None):
    if profile_pic:
        c.execute('''UPDATE users SET profile_pic = ? WHERE username = ?''', (profile_pic, username))
    c.execute('''UPDATE user_info SET age = ?, gender = ?, marital_status = ?, children = ?, education_level = ?, salary = ?, wakeup_time = ?, partners = ?, hobbies = ?, prefered_color = ? 
                 WHERE username = ?''', (age, gender, marital_status, children, education_level, salary, wakeup_time, partners, hobbies, prefered_color, username))
    conn.commit()

# Page d'inscription
def signup_page():
    st.title("Inscription")

    username = st.text_input("Nom d'utilisateur")
    email = st.text_input("Adresse e-mail")
    phone = st.text_input("Numéro de téléphone")
    country = st.text_input("Pays")
    province = st.text_input("Province")
    region = st.text_input("Région")
    langue = ["Anglais", "Français", "Swahili", "Lingala", "Chiluba", "Kikongo", "Kinyarwanda", "Autre"]
    language = st.selectbox("Langue parlée", langue)
    religion = st.selectbox("Religion", ["Chrétien", "Musulman", "Kimbangiste", "Animiste", "Autre"])
    password = st.text_input("Mot de passe", type='password')
    profile_pic = st.file_uploader("Importer une photo de profil", type=["jpg", "jpeg", "png"])

    if profile_pic is not None:
        profile_pic = profile_pic.read()

    #st.button("Entrer vos informations en cliquant sur ce bouton")
    st.title("Informations Personnelles")
    age = st.number_input("Âge", min_value=0)
    gender = st.selectbox("Genre", ["Homme", "Femme", "Autre"])
    marital_status = st.selectbox("État civil", ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
    children = st.number_input("Nombre d'enfants", min_value=0)
    education_level = st.selectbox("Niveau d'études", ["École primaire", "Lycée", "Université", "Master", "Doctorat"])
    salary = st.number_input("Salaire", min_value=0.0)
    wakeup_time = st.number_input("Heure de réveil", min_value = 0.00, max_value = 12.00, step = 0.01)
    partners = st.number_input("Nombre de partenaires", min_value=0)
    hobbies = st.text_input("Occupations ou centres d'intérêt")
    prefered_color = st.text_input("Entrer votre couleur préférée")
        
                
    if st.button("Sauvegarder les informations"):
        add_user(username, email, phone, country, province, region, language, religion, password, profile_pic)
        add_user_info(username, age, gender, marital_status, children, education_level, salary, wakeup_time, partners, hobbies, prefered_color)
        st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")

# Page de connexion
def login_page():
    st.title("Connexion")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type='password')

    if st.button("Se connecter"):
        user = login_user(username, password)
        if user:
            st.success("Connexion réussie !")
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

# Page principale
def main_page(username):
    profile_pic = get_profile_pic(username)
    if profile_pic is not None:
        st.sidebar.markdown("""<style>.profile_pic {border-radius: 50%; /* Rendre l'image circulaire */ width: 100px; /* Largeur souhaitée */ height: 100px; /* Hauteur souhaitée */ object-fit: cover; /* Couvrir l'espace sans déformer l'image */} <style>""", unsafe_allow_html = True)
        
        #st.sidebar.image(BytesIO(profile_pic), use_container_width= False, width = 100, caption = "", output_format = "auto") #ceci est mis en commentaire pour éviter la répétition de l'image encadré dans un carré.
        
        st.sidebar.markdown('<img src = "data:image/jpg;base64,{0}" class = "profile_pic" />'.format(base64.b64encode(profile_pic).decode()), unsafe_allow_html = True)
    
    # Afficher les éventualités/possibilités de passage d'une page à l'autre
    st.sidebar.title("Menu")
    option = st.sidebar.radio("Aller à :", ["Mon compte", "Accueil", "Prédiction", "Documentation", "Contacter le programmeur"])
    
    if option == "Accueil":
        with st.spinner("Veillez patientez..."):
            import time
            debut1 = time.time()
            st.title("Accueil")
            #st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{"""Bienvenue dans l'application !"""}</div>", unsafe_allow_html=True)
        
            st.subheader("Bienvenue dans l'application !")
            #st.write("Cette application aux multiples fonctions est avant tout un outil incontournable de prédiction de la consommation énergetique pour les opérations de chauffage et refroidissement dans une industrie minière. Basée sur l'intélligence artificille, cet outil est une application directe de l'intélligence artificielle dans le secteur minier. Cette application offre, à tout utilisateur iscrit sur notre base de données, la possibilité de charger et prédire les cibles avec un maximum de huit caractérisques propres à la mine, avec une précision de plus de 99% contre une erreur quadratique moyenne d'environ 0,44. Entrainé sur des données de l'UCI, le modèle de neurones artificiels en charge de la prédiction a montré, avec succès, une performance excellente rapportée par une précision maximale impliquant un coefficient de détermination de 100% contre une erreur quadratique moyenne nulle en entrainnemnt.")
            text1 = """Cette application aux multiples fonctions est avant tout un outil incontournable de prédiction de la consommation énergetique pour les opérations de chauffage et refroidissement dans une industrie minière. Basée sur l'intélligence artificille, cet outil est une application directe de l'intélligence artificielle dans le secteur minier. Cette application offre, à tout utilisateur iscrit sur notre base de données, la possibilité de charger et prédire les cibles avec un maximum de huit caractérisques propres à la mine, avec une précision de plus de 99% contre une erreur quadratique moyenne d'environ 0,44. Entrainé sur des données de l'UCI, le modèle de neurones artificiels en charge de la prédiction a montré, avec succès, une performance excellente rapportée par une précision maximale impliquant un coefficient de détermination de 100% contre une erreur quadratique moyenne nulle en entrainnemnt."""
            st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text1}</div>", unsafe_allow_html=True) #pour la justification du text1 et son écriture dans le style Times New Roman

            text2 = """Dans un soucis de développent de cette application, les informations personnelles relatives à l'utilisateur sont enregistrées dans la base de données et servent/serviront de données pour une amélioration de cette application. Néanmoins, nous garantissons à l'utilisateur la sécurité de ses informations et un total annonymat. Les données sauvegardées sont conservées pour servir de base de données nécessaire à la possible élaboration d'un modèle, plus sûr et plus rigureux, de prédiction de la profession. Dans une perspective de respect de consentement de l'utilisateur, ce dernier est libre de modifier à tout moment ces informations. Nous suggérons donc à l'utilisateur de supprimer ces informations avec une mention <span style='font-size: 12px;color:blue; text-decoration: underline;'>FAUSSES INFORMATIONS</span> dans la rubrique de la réligion pour permettre un tri entre les informations devant servir d'entrainnement au prochain modèle de Machine Learning"""
            st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text2}</div>", unsafe_allow_html=True) #pour la justification du text2

            #st.write("Dans un soucis de développent de cette application, les informations personnelles relatives à l'utilisateur sont enregistrées dans la base de données et servent/serviront de données pour une amélioration de cette application. Néanmoins, nous garantissons à l'utilisateur la sécurité de ses informations et un total annonymat. Les données sauvegardées sont conservées pour servir de base de données nécessaire à la possible élaboration d'un modèle, plus sûr et plus rigureux, de prédiction de la profession. Dans une perspective de respect de consentement de l'utilisateur, ce dernier est libre de modifier à tout moment ces informations. Nous suggérons donc à l'utilisateur de supprimer ces informations avec une mention FAUSSES INFORMATIONS dans la rubrique de la réligion pour permettre un tri entre les informations devant servir d'entrainnement au prochain modèle de Machine Learning.")
        
            #st.write("Ainsi, nous vous souhaitons une meilleure expérience avec cette application. N'hésitez pas à nous faire part de vos questions, préoccupations, suggéstions et appréciations dans la rubrique CONTACTER LE PROGRAMMEUR ou de consulter la rubrique DOCUMENTATION pour tout savoir sur cette application et sur son fonctionnement")
        
            text3 = """Ainsi, nous vous souhaitons une meilleure expérience avec cette application. N'hésitez pas à nous faire part de vos questions, préoccupations, suggéstions et appréciations dans la rubrique <span style='font-size: 12px;color:blue; text-decoration: underline;'>CONTACTER LE PROGRAMMEUR</span> ou de consulter la rubrique <span style='font-size: 12px;color:blue; text-decoration: underline;'>DOCUMENTATION</span> pour tout savoir sur cette application et sur son fonctionnement."""
            st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text3}</div>", unsafe_allow_html=True) #pour la justification du text3
            fin1 = time.time()
            temps1 = fin1 - debut1
            time.sleep(temps1)
                 
    elif option == "Prédiction":
        st.title("Prédiction")
        text4 = """Ici, vous pourrez faire des prédictions avec un modèle de Machine Learning selon vos préférences. L'application vous offre la possibilité de choisir entre le modèle de <span style='font-size: 18px;color:blue; text-decoration: underline'>reseau de neurones artificiels</span> (RNA) et le modèle <span style='font-size: 18px;color:blue; text-decoration: underline'>Gradient Boosting Machine</span> (GBM). En choisissant le modèle RNA vous avez une seule sortie qui réprend la charge de chauffage et la charge de réfroidissement. Cependant, en choisissant le modèle GBM vous avez deux sorties qui correspondent respectivement à la charge de chauffage et la charge de réfroidissement."""
        st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text4}</div>", unsafe_allow_html=True) #pour la justification du text4
        
        #Choix de l'utilisateur
        st.write("                    ")
        st.write("                    ")
        choix = st.radio("Que souhaitez-vous faire ?",("Charger un fichier", "Insérer un tableau sous forme d'une matrice"))
        if choix == "Charger un fichier":
            fichier = st.file_uploader("Choisissez un fichier CSV ou XLSX", type = ["csv", "xlsx"])
            if fichier is not None:
                # Vérifier le type de fichier et le lire
                if fichier.name.endswith('.csv'):
                    df = pd.read_csv(fichier)
                elif fichier.name.endswith('.xlsx'):
                    df = pd.read_excel(fichier)
            # Affichage du fichier chargé
            donnees_chargees = st.write("Voici les données chargées");
            st.dataframe(df)
            # Choix du modèle à utiliser
            st.write("                    ")
            st.write("                    ")
            choix_model1 = st.radio("Quel modèle souhaitez-vous utiliser ?",("Reseau de neurones", "Gradient Boosting Machine"))
            if choix_model1 == "Reseau de neurones":
                #Chargement du modèle entrainé
                model_neurones = joblib.load("FinProjAIBac3.pkl")

                # Prédiction des valeurs chargées ou de la matrice insérée
                y_pred_reel = model_neurones.predict(df)
                st.write("Les résultats de la prédiction sont :")
                st.dataframe(y_pred_reel)
            else:
                st.write("Modèle GBM")
                #Chargement du modèle entrainné pour la première sortie
        
        else:
            num_rows = st.number_input("Entrer le nombre de lignes de votre tableau de 8 colonnes", min_value = 1, max_value = 10000, step = 1)
            # Création d'un DataFrame vide avec 8 colonnes
            matrix = np.zeros((num_rows,8))
            df = pd.DataFrame(matrix, columns = [f'Colonne {i+1}' for i in range(8)])
            
            # Saisie des valeurs dans la matrice
            for i in range(num_rows):
                st.write(f"Ligne {i+1}:")
                for j in range(8):
                    valeurs = st.number_input(f"Valeur pour colonne {j+1} (Ligne {i+1}) :", value = 0.00, key = f"input_{i}_{j}")
                    df.iloc[i, j] = valeurs   
            # Affichage de la matrice saisie
            st.write("Voici la matrice saisie :")
            st.dataframe(df)
            # Choix du modèle à utiliser
            st.write("                    ")
            st.write("                    ")
            choix_model2 = st.radio("Quel modèle souhaitez-vous utiliser ?",("Reseau de neurones", "Gradient Boosting Machine"))
            if choix_model2 == "Reseau de neurones":
                import joblib
                #Chargement du modèle entrainé
                model_neurones = joblib.load("FinProjAIBac3.pkl")

                # Prédiction des valeurs chargées ou de la matrice insérée
                import time
                debut2 = time.time()
                y_pred_reel1 = model_neurones.predict(df)
                st.write("Les résultats de la prédiction sont :")
                st.dataframe(y_pred_reel1)
                fin2 = time.time()
                temps_neurones = fin2 - debut2
                temps_neurones_arrondi = round(temps_neurones, 3)
                st.write(f"Le temps nécessaire pour réaliser cette prédiction a été de {temps_neurones_arrondi} secondes")
            else:
                #Chargement du modèle entrainné pour la première et deuxième sortie
                import joblib
                import pickle as pkl
                #model_MLP = joblib.load("FinProjAIBAC3_MLP.pkl")
                #model_gbm_1 = joblib.load("FinProjAIBac3GBM1.pkl")
                #model_gbm_2 = joblib.load("FinProjAIBac3GBM2.pkl")
                st.error("Désolé ! Cette fonctionnalité n'est pas disponible pour cette version. Veillez rester branché pour la nouvelle version")

    elif option == "Documentation":
        st.title("Documentation")
        possibilites = st.radio("Vous êtes intérressé par", ["La documentation technique", "La documentation utilisateur"])
        if possibilites == "La documentation technique":
            option_1 = st.pills("Que voule-vous savoir ?", ["Le rojet", "Les données", "L'outil de prédiction", "Le code source"])
            if option_1 == "Le rojet":
                text5 = """Ce logiciel intervient dans le cadre du projet de prédiction des coûts énergétiques dans les processus miniers. Il vise à développer un modèle pour estimer la consommation énergétique des processus industriels dans le secteur minier. Pour ce faire, les données d'entrée sont récoltées dans le cas d'une mine spécifique et les prédictions sont basées sur des modèles de Machhine Learning. Le but est de prédire la charge de chaffage et la charge de réfroidissement dans une mine spécifique."""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text5}</div>", unsafe_allow_html=True) #pour la justification du text5
            elif option_1 == "Les données":
                text6 = """L'ensemble de données sur l'efficacité énergétique provenant de l'UCI est utilisé pour former entrainner modèles. Les huit premières colonnes de données représentent les caractéristiques propres à l'industrie, pendant que les deux dernières colonnes font référence aux sorties ou cibles visées. En dépit du fait que ces données semblent s'écarter du contexte minier, dans le cadre de ce projet fictif, elles sont partitionnées en données d'entrainnement. Quatre vingts pourcents de ces données sont utilisés en entrainnemnt contre vingt pourcent en test. Pour en savoir plus sur les données UCI basées sur The Energy Efficiency, veillez suivre le lien ci-après :"""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text6}</div>", unsafe_allow_html=True) #pour la justification du text6
                st.write("[Energy Efficiency Data Set (UCI)](https://archive.ics.uci.edu/ml/datasets/Energy+efficiency)")
                st.divider()
                text6_1 = """Ci-dessous les données utilisées pour l'entrainnement et le test des modèles :"""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text6_1}</div>", unsafe_allow_html=True) #pour la justification du text6_1
                import pandas as pd
                df_donnees = pd.read_excel("energy_efficiency.xlsx")
                donnees_model = st.table(df_donnees) # cette commande tranforme la dataframe en tableau
            elif option_1 == "L'outil de prédiction":
                text7 = """Les données étant des nombres réels et pas exclusivement entiers, il s'est averé que ce problème ne peut se ramener à une classification. Il s'agit d'une régression. Pour ce faire, plusieurs modèles de regression ont été séléctionnées, entrainnés et testés respectivement sur l'ensemble des données d'entrainnement et de données de test. Les modèles ont été valués selon leurs erreurs quadratiques moyennes et leurs coéfficients de déterminations respectifs. Ce long processus, qui a regroupé plus d'une trentaine de modèles de régression, s'est conclu par le choix de deux modèles par excellence qui ont montré leur maitrise quant à l'appentissage des liens entre les données en place. Il s'agit du modèle de reseau de neurones artificiels (RNA) et le modèle GBM (Gradient Boosting Machine). Le RNA est optimisé par la méthode d'optimisation par descente de gradient en paquets et amélioré, appelé Adam, et par le MSE (pour l'optimisation des erreurs). La fonction d'activation pour ce modèle est la tangente hyperbolique. Pour en savoir plus sur ces concepts, veillez cliquer sur les liens ci-dessous :"""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text7}</div>", unsafe_allow_html=True) #pour la justification du text7
                st.write("""[Gradient Boosting Machines (GBM)](https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)""")
                st.write(""" [Introduction aux Réseaux de Neurones](https://fr.wikipedia.org/wiki/R%C3%A9seau_de_neurones_artificiel)""")
                st.write("""[Machine Learning pour l'Efficacité Énergétique](https://www.sciencedirect.com/science/article/pii/S0360132317300505)""")
                st.divider()
                text7_1 = """Ci-dessous sont présentés les performations des modèles retenues pour ce projet, où la flèche rouge descendante fait référence à une possible optimisation de l'erreur quadratique moyenne (MSE) et r2 est le coefficient de détermination :"""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text7_1}</div>", unsafe_allow_html=True) #pour la justification du text7_1
                col1, col2, col3 = st.columns(3)
                col1.metric("RNA", "r2 = 0.995", "MSE = 0.448", "inverse", border = True)
                col2.metric("GBM cible 1", "r2 = 0.999", "MSE = 0.109", "inverse", border = True )
                col3.metric("GBM cible 2", "r2 = 0.996", "MSE = O.346", "inverse", border = True)
            
            else:
                option_2 = st.segmented_control("Veillez cliquez sur la partie qui vous intéresse", ["Production du code", "Documentation du code", "Déploiement du logiciel"])
                if option_2 == "Production du code":
                    text8 = """Le code source pour le modèle s'est effectué dans Jypyter Notebook. La bibliothèque scikit-learn a été d'une grande importance dans la production de ce code. Les lignes de code sont réalisées avec la plus haute simplicité. Les mots clés, renvoyant aux variabes dans leur contexte de la vie réelle, sont écrits soit en anglais soit en français, selon les préférences du développeur. Le code suit un cheminnement logique: du début à la fin, la complexité du code varie en augmenant. Un effort est toutefois fourni afin de maintenir ce dode plus lisible, lair et facile à intérpreter. Quant au code source du logiciel, il a été implementé dans Python grâce à la bibliothèque streamlit. Le SGBD a été assuré par DB Browser SQLite pour une petite base de données servant à enregistrer les informations de l'utilisateur tout en lui garantissant libre accès à son compte. Vous pouvez trouver ce code source sur le compte GitHub du développeur en suivant le lien ci-dessous :"""
                    st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text8}</div>", unsafe_allow_html=True) #pour la justification du text8
                    st.write("[Compte GitHub du développeur](https://github.com/rug15)""")
                elif option_2 == "Documentation du code":
                    text9 = """Les deux codes sources sont docmentés presque à chaque ligne de code. Cette documentation est en français. Elle permettra de faciliter les futurs développements de ce logiciel. Le développeur a foi en ces documentations, en ce sens qu'elles sont claires. Les commentaires sont ajustés régulièrement de manière à ne pas interférer avec les lignes de codes et compliquer les résultats. Ces espacements permettent, en outre, à tout futur développeur en charge de l'évolution de cette application, de pouvroir facilemnt suivre le rythme et gagner en temps. Dans ce code, les commentaires sont souvent de la forme suivante :"""
                    st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text9}</div>", unsafe_allow_html=True) #pour la justification du text9
                    st.code("model = GradientBoostingRegressor(n_estimators=20000, random_state=50)  #choiw du modèle")
                    st.code("model.fit()  #entrainnement du modèle")
                    st.code("y_pred = model.pred()  #prédiction des cibles par le modèle entrainné")
                else:
                    text10 = """Le déploiement de cette application s'est fait sur streamlit. En fusionnant le Cloud du GitHub et Streamlit, Streamlit offre la possibilité de déploiement des applications. Le fait que l'application ait été déployé sur Streamlit en fait un contenu public modifiable par n'importe quel développeur sur le compte GitHub du développeur. Ainsi, le développeur attend du grand pubic expérimenté, une amélioration continue de cette application, dans le respect de son idée de conception: prédiction des charges énergétiques de chauffage et de réfroidissement dans une mine."""
                    st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text10}</div>", unsafe_allow_html=True) #pour la justification du text10
        else:
            option_3 = st.pills("Que voule-vous savoir", ["Inscription/Connexion", "Mon compte", "Prédiction", "Contacter le programmeur"])
            if option_3 == "Inscription/Connexion":
                text11 = """En entrant vos informations, par le remplissage de ce petit formulaire, vous intégrez notre communauté et avez donc accès à tout ce qui cadre avec cette application. Après vous être enregistré, rentrer vous connecter avec votre NOM D'UTILISATEUR et votre MOT DE PASSE tels que vous les avez sauvegardés dans la phase de l'inscription. Tachez de ne pas perdre votre mot de passe et de ne point oublier votre nom d'utilisateur pour pouvoir avoir accès de manière continue à votre compte. Cette version rudimentaire de l'application n'offre pas encore la possibilité de générer un nouveau mot de passe. Perdre vos informations de connexion revient à être contraint de refaire votre inscription."""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text11}</div>", unsafe_allow_html=True) #pour la justification du text11
            elif option_3 == "Mon compte":
                text12 = """La page MON COMPTE vous offre la possibilité de visualiser vos informations tellesque vous les avez sauvegardées dans la phase d'insciption. En outre, vous avez la possibilité de modifier vos informations personnelles en fonction de votre évolution selon votre convenance. Pour ce faire, il vous suffit d'entrer de nouvelles informations et, avant de quitter la page, de clique sur le boutons METTRE A JOUR LES MODIFICATIONS"""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text12}</div>", unsafe_allow_html=True) #pour la justification du text12
            elif option_3 == "Prédiction":
                text13 = """La page de prédiction vous offre la possibilité de charger vos données selon votre convenance: soit sous forme de fichier excel ou csv, ou soit sous forme d'une matrice de huit colonnes et de lignes à spécifier. Selon les données entrées, vous avez la possiblité de choisir entre le modèle de réseau de neurones ou le Gradient Boosting Machine. Les données de sortie sont présentées en fin de la page. Si vous choisissez le modèle du réseau de neurones comme modèle de prédiction, dans le tableau/la matrice qui s'affiche, la première colonne correspond à la charge de chauffage et la seconde correspond à la charge de réfroidissement."""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text13}</div>", unsafe_allow_html=True) #pour la justification du text13
            else:
                text14 = """La page CONTACTER LE PROGRAMMEUR est dédiée à la possibilité d'entrer en contact en les membres de l'équipe de projet qui ont mis sur pieds cette application. Selon l'orientation de votre discussion, vous trouverez les tâches assignées à chacun des membres de l'équipe. Cela permet de faciliter la conversation entre vous et l'équipe tout en vous faisant gagner en temps et en compétences cibles."""
                st.markdown(f"<div style='text-align:justify; font-family: \"Times New Roman\";'>{text14}</div>", unsafe_allow_html=True) #pour la justification du text14

    elif option == "Contacter le programmeur":
        import time
        debut_1 = time.time()

        st.header("👨‍💻 À PROPROPOS DES CRÉATEURS 🦺")
        st.write("Nous sommes une équipe de trois développeurs passionnés et Ingénieurs Civils des Mines.")
    
        def display_creator_info(name, bio, phone, email, social_links):
            st.subheader(name)
            st.write(bio)
            st.write(f"📞 {phone}")
            st.write(f"📧 [Email]({email})")
            st.write("🔗 Réseaux :")
            
            social_icons = '''
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                .icon_container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin: 20px 0;
                }
                .icon_lien {
                    display: inline-flex;
                    align-items: center;
                    text-decoration: none;
                    font-family: 'Lucida Sans';
                    color: inherit;
                }
                span {
                    margin-right: 8px;
                }
                .fa-facebook { color: blue; }
                .fa-instagram { color: red; }
                .fa-twitter { color: rgb(77, 158, 245); }
                .fa-tiktok { color: black; }
                .fa-linkedin { color: #0077b5; }
                .fa-whatsapp { color: #25D366; }
                .fa-github { color: black; }
                .fa-envelope { color: #EA4335; }
            </style>
            <div class="icon_container">'''
            
            for platform, link in social_links.items():
                social_icons += f'<a href="{link}" class="icon_lien" target="_blank"><span class="fab fa-{platform}"></span>{platform.capitalize()}</a>'
            
            social_icons += '</div>'
            st.markdown(social_icons, unsafe_allow_html=True)
        st.image("PHOTO22.jpg", caption="") 
        display_creator_info(
            
            "ASHUZA KULIMUSHI Ozias",
            "Développeur full-stack , passionnée par l'UI/UX et designer web.",
            "+243 971 418 729",
            "ashuzaozias@uob.ac.cd",
            
            {
                "facebook": "https://www.facebook.com/public/Ozias-Ashuza/",
                "instagram": "https://www.instagram.com/https://www.instagram.com/ozias_ashuza/",
                "twitter": "https://twitter.com/@AshuzaO",
                "tiktok": "https://www.tiktok.com/@ozias_as27/",
                "linkedin": "https://cd.linkedin.com/in/ozias-ashuza-7a6a18241",
                "whatsapp": "https://wa.me/+243971418729",
                "github": "https://github.com/AshuzaOzias/",
               
            }
        )
        st.markdown("---") 
        st.image("011.jpg", caption="Toutes choses concourent au bien... Rm8:28")  
        display_creator_info(
            "MAPENDANO NTUGULO Lebon",
            "Développeur back-end avec un amour pour la nature et la randonnée.",
            "+243 973 715 123",
            "lebonroy2@gmail.com",
            {
                "facebook": "https://www.facebook.com/lebon.ntugulo/",
                "instagram": "https://www.instagram.com/lebonroy2",
                "twitter": "https://twitter.com/lebonroy2",
                "linkedin": "https://cd.linkedin.com/in/lebon-roy-78922b2a1",
                "whatsapp": "https://wa.me/+243973715123",
                "github": "https://github.com/mapendanoNtugulo/",
                
            }
        )
        st.markdown("---")  
        st.image("1JON.jpg", caption="La diversité fait la beauté des vivants")        
        display_creator_info(
            "USHINDI RUGAMIKA Jonathan",
            "Chef de projet full-stack spécialisé.",
            "+243 992 766 814",
            "ushindirugamikajonathan@gmail.com",
            {
                "facebook": "https://www.facebook.com/jonathan_facebook",
                "instagram": "https://www.instagram.com/rugamika_jonathan/",
                "twitter": "https://twitter.com/jonathan_twitter",
                "linkedin": "https://cd.linkedin.com/in/ushindi-rugamika",
                "whatsapp": "https://wa.me/+243992766814",
                "github": "https://github.com/",
                
            }
        )

        st.markdown("---")  
        # Footer
        
        st.image("1A5.jpg", caption="Notre équipe")
        st.markdown("---")
        st.markdown("<p style='text-align: center;'>🌸 Merci de visiter notre application Streamlit 💫 | Fait avec ❤️ par notre équipe.</p>", unsafe_allow_html=True)
        st.balloons()
        st.toast('CONGRATULATIONS!', icon='🎉')
        fin_1 = time.time()
        ecart_temps = fin_1 - debut_1
        with st.spinner('Wait for it...'):
            time.sleep(ecart_temps)
        st.success("We did it !")
        st.divider()
        st.write("To rate the application")
        st.feedback("stars")

    elif option == "Mon compte": # Afficher les informations du compte utilisateur dans la section "Mon compte"
        st.title("Mon compte")
        if not check_user_info(username):
            st.write("Aucune information personnelle enregistrée.")
        else:
            user_info = check_user_info(username)
            st.write(f"Nom d'utilisateur : {username}")
            st.write(f"Âge : {user_info[1]}")
            st.write(f"Sexe : {user_info[2]}")
            st.write(f"État civil : {user_info[3]}")
            st.write(f"Nombre d'enfants : {user_info[4]}")
            st.write(f"Niveau d'études : {user_info[5]}")
            st.write(f"Salaire : {user_info[6]}")
            st.write(f"Heure de réveil : {user_info[7]}")
            st.write(f"Nombre de partenaires : {user_info[8]}")
            st.write(f"Occupations ou centres d'intérêt : {user_info[9]}")
            st.write(f"Couleur préférée : {user_info[10]}")

            st.write("Modifier les informations personnelles")
            profile_pic = st.file_uploader("Modifier la photo de profil", type=["jpg", "jpeg", "png"])
            age = st.number_input("Âge", min_value=0, value=user_info[1])
            gender = st.selectbox("Genre", ["Homme", "Femme","Autre"], index=["Homme", "Femme", "Autre"].index(user_info[2]))
            marital_status = st.selectbox("État civil", ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"], index=["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"].index(user_info[3]))
            children = st.number_input("Nombre d'enfants", min_value=0, value=user_info[4])
            education_level = st.selectbox("Niveau d'études", ["École primaire", "Lycée", "Université", "Master", "Doctorat"], index=["École primaire", "Lycée", "Université", "Master", "Doctorat"].index(user_info[5]))
            salary = st.number_input("Salaire", min_value=0.0, value=user_info[6])
            wakeup_time = st.number_input("Heure de réveil", min_value=0.00, max_value=12.00, step=0.01, value=float(user_info[7]))
            partners = st.number_input("Nombre de partenaires", min_value=0, value=user_info[8])
            hobbies = st.text_input("Occupations ou centres d'intérêt", value=user_info[9])
            prefered_color = st.text_input("Couleur préférée", value = user_info[10])

            if st.button("Mettre à jour les informations"):
                if profile_pic is not None:
                    profile_pic = profile_pic.read()
                update_user_info(username, age, gender, marital_status, children, education_level, salary, wakeup_time, partners, hobbies,prefered_color, profile_pic)
                st.success("Informations personnelles mises à jour avec succès !")

# Interface principale
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'show_main' not in st.session_state:
    st.session_state.show_main = False

if not st.session_state.logged_in:
    st.sidebar.title("Menu")
    choice = st.sidebar.selectbox("Choisissez une option", ["Se connecter", "S'inscrire"])

    if choice == "S'inscrire":
        signup_page()
    else:
        login_page()
else:
    if not st.session_state.show_main:
        main_page(st.session_state.username)
    else:
        show_app_options()