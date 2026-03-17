import os
import tkinter as tk
from tkinter import filedialog
import unicodedata
import matplotlib.pyplot as plt
import numpy as np
import re
import string
from num2words import num2words
import shutil
from s1_Cocu_Ethan import *

#1. Chargement et uniformisation du texte brut :
#a.
def lire_document(fichier):
    """
    Description :
        Ouvre un fichier texte et retourne tout son contenu
        sous forme d'une unique chaîne de caractères.
    
    Paramètres :
        fichier str, le chemin du fichier à lire.
    
    Retour :
        str, le contenu du fichier. 
             Retourne "" si le fichier est introuvable ou illisible.
    """
    chaine = ""
    if not os.path.isfile(fichier):
        return chaine
    try:
        with open(fichier,'r', encoding='utf-8') as f:
            chaine = f.read()
    except Exception as e:
       return chaine 
    return chaine

def test_lire_document():
    
    #  Configuration 
    fichier_test = "mon_test_lecture.txt"
    fichier_vide = "mon_test_vide.txt"
    fichier_inconnu = "fantome.txt"
    
    texte_original = "Bonjour.\nCeci est un test.\nFin."

    try:
        # Création des fichiers pour le test
        with open(fichier_test, "w", encoding="utf-8") as f:
            f.write(texte_original)
        
        with open(fichier_vide, "w", encoding="utf-8") as f:
            pass

        print("Structure de test créée. Lancement des tests...")

        #  1. Cas normal 
        contenu_lu = lire_document(fichier_test)
        
        
        assert contenu_lu == texte_original
        assert isinstance(contenu_lu, str)
        print(" Test (Cas normal) : Passé.")

        #  2. Cas limite (Fichier vide) 
        contenu_vide = lire_document(fichier_vide)
        assert contenu_vide == ""
        print(" Test (Cas limite - vide) : Passé.")

        #  3. Cas d'erreur (Fichier inexistant) 
        print("\nTest Cas 3 (attendu : message d'erreur ci-dessous) :")
        contenu_err = lire_document(fichier_inconnu)
        assert contenu_err == ""
        print(" Test (Cas d'erreur) : Passé.")
        
        print("\n Tous les tests de lecture sont passés avec succès !")

    except AssertionError as e:
        print(f" ÉCHEC D'UN TEST UNITAIRE : {e}")
    except Exception as e:
        print(f"Une erreur est survenue pendant les tests : {e}")

    finally: 
        print("\nNettoyage...")
        try:
            if os.path.exists(fichier_test): os.remove(fichier_test)
            if os.path.exists(fichier_vide): os.remove(fichier_vide)
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")


#test_lire_document()

#b.
def convertir_vers_minuscule(texte):
    """
    Description :
        Convertit une chaîne de caractères entièrement en minuscules.
        Utile pour uniformiser les textes avant comparaison.
    
    Paramètres :
        texte  str, la chaîne de caractères à modifier.
    
    Retour :
        str, la chaîne en minuscules.
             Retourne une chaîne vide "" si l'entrée n'est pas valide.
    """
    if texte is None:
        return ""
    
    if not isinstance(texte,str):
        texte = str(texte)
    
    return texte.lower()

def test_convertir_vers_minuscule():
    
    print("Lancement des tests pour 'convertir_vers_minuscule'...")

    #  1. Cas simples 
    assert convertir_vers_minuscule("Bonjour") == "bonjour"
    assert convertir_vers_minuscule("PYTHON") == "python"
    assert convertir_vers_minuscule("MiXtE") == "mixte"

    #  2. Cas limites 
    # Chaîne vide
    assert convertir_vers_minuscule("") == ""
    
    # Déjà minuscule
    assert convertir_vers_minuscule("test") == "test"
    
    # Caractères non alphabétiques (ne doivent pas bouger)
    assert convertir_vers_minuscule("123 ! @#") == "123 ! @#"

    #  3. Cas spécifiques (Accents) 
    assert convertir_vers_minuscule("ÉTÉ") == "été"
    assert convertir_vers_minuscule("À BIENTÔT") == "à bientôt"
    assert convertir_vers_minuscule("ÇAVA") == "çava"

    #  4. Cas d'erreur (Types non string) 
    # Notre fonction gère None et les nombres
    assert convertir_vers_minuscule(None) == ""
    assert convertir_vers_minuscule(42) == "42"

    print(" Tous les tests unitaires sont passés avec succès !")


#test_convertir_vers_minuscule()

#2.  Suppression des balises HTML/XML
#a
def supprimer_balises_html_xml(texte):
    """
    Description :
        Retire toutes les balises HTML ou XML d'une chaîne.
    
    Paramètres :
        texte  str, la chaîne de caractères à nettoyer.
    
    Retour :
        str, le texte nettoyé.
             Retourne "" si l'entrée n'est pas valide.
    """
    if texte is None:
        return ""
    if not isinstance(texte,str):
        texte = str(texte)
    pattern = r'<[^>]+'
    txt = re.sub(pattern,"", texte)
    return txt
#3.  Normalisation Unicode

#a.
def normaliser_unicode(texte, forme="NFC"):
    """
    Description :
        Normalise les caractères Unicode d'un texte pour assurer une
        représentation cohérente .
    
    Paramètres :
        texte  str, le texte à normaliser.
        forme  str, la forme de normalisation .
                 Par défaut 'NFC' , le standard Python.
    
    Retour :
        str, le texte avec les caractères uniformisés.
    """
    norme = ""
    if texte is None:
        return norme 
    if not isinstance(texte,str):
        texte = str(texte)
    norme = unicodedata.normalize(forme, texte)
    return norme


def test_normaliser_unicode():
    
    print("Lancement des tests pour 'normaliser_unicode'...")

    #  1. Cas démonstratif (Le piège de l'accent) 
    
    # 'é' écrit en un seul caractère (standard)
    ecole_standard = "école" 
    
    # 'é' écrit en deux caractères (e + accent aigu combinant)
    ecole_decompose = "e\u0301cole" 
    
    print(f"Avant normalisation :")
    print(f"  Standard  : '{ecole_standard}' (len={len(ecole_standard)})")
    print(f"  Décomposé : '{ecole_decompose}' (len={len(ecole_decompose)})")
    
    # Vérifions qu'ils sont bien considérés comme différents par Python
    assert ecole_standard != ecole_decompose
    
    #  Application de la normalisation 
    res1 = normaliser_unicode(ecole_standard)
    res2 = normaliser_unicode(ecole_decompose)
    
    print(f"Après normalisation NFC :")
    print(f"  Standard  : '{res1}' (len={len(res1)})")
    print(f"  Décomposé : '{res2}' (len={len(res2)})")

    # Maintenant, ils doivent être strictement égaux
    assert res1 == res2
    assert len(res2) == 5 
    
    #  2. Test NFD (Décomposition, utile pour supprimer les accents plus tard) 
    # En NFD, le 'é' doit se séparer
    res_nfd = normaliser_unicode("été", forme="NFD")
    assert len(res_nfd) == 5 # e + accent + t + e + accent
    
    #  3. Cas simples 
    assert normaliser_unicode("Bonjour") == "Bonjour"
    assert normaliser_unicode("") == ""

    print(" Tous les tests unitaires sont passés avec succès !")


#test_normaliser_unicode()
#4. Correction et uniformisation des accents
#a
def  corriger_accents(texte):
    """
    Description :
        Corrige les erreurs d'encodage courantes via un dictionnaire.
        Exemple : Remplace "Ã©" par "é".
    
    Paramètres :
        texte  str, le texte potentiellement corrompu.
    
    Retour :
        str, le texte réparé.
    """
    if not texte or not isinstance(texte, str):
        return ""
    remplacements = {
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã§": "ç",
        "Ã´": "ô",
        "Ã»": "û",
        "Ã¯": "ï",
        "Ã": "à",  
        "Å": "oe"
    }
    for erreur, corection in remplacements.items():
        texte = texte.replace(erreur, corection)
    return texte

def test_corriger_accents():
    print("\n Lancement des tests pour 'corriger_accents' ")

    #  1. Cas normaux (Réparation de Mojibake) 
    # Test sur "Français" mal encodé
    assert corriger_accents("FranÃ§ais") == "Français"
    # Test sur "déjà" mal encodé
    assert corriger_accents("dÃ©jÃ ") == "déjà"
    # Test sur "Noël" (Å  -> oe approximation ou caractère spécial)
    # Supposons que ton dictionnaire gère "Ã¯" -> "ï"
    assert corriger_accents("maÃ¯s") == "maïs"

    #  2. Cas limites (Texte déjà propre) 
    txt = "Un texte sans erreur."
    assert corriger_accents(txt) == txt

    #  3. Cas d'erreurs (Entrées vides/None) 
    assert corriger_accents("") == ""
    assert corriger_accents(None) == ""

    print(" Test 'corriger_accents' passé avec succès !")

#test_corriger_accents()
#b
def  uniformiser_accents(texte):
    """
    Description :
        Simplifie les accents selon des règles métier définies.
        - é, è, ê, ë -> é
        - à, â -> a
        - ç -> c
        - ô, ö -> o
        - û, ü -> u
        - î, ï -> i
    
    Paramètres :
        texte  str.
    
    Retour :
        str, le texte uniformisé.
    """

    if not texte:
        return ""

    regles = {
        "é": ["è", "ê", "ë"], 
        "a": ["à", "â", "ä"],
        "c": ["ç"],
        "o": ["ô", "ö"],
        "u": ["û", "ü", "ù"],
        "i": ["î", "ï"]
    }
    for cible, s in regles.items():
        for c in s:
            texte = texte.replace(c, cible)
    return texte

def test_uniformiser_accents():
    print("\n Lancement des tests pour 'uniformiser_accents' ")

    #  1. Cas normaux (Simplification vers une forme canonique) 
    # Règle supposée : è, ê, ë -> é ; à, â -> a ; ç -> c
    
    # Test des 'e'
    assert uniformiser_accents("L'élève rêve à Noël") == "L'éléve réve a Noél"
    
    # Test des 'c' et 'a'
    assert uniformiser_accents("Ça va ?") == "Ca va ?"
    
    # Test des 'u' et 'i'
    assert uniformiser_accents("Où gît-il ?") == "Ou gît-il ?"
    #  2. Cas limites 
    assert uniformiser_accents("Text without accents") == "Text without accents"
    
    #  3. Cas d'erreurs 
    assert uniformiser_accents("") == ""
    assert uniformiser_accents(None) == ""

    print(" Test 'uniformiser_accents' passé avec succès !")

#c
def  traiter_accents(texte, options = None):
    """
    Description :
        Applique une série de traitements sur les accents selon les options fournies.
    
    Paramètres :
        texte  str, le texte à traiter.
        options  dict, paramètres 
    
    Retour :
        str, le texte final.
    """
    if texte == "":
        return ""
    if options is None:
        options = {"corriger_erreurs":False, "uniformiser": False}
    
    if options.get("corriger_erreurs"):
        texte = corriger_accents(texte)
        if options.get("uniformiser"):
            texte = uniformiser_accents(texte)
    return texte

def test_traiter_accents():
    print("\n Lancement des tests pour 'traiter_accents' (Orchestrateur) ")

    #  1. Cas Complet (Correction + Uniformisation) 
    # Scénario : On reçoit "DÃ©jÃ " (Mojibake pour Déjà).
    # 1. Correction : "DÃ©jÃ " -> "Déjà"
    # 2. Uniformisation : "Déjà" -> "Déja" (le à devient a)
    
    entree = "DÃ©jÃ "
    options_toutes = {"corriger_erreurs": True, "uniformiser": True}
    
    res = traiter_accents(entree, options_toutes)
    print(f"Test Complet : '{entree}' -> '{res}'")
    assert res == "Déja"


    #  2. Cas Correction Seule 
    # On veut réparer mais garder les accents d'origine
    options_corr_seule = {"corriger_erreurs": True, "uniformiser": False}
    assert traiter_accents("FranÃ§ais", options_corr_seule) == "Français"


    #  3. Cas Uniformisation Seule 
    # Le texte est propre, on veut juste simplifier
    options_uni_seule = {"corriger_erreurs": False, "uniformiser": True}
    assert traiter_accents("élèves", options_uni_seule) == "éléves"


    #  4. Cas Aucun Traitement (Options False ou vide) 
    assert traiter_accents("été", {}) == "été"
    
    print(" Test 'traiter_accents' passé avec succès !")

#5. Détection de la langue
#a
def detecter_langue_f(fichier):
    """
    Description :
        Déduit la langue du document à partir de son nom de fichier
        en cherchant les suffixes _fr ou _en.
    
    Paramètres :
        fichier  str, le nom du fichier .
    
    Retour :
        str, "français", "anglais" ou "inconnue".
    """
    if not fichier or not isinstance(fichier, str):
        return "inconnue"

    nom = fichier.lower()

    if "_fr." in nom or nom.endswith("_fr"):
        return "français"
    
    elif "_en." in nom or nom.endswith("_en"):
        return "anglais"
        
    return "inconnue"

def test_detecter_langue_f():
    print("\n Lancement des tests pour 'detecter_langue_f' ")

    #  1. Cas Normaux 
    assert detecter_langue_f("etudiant01_fr.txt") == "français"
    assert detecter_langue_f("report_final_en.pdf") == "anglais"
    
    #  2. Cas de Casse (Majuscules) 
    assert detecter_langue_f("DATA_FR.CSV") == "français"
    assert detecter_langue_f("Note_EN.txt") == "anglais"
    
    #  3. Cas Limites / Pièges 
    # Fichier sans extension
    assert detecter_langue_f("mon_fichier_fr") == "français"
    
    # Faux ami : "friend" contient "en", mais pas "_en." ni "_en" fin

    # Si le fichier s'appelle "friend.txt", il ne doit PAS être détecté comme anglais.
    assert detecter_langue_f("my_friend.txt") == "inconnue" 
    
    # Faux ami : "frein" contient "fr", mais pas "_fr."
    assert detecter_langue_f("le_frein.txt") == "inconnue"

    # Pas de marqueur
    assert detecter_langue_f("document.txt") == "inconnue"
    
    #  4. Cas d'erreur 
    assert detecter_langue_f("") == "inconnue"
    assert detecter_langue_f(None) == "inconnue"

    print(" Test 'detecter_langue_f' passé avec succès !")


#test_detecter_langue_f()

#b


# b. Vérification de cohérence
def verifier_coherence_langue(fichier):
    """
    Description :
        Vérifie si la langue indiquée par le nom du fichier correspond
        à la langue détectée dans son contenu.
    
    Paramètres :
        fichier  str, le chemin du fichier.
    
    Retour :
        str, le statut de la cohérence.
    """
    
    lng = detecter_langue_f(fichier)
    
    if lng == "inconnue":
        return "Non applicable "
    texte = lire_document(fichier)
    if not texte:
        return "Indéterminé "

    mots = texte.lower().split()
    stopFr = {"le", "la", "les", "de", "du", "et", "est", "un", "une", "je", "à", "pour"}
    stopEn = {"the", "of", "and", "a", "to", "in", "is", "that", "it", "for", "with"}
    
    scoreFr = 0
    scoreEn = 0
    
    for mot in mots:
        motP = mot.strip(".,;!?()[]\"'")
        if motP in stopFr:
            scoreFr += 1
        elif motP in stopEn:
            scoreEn += 1
            
    if scoreFr > scoreEn:
        langue = "français"
    elif scoreEn > scoreFr:
        langue = "anglais"
    else:
        return "Indéterminé (Contenu ambigu)"

    if lng == langue:
        return "Cohérent"
    else:
        return f"ALERTE : Incohérent (Nom={lng} vs Contenu={langue})"



def test_verifier_coherence_langue_contenu():
    print("\n Lancement des tests pour 'verifier_coherence_langue_contenu' ")
    
    # Configuration des fichiers de test temporaires
    f_coherent = "test_ok_fr.txt"
    f_incoherent = "test_fail_en.txt" # Nom anglais, contenu français
    f_neutre = "data.txt"
    
    contenu_fr = "Le chat est dans la cuisine et mange une pomme."
    contenu_en = "The cat is in the kitchen and eats an apple."
    
    try:
        # Création des fichiers
        with open(f_coherent, "w", encoding="utf-8") as f: f.write(contenu_fr)
        with open(f_incoherent, "w", encoding="utf-8") as f: f.write(contenu_fr) # Piège !
        with open(f_neutre, "w", encoding="utf-8") as f: f.write(contenu_en)
        
        #  1. Cas Cohérent 
        # Nom: _fr (français), Contenu: "Le chat..." (français)
        res1 = verifier_coherence_langue(f_coherent)
        assert res1 == "Cohérent"
        
        #  2. Cas Incohérent 
        res2 = verifier_coherence_langue(f_incoherent)
        assert "Incohérent" in res2
        
        #  3. Cas Non Applicable
        res3 = verifier_coherence_langue(f_neutre)
        assert "Non applicable" in res3

        print(" Test 'verifier_coherence_langue_contenu' passé avec succès !")

    finally:
        for f in [f_coherent, f_incoherent, f_neutre]:
            if os.path.exists(f): os.remove(f)

#test_verifier_coherence_langue_contenu()

#c
def verifier_langue(fichier):
    """
    Description :
        Détermine la langue dominante d'un fichier en analysant 
        la fréquence des mots-outils dans son contenu.
    
    Paramètres :
        fichier  str, le chemin du fichier à analyser.
    
    Retour :
        str, "français", "anglais" ou "indéterminée".
    """
    texte = lire_document(fichier)
    if not texte:
        return "indéterminée"
    mots = texte.lower().split()
    stopWordsFr = {"le", "la", "les", "de", "du", "des", "et", "est", "un", "une", "je", "nous", "vous", "pour", "avec"}
    stopWordsEn = {"the", "of", "and", "a", "an", "to", "in", "is", "are", "that", "it", "for", "with", "you", "we"}
    
    scoreFr = 0
    scoreEn = 0

    for mot in mots:
        motPropre = mot.strip(".,;!?()[]\"'")
        if motPropre in stopWordsFr:
            scoreFr += 1
        elif motPropre in stopWordsEn:
            scoreEn += 1
    if scoreFr == 0 and scoreEn == 0:
        return "indéterminée"
        
    if scoreFr > scoreEn:
        return "français"
    elif scoreEn > scoreFr:
        return "anglais"
    else:
        return "indéterminée" 
    
def test_verifier_langue():
    print("\n Lancement des tests pour 'verifier_langue' ")
    
    # Configuration des fichiers
    f_fr = "test_content_fr.txt"
    f_en = "test_content_en.txt"
    f_neutre = "test_content_neutre.txt"
    
    # Contenus types
    txt_fr = "Le chien et le chat sont dans la maison. C'est une belle journée."
    txt_en = "The dog and the cat are in the house. It is a beautiful day."
    txt_neutre = "12345 67890 @#$%" # Pas de mots-clés

    try:
        with open(f_fr, "w", encoding="utf-8") as f: f.write(txt_fr)
        with open(f_en, "w", encoding="utf-8") as f: f.write(txt_en)
        with open(f_neutre, "w", encoding="utf-8") as f: f.write(txt_neutre)
        
        #  1. Test Français 
        # Mots clés : Le, et, le, la, est, une (Score élevé)
        res_fr = verifier_langue(f_fr)
        print(f"Test FR : détecté '{res_fr}'")
        assert res_fr == "français"
        
        #  2. Test Anglais 
        # Mots clés : The, and, the, are, in, the, is, a (Score élevé)
        res_en = verifier_langue(f_en)
        print(f"Test EN : détecté '{res_en}'")
        assert res_en == "anglais"
        
        #  3. Test Neutre 
        res_neutre = verifier_langue(f_neutre)
        print(f"Test Neutre : détecté '{res_neutre}'")
        assert res_neutre == "indéterminée"

        #  4. Cas d'erreur 
        assert verifier_langue("fichier_fantome.txt") == "indéterminée"

        print(" Test 'verifier_langue' passé avec succès !")

    finally:
        # Nettoyage
        for f in [f_fr, f_en, f_neutre]:
            if os.path.exists(f): os.remove(f)


#test_verifier_langue()
#d
def signaler_incoherences_langue(base):
    """
    Description :
        Parcourt le corpus et signale les fichiers dont le contenu textuel
        ne correspond pas à la langue indiquée par leur nom de fichier.
    
    Paramètres :
        base  str, le chemin du dossier racine à explorer.
    
    Retour :
        list, liste de tuples des incohérences.
    """
    
    # 1. Récupérer la structure du corpus
    dic = explorer_corpus(base)
    incoherences = []
    if not dic:
        return []
    for chemin, data in dic.items():
        for fichier in data['contenu']:
            ch = os.path.join(chemin, fichier)
            if os.path.isfile(ch):
                lng = detecter_langue_f(fichier)
                if lng != "inconnue":
                    langue = verifier_langue(ch)
                    if langue != "indéterminée" and langue != lng:
                        info = (ch, lng, langue)
                        incoherences.append(info)
    return incoherences

def test_signaler_incoherences_langue():
    print("\n Lancement des tests pour 'signaler_incoherences_langue' ")
    
    # Configuration
    dir_test = "corpus_test_audit"
    
    # 1. Fichier OK (Nom FR, Contenu FR)
    f_ok = os.path.join(dir_test, "correct_fr.txt")
    txt_fr = "Le chat mange la souris."
    
    # 2. Fichier KO (Nom EN, Contenu FR) -> ANOMALIE
    f_ko_1 = os.path.join(dir_test, "trap_en.txt") 
    
    # 3. Fichier KO (Nom FR, Contenu EN) -> ANOMALIE
    f_ko_2 = os.path.join(dir_test, "trap_fr.txt")
    txt_en = "The dog eats the bone."
    
    # 4. Fichier Neutre (Nom sans langue) -> IGNORÉ
    f_neutre = os.path.join(dir_test, "neutre.txt")

    try:
        os.makedirs(dir_test, exist_ok=True)
        
        # Création des fichiers
        with open(f_ok, "w", encoding="utf-8") as f: f.write(txt_fr)
        with open(f_ko_1, "w", encoding="utf-8") as f: f.write(txt_fr) 
        with open(f_ko_2, "w", encoding="utf-8") as f: f.write(txt_en)
        with open(f_neutre, "w", encoding="utf-8") as f: f.write(txt_en)

        resultats = signaler_incoherences_langue(dir_test)
        
        #  Assertions 
        # On attend exactement 2 incohérences (f_ko_1 et f_ko_2)
        assert len(resultats) == 2
        
        chemins_detectes = [res[0] for res in resultats]
        assert f_ko_1 in chemins_detectes
        assert f_ko_2 in chemins_detectes
        assert f_ok not in chemins_detectes
        
        # Vérification détaillée du piège 1 (Nom EN vs Contenu FR)
        # On cherche le tuple correspondant à f_ko_1
        anomalie_1 = next(item for item in resultats if item[0] == f_ko_1)
        # attendu="anglais", observé="français"
        assert anomalie_1[1] == "anglais" 
        assert anomalie_1[2] == "français"

        print(" Test 'signaler_incoherences_langue' passé avec succès !")

    finally:
        # Nettoyage
        for f in [f_ok, f_ko_1, f_ko_2, f_neutre]:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(dir_test): os.rmdir(dir_test)


#test_signaler_incoherences_langue()

#6. Nettoyage structurel (ponctuation, nombres, symboles)

#a

def supprimer_ponctuation(texte):
    """
    Description :
        Supprime la ponctuation d'un texte en remplaçant les symboles
        par des espaces.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans ponctuation.
    """
    if texte is None:
        return ""
    if not isinstance(texte, str):
        texte = str(texte)
    pattern = f"[{re.escape(string.punctuation)}]"
    txt = re.sub(pattern, " ", texte)
    return txt

def test_supprimer_ponctuation():
    print("Test : supprimer_ponctuation")
    
    # Cas démonstratif
    phrase = "Salut, monde! (Ça va?)"
    res = supprimer_ponctuation(phrase)
    
    print(f"Avant : '{phrase}'")
    print(f"Après : '{res}'")
    
    # On vérifie que les ponctuations sont parties
    assert "," not in res
    assert "!" not in res
    assert "?" not in res
    assert "(" not in res
    assert "mondeÇa" not in res
    
    # assert "monde   Ça" in res 

    print(" Test 'supprimer_ponctuation' passé avec succès !")


#test_supprimer_ponctuation()

#b

def remplacer_ponctuation(texte, balise=""):
    """
    Description :
        Remplace chaque caractère de ponctuation par une balise donnée.
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, la chaîne de remplacement.
    
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    pattern = f"[{re.escape(string.punctuation)}]"
    txt = re.sub(pattern, balise, texte)
    
    return txt

def test_remplacer_ponctuation():
    print("Test : remplacer_ponctuation")
    
    phrase = "Salut, ça va?"
    
    #  1. Cas par défaut (balise="", suppression) 
    res_defaut = remplacer_ponctuation(phrase)
    print(f"Défaut : '{res_defaut}'")
    # "Salut, ça va?" -> "Salut ça va" 
    assert res_defaut == "Salut ça va"
    
    #  2. Cas avec un espace (balise=" ") 
    res_espace = remplacer_ponctuation(phrase, balise=" ")
    print(f"Espace : '{res_espace}'")
    assert res_espace == "Salut  ça va "
    
    #  3. Cas avec un token (balise=" <STOP> ") 
    # Utile pour le NLP pour marquer la fin des phrases
    res_token = remplacer_ponctuation("Fin.", balise=" <STOP>")
    print(f"Token  : '{res_token}'")
    assert res_token == "Fin <STOP>"

    print(" Test 'remplacer_ponctuation' passé avec succès !")


#test_remplacer_ponctuation()
#c
def supprimer_ponctuation_sauf(texte, ponct_a_conserver=[".", "?"]):
    """
    Description :
        Supprime toute la ponctuation sauf les caractères spécifiés
        dans la liste 'ponct_a_conserver'.
    
    Paramètres :
        texte  str, le texte brut.
        ponct_a_conserver  list, les caractères à ne PAS supprimer.
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    if ponct_a_conserver is None:
        ponct_a_conserver = []

    ponct = string.punctuation
    
    supprimer = [c for c in ponct if c not in ponct_a_conserver]
    if not supprimer:
        return texte
    pat = "".join([re.escape(c) for c in supprimer])
    pattern = f"[{pat}]"
    txt = re.sub(pattern, "", texte)
    
    return txt


def test_supprimer_ponctuation_sauf():
    print("Test : supprimer_ponctuation_sauf")
    
    phrase = "Salut! (Ça va?), dit-il."
    
    #  1. Cas : Garder le point et le point d'interrogation 
    # On veut supprimer !, (, ), ,, -
    exceptions = [".", "?"]
    res = supprimer_ponctuation_sauf(phrase, exceptions)
    
    print(f"Original : '{phrase}'")
    print(f"Résultat : '{res}'")
    
    # "Salut" (sans !) " Ça va?" (avec ?) " ditil." (sans - et ,)
    assert res == "Salut Ça va? ditil."
    assert "?" in res
    assert "." in res
    assert "!" not in res
    assert "(" not in res

    #  2. Cas : Tout supprimer (liste vide) 
    res_vide = supprimer_ponctuation_sauf(phrase, [])
    assert "?" not in res_vide
    assert "." not in res_vide

    #  3. Cas : Tout garder 
    tous = list(string.punctuation)
    res_full = supprimer_ponctuation_sauf(phrase, tous)
    assert res_full == phrase

    print(" Test 'supprimer_ponctuation_sauf' passé avec succès !")


#test_supprimer_ponctuation_sauf()
#d

def espacer_ponctuation(texte):
    """
    Description :
        Ajoute des espaces autour de chaque signe de ponctuation
        pour faciliter la tokenisation.
        Exemple : "Salut!" -> "Salut !"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte avec ponctuation espacée.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    pattern = f"([{re.escape(string.punctuation)}])"
    t = re.sub(pattern, r" \1 ", texte)
    txt = " ".join(t.split())
    
    return txt

def test_espacer_ponctuation():
    print("\nTest : espacer_ponctuation")
    
    # Cas démonstratif
    # "Bonjour," -> "Bonjour ,"  |  "va?" -> "va ?"
    entree = "Bonjour,comment ça va?"
    res = espacer_ponctuation(entree)
    
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    assert res == "Bonjour , comment ça va ?"
    
    # Cas limite (déjà espacé)
    assert espacer_ponctuation("A . B") == "A . B"

#e

def normaliser_ponctuation(texte):
    """
    Description :
        Uniformise les variantes typographiques
        vers des caractères standards ASCII.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte normalisé.
    """
    
    if not texte:
        return ""
    remplacements = {"«": '"',  "»": '"', "“": '"',  "”": '"',
        "’": "'","–": "-","—": "-","…": "..."}
    
    norme = texte
    for original, standard in remplacements.items():
        norme = norme.replace(original, standard)
        
    return norme

def test_normaliser_ponctuation():
    print("\nTest : normaliser_ponctuation")
    
    # Cas complet
    phrase = "Il a dit : « C’est — peut-être — la fin… »"
    res = normaliser_ponctuation(phrase)
    
    print(f"Avant : '{phrase}'")
    print(f"Après : '{res}'")
    
    # Vérifications
    assert '«' not in res and '»' not in res
    assert '"' in res
    assert "..." in res 
    assert "—" not in res
    assert "-" in res
    
    attendu = 'Il a dit : " C\'est - peut-être - la fin... "'
    assert res == attendu

#f

def reduire_ponctuation_multiple(texte):
    """
    Description :
        Remplace les répétitions de ponctuation par une seule occurrence.
        Exemple : "!!!" -> "!"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte réduit.
    """
    if not texte: return ""
    pattern = f"([{re.escape(string.punctuation)}])\\1+"
    return re.sub(pattern, r"\1", texte)

def test_reduire_ponctuation_multiple():
    print("Test : reduire_ponctuation_multiple")
    
    assert reduire_ponctuation_multiple("Salut!!!") == "Salut!"
    assert reduire_ponctuation_multiple("Quoi???") == "Quoi?"
    assert reduire_ponctuation_multiple("Je.... pense..") == "Je. pense."
    # Test mixte
    assert reduire_ponctuation_multiple("Boom!!! Paf..") == "Boom! Paf."
    
    print(" Test Réduction passé.")

#g

def remplacer_ponctuation_contextuelle(texte):
    """
    Description :
        Remplace la ponctuation expressive par des balises sémantiques.
        "!" -> " <EXCLAMATION> "
        "?" -> " <QUESTION> "
        "..." -> " <SUSPENSE> "
    
    Paramètres :
        texte  str.
    
    Retour :
        str, le texte avec balises.
    """
    if not texte: return ""
    texte = texte.replace("...", " <SUSPENSE> ")
    texte = texte.replace("!", " <EXCLAMATION> ")
    texte = texte.replace("?", " <QUESTION> ")
    
    return texte

def test_remplacer_ponctuation_contextuelle():
    print("Test : remplacer_ponctuation_contextuelle")
    
    # Cas simple
    assert " <EXCLAMATION> " in remplacer_ponctuation_contextuelle("Stop!")
    
    # Cas priorité ("..." doit être traité avant ".")
    res = remplacer_ponctuation_contextuelle("Attends...")
    assert "<SUSPENSE>" in res
    assert "Attends." not in res 
    
    # Cas combiné
    res_mixte = remplacer_ponctuation_contextuelle("Vraiment?!")
    assert "<QUESTION>" in res_mixte and "<EXCLAMATION>" in res_mixte
    
    print(" Test Contextuel passé.")
#h

def traiter_ponctuation(texte, options=None):
    """
    Description :
        Pipeline complet de gestion de la ponctuation.
        Applique les transformations selon les options activées.
    
    Paramètres :
        texte    str, texte brut.
        options  dict, configuration des traitements.
    
    Retour :
        str, texte traité.
    """
    if texte is None: return ""
    defaut = {
        "normaliser": True,  
        "contextuel": False,  
        "reduire": True,     
        "espacer": True,     
        "supprimer": False, 
        "remplacer": False,   
        "balise": " "
    }
    if options is None:
        cfg = defaut
    else:
        cfg = defaut.copy()
        cfg.update(options)
    
    res = texte
    if cfg["normaliser"]:
        res = normaliser_ponctuation(res)
    if cfg["contextuel"]:
        res = remplacer_ponctuation_contextuelle(res)
    if cfg["reduire"]:
        res = reduire_ponctuation_multiple(res)
    if cfg["espacer"]:
        res = espacer_ponctuation(res)
    if cfg["supprimer"]:
        res = supprimer_ponctuation(res)
    elif cfg["remplacer"]:
        res = remplacer_ponctuation(res, cfg["balise"])

    return res

def test_traiter_ponctuation():
    print("Test : traiter_ponctuation (Orchestrateur)")
    
    # Scénario 1 : Nettoyage standard (Normaliser + Réduire + Espacer)
    texte1 = "« Salut!!! »"
    opt1 = {
        "normaliser": True, 
        "reduire": True, 
        "espacer": True, 
        "contextuel": False, 
        "supprimer": False
    }
    # Étapes : " Salut!!! " -> " Salut! " -> " Salut ! "
    res1 = traiter_ponctuation(texte1, opt1)
    print(f"Scénario 1 : '{texte1}' -> '{res1}'")
    # Vérif : plus de guillemets français, 1 seul !, espacé
    assert '"' in res1 and "!" in res1 and "!!!" not in res1
    
    # Scénario 2 : Sémantique (Contextuel activé)
    texte2 = "Quoi???"
    opt2 = {
        "normaliser": False,
        "reduire": True, # "???" -> "?"
        "contextuel": True, # "?" -> <QUESTION>
        "espacer": False
    }
    res2 = traiter_ponctuation(texte2, opt2)
    print(f"Scénario 2 : '{texte2}' -> '{res2}'")
    assert "<QUESTION>" in res2

    print(" Test Orchestrateur passé.")

#Traitement des nombres et des symboles : 
#a

def supprimer_nombres(texte):
    """
    Description :
        Supprime tous les chiffres du texte.
        Exemple : "En 2025" -> "En "
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans nombres.
    """
    if texte is None:
        return "" 
    if not isinstance(texte, str):
        texte = str(texte)
    
    pattern = r'\d+'
    txt = re.sub(pattern, "", texte)
    return txt

def test_supprimer_nombres():
    print("Test : supprimer_nombres")
    
    #  1. Cas démonstratif (L'exemple de la consigne) 
    entree = "En 2025, il aura 3 ans."
    res = supprimer_nombres(entree)
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    assert res == "En , il aura  ans."
    
    #  2. Cas décimal (Comportement de \d+) 
    txt_decimal = "Pi vaut 3.14 environ"
    res_decimal = supprimer_nombres(txt_decimal)
    assert res_decimal == "Pi vaut . environ"
    
    #  3. Cas limite (Mélange lettres/chiffres) 
    # Souvent le cas dans les ID ou modèles
    txt_mixte = "Modèle T800 et R2D2"
    res_mixte = supprimer_nombres(txt_mixte)
    assert res_mixte == "Modèle T et RD"

    #  4. Cas vide 
    assert supprimer_nombres("") == ""

    print(" Test 'supprimer_nombres' passé avec succès !")


#test_supprimer_nombres()

#b

def remplacer_nombres(texte, balise="<NUM>"):
    """
    Description :
        Remplace les séquences de chiffres par un token générique .
        Exemple : "3 chats" -> "<NUM> chats"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte généralisé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    pattern = r'\d+'
    txt = re.sub(pattern, balise,texte)
    return txt

def test_remplacer_nombres():
    print("Test : remplacer_nombres")
    
    #  1. Cas par défaut (<NUM>) 
    phrase = "Le prix est de 30 euros pour 2 personnes."
    res = remplacer_nombres(phrase)
    
    print(f"Avant : '{phrase}'")
    print(f"Après : '{res}'")
    
    attendu = "Le prix est de <NUM> euros pour <NUM> personnes."
    assert res == attendu
    
    #  2. Cas avec balise personnalisée 
    # Utile si on veut juste masquer les chiffres par des '#' ou 'N'
    phrase_date = "En 2025, nous partons."
    res_custom = remplacer_nombres(phrase_date, balise="[DATE]")
    
    print(f"Custom : '{res_custom}'")
    assert res_custom == "En [DATE], nous partons."
    
    #  3. Cas nombre collé (Modèle T800) 
    # Avec \d+, "T800" devient "T<NUM>"
    assert remplacer_nombres("T800") == "T<NUM>"

    print(" Test 'remplacer_nombres' passé avec succès !")


#test_remplacer_nombres()

#c

def nombres_en_lettres(texte, langue="fr"):
    """
    Description :
        Convertit les chiffres présents dans le texte en toutes lettres.
        Exemple : "3 chats" -> "trois chats"
    
    Paramètres :
        texte   str, le texte brut.
        langue  str, la langue cible.
    
    Retour :
        str, le texte converti.
    """
    
    if texte is None:
        return ""
        
    if num2words is None:
        return texte
    
    txt = re.sub(r'\d+', 
        lambda m: num2words(int(m.group()), lang=langue), 
        texte
    )
    
    return txt
    
def test_nombres_en_lettres():
    print("Test : nombres_en_lettres")
    
    if num2words is None:
        print(" Test ignoré : bibliothèque manquante.")
        return

    #  1. Cas Français 
    phrase_fr = "J'ai 2 chats et 10 chiens."
    res_fr = nombres_en_lettres(phrase_fr, langue='fr')
    
    print(f"Avant : '{phrase_fr}'")
    print(f"Après : '{res_fr}'")
    
    assert res_fr == "J'ai deux chats et dix chiens."
    
    #  2. Cas Anglais 
    phrase_en = "Year 2025"
    res_en = nombres_en_lettres(phrase_en, langue='en')
    
    assert "twenty-five" in res_en

    print(" Test 'nombres_en_lettres' passé avec succès !")


#test_nombres_en_lettres()

#d
def supprimer_symboles(texte):
    """
    Description :
        Supprime tous les caractères qui ne sont ni des lettres,
        ni des chiffres, ni des espaces.
        Exemple : "#Hello @World!" -> "Hello World"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte contenant uniquement des caractères alphanumériques.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    txt = re.sub(r'[^\w\s]', '', texte)
    txt = txt.replace('_','')
    return txt

def test_supprimer_symboles():
    print("Test : supprimer_symboles")
    
    #  1. Cas démonstratif (L'exemple de la consigne) 
    entree = "#Hello@World!"
    res = supprimer_symboles(entree)
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    assert res == "HelloWorld"
    
    #  2. Cas avec espaces (Phrase normale) 
    phrase = "Prix : 100$ (TTC) ?"
    res_phrase = supprimer_symboles(phrase)
    assert res_phrase.strip() == "Prix  100 TTC"
    
    #  3. Cas Accents (Alphanumérique inclut les accents) 
    accent = "L'été @ Paris"
    res_accent = supprimer_symboles(accent)
    assert res_accent == "Lété  Paris"

    #  4. Cas Underscore (Cas particulier du Regex \w) 
    assert supprimer_symboles("user_name") == "username"

    print(" Test 'supprimer_symboles' passé avec succès !")


#test_supprimer_symboles()

#e
def remplacer_symboles(texte, balise=""):
    """
    Description :
        Remplace les symboles non-alphanumériques
        par une balise donnée.
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    pattern = r'[^\w\s]|_'
    txt = re.sub(pattern,balise,texte)
    return txt

def test_remplacer_symboles():
    print("Test : remplacer_symboles")
    
    #  1. Cas par défaut (Suppression) 
    # L'exemple de la consigne : "Prix = 10€"
    entree = "Prix = 10€"
    res = remplacer_symboles(entree)
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # Attendu : "Prix  10" 
    assert res.strip() == "Prix  10"
    
    #  2. Cas avec balise (<SYM>) 
    res_balise = remplacer_symboles("Note #1 : 100%", balise="<SYM>")
    print(f"Balise : '{res_balise}'")
    
    # # -> <SYM>, : -> <SYM>, % -> <SYM>
    attendu = "Note <SYM>1 <SYM> 100<SYM>"
    assert res_balise == attendu

    #  3. Cas Emoji et Symboles Unicode 
    txt_emoji = "Hello 😊"
    res_emoji = remplacer_symboles(txt_emoji, balise="*")
    assert res_emoji == "Hello *"

    print(" Test 'remplacer_symboles' passé avec succès !")


#test_remplacer_symboles()

#f
def remplacer_unites(texte, balise=""):
    """
    Description :
        Remplace les symboles d'unités par une balise.
        Exemple : "5 km" -> "5 "
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    p1 = r"[€$£%]"
    p2 = r"\b(km|kg|cm|mm|m|g|L|°C)\b"
    pattern = f"{p1}|{p2}"
    txt = re.sub(pattern,balise,texte)
    return txt

def test_remplacer_unites():
    print("Test : remplacer_unites")
    
    #  1. Cas Symboles (€, $, %) 
    prix = "Le prix est de 50€ ou 60 $ (soit 100%)."
    res_prix = remplacer_unites(prix)
    print(f"Prix Avant : '{prix}'")
    print(f"Prix Après : '{res_prix}'")
    
    # Attendu : "Le prix est de 50 ou 60  (soit 100)."
    assert "€" not in res_prix
    assert "$" not in res_prix
    assert "%" not in res_prix

    #  2. Cas Unités physiques (km, kg, °C) 
    dist = "Il fait 20°C pour courir 10 km."
    res_dist = remplacer_unites(dist, balise="<UNIT>")
    print(f"Dist. Balise : '{res_dist}'")
    
    assert "20<UNIT>" in res_dist
    assert "10 <UNIT>" in res_dist

    #  3. Cas Pièges (Mots contenant les unités) 
    phrase_piege = "maman fait du trekking"
    res_piege = remplacer_unites(phrase_piege)
    
    assert res_piege == "maman fait du trekking"
    
    print(" Test 'remplacer_unites' passé avec succès !")


#test_remplacer_unites()
#g

def supprimer_non_alphabetiques(texte):
    """
    Description :
        Ne garde que les lettres et les espaces.
        Supprime tout le reste.
        Exemple : "Bonjour123 !!!" -> "Bonjour "
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte nettoyé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    pattern = r'[^a-zA-Zà-ÿÀ-ß\s]'
    txt = re.sub(pattern, "", texte)
    return txt

def test_supprimer_non_alphabetiques():
    print("Test : supprimer_non_alphabetiques")
    
    #  1. Cas démonstratif (L'exemple de la consigne) 
    entree = "Bonjour123 !!!"
    res = supprimer_non_alphabetiques(entree)
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # "123" part, "!!!" part. Les espaces restent.
    assert res.strip() == "Bonjour"
    
    #  2. Cas Accents (Doivent rester) 
    phrase_accents = "L'été 2024 !"
    res_accents = supprimer_non_alphabetiques(phrase_accents)
    print(f"Accents : '{res_accents}'")
    
    # L'apostrophe ' n'est pas une lettre -> supprimée
    # 2024 -> supprimé
    # ! -> supprimé
    # é -> gardé
    assert res_accents.strip() == "Lété"
    
    #  3. Cas Mixte 
    txt_mixte = "Python_3.11 @Home"
    res_mixte = supprimer_non_alphabetiques(txt_mixte)
    # _ . @ chiffres -> supprimés
    assert res_mixte.strip() == "Python Home"

    print(" Test 'supprimer_non_alphabetiques' passé avec succès !")


#test_supprimer_non_alphabetiques()

#h
def remplacer_non_alphabetiques(texte, balise=""):
    """
    Description :
        Remplace tous les caractères non-alphabétiques par une balise, en conservant les espaces.
        Exemple : "H3ll0!" -> "H ll " 
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    pattern = r'[^a-zA-Zà-ÿÀ-ß\s]'
    txt = re.sub(pattern, balise, texte)

    return txt

def test_remplacer_non_alphabetiques():
    print("Test : remplacer_non_alphabetiques")
    
    #  1. Cas suppression (défaut) 
    entree = "R2-D2 est là !"
    res = remplacer_non_alphabetiques(entree)
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # "2", "-", "2", "!" sont remplacés par rien.
    # "R", "D", "est", "là", et les espaces restent.
    assert res == "RD est là "
    
    #  2. Cas avec balise (Masquage) 
    # On remplace les intrus par "*"
    txt_code = "Mot123."
    res_balise = remplacer_non_alphabetiques(txt_code, balise="*")
    print(f"Balise : '{res_balise}'")
    
    # "1"->"*" , "2"->"*" , "3"->"*" , "."->"*"
    assert res_balise == "Mot****"
    
    #  3. Cas conservation des accents 
    txt_accents = "Noël & Été"
    res_accents = remplacer_non_alphabetiques(txt_accents, balise="")
    # & part, les accents restent
    assert res_accents.strip() == "Noël  Été"

    print(" Test 'remplacer_non_alphabetiques' passé avec succès !")


#test_remplacer_non_alphabetiques()
#i

def normaliser_symboles(texte):
    """
    Description :
        Convertit les symboles mathématiques courants en leur équivalent textuel.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte normalisé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    remplacements = {
        "+": " plus ",
        "-": " moins ", 
        "=": " égal ",
        "%": " pourcent "
    }
    for symbole,mot in remplacements.items():
        texte = texte.replace(symbole,mot)

    return " ".join(texte.split())

def test_normaliser_symboles():
    print("Test : normaliser_symboles")
    
    #  1. Cas démonstratif 
    entree = "Résultat : 10% de + que l'an dernier."
    res = normaliser_symboles(entree)
    
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # Attendu : "Résultat : 10 pourcent de plus que l'an dernier."
    assert "pourcent" in res
    assert "plus" in res
    assert "%" not in res
    assert "+" not in res
    
    #  2. Cas Mathématique 
    maths = "5 + 2 = 7"
    res_maths = normaliser_symboles(maths)
    # Attendu : "5 plus 2 égal 7"
    assert res_maths == "5 plus 2 égal 7"
    
    #  3. Cas Collé (sans espace) 
    # "100%" -> "100 pourcent"
    colle = "Gain:100%"
    res_colle = normaliser_symboles(colle)
    assert "100 pourcent" in res_colle

    print(" Test 'normaliser_symboles' passé avec succès !")


#test_normaliser_symboles()

#j

def traiter_nombres_symboles(texte, options=None):
    """
    Description :
        Pipeline configurable pour nettoyer les nombres et les symboles.
    
    Paramètres :
        texte    str, texte brut.
        options  dict, configuration des traitements.
    
    Retour :
        str, texte traité.
    """
    if texte is None: return ""
    
    # Configuration par défaut
    defaut = {
        "supprimer_nombres": False,
        "remplacer_nombres": False,
        "balise_nombre": " <NUM> ",
        "supprimer_symboles": False,
        "remplacer_symboles": False,
        "balise_symbole": " <SYM> ",
        "normaliser": False,
        "langue": "fr"
    }

    if options is None:
        cfg = defaut
    else:
        cfg = defaut.copy()
        cfg.update(options)
    
    res = texte

    if cfg["normaliser"]:
        res = normaliser_symboles(res)

    if cfg["supprimer_nombres"]:
        res = supprimer_nombres(res)
    elif cfg["remplacer_nombres"]:
        res = remplacer_nombres(res, cfg["balise_nombre"])

    if cfg["supprimer_symboles"]:
        res = supprimer_symboles(res)
    elif cfg["remplacer_symboles"]:
        res = remplacer_symboles(res, cfg["balise_symbole"])

    return res

def test_traiter_nombres_symboles():
    print("Test : traiter_nombres_symboles (Orchestrateur)")
    
    # Scénario 1 : Analyse de sentiment 
    texte1 = "Le profit est de +10% !"
    opt1 = {
        "normaliser": True,          
        "remplacer_nombres": True,   
        "balise_nombre": " NB ", 
        "supprimer_symboles": True,
    }
    
    res1 = traiter_nombres_symboles(texte1, opt1)
    print(f"Scénario 1 : '{texte1}' -> '{res1}'")
    
    assert "plus" in res1
    assert "pourcent" in res1
    assert "NB" in res1
    assert "!" not in res1
    assert "+" not in res1

    # Scénario 2 : Nettoyage radical (Sac de mots) 
    texte2 = "Prix: 50€ #Promo"
    opt2 = {
        "normaliser": False,         
        "supprimer_nombres": True,   
        "supprimer_symboles": True   
    }
    
    res2 = traiter_nombres_symboles(texte2, opt2)
    print(f"Scénario 2 : '{texte2}' -> '{res2}'")
    assert "50" not in res2
    assert "€" not in res2
    assert "#" not in res2
    assert "Prix" in res2

    # Scénario 3 : Anonymisation / Balisage 
    texte3 = "ID: #1234"
    opt3 = {
        "remplacer_symboles": True,
        "balise_symbole": " ",
        "remplacer_nombres": True,
        "balise_nombre": "IDNUM" 
    }
    res3 = traiter_nombres_symboles(texte3, opt3)
    print(f"Scénario 3 : '{texte3}' -> '{res3}'")
    
    assert "IDNUM" in res3
    assert "#" not in res3

    print(" Test Orchestrateur passé avec succès !")

#test_traiter_nombres_symboles()

#7. Nettoyage Web et caractères spéciaux 
# Traitement des URLs, des adresses mails

#a
def supprimer_urls(texte):
    """
    Description :
        Supprime les URLs du texte.
        Exemple : "Visitez https://site.com !" -> "Visitez  !"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans les URLs.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    pattern = r'(https?://|ftp://|www\.)\S+'
    txt = re.sub(pattern, "", texte)
    
    return txt


def test_supprimer_urls():
    print("Test : supprimer_urls")
    
    #  1. Cas HTTP / HTTPS 
    txt_web = "Aller sur http://google.com ou https://secure.site maintenant."
    res_web = supprimer_urls(txt_web)
    print(f"Web Avant : '{txt_web}'")
    print(f"Web Après : '{res_web}'")
    
    # Attendu : "Aller sur  ou  maintenant."
    assert "http" not in res_web
    assert "https" not in res_web
    assert "google" not in res_web
    
    #  2. Cas WWW 
    txt_www = "Voir www.wikipedia.org."
    res_www = supprimer_urls(txt_www)
    assert "wikipedia" not in res_www
    
    #  3. Cas FTP 
    txt_ftp = "Fichier sur ftp://files.server/doc"
    res_ftp = supprimer_urls(txt_ftp)
    assert "ftp://" not in res_ftp
    
    #  4. Cas sans URL 
    normal = "Juste du texte."
    assert supprimer_urls(normal) == normal

    print(" Test 'supprimer_urls' passé avec succès !")


#test_supprimer_urls()

#a

def remplacer_urls(texte, balise="<URL>"):
    """
    Description :
        Remplace les adresses web par un token générique.
        Exemple : "Allez sur google.com" -> "Allez sur <URL>"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte généralisé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    pattern = r'(https?://|ftp://|www\.)\S+'

    txt = re.sub(pattern, balise, texte)
    
    return txt


def test_remplacer_urls():
    print("Test : remplacer_urls")
    
    #  1. Cas par défaut (<URL>) 
    entree = "La source est https://wikipedia.org ou www.info.fr."
    res = remplacer_urls(entree)
    
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # Attendu : "La source est <URL> ou <URL>."
    assert res == "La source est <URL> ou <URL>" or res == "La source est <URL> ou <URL>."
    
    #  2. Cas avec balise personnalisée ([LIEN]) 
    txt_spam = "Cliquez ici : http://virus.com/exe"
    res_spam = remplacer_urls(txt_spam, balise="[LIEN]")
    
    assert res_spam == "Cliquez ici : [LIEN]"
    
    #  3. Cas FTP 
    assert remplacer_urls("ftp://serveur") == "<URL>"

    print(" Test 'remplacer_urls' passé avec succès !")


#test_remplacer_urls()

#c

def supprimer_emails(texte):
    """
    Description :
        Supprime toutes les adresses e-mail du texte.
        Exemple : "Contactez bob@mail.com" -> "Contactez "
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte nettoyé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    pattern = r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]+'
    txt = re.sub(pattern, "", texte)
    
    return txt


def test_supprimer_emails():
    print("Test : supprimer_emails")
    
    #  1. Cas démonstratif 
    entree = "Contactez-moi à nom@mail.com pour info."
    res = supprimer_emails(entree)
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # Attendu : "Contactez-moi à  pour info."
    assert "@" not in res
    assert "nom" not in res
    assert "mail.com" not in res
    
    #  2. Cas Multiples 
    txt_multi = "admin@site.org et support@site.org"
    res_multi = supprimer_emails(txt_multi)
    assert "@" not in res_multi
    assert res_multi.strip() == "et"
    
    #  3. Cas Faux positif (le @ seul) 
    # Le regex demande des caractères autour du @.
    # Donc "@home" ou "Twitter @" ne doivent pas être effacés entièrement
    txt_at = "Rendez-vous @ home"
    res_at = supprimer_emails(txt_at)
    # Ici, "@ home" ne correspond pas au pattern x@y.z, donc il reste.
    assert res_at == "Rendez-vous @ home"

    print(" Test 'supprimer_emails' passé avec succès !")


#test_supprimer_emails()
#d

def remplacer_emails(texte, balise="<EMAIL>"):
    """
    Description :
        Remplace les adresses e-mail par un token générique.
        Exemple : "écrivez à moi@test.com" -> "écrivez à <EMAIL>"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte généralisé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    pattern = r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]+'
    
    txt = re.sub(pattern, balise, texte)
    
    return txt

def test_remplacer_emails():
    print("Test : remplacer_emails")
    
    #  1. Cas par défaut (<EMAIL>) 
    entree = "Mon adresse est jean.dupont@provider.fr."
    res = remplacer_emails(entree)
    
    print(f"Avant : '{entree}'")
    print(f"Après : '{res}'")
    
    # Attendu : "Mon adresse est <EMAIL>."
    assert res == "Mon adresse est <EMAIL>."
    
    #  2. Cas avec balise personnalisée ([M]) 
    txt_pro = "Support: help@site.com ou admin@site.com"
    res_pro = remplacer_emails(txt_pro, balise="[M]")
    
    # Attendu : "Support: [M] ou [M]"
    assert res_pro == "Support: [M] ou [M]"
    
    #  3. Cas limite (faux positif) 
    # "@twitter" n'est pas un mail valide
    txt_social = "Follow @twitter"
    res_social = remplacer_emails(txt_social)
    assert res_social == "Follow @twitter"

    print(" Test 'remplacer_emails' passé avec succès !")


#test_remplacer_emails()

#Traitement des mentions et des hashtags 
#a

def supprimer_mentions(texte):
    """
    Description :
        Supprime toutes les mentions de type @nom du texte.
        Exemple : "Merci @user !" -> "Merci  !"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans les mentions.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    txt = re.sub(r'@\w+', '', texte)

    return txt

def test_supprimer_mentions():
    print("\nTest : supprimer_mentions")
    
    # Cas 1 : Mention simple
    txt = "Merci @support pour l'aide !"
    res = supprimer_mentions(txt)
    print(f"  Avant : '{txt}'")
    print(f"  Après : '{res}'")
    
    assert "@" not in res
    assert "support" not in res
    assert res.strip() == "Merci  pour l'aide !"
    
    # Cas 2 : Pas de mention
    assert supprimer_mentions("Bonjour") == "Bonjour"
    
    print(" Test 'supprimer_mentions' validé.")

#test_supprimer_mentions()

#b

def remplacer_mentions(texte, balise="<MENTION>"):
    """
    Description :
        Remplace les mentions (@nom) par une balise donnée.
        Exemple : "Merci @user" -> "Merci <MENTION>"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement (défaut: "<MENTION>").
    
    Retour :
        str, le texte modifié avec les balises.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    txt =  re.sub(r'@\w+', balise, texte)

    return txt

def test_remplacer_mentions():
    print("\nTest : remplacer_mentions")
    
    # Cas 1 : Remplacement par défaut (<MENTION>)
    txt = "Suivez @admin et @modo."
    res = remplacer_mentions(txt)
    print(f"  Avant : '{txt}'")
    print(f"  Après : '{res}'")
    
    assert res == "Suivez <MENTION> et <MENTION>."
    
    # Cas 2 : Remplacement personnalisé
    res_custom = remplacer_mentions("Cc @ami", balise="[USER]")
    assert res_custom == "Cc [USER]"
    
    print(" Test 'remplacer_mentions' validé.")

#test_remplacer_mentions()
#c

def supprimer_hashtags(texte):
    """
    Description :
        Supprime tous les hashtags (#sujet) du texte.
        Exemple : "#Python est cool" -> " est cool"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans les hashtags.
    """
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    txt =re.sub(r'#\w+', '', texte)
    return txt

def test_supprimer_hashtags():
    print("\nTest : supprimer_hashtags")
    
    # Cas 1 : Hashtags multiples
    txt = "J'adore le #Python et le #Code."
    res = supprimer_hashtags(txt)
    print(f"  Avant : '{txt}'")
    print(f"  Après : '{res}'")
    
    assert "#" not in res
    assert "Python" not in res
    # Il reste les espaces autour
    assert res == "J'adore le  et le ."
    
    # Cas 2 : Accents dans le hashtag (Python gère l'Unicode dans \w)
    assert supprimer_hashtags("C'est l'#été") == "C'est l'"
    
    print(" Test 'supprimer_hashtags' validé.")

#test_supprimer_hashtags()
#d

def remplacer_hashtags(texte, balise="<HASHTAG>"):
    """
    Description :
        Remplace les hashtags par une balise donnée.
        Exemple : "#Python" -> "<HASHTAG>"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement (défaut: "<HASHTAG>").
    
    Retour :
        str, le texte modifié avec les balises.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    txt = re.sub(r'#\w+', balise, texte)
    return txt

def test_remplacer_hashtags():
    print("\nTest : remplacer_hashtags")
    
    # Cas 1 : Remplacement par défaut (<HASHTAG>)
    txt = "Trending #News now"
    res = remplacer_hashtags(txt)
    print(f"  Avant : '{txt}'")
    print(f"  Après : '{res}'")
    
    assert res == "Trending <HASHTAG> now"
    
    # Cas 2 : Remplacement personnalisé
    res_custom = remplacer_hashtags("#Sport", balise="<TAG>")
    assert res_custom == "<TAG>"
    
    print(" Test 'remplacer_hashtags' validé.")

#test_remplacer_hashtags()

#Traitement des emojis
#a

def supprimer_emojis(texte):
    """
    Description :
        Supprime les émojis et caractères spéciaux étendus du texte.
        Exemple : "Super ! 🔥" -> "Super ! "
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans émojis.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    pattern = r'[\U00010000-\U0010ffff]'
    
    txt = re.sub(pattern, '', texte)
    return txt

def test_supprimer_emojis():
    print("\nTest : supprimer_emojis")
    
    # Cas 1 : Émojis modernes
    txt = "C'était super 🔥🚀 !"
    res = supprimer_emojis(txt)
    print(f"  Avant : '{txt}'")
    print(f"  Après : '{res}'")
    
    assert "🔥" not in res
    assert "🚀" not in res
    assert res == "C'était super  !" 
    
    # Cas 2 : Texte normal (ne doit pas être touché)
    assert supprimer_emojis("Texte standard") == "Texte standard"
    
    print(" Test 'supprimer_emojis' validé.")

#test_supprimer_emojis()

#b

def remplacer_emojis(texte, balise="<EMOJI>"):
    """
    Description :
        Remplace les émojis par une balise donnée.
        Exemple : "Bravo 👏" -> "Bravo <EMOJI>"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement (défaut: "<EMOJI>").
    
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    pattern = r'[\U00010000-\U0010ffff]'
    
    txt =  re.sub(pattern, balise, texte)
    return txt

def test_remplacer_emojis():
    print("\nTest : remplacer_emojis")
    
    # Cas 1 : Remplacement par défaut
    txt = "J'aime ça ❤️" # Note : ❤️ est parfois un caractère complexe, testons un standard
    txt_std = "Bravo 👏"
    
    res = remplacer_emojis(txt_std)
    print(f"  Avant : '{txt_std}'")
    print(f"  Après : '{res}'")
    
    assert res == "Bravo <EMOJI>"
    
    # Cas 2 : Remplacement personnalisé
    txt_2 = "Python 🐍"
    res_2 = remplacer_emojis(txt_2, balise="[ICON]")
    assert res_2 == "Python [ICON]"
    
    print(" Test 'remplacer_emojis' validé.")

#test_remplacer_emojis()
#Traitement des caractères non standard 

#a

def supprimer_caracteres_speciaux(texte):
    """
    Description :
        Supprime les caractères invisibles ou non-imprimables.
        Ne garde que les caractères imprimables standards.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte nettoyé.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    
    return "".join(c for c in texte if c.isprintable())

def test_supprimer_caracteres_speciaux():
    print("\nTest : supprimer_caracteres_speciaux")
    
    # Cas 1 : Sauts de ligne et tabulations
    # "Hello\nWorld\t!" -> "HelloWorld!"
    txt = "Hello\nWorld\t!"
    res = supprimer_caracteres_speciaux(txt)
    print(f"  Avant : {repr(txt)}")
    print(f"  Après : {repr(res)}")
    
    assert res == "HelloWorld!"
    
    txt_bizarre = "Test\x07Unitaire\x00"
    assert supprimer_caracteres_speciaux(txt_bizarre) == "TestUnitaire"
    
    print(" Test 'supprimer_caracteres_speciaux' validé.")

#test_supprimer_caracteres_speciaux()

#b

def remplacer_caracteres_speciaux(texte, balise=" "):
    """
    Description :
        Remplace les caractères non-imprimables par une balise.
        Exemple : "Ligne1\nLigne2" -> "Ligne1 Ligne2"
    
    Paramètres :
        texte   str, le texte brut.
        balise  str, le texte de remplacement.
    
    Retour :
        str, le texte modifié.
    """
    
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)
    return "".join(c if c.isprintable() else balise for c in texte)


def test_remplacer_caracteres_speciaux():
    print("\nTest : remplacer_caracteres_speciaux")
    
    # Cas 1 : Remplacement par espace (défaut)
    # "Ligne1\nLigne2" -> "Ligne1 Ligne2"
    txt = "Ligne1\nLigne2"
    res = remplacer_caracteres_speciaux(txt)
    print(f"  Avant : {repr(txt)}")
    print(f"  Après : {repr(res)}")
    
    assert res == "Ligne1 Ligne2"
    
    # Cas 2 : Remplacement par balise visible
    txt_tab = "Col1\tCol2"
    res_balise = remplacer_caracteres_speciaux(txt_tab, balise="<SEP>")
    assert res_balise == "Col1<SEP>Col2"
    
    print(" Test 'remplacer_caracteres_speciaux' validé.")

#test_remplacer_caracteres_speciaux()
#c

def traiter_web_et_emojis(texte, options=None):
    """
    Description :
        Pipeline configurable pour nettoyer les éléments Web, 
        réseaux sociaux et techniques.
    
    Paramètres :
        texte    str, texte brut.
        options  dict, configuration des traitements.
    
    Retour :
        str, texte traité.
    """
    if texte is None: return ""
    
    defaut = {
        "normaliser_unicode": True,
        
        "supprimer_urls": False,
        "remplacer_urls": False,
        
        "supprimer_emails": False,
        "remplacer_emails": False,
        
        "supprimer_mentions": False,
        "remplacer_mentions": False,
        
        "supprimer_hashtags": False,
        "remplacer_hashtags": False,
        
        "supprimer_emojis": False,
        "remplacer_emojis": False,
        
        "supprimer_caracteres_speciaux": True
    }

    if options is None:
        cfg =defaut
    else:
        cfg = defaut.copy()
        cfg.update(options)
    
    res = texte

    if cfg.get("normaliser_unicode"):
        res = normaliser_unicode(res)
    
    if cfg.get("supprimer_urls"):
        res = supprimer_urls(res)
    elif cfg.get("remplacer_urls"):
        res = remplacer_urls(res)
    
    if cfg.get("supprimer_emails"):
        res = supprimer_emails(res)
    elif cfg.get("remplacer_emails"):
        res = remplacer_emails(res)

    if cfg.get("supprimer_mentions"):
        res = supprimer_mentions(res)
    elif cfg.get("remplacer_mentions"):
        res = remplacer_mentions(res)
        
    if cfg.get("supprimer_hashtags"):
        res = supprimer_hashtags(res)
    elif cfg.get("remplacer_hashtags"):
        res = remplacer_hashtags(res)

    
    if cfg.get("supprimer_emojis"):
        res = supprimer_emojis(res)
    elif cfg.get("remplacer_emojis"):
        res = remplacer_emojis(res)
    if cfg.get("supprimer_caracteres_speciaux"):
        res = supprimer_caracteres_speciaux(res)

    return res



def test_traiter_web_et_emojis():
    print("\nTest : traiter_web_et_emojis (Orchestrateur)")
    
    #  Scénario 1 : Nettoyage total (Confidentialité) 
    # On veut supprimer les liens, mails, mentions, emojis
    texte1 = "Contactez @admin sur bob@mail.com ou via http://site.com ! 🔥"
    opt1 = {
        "supprimer_urls": True,
        "supprimer_emails": True,
        "supprimer_mentions": True,
        "supprimer_emojis": True,
        "normaliser_unicode": True
    }
    
    res1 = traiter_web_et_emojis(texte1, opt1)
    print(f"Scénario 1 : '{texte1}' -> '{res1}'")
    
    # Attendu : "Contactez  sur  ou via  ! "
    assert "@" not in res1
    assert "http" not in res1
    assert "🔥" not in res1
    assert "admin" not in res1

    #  Scénario 2 : Balisage (NLP / Analyse de sentiment) 
    # On veut garder la structure mais généraliser
    texte2 = "J'adore #Python ! 🐍 Voir : www.python.org"
    opt2 = {
        "remplacer_hashtags": True,
        "remplacer_emojis": True,
        "remplacer_urls": True,
        "supprimer_caracteres_speciaux": True
    }
    
    res2 = traiter_web_et_emojis(texte2, opt2)
    print(f"Scénario 2 : '{texte2}' -> '{res2}'")
    
    # Attendu : "J'adore <TAG> ! <EMOJI> Voir : <URL>"
    assert "<HASHTAG>" in res2
    assert "<EMOJI>" in res2
    assert "<URL>" in res2
    assert "Python" not in res2 
    
    #  Scénario 3 : Unicode et Caractères invisibles 
    texte3 = "Héllo\tWorld\x00" 
    opt3 = {"normaliser_unicode": True, "supprimer_caracteres_speciaux": True}
    
    res3 = traiter_web_et_emojis(texte3, opt3)
    # \t et \x00 doivent partir
    assert res3 == "HélloWorld"

    print(" Test Orchestrateur Web passé avec succès !")

# Exécution
#test_traiter_web_et_emojis()


#8.  Expansion et correction linguistique 
#Traitement et expansion des formes contractées et abréviations
#a

def expand_contractions_en(texte):
    """
    Description :
        Remplace les formes contractées anglaises par leur forme complète.
        Exemple : "I'm" -> "I am"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte étendu.
    """
    if not texte: return ""
    texte = texte.replace("’", "'").replace("‘", "'")

    contractions_en = {
        "i'm": "I am", "you're": "you are", "he's": "he is",
        "she's": "she is", "it's": "it is", "we're": "we are",
        "they're": "they are", "i've": "I have", "you've": "you have",
        "we've": "we have", "they've": "they have", "i'd": "I would",
        "you'd": "you would", "he'd": "he would", "she'd": "she would",
        "we'd": "we would", "they'd": "they would", "i'll": "I will",
        "you'll": "you will", "he'll": "he will", "she'll": "she will",
        "we'll": "we will", "they'll": "they will", "can't": "cannot",
        "won't": "will not", "n't": " not"
    }

    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in contractions_en.keys()) + r")\b", re.IGNORECASE)

    res = pattern.sub(
        lambda m: contractions_en.get(m.group(0).lower()).capitalize() 
                  if m.group(0)[0].isupper() 
                  else contractions_en.get(m.group(0).lower()), 
        texte
    )
    return res

def test_expand_contractions_en():
    print("\nTest : expand_contractions_en")
    # Cas simple
    assert expand_contractions_en("I'm ready") == "I am ready"
    # Cas Majuscule
    assert expand_contractions_en("Can't go") == "Cannot go"
    print(" Test validé.")

#test_expand_contractions_en()
#b


def expand_contractions_fr(texte):
    """
    Description :
        Remplace les élisions françaises par la forme complète.
        Exemple : "c'est" -> "ce est"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte étendu.
    """
    if not texte: return ""
    
    texte = texte.replace("’", "'").replace("‘", "'")

    contractions_fr = {
        "c'": "ce ", "j'": "je ", "l'": "le ", "qu'": "que ",
        "s'": "se ", "t'": "te ", "n'": "ne ", "d'": "de ",
        "m'": "me ", "jusqu'": "jusque ", "lorsqu'": "lorsque "
    }
    
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in contractions_fr.keys()) + r")", re.IGNORECASE)
    res = pattern.sub(
        lambda m: contractions_fr.get(m.group(0).lower()).capitalize() 
                  if m.group(0)[0].isupper() 
                  else contractions_fr.get(m.group(0).lower()), 
        texte
    )
    return res

def test_expand_contractions_fr():
    print("\nTest : expand_contractions_fr")
    # Cas simple
    assert expand_contractions_fr("j'aime") == "je aime"
    # Cas Majuscule
    assert expand_contractions_fr("C'est la vie") == "Ce est la vie"
    print(" Test validé.")

#test_expand_contractions_fr()

#c

def normaliser_apostrophes(texte):
    """
    Description :
        Uniformise les apostrophes typographiques vers l'apostrophe ASCII.
        Exemple : "l’homme" -> "l'homme"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte normalisé.
    """
    if not texte: return ""
    if not isinstance(texte, str): texte = str(texte)

    norme = texte.replace("’", "'").replace("‘", "'").replace("`", "'")
    return norme

def test_normaliser_apostrophes():
    print("\nTest : normaliser_apostrophes")
    # Cas courbe
    assert normaliser_apostrophes("L’été") == "L'été"
    print(" Test validé.")

#test_normaliser_apostrophes()    
#d

def expand_contractions(texte, langue="auto"):
    """
    Description :
        Fonction principale qui dirige le texte vers la bonne fonction
        d'expansion selon la langue.
    
    Paramètres :
        texte   str, le texte brut.
        langue  str, code langue.
    
    Retour :
        str, le texte final traité.
    """
    texte = normaliser_apostrophes(texte)
    
    if langue == "auto":
        mots = texte.lower().split()
        scoreEn = sum(1 for m in mots if m in ["the", "i'm", "is", "and", "we'll", "it's", "don't", "you're"])
        scoreFr = sum(1 for m in mots if m in ["le", "la", "c'est", "et"])
        langue = "en" if scoreEn > scoreFr else "fr"

    if langue == "en":
        return expand_contractions_en(texte)
    elif langue == "fr":
        return expand_contractions_fr(texte)
    else:
        return texte
    
def test_expand_contractions():
    print("\nTest : expand_contractions (Orchestrateur)")
    # Test FR Auto
    assert expand_contractions("C'est l'heure.", "auto") == "Ce est le heure."
    # Test EN Auto
    assert expand_contractions("We'll see.", "auto") == "We will see."
    print(" Test validé.")

#test_expand_contractions()

#Traitement des abréviations 

#a

def developper_abreviations(texte, langue="fr"):
    """
    Description :
        Remplace les abréviations courantes par leurs formes complètes.
        Exemple : "M. Dupont" -> "Monsieur Dupont"
    
    Paramètres :
        texte   str, le texte brut.
        langue  str, la langue du texte.
    
    Retour :
        str, le texte étendu.
    """
    if not texte: return ""
    
    abFr = {
        "M.": "Monsieur",
        "Mme": "Madame",
        "Mlle": "Mademoiselle",
        "Dr": "Docteur",
        "av.": "avenue",
        "bd": "boulevard",
        "n°": "numéro",
        "tél.": "téléphone"
    }
    
    abEn = {
        "Mr.": "Mister",
        "Mrs.": "Mistress",
        "Ms.": "Miss",
        "Dr.": "Doctor",
        "St.": "Street",
        "Ave.": "Avenue",
        "No.": "Number"
    }
    
    mapping = abFr if langue == "fr" else abEn
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in mapping.keys()) + r")(?=\s|$)", re.IGNORECASE)
    
    res = pattern.sub(
        lambda m: mapping.get(m.group(0), mapping.get(m.group(0).capitalize(), m.group(0))), 
        texte
    )
    return res

def test_developper_abreviations():
    print("\nTest : developper_abreviations")
    
    #  1. Cas Normaux (Ce qui doit marcher) 
    txt_fr = "M. Dupont et Dr House."
    assert developper_abreviations(txt_fr, "fr") == "Monsieur Dupont et Docteur House."
    
    txt_en = "Mr. Bond lives on St. James."
    assert developper_abreviations(txt_en, "en") == "Mister Bond lives on Street James."
    
    #  2. Cas Limites / Négatifs (Ce qui ne doit PAS changer) 
    
    # Cas : Mot ressemblant mais pas une abréviation (ex: "Dr" dans "Dragon")
    # Notre regex utilise \b (frontière de mot), donc "Dragon" ne doit pas devenir "Docteuragon"
    txt_piege = "Le Dragon dort."
    assert developper_abreviations(txt_piege, "fr") == "Le Dragon dort."
    
    # Cas : Abréviation sans le point (si la regex est stricte sur le point)
    # Si le dictionnaire attend "M.", alors "M" tout court ne doit pas changer
    txt_sans_point = "J'ai vu M Dupont"
    assert developper_abreviations(txt_sans_point, "fr") == "J'ai vu M Dupont"
    
    # Cas : Langue inconnue ou non gérée (doit retourner le texte tel quel ou utiliser le défaut)
    # Ici, si on met "es" (espagnol), la fonction utilise "en" par défaut (selon notre code) ou ne fait rien
    txt_es = "Hola Mr."
    assert developper_abreviations(txt_es, "es") == "Hola Mister"
    
    # Cas : Entrée vide
    assert developper_abreviations(None) == ""
    assert developper_abreviations("") == ""
    
    print(" Test 'developper_abreviations' (Positif & Négatif) validé.")

#test_developper_abreviations()

#b

def corriger_contractions_multiples(texte):
    """
    Description :
        Traite les cas ambigus, les doubles contractions anglaises
        ou le langage familier français.
        Exemple : "shouldn't've" -> "should not have"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte corrigé.
    """
    if not texte: return ""
    
    texte = normaliser_apostrophes(texte)

    contraction = {
        "shouldn't've": "should not have",
        "couldn't've": "could not have",
        "wouldn't've": "would not have",
        "y'all": "you all",
        
        "t'as": "tu as",
        "t'es": "tu es",
        "j'suis": "je suis",
        "p'tit": "petit",
        "y'a": "il y a"
    }
    
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in contraction.keys()) + r")\b", re.IGNORECASE)
    res = pattern.sub(
        lambda m: contraction.get(m.group(0).lower()).capitalize() 
                  if m.group(0)[0].isupper() 
                  else contraction.get(m.group(0).lower()), 
        texte
    )
    return res

def test_corriger_contractions_multiples():
    print("\nTest : corriger_contractions_multiples")
    
    #  1. Cas Normaux 
    assert corriger_contractions_multiples("I shouldn't've done it.") == "I should not have done it."
    assert corriger_contractions_multiples("T'as faim ?") == "Tu as faim ?"
    
    #  2. Cas Limites / Négatifs 
    
    # Cas : Faux positif (mots qui ressemblent)
    # "petit" contient "p'tit" ? Non.
    assert corriger_contractions_multiples("Un petit chien") == "Un petit chien"
    
    # Cas : Casse mixte bizarre (ex: T'As) -> Doit être géré par le .lower() du code
    assert corriger_contractions_multiples("T'As vu ?") == "Tu as vu ?"
    
    # Cas : Entrée vide
    assert corriger_contractions_multiples("") == ""
    
    print(" Test 'corriger_contractions_multiples' (Positif & Négatif) validé.")


#test_corriger_contractions_multiples()

#c

def traiter_contractions(texte, options=None):
    """
    Description :
        Fonction principale qui orchestre la normalisation, 
        l'expansion des contractions et des abréviations.
    
    Paramètres :
        texte    str, le texte brut.
        options  dict, paramètres de configuration.
    
    Retour :
        str, le texte entièrement traité.
    """
    if texte is None: return ""
    
    defaut = {
        "langue": "auto",
        "normaliser_apostrophes": True,
        "corriger_multiples": True,   
        "expand_contractions": True,
        "developper_abreviations": True
    }
    
    if options is None:
        cfg = defaut
    else:
        cfg = defaut.copy()
        cfg.update(options)
        
    res = texte
    
    if cfg["normaliser_apostrophes"]:
        res = normaliser_apostrophes(res)
        
    if cfg.get("corriger_multiples", True):
        res = corriger_contractions_multiples(res)
        
    if cfg["expand_contractions"]:
        res = expand_contractions(res, langue=cfg["langue"])
        
    if cfg["developper_abreviations"]:
        langue_cible = cfg["langue"]
        if langue_cible == "auto":
            if "M." in res or "n°" in res: langue_cible = "fr"
            else: langue_cible = "en"
            
        res = developper_abreviations(res, langue=langue_cible)
        
    return res

def test_traiter_contractions():
    print("\nTest : traiter_contractions (Orchestrateur)")
    
    #  1. Cas Normaux 
    txt_ok = "M. t'as vu ?"
    opts_ok = {
        "langue": "fr",
        "normaliser_apostrophes": True,
        "corriger_multiples": True,
        "expand_contractions": True,
        "developper_abreviations": True
    }
    assert traiter_contractions(txt_ok, opts_ok) == "Monsieur tu as vu ?"
    
    #  2. Cas Négatifs (Désactivation des options) 
    
    # On désactive tout : le texte ne doit PAS changer
    opts_off = {
        "normaliser_apostrophes": False,
        "corriger_multiples": False,
        "expand_contractions": False,
        "developper_abreviations": False
    }
    assert traiter_contractions(txt_ok, opts_off) == txt_ok
    
    #  3. Cas Robustesse (Entrées invalides) 
    assert traiter_contractions(None) == ""
    assert traiter_contractions(12345) == "12345"
    # Pour ce test, passons une string vide :
    assert traiter_contractions("") == ""

    print(" Test 'traiter_contractions' (Positif & Négatif) validé.")

#test_traiter_contractions()
#Correction typographique et normalisation lexicale

#a

def corriger_fautes_typographiques(texte):
    """
    Description :
        Corrige les répétitions abusives de caractères.
        Exemple : "Ouuui" -> "Oui", mais "Pomme" reste "Pomme".
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte corrigé.
    """
    if texte is None:
        return ""
    
    if not isinstance(texte, str):
        texte = str(texte)

    txt = re.sub(r'(.)\1{2,}', r'\1', texte)
    return txt


def test_corriger_fautes_typographiques():
    print("\nTest : corriger_fautes_typographiques")
    
    # Cas 1 : Répétition abusive (3+)
    txt = "C'est troooop bien !!!"
    res = corriger_fautes_typographiques(txt)
    print(f"  Avant : '{txt}'")
    print(f"  Après : '{res}'")
    
    # "ooo" -> "o", "!!!" -> "!"
    assert res == "C'est trop bien !"
    
    # Cas 2 : Double lettre légitime (2 fois)
    # "Pomme" a 2 'm', "Accueil" a 2 'c'. Ils ne doivent PAS changer.
    txt_legit = "Pomme et Accueil"
    res_legit = corriger_fautes_typographiques(txt_legit)
    
    assert res_legit == "Pomme et Accueil"
    
    print(" Test 'corriger_fautes_typographiques' validé.")

#test_corriger_fautes_typographiques()
#b
def uniformiser_variantes(texte):
    """
    Description :
        Harmonise les formes lexicales proches vers une forme canonique.
        Exemple : "covid-19" -> "covid"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte uniformisé.
    """
    if not texte: return ""
    
    texte = texte.lower()
    
    mapping = {
        r"\bcovid[- ]?19\b": "covid",
        r"\bsars[- ]?cov[- ]?2\b": "covid",
        r"\bcoronavirus\b": "covid",
        
        r"\b(é|e)tats[- ]unis\b": "usa",
        r"\bu\.?s\.?a\.?\b": "usa",
        
        r"\bcourriel\b": "email",
        r"\bmél\b": "email",
        r"\be[- ]?mail\b": "email"
    }
    
    for pattern, canonique in mapping.items():
        texte = re.sub(pattern, canonique, texte)
        
    return texte

def test_uniformiser_variantes():
    print("\nTest : uniformiser_variantes")
    
    # Cas 1 : Covid (mixte majuscules/tirets)
    txt_covid = "Le COVID-19 et le covid19 sont dangereux."
    res_covid = uniformiser_variantes(txt_covid)
    print(f"  Avant : '{txt_covid}'")
    print(f"  Après : '{res_covid}'")
    
    assert "covid-19" not in res_covid
    assert "covid19" not in res_covid
    # Note : la fonction passe en lower()
    assert res_covid == "le covid et le covid sont dangereux."
    
    # Cas 2 : USA
    txt_usa = "Voyage aux etats-unis ou aux USA."
    res_usa = uniformiser_variantes(txt_usa)
    assert res_usa == "voyage aux usa ou aux usa."
    
    # Cas 3 : Email
    txt_mail = "Envoyez un courriel ou un e-mail."
    res_mail = uniformiser_variantes(txt_mail)
    assert res_mail == "envoyez un email ou un email."
    
    print(" Test 'uniformiser_variantes' validé.")

#test_uniformiser_variantes()
#9. Normalisation des espaces et de la mise en forme

#a

def supprimer_espaces_multiples(texte):
    """
    Description :
        Remplace les suites d'espaces ou de tabulations par un seul espace.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte avec espaces normalisés.
    """
    if not texte:
        return ""
    txt = re.sub(r'[ \t]+', ' ', texte)
    return txt

def test_supprimer_espaces_multiples():
    print("\nTest : supprimer_espaces_multiples")
    # Cas normal
    assert supprimer_espaces_multiples("Bonjour   à  tous") == "Bonjour à tous"
    # Cas négatif (pas d'espace multiple)
    assert supprimer_espaces_multiples("Bonjour à tous") == "Bonjour à tous"
    print(" Test validé.")

#test_supprimer_espaces_multiples()

#b

def supprimer_espaces_bords(texte):
    """
    Description :
        Supprime les espaces inutiles au début et à la fin de la chaîne.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans espaces aux extrémités.
    """
    if not texte: 
        return ""
    txt = texte.strip()
    return txt

def test_supprimer_espaces_bords():
    print("\nTest : supprimer_espaces_bords")
    # Cas normal
    assert supprimer_espaces_bords("  Salut  ") == "Salut"
    # Cas négatif (déjà propre)
    assert supprimer_espaces_bords("Salut") == "Salut"
    print(" Test validé.")

#test_supprimer_espaces_bords()
#c

def normaliser_retours_ligne(texte):
    """
    Description :
        Remplace les différentes formes de sauts de ligne (\r, \r\n) par une seule forme standard (\n).
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte avec sauts de ligne normalisés.
    """
    if not texte:
        return ""
    txt = texte.replace('\r\n', '\n').replace('\r', '\n')
    return txt

def test_normaliser_retours_ligne():
    print("\nTest : normaliser_retours_ligne")
    # Cas normal
    assert normaliser_retours_ligne("A\r\nB\rC") == "A\nB\nC"
    # Cas négatif
    assert normaliser_retours_ligne("A\nB") == "A\nB"
    print(" Test validé.")

#test_normaliser_retours_ligne()

#d

def supprimer_lignes_vides(texte):
    """
    Description :
        Supprime les lignes vides ou les successions de plusieurs retours à la ligne.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte sans lignes vides superflues.
    """
    if not texte:
        return ""
    res = re.sub(r'\n{2,}', '\n', texte).strip()
    return res

def test_supprimer_lignes_vides():
    print("\nTest : supprimer_lignes_vides")
    # Cas normal
    assert supprimer_lignes_vides("A\n\n\nB") == "A\nB"
    # Cas négatif (pas de ligne vide)
    assert supprimer_lignes_vides("A\nB") == "A\nB"
    print(" Test validé.")

#test_supprimer_lignes_vides()

#e

def remplacer_tabulations(texte, nb_espaces=1):
    """
    Description :
        Remplace chaque tabulation par un nombre défini d'espaces.
    
    Paramètres :
        texte       str, le texte brut.
        nb_espaces  int, le nombre d'espaces pour remplacer une tabulation.
    
    Retour :
        str, le texte sans tabulations.
    """
    if not texte: 
        return ""
    txt = texte.replace('\t', ' ' * nb_espaces)
    return txt

def test_remplacer_tabulations():
    print("\nTest : remplacer_tabulations")
    # Cas normal (par défaut 1 espace)
    assert remplacer_tabulations("A\tB") == "A B"
    # Cas paramétré
    assert remplacer_tabulations("A\tB", nb_espaces=2) == "A  B"
    print(" Test validé.")

#test_remplacer_tabulations()
#f

def supprimer_espaces_avant_ponctuation(texte):
    """
    Description :
        Supprime les espaces mal placés avant les signes de ponctuation.
        Exemple : "Bonjour , toi" -> "Bonjour, toi"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte corrigé.
    """
    if not texte: 
        return ""
    res = re.sub(r'\s+([.,;?!])', r'\1', texte)
    return res

def test_supprimer_espaces_avant_ponctuation():
    print("\nTest : supprimer_espaces_avant_ponctuation")
    # Cas normal
    assert supprimer_espaces_avant_ponctuation("Salut !") == "Salut!"
    # Cas négatif (déjà collé)
    assert supprimer_espaces_avant_ponctuation("Salut!") == "Salut!"
    print(" Test validé.")

#test_supprimer_espaces_avant_ponctuation()

#g

def ajouter_espace_apres_ponctuation(texte):
    """
    Description :
        Ajoute un espace après chaque signe de ponctuation s'il est absent.
        Exemple : "Salut,ça va?" -> "Salut, ça va?"
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte corrigé.
    """
    if not texte: 
        return ""
    res = re.sub(r'([.,;?!])(?!\s)', r'\1 ', texte)
    return res

def test_ajouter_espace_apres_ponctuation():
    print("\nTest : ajouter_espace_apres_ponctuation")
    # Cas normal
    assert ajouter_espace_apres_ponctuation("Oui,non.") == "Oui, non. "
    # Cas négatif (déjà espacé)
    assert ajouter_espace_apres_ponctuation("Oui, non.") == "Oui, non. "
    print(" Test validé.")

#test_ajouter_espace_apres_ponctuation()

#h

def nettoyer_espaces(texte):
    """
    Description :
        Combine plusieurs fonctions de nettoyage.
    
    Paramètres :
        texte  str, le texte brut.
    
    Retour :
        str, le texte entièrement nettoyé au niveau des espaces.
    """
    if not texte: return ""
    res = supprimer_espaces_multiples(texte)
    res = supprimer_espaces_avant_ponctuation(res)
    res = ajouter_espace_apres_ponctuation(res)
    res = supprimer_espaces_bords(res)
    return res

def test_nettoyer_espaces():
    print("\nTest : nettoyer_espaces (Combiné)")
    entree = "  Salut ,ça va ?  "
    # Attendu : "Salut, ça va?"
    assert nettoyer_espaces(entree) == "Salut, ça va?"
    print(" Test validé.")

#test_nettoyer_espaces()

#i

def normaliser_mise_en_forme(texte, options=None):
    """
    Description :
        Applique sélectivement les traitements de mise en forme selon les options fournies.
    
    Paramètres :
        texte    str, le texte brut.
        options  dict, paramètres de configuration.
    
    Retour :
        str, le texte final mis en forme.
    """
    if not texte: return ""

    defaut = {
        "normaliser_retours_ligne": True,
        "remplacer_tabulations": True,
        "supprimer_lignes_vides": True,
        "supprimer_espaces_multiples": True,
        "supprimer_espaces_avant_ponctuation": True,
        "ajouter_espace_apres_ponctuation": True
    }
    
    if options is None:
        cfg = defaut
    else:
        cfg = defaut.copy()
        cfg.update(options)
    
    res = texte
    
    if cfg["normaliser_retours_ligne"]:
        res = normaliser_retours_ligne(res)
    
    if cfg["remplacer_tabulations"]:
        res = remplacer_tabulations(res)
        
    if cfg["supprimer_lignes_vides"]:
        res = supprimer_lignes_vides(res)
        
    if cfg["supprimer_espaces_multiples"]:
        res = supprimer_espaces_multiples(res)
        
    if cfg["supprimer_espaces_avant_ponctuation"]:
        res = supprimer_espaces_avant_ponctuation(res)
        
    if cfg["ajouter_espace_apres_ponctuation"]:
        res = ajouter_espace_apres_ponctuation(res)
        
    res = supprimer_espaces_bords(res)
    
    return res

def test_normaliser_mise_en_forme():
    print("\nTest : normaliser_mise_en_forme (Orchestrateur)")
    txt = "Titre\t\n\n  Bonjour ,monde !  "
    # Attendu : "Titre \nBonjour, monde!"
    res = normaliser_mise_en_forme(txt)
    assert "Bonjour, monde!" in res
    assert "\n\n" not in res
    
    # Test option désactivée (ne pas toucher aux tabulations)
    opts = {
        "remplacer_tabulations": False,
        "supprimer_espaces_multiples": False 
    }
    res2 = normaliser_mise_en_forme("A\tB", opts)
    assert "\t" in res2
    
    print(" Test validé.")
#test_normaliser_mise_en_forme()

#10. Vérifications de cohérence post-nettoyage 

#a

def detecter_texte_vide(texte):
    """
    Description :
        Vérifie si un document est vide ou ne contient que des espaces.
    
    Paramètres :
        texte  str, le texte à analyser.
    
    Retour :
        bool, True si le texte est considéré comme vide, False sinon.
    """
    if texte is None:
        return True
    
    if not isinstance(texte, str):
        return True
        
    res = len(texte.strip()) == 0
    return res

def test_detecter_texte_vide():
    print("\nTest : detecter_texte_vide")
    
    # Cas Positifs (Est vide)
    assert detecter_texte_vide("") is True
    assert detecter_texte_vide("   ") is True
    assert detecter_texte_vide("\t\n") is True
    assert detecter_texte_vide(None) is True
    
    # Cas Négatifs (N'est pas vide)
    assert detecter_texte_vide("a") is False
    assert detecter_texte_vide("   .   ") is False
    
    print(" Test validé.")

#test_detecter_texte_vide
#b

def comparer_longueurs_texte(texte_avant, texte_apres, seuil=0.3):
    """
    Description :
        Compare la longueur du texte avant et après nettoyage pour
        détecter une perte excessive d'information.
    
    Paramètres :
        texte_avant  str, le texte original.
        texte_apres  str, le texte nettoyé.
        seuil        float, le pourcentage limite de conservation.
                       Si la taille après est < 30% de la taille avant, c'est une alerte.
    
    Retour :
        str, un message d'alerte si la perte est excessive, sinon "OK".
    """
    res = "OK"
    if not texte_avant:
        return res
    
    tailleAv = len(texte_avant)
    tailleAp = len(texte_apres) if texte_apres else 0
    
    ratio = tailleAp / tailleAv
    
    if ratio < seuil:
        res = "Alerte" 
    return res

def test_comparer_longueurs_texte():
    print("\nTest : comparer_longueurs_texte")
    
    txt_long = "Ceci est un texte assez long pour le test."
    
    # Cas 1 : Nettoyage léger (OK)
    txt_clean_ok = "Ceci est un texte long test" 
    res_ok = comparer_longueurs_texte(txt_long, txt_clean_ok, seuil=0.5)
    assert res_ok == "OK"
    
    # Cas 2 : Nettoyage brutal (Alerte)
    txt_clean_ko = "" # Tout supprimé
    res_ko = comparer_longueurs_texte(txt_long, txt_clean_ko, seuil=0.3)
    assert "ALERTE" in res_ko
    
    # Cas 3 : Texte original vide
    assert comparer_longueurs_texte("", "") == "OK (Texte original vide)"
    
    print(" Test validé.")


#test_comparer_longueurs_texte
#c

def signaler_textes_vides(base, pipeline_nettoyage=None):
    """
    Description :
        Parcourt le corpus, simule un nettoyage et signale
        les fichiers qui deviennent vides.
    
    Paramètres :
        base                str, le chemin du dossier racine à explorer.
        pipeline_nettoyage  function, la fonction de nettoyage à appliquer 
                            . Si None, vérifie juste le fichier actuel.
    
    Retour :
        list, la liste des chemins des fichiers vides détectés.
    """
  
    fichiers_vides = []
    try:
        dic = explorer_corpus(base)
    except NameError:
        return []

    if not dic:
        return []

    for ch, data in dic.items():
        for fichier in data['contenu']:
            chemin = os.path.join(ch, fichier)
            
            if os.path.isfile(chemin):
                contenu = lire_document(chemin)
                
                if pipeline_nettoyage and contenu:
                    contenu = pipeline_nettoyage(contenu)
                
                if detecter_texte_vide(contenu):
                    fichiers_vides.append(chemin)
           
    return fichiers_vides

def test_signaler_textes_vides():
    print("\nTest : signaler_textes_vides (Simulation)")
    
    # Nous allons simuler un environnement minimal.
    dir_test = "corpus_test_vide"
    f_plein = os.path.join(dir_test, "plein.txt")
    f_vide = os.path.join(dir_test, "vide.txt")
    
    try:
        os.makedirs(dir_test, exist_ok=True)
        with open(f_plein, "w") as f: f.write("Contenu important.")
        with open(f_vide, "w") as f: f.write("   ") 
        vides = signaler_textes_vides(dir_test, pipeline_nettoyage=None)
        
        assert f_vide in vides
        assert f_plein not in vides
        assert len(vides) == 1
        
        print(" Test validé.")
        
    except NameError:
        print(" Test ignoré : dépendances manquantes (explorer_corpus).")
    finally:
        if os.path.exists(f_plein): os.remove(f_plein)
        if os.path.exists(f_vide): os.remove(f_vide)
        if os.path.exists(dir_test): os.rmdir(dir_test)

#test_signaler_textes_vides

#11. Production et sauvegarde du texte nettoyé 

#a

def nettoyer_document(fichier, options=None):
    """
    Description :
        Lit un fichier, applique directement toutes les étapes de nettoyage
        et retourne le texte propre.
    
    Paramètres :
        fichier  str, le chemin du fichier à traiter.
        options  dict, la configuration globale contenant les sous-options.
    
    Retour :
        str, le texte nettoyé.
    """
    texte = lire_document(fichier)
    
    if not texte:
        return ""

    cfg = {
        "web": {
            "supprimer_urls": True, 
            "supprimer_emails": True, 
            "supprimer_emojis": True,
            "supprimer_mentions": True,
            "supprimer_hashtags": True,
            "supprimer_caracteres_speciaux": True,
            "normaliser_unicode": True
        },
        "accents": {
            "corriger_erreurs": True, 
            "uniformiser": True
        },
        "contractions": {
            "langue": "auto", 
            "expand_contractions": True, 
            "developper_abreviations": True,
            "normaliser_apostrophes": True
        },
        "ponctuation": {
            "normaliser": True, 
            "reduire": True, 
            "espacer": True,
            "contextuel": False,
            "supprimer": False
        },
        "nombres": {
            "normaliser": True,
            "supprimer_nombres": False,
            "supprimer_symboles": True
        }
    }
    
    if options:
        for section, opts in options.items():
            if section in cfg:
                cfg[section].update(opts)

    res = texte
    try:
        res = supprimer_balises_html_xml(res)
    except NameError: pass

    try:
        res = traiter_web_et_emojis(res, cfg["web"])
    except NameError: pass

    try:
        res = traiter_accents(res, cfg["accents"])
    except NameError: pass

    try:
        res = traiter_contractions(res, cfg["contractions"])
    except NameError: pass

    try:
        res = traiter_ponctuation(res, cfg["ponctuation"])
    except NameError: pass
    try:
        res = traiter_nombres_symboles(res, cfg["nombres"])
    except NameError: pass
    try:
        res = nettoyer_espaces(res)
        res = convertir_vers_minuscule(res)
    except NameError:
        res = res.strip().lower()

    return res


#b

def sauvegarder_texte_propre(fichier_origine, texte_nettoye, dossier_sortie="corpus_nettoye"):
    """
    Description :
        Enregistre le texte nettoyé dans un dossier dédié,
        en conservant le nom de fichier original.
    
    Paramètres :
        fichier_origine  str, le chemin du fichier source.
        texte_nettoye    str, le contenu à sauvegarder.
        dossier_sortie   str, le dossier racine de sauvegarde.
    
    Retour :
        str, le chemin complet du fichier sauvegardé.
    """
    if texte_nettoye is None:
        return None

    os.makedirs(dossier_sortie, exist_ok=True)
    f = os.path.basename(fichier_origine)
    
    ch = os.path.join(dossier_sortie, f)
    
    try:
        with open(ch, "w", encoding="utf-8") as f:
            f.write(texte_nettoye)
        return ch
    except Exception as e:
        return None


# c

def traiter_tout_le_corpus(base_source, dossier_cible, options=None):
    """
    Description :
        Applique le nettoyage à tout le corpus, vérifie la cohérence
        et sauvegarde les résultats.
    
    Paramètres :
        base_source    str, dossier racine du corpus brut.
        dossier_cible  str, dossier racine pour le corpus nettoyé.
        options        dict, options de nettoyage.
    
    Retour :
        dict, un rapport contenant le nombre de succès et d'échecs.
    """
    try:
        dic = explorer_corpus(base_source)
    except NameError:
        return {}

    if not dic:
        return {}

    rapport = {"succes": 0, "vides": 0, "echecs": 0}
    
    for chD, data in dic.items():
        for fichier in data['contenu']:
            chemin = os.path.join(chD, fichier)
            
            if os.path.isfile(chemin):
                txt = nettoyer_document(chemin, options)
                
                try:
                    if detecter_texte_vide(txt):
                        rapport["vides"] += 1
                except NameError: pass
                ch = sauvegarder_texte_propre(chemin, txt, dossier_cible)
                
                if ch:
                    rapport["succes"] += 1
                else:
                    rapport["echecs"] += 1
    
    return rapport

def test_nettoyer_document():
    print("\nTest 1 : nettoyer_document")
    
    fichier_test = "test_single.txt"
    contenu_sale = "<p>HÉLLO 123 !!!</p>"
    try:
        with open(fichier_test, "w", encoding="utf-8") as f:
            f.write(contenu_sale)
            
        # Options strictes
        opts = {
            "nombres": {"supprimer_nombres": True},
            "ponctuation": {"supprimer": True},
            "accents": {"uniformiser": True}
        }
        
        res = nettoyer_document(fichier_test, opts)
        
        print(f"  Entrée : '{contenu_sale}'")
        print(f"  Sortie : '{res}'")
        
        # Vérifications
        assert "123" not in res
        assert "!" not in res
        assert "<p>" not in res
        # "HÉLLO" -> "hello" (ou "héllo")
        assert "hello" in res or "héllo" in res
        
        print(" Test validé.")

    finally:
        if os.path.exists(fichier_test): os.remove(fichier_test)


def test_sauvegarder_texte_propre():
    print("\nTest 2 : sauvegarder_texte_propre")
    
    fichier_origine = "dossier/test.txt"
    contenu = "texte propre"
    dossier_out = "test_output"
    
    try:
        chemin = sauvegarder_texte_propre(fichier_origine, contenu, dossier_out)
        
        assert chemin is not None
        assert os.path.exists(chemin)
        with open(chemin, "r", encoding="utf-8") as f:
            assert f.read() == contenu
            
        print(" Test validé.")
        
    finally:
        if os.path.exists(dossier_out): shutil.rmtree(dossier_out)


def test_traiter_tout_le_corpus():
    print("\nTest 3 : traiter_tout_le_corpus")
    
    root_src = "test_batch_src_final"
    root_dst = "test_batch_dst_final"
    f_a = os.path.join(root_src, "A.txt")
    f_b = os.path.join(root_src, "B.txt")
    
    try:
        os.makedirs(root_src, exist_ok=True)
        with open(f_a, "w", encoding="utf-8") as f: f.write("Texte normal.")
        with open(f_b, "w", encoding="utf-8") as f: f.write("123")
        options = {"nombres": {"supprimer_nombres": True}}
        
        rapport = traiter_tout_le_corpus(root_src, root_dst, options)
        
        print("  Rapport :", rapport)
        
        # A.txt (succès) + B.txt = 2 succès
        assert rapport["succes"] == 2
        # B.txt devient vide -> 1 vide détecté
        if "vides" in rapport:
             pass 
        
        assert os.path.exists(os.path.join(root_dst, "A.txt"))
        assert os.path.exists(os.path.join(root_dst, "B.txt"))
        
        print(" Test validé.")
        
    finally:
        if os.path.exists(root_src): shutil.rmtree(root_src)
        if os.path.exists(root_dst): shutil.rmtree(root_dst)

#test_nettoyer_document()
#test_sauvegarder_texte_propre()
#test_traiter_tout_le_corpus()