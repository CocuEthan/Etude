import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
#Cocu Ethan
# a) Fonctions utilitaires pour naviguer dans la base :
#i
def choisir_document():

    """
    Description :
        Ouvre une boîte de dialogue graphique permettant à l'utilisateur de
        sélectionner un fichier texte.

    Paramètres :
        Aucun.

    Retour :
        str, le chemin complet du fichier sélectionné.
             Retourne une chaîne vide si l'utilisateur clique sur Annuler.
    """
    root = tk.Tk()
    root.withdraw()
    text = [('Fichiers texte', '*.txt'), ('Tous les fichiers', '*.*')]
    chemin = filedialog.askopenfilename(title="Choisir un fichier",filetypes=text)
    root.destroy()
    return chemin

# Tests unitaires  Exercice a) i

def test_choisir_document():

    #cas simple
    print("\nACTION REQUISE (Cas simple 1/2) :")
    print("Une boîte de dialogue va s'ouvrir. Sélectionne n'importe quel fichier.")

    chemin = choisir_document()

    print(f"Résultat obtenu : '{chemin}'")
    assert chemin != "", "ÉCHEC (Cas simple) : Le résultat ne doit pas être vide."
    assert isinstance(chemin, str), "ÉCHEC (Cas simple) : Le résultat doit être une chaîne (str)."
    print(" Test (Cas simple) : Passé.")

    #cas limite
    print("\nACTION REQUISE (Cas limite 2/2) :")
    print("La boîte de dialogue va s'ouvrir. Clique sur 'Annuler'.")

    ch = choisir_document()

    print(f"Résultat obtenu : '{ch}'")
    assert ch == "", f"ÉCHEC (Cas limite) : Le résultat devait être '', mais a été '{ch}'"
    print(" Test (Cas limite) : Passé.")

    #cas erreur ici pas possible
    print("\n Tous les tests manuels sont passés avec succès !")
#test_choisir_document()

# ii


def lister_document(chemin):
    """
    Description :
        Liste tous les fichiers d'un dossier qui est un fichier texte".

    Paramètres :
        chemin  str, le chemin du dossier à analyser.

    Retour :
        list, une liste des noms de fichiers (str) finissant par .txt.
              Retourne une liste vide [] si le chemin est invalide.
    """
    contenu = []

    # Si le chemin n'est pas un dossier valide
    if not os.path.isdir(chemin):
        return contenu

    try:
        # Parcourt tous les éléments du dossier
        for i in os.listdir(chemin):
            ch = os.path.join(chemin, i)
            if os.path.isfile(ch) and i.endswith('.txt'):
                contenu.append(i)

    except PermissionError:
        pass

    return contenu

# Tests unitaires  Exercice a) ii
def test_lister_document_txt_filtre():

    # Setup test
    dir_test = "dossier_test_filtre_txt"
    dir_vide = os.path.join(dir_test, "vide")
    dir_sans_txt = os.path.join(dir_test, "sans_txt")
    dir_sous_dossier = os.path.join(dir_test, "un_sous_dossier")

    f1_txt = os.path.join(dir_test, "notes.txt")
    f2_txt = os.path.join(dir_test, "journal.txt")
    f3_log = os.path.join(dir_test, "data.log")
    f4_ini = os.path.join(dir_sans_txt, "config.ini")
    f5_erreur = os.path.join(dir_test, "fichier_test_erreur.ini") # Fichier pour test d'erreur

    try:
        # Création de la structure
        os.makedirs(dir_vide, exist_ok=True)
        os.makedirs(dir_sans_txt, exist_ok=True)
        os.makedirs(dir_sous_dossier, exist_ok=True)

        for f_path in [f1_txt, f2_txt, f3_log, f4_ini, f5_erreur]:
            with open(f_path, "w") as f: f.write("test")

        print("Structure de test (filtre .txt) créée. Lancement des tests...")

        #  1. Cas simples 
        # Doit trouver 'notes.txt' et 'journal.txt' (2 éléments)
        # Doit ignorer 'data.log', 'un_sous_dossier', 'vide', 'sans_txt', 'fichier_test_erreur.ini'

        resultat_simple = lister_document(dir_test)
        attendu_simple = {"notes.txt", "journal.txt"}

        assert set(resultat_simple) == attendu_simple
        assert len(resultat_simple) == 2

        #  2. Cas limites 

        # Cas 2a: Dossier vide
        assert lister_document(dir_vide) == []

        # Cas 2b: Dossier contenant des fichiers, mais aucun .txt
        assert lister_document(dir_sans_txt) == []

        #  3. Cas d’erreurs 

        # Cas 3a: Le chemin n'existe pas
        # (La fonction imprime "le chemin n'existe pas" et retourne [])
        print("\nTest Cas 3a (attendu : 'le chemin n'existe pas') :")
        assert lister_document("dossier_inexistant_xyz_123") == []

        # Cas 3b: Le chemin est un fichier
        # (La fonction imprime "Erreur : ..." et retourne [])
        print(f"\nTest Cas 3b (attendu : 'Erreur : {f5_erreur}...') :")
        assert lister_document(f5_erreur) == []

        print("\n Tous les tests unitaires sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE : {e}")
    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        print("\nNettoyage de l'environnement de test...")
        try:
            if os.path.exists(f1_txt): os.remove(f1_txt)
            if os.path.exists(f2_txt): os.remove(f2_txt)
            if os.path.exists(f3_log): os.remove(f3_log)
            if os.path.exists(f4_ini): os.remove(f4_ini)
            if os.path.exists(f5_erreur): os.remove(f5_erreur)
            if os.path.exists(dir_sous_dossier): os.rmdir(dir_sous_dossier)
            if os.path.exists(dir_sans_txt): os.rmdir(dir_sans_txt)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_lister_document_txt_filtre()

def explorer_corpus(chemin_base):
    """
    Description :
        Explore récursivement un dossier de base.
        Retourne un dictionnaire mappant chaque sous-dossier trouvé à la liste
        de ses fichiers et à leur nombre.

    Paramètres :
        chemin_base = str, le chemin du dossier racine à explorer.

    Retour :
        dict, un dictionnaire des résultats.
              Retourne {} si le chemin est invalide.
    """

    res = {}
    #vérifie le chemin
    if not os.path.isdir(chemin_base):
        return res

    try:
        contenu = os.listdir(chemin_base)
    except PermissionError:
        return res
    i = 0
    f = []
    #boucle récursive pour explorer le corpus
    for element in contenu:
        ch = os.path.join(chemin_base, element)

        if os.path.isdir(ch):
            res.update(explorer_corpus(ch))

        elif os.path.isfile(ch):
            i += 1
            f.append(element)
    res[chemin_base] = {'contenu': f, 'nombre': i}
    return res
# Tests unitaires  Exercice a) iii
def test_explorer_corpus():

    # Setup 
    # Structure :
    # corpus_racine/
    #   -> fichier_racine.txt
    #   -> fichier_racine.log
    #   -> vide/
    #   -> sports/
    #      -> tennis.txt
    #      -> foot/
    #         -> regles.txt
    #   -> fichier_erreur.ini (pour test d'erreur)

    dir_test = "corpus_racine"
    dir_vide = os.path.join(dir_test, "vide")
    dir_sports = os.path.join(dir_test, "sports")
    dir_foot = os.path.join(dir_sports, "foot")

    # Fichiers
    f_root1 = os.path.join(dir_test, "fichier_racine.txt")
    f_root2 = os.path.join(dir_test, "fichier_racine.log")
    f_sports1 = os.path.join(dir_sports, "tennis.txt")
    f_foot1 = os.path.join(dir_foot, "regles.txt")
    f_erreur = os.path.join(dir_test, "fichier_erreur.ini")

    fichiers_a_creer = [f_root1, f_root2, f_sports1, f_foot1, f_erreur]
    dossiers_a_creer = [dir_vide, dir_foot] # dir_foot crée dir_sports aussi

    try:
        # Création de la structure
        for d in dossiers_a_creer: os.makedirs(d, exist_ok=True)
        for f in fichiers_a_creer:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test récursive créée. Lancement des tests...")
        resultat = explorer_corpus(dir_test)

        #  1. Cas simples (Vérification de la structure) 

        # Doit contenir 4 dossiers (racine, vide, sports, foot)
        assert len(resultat) == 4
        assert dir_test in resultat
        assert dir_vide in resultat
        assert dir_sports in resultat
        assert dir_foot in resultat

        # Vérification des comptages de fichiers
        assert resultat[dir_test]['nombre'] == 3
        # (On trie les listes pour une comparaison fiable)
        assert sorted(resultat[dir_test]['contenu']) == sorted(["fichier_racine.txt", "fichier_racine.log", "fichier_erreur.ini"])

        assert resultat[dir_sports]['nombre'] == 1
        assert resultat[dir_sports]['contenu'] == ["tennis.txt"]

        assert resultat[dir_foot]['nombre'] == 1
        assert resultat[dir_foot]['contenu'] == ["regles.txt"]

        #  2. Cas limites 

        # Cas 2a: Dossier vide
        assert resultat[dir_vide]['nombre'] == 0
        assert resultat[dir_vide]['contenu'] == []

        # Cas 2b: Appel direct sur un dossier vide
        assert explorer_corpus(dir_vide) == {dir_vide: {'contenu': [], 'nombre': 0}}

        #  3. Cas d’erreurs 

        # Cas 3a: Le chemin n'existe pas
        assert explorer_corpus("dossier_inexistant_xyz_123") == {}

        # Cas 3b: Le chemin est un fichier
        assert explorer_corpus(f_erreur) == {}

        print("\n Tous les tests unitaires (Exercice 5) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 5) : {e}")
    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 5)...")
        try:
            for f in fichiers_a_creer:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_foot): os.rmdir(dir_foot)
            if os.path.exists(dir_sports): os.rmdir(dir_sports)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_explorer_corpus()

#iv.
def afficher_structure(chemin_base):
    """
    Description :
        Génère une vue hiérarchique (arborescence) d'un dossier
        sous forme de chaîne de caractères en utilisant les données 
        de explorer_corpus().

    Paramètres :
        chemin_base  str, le chemin du dossier racine à analyser.

    Retour :
        str : La chaîne de caractères représentant l'arborescence complète.
    """
    dic = explorer_corpus(chemin_base)

    if not dic:
        return 0
    chn = os.path.normpath(chemin_base)
    nb = chn.count(os.path.sep)
    chemins = sorted(dic.keys())

    affichage = []

    affichage.append(f"Arborescence pour : {chn}")

    for i in chemins:
        temp = os.path.normpath(i)
        nv = temp.count(os.path.sep)
        ind = nv - nb
        indentation = "    " * ind
        
        # Ajout du dossier à la liste
        affichage.append(f"{indentation} ->{os.path.basename(i)}/")

        contenu = dic[i]['contenu']
        indf = "    " * (ind + 1)

        # Traitement des fichiers
        for element in sorted(contenu):
            ch = os.path.join(i, element)
            if os.path.isfile(ch):
                affichage.append(f"{indf}-> {element}")

    return "\n".join(affichage)
# Tests unitaires  Exercice a) iv
def test_afficher_structure():

    print("\n Lancement du test visuel pour 'afficher_structure' ")

    # Setup 
    # On recrée la même structure que pour le test de 'explorer_corpus'
    dir_test = "corpus_racine_visuel"
    dir_vide = os.path.join(dir_test, "vide")
    dir_sports = os.path.join(dir_test, "sports")
    dir_foot = os.path.join(dir_sports, "foot")

    f_root1 = os.path.join(dir_test, "fichier_racine.txt")
    f_sports1 = os.path.join(dir_sports, "tennis.txt")
    f_foot1 = os.path.join(dir_foot, "regles.txt")

    fichiers_a_creer = [f_root1, f_sports1, f_foot1]
    dossiers_a_creer = [dir_vide, dir_foot]

    try:
        for d in dossiers_a_creer: os.makedirs(d, exist_ok=True)
        for f in fichiers_a_creer:
            with open(f, "w") as f_out: f_out.write("test")

        #  1. Cas simple (Test visuel) 
        print("\nACTION REQUISE : Vérifiez visuellement l'arborescence ci-dessous.")
        print("La structure attendue est :")
        print("  corpus_racine_visuel/")
        print("      -> fichier_racine.txt")
        print("      -> foot/ (dans sports)")
        print("          -> regles.txt")
        print("      -> sports/")
        print("          -> tennis.txt")
        print("      -> vide/")
        print("")

        # Appel de la fonction à tester
        afficher_structure(dir_test)

        print("")

        #  2. Cas limite (Dossier vide) 
        print("\nTest cas limite (dossier vide) :")
        afficher_structure(dir_vide) # Doit afficher le dossier 'vide' et rien dessous

        #  3. Cas d’erreur (Chemin invalide) 
        print("\nTest cas d'erreur (chemin invalide) :")
        print("(Doit afficher 'Chemin ... non valide ou vide.')")
        afficher_structure("chemin_inexistant_12345")

        print("\n Test visuel terminé.")

    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 6)...")
        try:
            for f in fichiers_a_creer:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_foot): os.rmdir(dir_foot)
            if os.path.exists(dir_sports): os.rmdir(dir_sports)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_afficher_structure()



# b) Fonctions d’analyse statistique de base (sans lecture du contenu des fichiers)
#i.

def compter_sous_corpus(base):
    """
    Description :
        Compte le nombre de sous-dossiers directs 
        dans un dossier de base et retourne leur nombre et leurs noms.

    Paramètres :
        base  str, le chemin du dossier à inspecter.

    Retour :
        tuple (int, list), le nombre de sous-dossiers et la liste de leurs noms.
             Retourne (0, []) si le chemin est invalide.
    """
    #vérifie la base
    nom = []
    if not os.path.isdir(base):
        return 0, []

    try:
        contenu = os.listdir(base)
    except PermissionError:
        return 0, []
    #boucle de comptage
    for i in contenu:
        ch = os.path.join(base, i)
        if os.path.isdir(ch):
            nom.append(i)

    nb = len(nom)
    return nb, nom
# Tests unitaires  Exercice b) i
def test_compter_sous_corpus():

    # Setup 
    dir_test = "corpus_test_sous_corpus"
    dir_ufr = os.path.join(dir_test, "UFR")
    dir_iut = os.path.join(dir_test, "IUT")
    dir_vide = os.path.join(dir_test, "Dossier_Vide")

    f1 = os.path.join(dir_test, "readme.txt")
    f2 = os.path.join(dir_test, "config.log")
    f_erreur = os.path.join(dir_test, "erreur.ini") # Fichier pour test d'erreur

    try:
        # Création de la structure
        os.makedirs(dir_ufr, exist_ok=True)
        os.makedirs(dir_iut, exist_ok=True)
        os.makedirs(dir_vide, exist_ok=True)

        for f in [f1, f2, f_erreur]:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Exercice 7) créée. Lancement des tests...")

        #  1. Cas simples 
        # Doit trouver 'UFR', 'IUT', 'Dossier_Vide' (3 dossiers)
        # Doit ignorer 'readme.txt', 'config.log', 'erreur.ini'

        nb, nom = compter_sous_corpus(dir_test)

        assert nb == 3
        # On trie pour la comparaison
        assert sorted(nom) == sorted(["UFR", "IUT", "Dossier_Vide"])

        #  2. Cas limites 

        # Cas 2a: Dossier vide (devrait trouver 0 sous-dossier)
        nb_vide, nom_vide = compter_sous_corpus(dir_vide)
        assert nb_vide == 0
        assert nom_vide == []

        # Cas 2b: Dossier 'IUT' (qui est vide, donc 0 sous-dossier)
        nb_iut, nom_iut = compter_sous_corpus(dir_iut)
        assert nb_iut == 0
        assert nom_iut == []

        #  3. Cas d’erreurs 

        # Cas 3a: Le chemin n'existe pas
        print("\nTest Cas 3a (attendu : 'le chemin n'existe pas') :")
        nb_err1, nom_err1 = compter_sous_corpus("dossier_inexistant_xyz_123")
        assert nb_err1 == 0
        assert nom_err1 == []

        # Cas 3b: Le chemin est un fichier
        print(f"\nTest Cas 3b (attendu : 'Erreur : {f_erreur}...') :")
        nb_err2, nom_err2 = compter_sous_corpus(f_erreur)
        assert nb_err2 == 0
        assert nom_err2 == []

        print("\n Tous les tests unitaires (Exercice 7) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 7) : {e}")
    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 7)...")
        try:
            for f in [f1, f2, f_erreur]:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_ufr): os.rmdir(dir_ufr)
            if os.path.exists(dir_iut): os.rmdir(dir_iut)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_compter_sous_corpus()

#ii
def compter_document(base):
    """
    Description :
        Compte le nombre total de fichiers dans un dossier de base
        et tous ses sous-dossiers.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        int, le nombre total de fichiers trouvés.
    """

    dic = {}
    dic = explorer_corpus(base)
    res = 0
    for i in dic.values():
        res += i['nombre']
    return res
# Tests unitaires  Exercice b) ii
def test_compter_document():

    # Setup 
    # Structure :
    # corpus_total/
    #   -> f_root1.txt
    #   -> f_root2.log        (Total racine = 2)
    #   -> vide/              (Total vide = 0)
    #   -> docs/
    #      -> f_docs1.txt     (Total docs = 1)
    #      -> projets/
    #         -> f_proj1.txt
    #         -> f_proj2.md   (Total projets = 2)

    # Total attendu = 2 + 0 + 1 + 2 = 5 fichiers

    dir_test = "corpus_total"
    dir_vide = os.path.join(dir_test, "vide")
    dir_docs = os.path.join(dir_test, "docs")
    dir_projets = os.path.join(dir_docs, "projets")

    fichiers = [
        os.path.join(dir_test, "f_root1.txt"),
        os.path.join(dir_test, "f_root2.log"),
        os.path.join(dir_docs, "f_docs1.txt"),
        os.path.join(dir_projets, "f_proj1.txt"),
        os.path.join(dir_projets, "f_proj2.md"),
        os.path.join(dir_test, "fichier_erreur.ini") # Pour le test d'erreur (total +1)
    ]

    # Total attendu = 5 + 1 = 6 fichiers

    try:
        # Création de la structure
        os.makedirs(dir_vide, exist_ok=True)
        os.makedirs(dir_projets, exist_ok=True)

        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Exercice 8) créée. Lancement des tests...")

        #  1. Cas simples 
        # Doit trouver 6 fichiers (2 racine + 1 docs + 2 projets + 1 erreur.ini)

        total = compter_document(dir_test)
        assert total == 6

        #  2. Cas limites 

        # Cas 2a: Dossier vide
        assert compter_document(dir_vide) == 0

        # Cas 2b: Dossier 'docs' (qui contient 1 fichier + 2 dans un sous-dossier)
        assert compter_document(dir_docs) == 3

        #  3. Cas d’erreurs 

        # Cas 3a: Le chemin n'existe pas
        # (explorer_corpus retourne {}, la boucle ne s'exécute pas, res=0)
        assert compter_document("dossier_inexistant_xyz_123") == 0

        # Cas 3b: Le chemin est un fichier
        # (explorer_corpus retourne {}, la boucle ne s'exécute pas, res=0)
        assert compter_document(fichiers[0]) == 0

        print("\n Tous les tests unitaires (Exercice 8) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 8) : {e}")
    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 8)...")
        try:
            # On supprime tout (fichiers d'abord)
            for f in fichiers:
                if os.path.exists(f): os.remove(f)

            # Dossiers (le plus profond d'abord)
            if os.path.exists(dir_projets): os.rmdir(dir_projets)
            if os.path.exists(dir_docs): os.rmdir(dir_docs)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_compter_document()

#iii
def verifier_correspondance_langues(base):
    """
    Description :
        Vérifie la présence des paires de fichiers (_fr.txt et _en.txt)
        pour une liste attendue de 22 étudiants (etu01 à etu22).
        Imprime des alertes pour chaque manquant.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        int, le nombre total d'alertes.
    """

    dic = {}
    dic = explorer_corpus(base) 
    alertes = 0
    f = {}

    # Parcourir tous les fichiers trouvés par explorer_corpus et on trie en liste les fichier etu
    for ch, data in dic.items():
        for i in data['contenu']:
            
            if i.endswith('_fr.txt') or i.endswith('_en.txt'):
                nom = i.split('_')[0]
                if nom.startswith('etu'):
                    if nom not in f:
                        f[nom] = {'fr': None, 'en': None, 'dossier': os.path.basename(ch)}
                    if i.endswith('_fr.txt'):
                        f[nom]['fr'] = i
                    elif i.endswith('_en.txt'):
                        f[nom]['en'] = i

    
    e = [f"etu{i:02d}" for i in range(1, 23)]
    #vérifie la liste et alertes pour les fichier manquants
    for etu in e:
        if etu not in f:
            alertes += 2
        else:
            data = f[etu]
            if data['fr'] is None:
                alertes += 1
            if data['en'] is None:
                alertes += 1


    return alertes

# Tests unitaires  Exercice b) iii
def test_verifier_correspondance_langues():

    # Setup 
    dir_test = "corpus_test_correspondance"

    # Cas 1: etu01 complet
    dir_etu01 = os.path.join(dir_test, "UFR_Lettres")
    f_etu01_fr = os.path.join(dir_etu01, "etu01_fr.txt")
    f_etu01_en = os.path.join(dir_etu01, "etu01_en.txt")

    # Cas 2: etu02 (fr seul)
    dir_etu02 = os.path.join(dir_test, "UFR_Sciences")
    f_etu02_fr = os.path.join(dir_etu02, "etu02_fr.txt")

    # Cas 3: etu03 (en seul)
    f_etu03_en = os.path.join(dir_etu02, "etu03_en.txt") # Note: dans le même dossier

    # Cas 4: etu04 (manquant)

    # Cas 5: etu05 (fichiers séparés)
    dir_etu05 = os.path.join(dir_test, "IUT")
    f_etu05_fr = os.path.join(dir_etu01, "etu05_fr.txt") # Dans Lettres
    f_etu05_en = os.path.join(dir_etu05, "etu05_en.txt") # Dans IUT

    fichiers = [f_etu01_fr, f_etu01_en, f_etu02_fr, f_etu03_en, f_etu05_fr, f_etu05_en]
    dossiers = [dir_etu01, dir_etu02, dir_etu05]

    try:
        for d in dossiers: os.makedirs(d, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Exercice 9) créée. Lancement des tests...")

        #  1. Cas simple / 2. Cas limites 
        # On teste la structure créée :
        # - etu01 : OK (0 alerte)
        # - etu02 : 'en' manquant (1 alerte)
        # - etu03 : 'fr' manquant (1 alerte)
        # - etu04 : 'fr' et 'en' manquants (2 alertes)
        # - etu05 : OK (0 alerte, la fonction doit trouver les 2)
        # - etu06 à etu22 (17 étudiants) : tous manquants (17 * 2 = 34 alertes)
        # Total attendu = 0 + 1 + 1 + 2 + 0 + 34 = 38 alertes

        alertes_trouvees = verifier_correspondance_langues(dir_test)
        assert alertes_trouvees == 38

        #  3. Cas d’erreurs 

        # Cas 3a: Le chemin n'existe pas
        # (explorer_corpus retourne {}, f reste vide. 22 étudiants * 2 alertes = 44)
        print("\nTest Cas 3a (attendu : 44 alertes pour chemin inexistant) :")
        alertes_erreur = verifier_correspondance_langues("dossier_inexistant_xyz_123")
        assert alertes_erreur == 44

        print("\n Tous les tests unitaires (Exercice 9) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 9) : {e}")
    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 9)...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            for d in reversed(dossiers): # On supprime le plus profond d'abord
                 if os.path.exists(d) and not os.listdir(d): # S'il est vide
                     os.rmdir(d)
            if os.path.exists(dir_test): os.rmdir(dir_test) # Racine
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
#test_verifier_correspondance_langues()
#iv

def compter_par_langue(base):
    """
    Description :
        Compte le total des fichiers finissant par _fr.txt et _en.txt
        dans l'ensemble du corpus.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        tuple (int, int), le nombre (fr, en) de fichiers trouvés.
    """

    dic = {}
    dic = explorer_corpus(base) 
    fr = 0
    en = 0

    # Parcourt tous les dossiers
    for ch, data in dic.items():
        # Parcourt tous les fichiers de ce dossier et compte les fichiers
        for i in data['contenu']:
            chc = os.path.join(ch, i)
            if os.path.isfile(chc):
                if i.endswith('_fr.txt'):
                    fr += 1
                elif i.endswith('_en.txt'):
                    en += 1
    return fr, en
# Tests unitaires  Exercice b) iv
def test_compter_par_langue():

    # Setup 
    dir_test = "corpus_test_comptage_langue"
    dir_sub = os.path.join(dir_test, "sub")

    fichiers = [
        os.path.join(dir_test, "f1_fr.txt"),
        os.path.join(dir_test, "f2_en.txt"),
        os.path.join(dir_test, "f3.log"),
        os.path.join(dir_sub, "f4_fr.txt"),
        os.path.join(dir_sub, "f5_fr.txt"),
    ]
    # Total attendu : 3 FR, 1 EN

    try:
        os.makedirs(dir_sub, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Exercice 10) créée. Lancement des tests...")

        #  1. Cas simples 
        fr, en = compter_par_langue(dir_test)
        assert fr == 3
        assert en == 1

        #  2. Cas limites 
        # Test sur le sous-dossier (2 FR, 0 EN)
        fr_sub, en_sub = compter_par_langue(dir_sub)
        assert fr_sub == 2
        assert en_sub == 0

        #  3. Cas d’erreurs 
        # Cas 3a: Le chemin n'existe pas
        fr_err, en_err = compter_par_langue("dossier_inexistant_xyz_123")
        assert fr_err == 0
        assert en_err == 0

        print("\n Tous les tests unitaires (Exercice 10) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 10) : {e}")
    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 10)...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_sub): os.rmdir(dir_sub)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
#test_compter_par_langue()

#v
def repartition_langue_par_sous_corpus(base):
    """
    Description :
        Affiche un tableau de la répartition (en %) des fichiers
        _fr.txt et _en.txt pour chaque sous-dossier trouvé.
        Retourne également un dictionnaire de ces statistiques.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        dict, un dictionnaire des statistiques par sous-corpus, 
              ou {} si le chemin est invalide.
    """

    dic = {}
    dic = explorer_corpus(base)
    resultats = {}

    if not dic:
        return resultats
    tri = sorted(dic.keys())

    for ch in tri:
        data = dic[ch]
        nom = os.path.basename(ch) 
        total = data['nombre']
        fr = 0
        en = 0
        
        # On compte les fr/en de ce dossier
        for i in data['contenu']:
            if i.endswith('_fr.txt'):
                fr += 1
            elif i.endswith('_en.txt'):
                en += 1
                
        proportionF = (fr / total) * 100 if total > 0 else 0
        proportionE = (en / total) * 100 if total > 0 else 0
        resultats[nom] = {
            'total': total,
            'count_fr': fr,
            'count_en': en,
            'prop_fr_pct': proportionF,
            'prop_en_pct': proportionE
        }

    return resultats
# Tests unitaires  Exercice b) v
def test_repartition_langue_avec_retour():
    
    # sztup
    dir_test = "repart_base_retour"
    dir_ufr = os.path.join(dir_test, "UFR")
    dir_iut = os.path.join(dir_test, "IUT")
    dir_vide = os.path.join(dir_test, "VIDE")
    
    fichiers = [
        os.path.join(dir_ufr, "f1_fr.txt"), # UFR: Total 2, 1 FR (50.0%)
        os.path.join(dir_ufr, "f2.log"),
        os.path.join(dir_iut, "f3_fr.txt"), # IUT: Total 2, 1 FR, 1 EN (50.0% / 50.0%)
        os.path.join(dir_iut, "f4_en.txt"),
    ]

    try:
        os.makedirs(dir_ufr, exist_ok=True)
        os.makedirs(dir_iut, exist_ok=True)
        os.makedirs(dir_vide, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")
        
        print("\n--- Lancement du test automatisé (Exercice 11 Modifié) ---")
        
        # --- 1. Cas simple (Test automatisé) ---
        resultat = repartition_langue_par_sous_corpus(dir_test)
        
        print("--- Fin de l'affichage / Début des assertions ---")

        assert resultat is not None
        assert "UFR" in resultat
        assert "IUT" in resultat
        assert "VIDE" in resultat
        
        # Vérification UFR
        assert resultat['UFR']['total'] == 2
        assert resultat['UFR']['prop_fr_pct'] == 50.0
        assert resultat['UFR']['prop_en_pct'] == 0.0

        # Vérification IUT
        assert resultat['IUT']['total'] == 2
        assert resultat['IUT']['prop_fr_pct'] == 50.0
        assert resultat['IUT']['prop_en_pct'] == 50.0
        
        # --- 2. Cas limites ---
        assert resultat['VIDE']['total'] == 0
        assert resultat['VIDE']['prop_fr_pct'] == 0.0

        # --- 3. Cas d’erreur ---
        resultat_err = repartition_langue_par_sous_corpus("chemin_inexistant_12345")
        assert resultat_err == {} # Doit retourner un dict vide
        
        print("\n Tous les tests unitaires sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE : {e}")
    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        # --- Nettoyage (Teardown) ---
        print("\nNettoyage de l'environnement de test...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_ufr): os.rmdir(dir_ufr)
            if os.path.exists(dir_iut): os.rmdir(dir_iut)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
            
#test_repartition_langue_avec_retour()
#vi

def detecter_doublons(base):
    """
    Description :
        Détecte les fichiers qui existent dans
        plusieurs dossiers différents de l'arborescence.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        int, le nombre de noms de fichiers en doublon.
    """

    dic = {}
    dic = explorer_corpus(base)
    f = {} 
    # Construit le dictionnaire des fichiers et où on les a vus
    for ch, data in dic.items():
        for i in data['contenu']:
            chc = os.path.join(ch, i)
            if os.path.isfile(chc):
                if i not in f:
                    f[i] = []
                f[i].append(ch)
    anomalies = 0

    # Analyse le dictionnaire f
    for i, chemins in f.items():
        if len(chemins) > 1:
            if len(set(chemins)) > 1:
                for ch in set(chemins):
                    print(f"  -> {ch}")
                anomalies += 1


    return anomalies
# Tests unitaires  Exercice b) vi
def test_detecter_doublons():

    # Setup 
    dir_test = "corpus_test_doublons"
    dir_A = os.path.join(dir_test, "Dossier_A")
    dir_B = os.path.join(dir_test, "Dossier_B")

    fichiers = [
        os.path.join(dir_A, "fichier_unique_A.txt"),
        os.path.join(dir_A, "doublon.txt"), # Fichier en doublon
        os.path.join(dir_B, "fichier_unique_B.txt"),
        os.path.join(dir_B, "doublon.txt"), # Fichier en doublon
    ]

    try:
        os.makedirs(dir_A, exist_ok=True)
        os.makedirs(dir_B, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Exercice 12) créée. Lancement des tests...")

        #  1. Cas simples 
        # Doit trouver 1 anomalie pour "doublon.txt"
        anomalies = detecter_doublons(dir_test)
        assert anomalies == 1

        #  2. Cas limites 
        # Test sur un dossier sans doublons (Dossier_A seul)
        anomalies_A = detecter_doublons(dir_A)
        assert anomalies_A == 0

        #  3. Cas d’erreurs 
        # Cas 3a: Le chemin n'existe pas
        anomalies_err = detecter_doublons("dossier_inexistant_xyz_123")
        assert anomalies_err == 0

        print("\n Tous les tests unitaires (Exercice 12) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 12) : {e}")
    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 12)...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_A): os.rmdir(dir_A)
            if os.path.exists(dir_B): os.rmdir(dir_B)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
#test_detecter_doublons()
#vii
def verifier_extensions(base):
    """
    Description :
        Vérifie que tous les fichiers du corpus ont l'extension ".txt".
        Imprime la liste des fichiers non conformes.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        int, le nombre de fichiers avec une extension non conforme.
    """

    dic = {}
    dic = explorer_corpus(base)
    anomalies = []
    extension = ".txt"
    # Parcourt tous les dossiers et leurs fichiers
    for ch, data in dic.items():
        for i in data['contenu']:
            ch_complet = os.path.join(ch, i)
            if os.path.isfile(ch_complet):
                if not i.endswith(extension):
                    anomalies.append(ch_complet)


    return len(anomalies)
# Tests unitaires  Exercice b) vii
def test_verifier_extensions():

    # Setup 
    dir_test = "corpus_test_extensions"
    dir_sub = os.path.join(dir_test, "sub")
    dir_vide = os.path.join(dir_test, "vide")

    fichiers = [
        os.path.join(dir_test, "f1.txt"),       # OK
        os.path.join(dir_test, "f2.log"),       # Anomalie 1
        os.path.join(dir_sub, "f3.txt"),        # OK
        os.path.join(dir_sub, "f4.ini"),        # Anomalie 2
        os.path.join(dir_sub, "README"),        # Anomalie 3
    ]
    # Total attendu : 3 anomalies

    try:
        os.makedirs(dir_sub, exist_ok=True)
        os.makedirs(dir_vide, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Exercice 13) créée. Lancement des tests...")

        #  1. Cas simples 
        anomalies = verifier_extensions(dir_test)
        assert anomalies == 3

        #  2. Cas limites 

        # Cas 2a: Dossier vide
        anomalies_vide = verifier_extensions(dir_vide)
        assert anomalies_vide == 0

        # Cas 2b: Dossier 'sub' (contient 1 OK, 2 anomalies)
        anomalies_sub = verifier_extensions(dir_sub)
        assert anomalies_sub == 2

        #  3. Cas d’erreurs 

        # Cas 3a: Le chemin n'existe pas
        anomalies_err = verifier_extensions("dossier_inexistant_xyz_123")
        assert anomalies_err == 0

        print("\n Tous les tests unitaires (Exercice 13) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 13) : {e}")
    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 13)...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_sub): os.rmdir(dir_sub)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
#test_verifier_extensions()

#viii
def compter_etudiants(base):
    """
    Description :
        Compte le nombre d'étudiants qui possèdent à la fois un 
        fichier _fr.txt ET un fichier _en.txt dans l'arborescence.

    Paramètres :
        base -- str, le chemin du dossier racine à explorer.

    Retour :
        int, le nombre d'étudiants ayant les deux fichiers.
    """

    dic = {}
    dic = explorer_corpus(base)
    f = {} 

    for ch, data in dic.items():
        for i in data['contenu']:
            if i.endswith('_fr.txt') or i.endswith('_en.txt'):
                nom = i.split('_')[0] 

                if nom.startswith('etu'):
                    if nom not in f:
                        f[nom] = {'fr': 0, 'en': 0}
                    if i.endswith('_fr.txt'):
                        f[nom]['fr'] = 1
                    elif i.endswith('_en.txt'):
                        f[nom]['en'] = 1
                        
    nbe = 0

    for etu, data in f.items():
        if data['fr'] == 1 and data['en'] == 1:
            nbe += 1

    return nbe
def test_compter_etudiants():
    
    # setup
    dir_test = "corpus_test_etu_complets"
    dir_ufr1 = os.path.join(dir_test, "UFR1")
    dir_ufr2 = os.path.join(dir_test, "UFR2")
    dir_vide = os.path.join(dir_test, "vide")

    fichiers = [
        # etu01: Complet (dans UFR1)
        os.path.join(dir_ufr1, "etu01_fr.txt"),
        os.path.join(dir_ufr1, "etu01_en.txt"),
        
        # etu02: Incomplet (FR seul, dans UFR1)
        os.path.join(dir_ufr1, "etu02_fr.txt"),
        
        # etu03: Incomplet (EN seul, dans UFR2)
        os.path.join(dir_ufr2, "etu03_en.txt"),
        
        # etu04: Complet (fichiers séparés dans UFR1 et UFR2)
        os.path.join(dir_ufr1, "etu04_fr.txt"),
        os.path.join(dir_ufr2, "etu04_en.txt"),

        # etu05: Incomplet (doublon FR, mais pas EN)
        os.path.join(dir_ufr1, "etu05_fr.txt"),
        os.path.join(dir_ufr2, "etu05_fr.txt"),
    ]
    # Total attendu : 2 étudiants complets (etu01, etu04)

    try:
        os.makedirs(dir_ufr1, exist_ok=True)
        os.makedirs(dir_ufr2, exist_ok=True)
        os.makedirs(dir_vide, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")
        
        print("Structure de test (Exercice 14) créée. Lancement des tests...")

        # --- 1. Cas simples ---
        # Doit trouver etu01 et etu04
        nombre_complets = compter_etudiants(dir_test)
        assert nombre_complets == 2, f"Attendu 2, obtenu {nombre_complets}"

        # --- 2. Cas limites ---
        
        # Cas 2a: Dossier vide
        assert compter_etudiants(dir_vide) == 0, "Un dossier vide doit retourner 0"
        
        # Cas 2b: Test sur un sous-dossier (UFR1 seul)
        # Contient etu01 (complet), etu02 (fr), etu04 (fr), etu05 (fr)
        # Devrait trouver 1 seul complet (etu01)
        assert compter_etudiants(dir_ufr1) == 1, "Le test sur UFR1 doit retourner 1"


        # --- 3. Cas d’erreurs ---
        
        # Cas 3a: Le chemin n'existe pas
        assert compter_etudiants("dossier_inexistant_xyz_123") == 0, "Un chemin inexistant doit retourner 0"
        
        print("\n Tous les tests unitaires (Exercice 14) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 14) : {e}")
    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        # --- Nettoyage (Teardown) ---
        print("\nNettoyage de l'environnement de test (Exercice 14)...")
        try:
            # Supprime les fichiers
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_ufr1): os.rmdir(dir_ufr1)
            if os.path.exists(dir_ufr2): os.rmdir(dir_ufr2)
            if os.path.exists(dir_vide): os.rmdir(dir_vide)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_compter_etudiants()
#ix
def statistiques_structure(base):
    """
    Description :
        Imprime un rapport statistique complet sur le corpus
        et RETOURNE un dictionnaire contenant ces statistiques.

    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        dict, un dictionnaire des statistiques, ou None si la base est invalide.
    """
    if not os.path.isdir(base):
        return None 
    rapport = {}

    nb, _ = compter_sous_corpus(base)
    rapport['sous_corpus'] = nb
    totalf = compter_document(base)
    rapport['totalf'] = totalf
    totalfr, totale = compter_par_langue(base)
    rapport['totalfr'] = totalfr
    rapport['totalen'] = totale
    totalec = compter_etudiants(base)
    rapport['etudiantsComplets'] = totalec
    anomaliesl = verifier_correspondance_langues(base)
    rapport['anomaliesLangues'] = anomaliesl
    anomaliesExtensions = verifier_extensions(base)
    rapport['anomaliesExtensions'] = anomaliesExtensions
    anomaliesDoublons = detecter_doublons(base)
    rapport['anomaliesDoublons'] = anomaliesDoublons
    totalAnomalies = anomaliesl + anomaliesExtensions + anomaliesDoublons
    rapport['totalAnomalies'] = totalAnomalies
    return rapport

def test_statistiques_structure():

    # Setup 
    # Structure complexe pour tester TOUTES les fonctions

    dir_test = "corpus_bilan_stats_retour"
    dir_ufr = os.path.join(dir_test, "UFR")
    dir_iut = os.path.join(dir_test, "IUT")

    fichiers = [
        # UFR (2 fichiers)
        os.path.join(dir_ufr, "etu01_fr.txt"),
        os.path.join(dir_ufr, "etu01_en.txt"),

        # IUT (3 fichiers)
        os.path.join(dir_iut, "etu02_fr.txt"), # Etu 02 incomplet
        os.path.join(dir_iut, "doublon.txt"),  # Doublon
        os.path.join(dir_iut, "anomalie.log"), # Extension

        # Racine (2 fichiers)
        os.path.join(dir_test, "doublon.txt"), # Doublon
        os.path.join(dir_test, "README.md"),   # Extension
    ]

    #  Statistiques attendues (pour les asserts) 
    # 1. Sous-corpus : 2 (UFR, IUT)
    # 2. Total fichiers : 7 (2 UFR + 3 IUT + 2 Racine)
    # 3. FR/EN : 2 FR / 1 EN
    # 4. Etudiants Complets : 1 (etu01)
    # 5. Anomalies :
    #    - Langues : 41 (etu02 (1) + etu03-22 (40))
    #    - Extensions : 2 (anomalie.log, README.md)
    #    - Doublons : 1 (doublon.txt)
    #    - Total Anomalies = 41 + 2 + 1 = 44

    try:
        os.makedirs(dir_ufr, exist_ok=True)
        os.makedirs(dir_iut, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("\n Lancement du test (Exercice 16) ")

        #  1. Cas simple (Test automatisé) 
        print("(Le rapport visuel va s'afficher ci-dessous...)")

        # Appel de la fonction à tester
        rapport = statistiques_structure(dir_test)

        print("\n(Fin du rapport visuel. Début des assertions...)")

        # Vérifie que le retour n'est pas None
        assert rapport is not None

        # Vérifie chaque valeur
        assert rapport['sous_corpus'] == 2
        assert rapport['total_fichiers'] == 7
        assert rapport['total_fr'] == 2
        assert rapport['total_en'] == 1
        assert rapport['etudiants_complets'] == 1
        assert rapport['anomalies_langues'] == 41
        assert rapport['anomalies_extensions'] == 2
        assert rapport['anomalies_doublons'] == 1
        assert rapport['total_anomalies'] == 44

        print(" Assertions automatiques passées !")

        #  2. Cas d’erreur 
        print("\nTest cas d'erreur (chemin invalide) :")
        rapport_err = statistiques_structure("chemin_inexistant_12345")
        assert rapport_err is None
        print(" Assertion (cas d'erreur) passée.")

        print("\n Tous les tests unitaires (Exercice 16) sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE (Exercice 16) : {e}")
    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test (Exercice 16)...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_ufr): os.rmdir(dir_ufr)
            if os.path.exists(dir_iut): os.rmdir(dir_iut)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

#test_statistiques_structure()



# c) Fonctions de visualisation et tableau de bord (sans lecture du contenu des fichiers)
#i
def afficher_repartition_sous_corpus(base):
    """
    Description :
        Génère un diagramme en barres du nombre de documents
        par sous-corpus et retourne l'objet Figure.

    Paramètres :
        base str, le chemin du dossier racine à explorer.

    Retour :
        matplotlib.figure.Figure : L'objet contenant le graphique (ou None en cas d'erreur).
    """    
    dic = explorer_corpus(base)
    
    if not dic:
        return None

    noms = [os.path.basename(ch) for ch in dic.keys()]
    comptes = [data['nombre'] for data in dic.values()]

    fig = plt.figure(figsize=(10, 6))
    
    plt.bar(noms, comptes, color='skyblue')
    plt.title('Nombre de documents par sous-corpus')
    plt.ylabel('Nombre de documents')
    plt.xlabel('Sous-corpus')
    plt.xticks(rotation=90)
    plt.tight_layout()

    return fig
#ii
def afficher_repartition_langues(base):
    """
    Description :
        Génère un diagramme circulaire de la proportion des fichiers 
        FR et EN dans tout le corpus et retourne l'objet Figure.

    Paramètres :
        base -- str, le chemin du dossier racine à explorer.

    Retour :
        matplotlib.figure.Figure : L'objet graphique (ou None si aucune donnée).
    """
    fr, en = compter_par_langue(base)

    if fr == 0 and en == 0:
        return None

    tailles = [fr, en]
    labels = [f'Français ({fr})', f'Anglais ({en})']
    couleurs = ['cornflowerblue', 'darkorange']

    fig = plt.figure(figsize=(7, 7))

    plt.pie(tailles, labels=labels, colors=couleurs, autopct='%1.1f%%',
            startangle=90)
    plt.title('Proportion des langues Français / Anglais')
    plt.axis('equal')

    return fig
def afficher_repartition_langues_par_sous_corpus(base):
    """
    Description :
        Génère un diagramme en barres groupées de la répartition 
        FR/EN pour chaque sous-corpus et retourne l'objet Figure.

    Paramètres :
        base -- str, le chemin du dossier racine à explorer.

    Retour :
        matplotlib.figure.Figure : L'objet graphique (ou None en cas d'erreur).
    """
    # print("\n[Graphique 3] Génération : Répartition FR/EN par sous-corpus...")
    
    dic = explorer_corpus(base)
    
    if not dic:
        print("Erreur : Impossible de générer le graphique, corpus vide ou invalide.")
        return None

    noms = []
    nbfr = [] 
    nben = [] 

    # Récupération des données
    for ch in sorted(dic.keys()):
        noms.append(os.path.basename(ch))
        data = dic[ch]

        fr = 0
        en = 0

        for i in data['contenu']:
            ch_complet = os.path.join(ch, i)
            if os.path.isfile(ch_complet):
                if i.endswith('_fr.txt'):
                    fr += 1 
                elif i.endswith('_en.txt'):
                    en += 1 

        nbfr.append(fr) 
        nben.append(en)

    x = np.arange(len(noms))
    largeur = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    rects1 = ax.bar(x - largeur/2, nbfr, largeur,
                    label='Français', color='cornflowerblue')
    rects2 = ax.bar(x + largeur/2, nben, largeur,
                    label='Anglais', color='darkorange')

    ax.set_title('Nombre de documents FR/EN par sous-corpus')
    ax.set_ylabel('Nombre de documents')
    ax.set_xlabel('Sous-corpus')
    ax.set_xticks(x)
    ax.set_xticklabels(noms, rotation=90)
    ax.legend()

    fig.tight_layout()

    return fig
#iv
def tableau_de_bord_corpus(base):
    """
    Description :
        Exécute les 3 fonctions de génération graphique, récupère
        les objets Figure et les affiche l'un après l'autre.
        
    Paramètres :
        base  str, le chemin du dossier racine à explorer.

    Retour :
        None.
    """
    if not os.path.isdir(base):
        return
    fig1 = afficher_repartition_sous_corpus(base)
    # Si la figure a  été créée (n'est pas None), on l'affiche
    if fig1:
        fig1.show() 
        plt.show() 

    # --- Graphique 2 ---
    fig2 = afficher_repartition_langues(base)
    if fig2:
        fig2.show()
        plt.show()

    # --- Graphique 3 ---
    fig3 = afficher_repartition_langues_par_sous_corpus(base)
    if fig3:
        fig3.show()
        plt.show()

    return

# --- Tests unitaires (Exercice c) ---
def test_visuel_tableau_de_bord_corpus():

    # Setup 
    dir_test = "corpus_test_dashboard_seq"
    dir_ufr = os.path.join(dir_test, "UFR")
    dir_iut = os.path.join(dir_test, "IUT")

    fichiers = [
        os.path.join(dir_ufr, "etu01_fr.txt"),
        os.path.join(dir_ufr, "etu01_en.txt"),
        os.path.join(dir_iut, "etu03_en.txt"),
        os.path.join(dir_iut, "autre.log"),
        os.path.join(dir_test, "RACINE_fr.txt")
    ]
    # Total attendu: 2fr, 2en

    try:
        os.makedirs(dir_ufr, exist_ok=True)
        os.makedirs(dir_iut, exist_ok=True)
        for f in fichiers:
            with open(f, "w") as f_out: f_out.write("test")

        print("Structure de test (Tableau de Bord Séquentiel) créée...")

        #  1. Cas simple (Test visuel/manuel) 
        print("\n[TEST] Lancement du test visuel")
        print("ACTION REQUISE : 3 fenêtres de graphiques vont s'ouvrir l'une après l'autre.")
        print("Vérifiez visuellement chaque graphique, puis fermez-les pour continuer.\n")

        # Appel de la fonction à tester
        tableau_de_bord_corpus(dir_test)

        print("\n[TEST] Cas simple : Terminé.")

        #  2. Cas d’erreurs 
        print("\n[TEST] Cas d'erreur (chemin invalide) :")
        tableau_de_bord_corpus("chemin_errone_123")
        print("[TEST] Cas d'erreur : Passé")

        print("\n>>> Tous les tests du tableau de bord séquentiel sont passés.")

    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally:
        #  Nettoyage (Teardown) 
        print("\nNettoyage de l'environnement de test...")
        try:
            for f in fichiers:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(dir_ufr): os.rmdir(dir_ufr)
            if os.path.exists(dir_iut): os.rmdir(dir_iut)
            if os.path.exists(dir_test): os.rmdir(dir_test)
            print("Nettoyage terminé.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")

# Lancement du test
#test_visuel_tableau_de_bord_corpus()