import numpy as np

# III. Onglet principal : Recherche documentaire
# 1. Saisie et configuration de la requête
# a) Paramétrage de la requête

def initialiser_fiche_requete(id_requete, texte, type_unite="phrase", langue=None, config_id=None):
    """
    Description :
        Crée une fiche de requête vide ou pré-remplie avec les informations de base.
        Cette structure (dictionnaire) servira de conteneur pour assurer la traçabilité
        des traitements (prétraitement, vectorisation) appliqués à la requête.
        
        Vérifie la validité des types d'entrée pour éviter les erreurs en cascade plus tard.

    Paramètres :
        id_requete  str ou int, identifiant unique de la requête. Ne peut pas être None.
        texte       str, le contenu textuel brut de la requête.
        type_unite  str, le type d'unité linguistique ('phrase' ou 'document'). 
                    Par défaut "phrase".
        langue      str, la langue de la requête (ex: 'fr', 'en'). Par défaut None.
        config_id   str, l'identifiant de la configuration de prétraitement choisie 
                    (ex: 'config_base', 'config_stemming'). Par défaut None.

    Retour :
        dict, la fiche de requête initialisée contenant les métadonnées et 
              un statut 'non_calcule'.
              
    Lève :
        ValueError si id_requete est None.
        TypeError si le texte n'est pas une chaîne de caractères.
    """
    
    # Vérification défensive des entrées (pour gérer les cas d'erreurs)
    if id_requete is None:
        raise ValueError("L'identifiant de la requête (id_requete) ne peut pas être None.")
        
    if not isinstance(texte, str):
        raise TypeError(f"Le texte de la requête doit être de type str. Reçu : {type(texte)}")

    fiche = {
        "id": id_requete,
        "texte": texte,
        "type_unite": type_unite,
        "langue": langue,
        "config_id": config_id,
        "statut": "non_calcule",  # Indique que le prétraitement/vectorisation n'est pas fait
        "options_oov": "ignorer", # Gestion des mots hors vocabulaire (par défaut)
        
        # Réservoirs pour les étapes futures :
        "tokens": [],             # Liste des mots après prétraitement
        "vecteur": None,          # Vecteur numérique (TF-IDF ou Embedding)
        "resultats": []           # Liste des documents trouvés
    }
    
    return fiche

# Tests unitaires Exercice III.1.a

def test_initialiser_fiche_requete():
    print("\n Test : initialiser_fiche_requete ")
    
    # --- 1. Cas Standard (Nominal) ---
    print("  [1] Test Cas Standard...")
    id_test = "REQ_001"
    texte_test = "L'intelligence artificielle en médecine."
    config_test = "standard"
    
    ma_requete = initialiser_fiche_requete(id_test, texte_test, config_id=config_test)
    
    # Vérifications des valeurs
    assert ma_requete["id"] == id_test
    assert ma_requete["texte"] == texte_test
    assert ma_requete["config_id"] == config_test
    assert ma_requete["statut"] == "non_calcule"
    assert ma_requete["vecteur"] is None
    print("      -> Succès (Données correctement stockées).")

    # --- 2. Cas Limites ---
    print("  [2] Test Cas Limites (Valeurs vides ou par défaut)...")
    
    # Texte vide
    req_vide = initialiser_fiche_requete("REQ_VIDE", "")
    assert req_vide["texte"] == ""
    assert req_vide["tokens"] == []
    
    # Vérification des valeurs par défaut (langue None, type_unite phrase)
    assert req_vide["langue"] is None
    assert req_vide["type_unite"] == "phrase"
    print("      -> Succès (Gestion du texte vide et des valeurs par défaut).")

    # --- 3. Cas d'erreurs (Entrées invalides) ---
    print("  [3] Test Cas d'erreurs (Types invalides)...")
    
    # A. Test ID None
    try:
        initialiser_fiche_requete(None, "Texte valide")
        print("      -> ÉCHEC : Aurait dû lever une ValueError pour ID None.")
        assert False # Force l'échec si pas d'exception
    except ValueError as e:
        print(f"      -> Succès : Erreur correctement détectée ({e})")
        
    # B. Test Texte invalide (ex: un nombre au lieu d'un str)
    try:
        initialiser_fiche_requete("REQ_BAD", 12345) # On passe un int au lieu d'un str
        print("      -> ÉCHEC : Aurait dû lever une TypeError pour le texte.")
        assert False
    except TypeError as e:
        print(f"      -> Succès : Erreur de type correctement détectée ({e})")

    print("\n Test validé : La fonction est robuste.")

# Lancement du test si le script est exécuté directement
if __name__ == "__main__":
    test_initialiser_fiche_requete()

import numpy as np

# III. Onglet principal : Recherche documentaire
# 1. Saisie et configuration de la requête
# b) Détermination du type d'unité

def choisir_type_requete(fiche_requete, seuil_mots=50):
    """
    Description :
        Analyse le texte contenu dans la fiche de requête pour déterminer 
        automatiquement si elle doit être traitée comme une 'phrase' ou un 'document'.
        Met à jour le champ 'type_unite' de la fiche.

        Règles heuristiques :
        - Si le texte contient des sauts de ligne (\n), c'est un 'document'.
        - Si le nombre de mots dépasse le seuil (défaut 50), c'est un 'document'.
        - Sinon, c'est une 'phrase'.

    Paramètres :
        fiche_requete  dict, la structure créée par initialiser_fiche_requete.
        seuil_mots     int, le nombre de mots au-delà duquel une requête est 
                       considérée comme un document (défaut 50).

    Retour :
        dict, la fiche de requête mise à jour.
        
    Lève :
        ValueError si la fiche est None ou mal formée (pas de clé 'texte').
    """
    
    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    if not isinstance(fiche_requete, dict) or "texte" not in fiche_requete:
        raise ValueError("La fiche fournie est invalide (doit être un dict avec une clé 'texte').")

    texte = fiche_requete["texte"]
    
    # Cas particulier : texte vide -> on laisse par défaut (phrase) ou on gère
    if not texte:
        fiche_requete["type_unite"] = "phrase"
        return fiche_requete

    # 2. Analyse du contenu
    # Découpage sommaire sur les espaces pour compter les mots
    nb_mots = len(texte.split())
    contient_sauts_ligne = "\n" in texte

    # 3. Prise de décision
    if contient_sauts_ligne or nb_mots > seuil_mots:
        nouveau_type = "document"
    else:
        nouveau_type = "phrase"

    # 4. Mise à jour de la fiche
    fiche_requete["type_unite"] = nouveau_type
    
    return fiche_requete


# Tests unitaires Exercice III.1.b

def test_choisir_type_requete():
    print("\n Test : choisir_type_requete ")

    # --- 1. Cas Standard : Phrase courte ---
    print("  [1] Test Cas Standard (Phrase courte)...")
    req_phrase = {"id": "R1", "texte": "Ceci est une petite requête."}
    req_phrase = choisir_type_requete(req_phrase)
    
    assert req_phrase["type_unite"] == "phrase"
    print("      -> Succès (Détecté comme 'phrase').")

    # --- 2. Cas Standard : Document (Sauts de ligne) ---
    print("  [2] Test Cas Standard (Multi-lignes)...")
    req_doc_lines = {"id": "R2", "texte": "Titre\nParagraphe 1\nParagraphe 2"}
    req_doc_lines = choisir_type_requete(req_doc_lines)
    
    assert req_doc_lines["type_unite"] == "document"
    print("      -> Succès (Détecté comme 'document' grâce aux \\n).")

    # --- 3. Cas Limite : Seuil de mots ---
    print("  [3] Test Cas Limite (Seuil de mots)...")
    # Génération d'un texte de 51 mots
    texte_long = "mot " * 51
    req_longue = {"id": "R3", "texte": texte_long.strip()}
    
    # On teste avec un seuil à 50
    req_longue = choisir_type_requete(req_longue, seuil_mots=50)
    assert req_longue["type_unite"] == "document"
    
    # On teste le même texte avec un seuil très haut (100) -> devrait redevenir phrase
    req_longue = choisir_type_requete(req_longue, seuil_mots=100)
    assert req_longue["type_unite"] == "phrase"
    
    print("      -> Succès (Gestion correcte du seuil de longueur).")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Fiche None
    try:
        choisir_type_requete(None)
        print("      -> ÉCHEC : Aurait dû lever ValueError pour None.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Erreur détectée ({e})")

    # B. Fiche mal formée (pas de clé 'texte')
    try:
        bad_fiche = {"id": "R_BAD", "pas_de_texte": "..."}
        choisir_type_requete(bad_fiche)
        print("      -> ÉCHEC : Aurait dû lever ValueError pour clé manquante.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Erreur de structure détectée ({e})")

    print("\n Test validé : La détection de type fonctionne.")

# Lancement du test si le script est exécuté directement
if __name__ == "__main__":
    test_choisir_type_requete()

import numpy as np

# III. Onglet principal : Recherche documentaire
# 1. Saisie et configuration de la requête
# b) Détermination du type d'unité

def choisir_type_requete(fiche_requete, seuil_mots=50):
    """
    Description :
        Analyse le texte contenu dans la fiche de requête pour déterminer 
        automatiquement si elle doit être traitée comme une 'phrase' ou un 'document'.
        Met à jour le champ 'type_unite' de la fiche.

        Règles heuristiques :
        - Si le texte contient des sauts de ligne (\n), c'est un 'document'.
        - Si le nombre de mots dépasse le seuil (défaut 50), c'est un 'document'.
        - Sinon, c'est une 'phrase'.

    Paramètres :
        fiche_requete  dict, la structure créée par initialiser_fiche_requete.
        seuil_mots     int, le nombre de mots au-delà duquel une requête est 
                       considérée comme un document (défaut 50).

    Retour :
        dict, la fiche de requête mise à jour.
        
    Lève :
        ValueError si la fiche est None ou mal formée (pas de clé 'texte').
    """
    
    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    if not isinstance(fiche_requete, dict) or "texte" not in fiche_requete:
        raise ValueError("La fiche fournie est invalide (doit être un dict avec une clé 'texte').")

    texte = fiche_requete["texte"]
    
    # Cas particulier : texte vide -> on laisse par défaut (phrase) ou on gère
    if not texte:
        fiche_requete["type_unite"] = "phrase"
        return fiche_requete

    # 2. Analyse du contenu
    # Découpage sommaire sur les espaces pour compter les mots
    nb_mots = len(texte.split())
    contient_sauts_ligne = "\n" in texte

    # 3. Prise de décision
    if contient_sauts_ligne or nb_mots > seuil_mots:
        nouveau_type = "document"
    else:
        nouveau_type = "phrase"

    # 4. Mise à jour de la fiche
    fiche_requete["type_unite"] = nouveau_type
    
    return fiche_requete


# Tests unitaires Exercice III.1.b

def test_choisir_type_requete():
    print("\n Test : choisir_type_requete ")

    # --- 1. Cas Standard : Phrase courte ---
    print("  [1] Test Cas Standard (Phrase courte)...")
    req_phrase = {"id": "R1", "texte": "Ceci est une petite requête."}
    req_phrase = choisir_type_requete(req_phrase)
    
    assert req_phrase["type_unite"] == "phrase"
    print("      -> Succès (Détecté comme 'phrase').")

    # --- 2. Cas Standard : Document (Sauts de ligne) ---
    print("  [2] Test Cas Standard (Multi-lignes)...")
    req_doc_lines = {"id": "R2", "texte": "Titre\nParagraphe 1\nParagraphe 2"}
    req_doc_lines = choisir_type_requete(req_doc_lines)
    
    assert req_doc_lines["type_unite"] == "document"
    print("      -> Succès (Détecté comme 'document' grâce aux \\n).")

    # --- 3. Cas Limite : Seuil de mots ---
    print("  [3] Test Cas Limite (Seuil de mots)...")
    # Génération d'un texte de 51 mots
    texte_long = "mot " * 51
    req_longue = {"id": "R3", "texte": texte_long.strip()}
    
    # On teste avec un seuil à 50
    req_longue = choisir_type_requete(req_longue, seuil_mots=50)
    assert req_longue["type_unite"] == "document"
    
    # On teste le même texte avec un seuil très haut (100) -> devrait redevenir phrase
    req_longue = choisir_type_requete(req_longue, seuil_mots=100)
    assert req_longue["type_unite"] == "phrase"
    
    print("      -> Succès (Gestion correcte du seuil de longueur).")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Fiche None
    try:
        choisir_type_requete(None)
        print("      -> ÉCHEC : Aurait dû lever ValueError pour None.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Erreur détectée ({e})")

    # B. Fiche mal formée (pas de clé 'texte')
    try:
        bad_fiche = {"id": "R_BAD", "pas_de_texte": "..."}
        choisir_type_requete(bad_fiche)
        print("      -> ÉCHEC : Aurait dû lever ValueError pour clé manquante.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Erreur de structure détectée ({e})")

    print("\n Test validé : La détection de type fonctionne.")

# Lancement du test si le script est exécuté directement
if __name__ == "__main__":
    test_choisir_type_requete()

import os



def choisir_source_requete(fiche_requete, source, chemin_fichier=None):
    """
    Description :
        Définit la provenance de la requête (Saisie, Corpus, ou Fichier).
        Si la source est 'fichier', la fonction tente immédiatement de lire le contenu
        du fichier pour mettre à jour le champ 'texte' de la fiche.

    Paramètres :
        fiche_requete   dict, la structure créée par initialiser_fiche_requete.
        source          str, l'origine choisie : 'saisie', 'corpus', ou 'fichier'.
        chemin_fichier  str, le chemin complet du fichier (obligatoire si source='fichier').
                        Par défaut None.

    Retour :
        dict, la fiche de requête mise à jour avec la nouvelle source (et le nouveau texte si fichier).
    
    Lève :
        ValueError si la fiche est None.
        ValueError si la source n'est pas valide.
        FileNotFoundError si le fichier spécifié n'existe pas.
        IOError si le fichier ne peut pas être lu.
    """
    
    # 1. Vérifications défensives de base
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    SOURCES_VALIDES = ["saisie", "corpus", "fichier"]
    if source not in SOURCES_VALIDES:
        raise ValueError(f"Source invalide '{source}'. Choisir parmi : {SOURCES_VALIDES}")

    # 2. Traitement selon la source
    if source == "fichier":
        # Vérification du chemin
        if chemin_fichier is None:
            raise ValueError("Le paramètre chemin_fichier est obligatoire pour la source 'fichier'.")
        
        if not os.path.exists(chemin_fichier):
            raise FileNotFoundError(f"Le fichier n'existe pas : {chemin_fichier}")
            
        # Lecture et mise à jour du texte
        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            # Mise à jour de la fiche
            fiche_requete["texte"] = contenu
            fiche_requete["chemin_fichier"] = chemin_fichier
            
        except Exception as e:
            raise IOError(f"Erreur lors de la lecture du fichier : {e}")

    elif source == "corpus":
        # Pour le corpus, on note juste la source. 
        # Le texte sera probablement injecté par une autre fonction (ex: sélection dans une liste)
        # ou bien il est déjà présent si on a cliqué sur "Utiliser comme requête".
        pass

    elif source == "saisie":
        # Si on revient en mode saisie, on garde le texte actuel ou on le vide selon la logique voulue.
        # Ici, on conserve le texte existant pour ne pas perdre ce que l'utilisateur a tapé.
        pass

    # 3. Enregistrement de la métadonnée
    fiche_requete["source"] = source
    
    # Si on change de source, le statut de calcul doit être réinitialisé
    fiche_requete["statut"] = "non_calcule"
    
    return fiche_requete


# Tests unitaires Exercice III.1.a (Suite)

def test_choisir_source_requete():
    print("\n Test : choisir_source_requete ")
    
    # Préparation d'une fiche vierge
    fiche_base = {"id": "TEST", "texte": "Ancien texte", "statut": "calcule"}

    # --- 1. Cas Standard : Source 'saisie' ---
    print("  [1] Test Cas Standard (Saisie)...")
    res_saisie = choisir_source_requete(fiche_base.copy(), "saisie")
    assert res_saisie["source"] == "saisie"
    assert res_saisie["texte"] == "Ancien texte" # Le texte ne change pas
    print("      -> Succès.")

    # --- 2. Cas Standard : Source 'fichier' ---
    print("  [2] Test Cas Standard (Fichier)...")
    
    # Création d'un fichier temporaire
    nom_fichier_tmp = "test_req_tmp.txt"
    contenu_fichier = "Ceci est le contenu du fichier externe."
    with open(nom_fichier_tmp, "w", encoding="utf-8") as f:
        f.write(contenu_fichier)
    
    try:
        res_fichier = choisir_source_requete(fiche_base.copy(), "fichier", chemin_fichier=nom_fichier_tmp)
        
        assert res_fichier["source"] == "fichier"
        assert res_fichier["texte"] == contenu_fichier # Le texte DOIT avoir été remplacé
        assert res_fichier["chemin_fichier"] == nom_fichier_tmp
        assert res_fichier["statut"] == "non_calcule" # Reset du statut
        print("      -> Succès (Texte chargé depuis le fichier).")
        
    finally:
        # Nettoyage
        if os.path.exists(nom_fichier_tmp):
            os.remove(nom_fichier_tmp)

    # --- 3. Cas d'erreurs ---
    print("  [3] Test Cas d'erreurs...")
    
    # A. Source inconnue
    try:
        choisir_source_requete(fiche_base, "source_imaginaire")
        print("      -> ÉCHEC : Aurait dû lever ValueError (source invalide).")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Source invalide détectée ({e})")
        
    # B. Fichier manquant (paramètre None)
    try:
        choisir_source_requete(fiche_base, "fichier", chemin_fichier=None)
        print("      -> ÉCHEC : Aurait dû lever ValueError (chemin manquant).")
        assert False
    except ValueError:
        print("      -> Succès : Absence de chemin détectée.")

    # C. Fichier inexistant (chemin faux)
    try:
        choisir_source_requete(fiche_base, "fichier", chemin_fichier="fichier_fantome_999.txt")
        print("      -> ÉCHEC : Aurait dû lever FileNotFoundError.")
        assert False
    except FileNotFoundError:
        print("      -> Succès : Fichier inexistant détecté.")

    print("\n Test validé : La gestion des sources est correcte.")

test_choisir_source_requete()

def definir_langue_requete(fiche_requete, langue):
    """
    Description :
        Assigne ou modifie la langue de la requête (ex: 'fr', 'en', 'multi').
        Si la langue est modifiée, le statut de la fiche est réinitialisé à 'non_calcule'
        car cela invalide les traitements linguistiques précédents (stopwords, stemming).

    Paramètres :
        fiche_requete  dict, la structure de requête.
        langue         str, le code langue (ex: 'fr', 'en'). Ne peut être vide.

    Retour :
        dict, la fiche de requête mise à jour.

    Lève :
        ValueError si la fiche est None ou la langue vide.
        TypeError si la langue n'est pas une chaîne de caractères.
    """
    
    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    if not isinstance(langue, str):
        raise TypeError(f"La langue doit être une chaîne de caractères (str). Reçu : {type(langue)}")
        
    if not langue.strip():
        raise ValueError("La langue ne peut pas être une chaîne vide.")

    # 2. Vérification du changement d'état
    ancienne_langue = fiche_requete.get("langue")
    
    # On met à jour seulement si c'est nécessaire
    if ancienne_langue != langue:
        fiche_requete["langue"] = langue
        
        # IMPORTANT : Changer la langue invalide les vecteurs potentiels
        # car le prétraitement (stopwords, stemming) dépend de la langue.
        fiche_requete["statut"] = "non_calcule"
        
        # On peut aussi vouloir vider les tokens s'ils ont été calculés avec la mauvaise langue
        fiche_requete["tokens"] = [] 
        fiche_requete["vecteur"] = None

    return fiche_requete


# Tests unitaires Exercice III.1.a (Suite)

def test_definir_langue_requete():
    print("\n Test : definir_langue_requete ")
    
    # Préparation d'une fiche fictive déjà "calculée" en anglais
    fiche_test = {
        "id": "REQ_TEST", 
        "texte": "Hello world", 
        "langue": "en", 
        "statut": "calcule",
        "tokens": ["hello", "world"],
        "vecteur": [0.1, 0.2]
    }

    # --- 1. Cas Standard : Changement de langue ---
    print("  [1] Test Cas Standard (Changement de langue)...")
    # On passe de 'en' à 'fr'
    res_change = definir_langue_requete(fiche_test.copy(), "fr")
    
    assert res_change["langue"] == "fr"
    assert res_change["statut"] == "non_calcule" # Doit être reset
    assert res_change["tokens"] == []            # Doit être vidé
    assert res_change["vecteur"] is None
    print("      -> Succès (Mise à jour et Reset effectués).")

    # --- 2. Cas Standard : Même langue (Pas de changement) ---
    print("  [2] Test Cas Optimisation (Même langue)...")
    # On réassigne 'en' à une fiche déjà 'en'
    res_meme = definir_langue_requete(fiche_test.copy(), "en")
    
    assert res_meme["langue"] == "en"
    assert res_meme["statut"] == "calcule" # Ne doit PAS être reset car rien n'a changé
    assert res_meme["tokens"] == ["hello", "world"]
    print("      -> Succès (État préservé).")

    # --- 3. Cas d'erreurs ---
    print("  [3] Test Cas d'erreurs...")
    
    # A. Langue vide
    try:
        definir_langue_requete(fiche_test, "   ")
        print("      -> ÉCHEC : Aurait dû lever ValueError pour langue vide.")
        assert False
    except ValueError:
        print("      -> Succès : Langue vide détectée.")

    # B. Mauvais type
    try:
        definir_langue_requete(fiche_test, 123)
        print("      -> ÉCHEC : Aurait dû lever TypeError.")
        assert False
    except TypeError:
        print("      -> Succès : Mauvais type détecté.")

    print("\n Test validé : La gestion de la langue est correcte.")

test_definir_langue_requete()

def choisir_configuration_pretraitement(fiche_requete, config_id):
    """
    Description :
        Associe une configuration de prétraitement (ex: 'standard', 'stemming') 
        à la requête.
        Vérifie que l'identifiant de configuration est valide.
        Si la configuration change, réinitialise les calculs dépendants (tokens, vecteurs).

    Paramètres :
        fiche_requete  dict, la structure de requête.
        config_id      str, l'identifiant de la configuration cible.
                       Doit correspondre aux clés utilisées dans la Séance 3.

    Retour :
        dict, la fiche de requête mise à jour.

    Lève :
        ValueError si la fiche est None ou si config_id est invalide/vide.
    """
    
    # Liste des configurations acceptées (Simulé selon les séances précédentes)
    # Dans une application finale, cette liste viendrait d'une constante globale ou d'un fichier config.
    CONFIGS_VALIDES = ["brut", "standard", "stemming", "frequence", "avance"]

    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    if not isinstance(config_id, str) or not config_id.strip():
        raise ValueError("L'identifiant de configuration (config_id) doit être une chaîne non vide.")
        
    if config_id not in CONFIGS_VALIDES:
        raise ValueError(f"Configuration inconnue : '{config_id}'. "
                         f"Valeurs possibles : {CONFIGS_VALIDES}")

    # 2. Gestion du changement d'état
    ancienne_config = fiche_requete.get("config_id")
    
    # Si la configuration change, tout ce qui en découle est obsolète
    if ancienne_config != config_id:
        fiche_requete["config_id"] = config_id
        
        # Reset total des calculs
        fiche_requete["statut"] = "non_calcule"
        fiche_requete["tokens"] = []
        fiche_requete["vecteur"] = None
        fiche_requete["resultats"] = []

    return fiche_requete


# Tests unitaires Exercice III.1.a (Fin)

def test_choisir_configuration_pretraitement():
    print("\n Test : choisir_configuration_pretraitement ")
    
    # Préparation d'une fiche fictive déjà calculée avec la config 'standard'
    fiche_test = {
        "id": "REQ_TEST",
        "texte": "Les chats mangent.",
        "config_id": "standard",
        "statut": "calcule",
        "tokens": ["les", "chats", "mangent"],
        "vecteur": [0.5, 0.5, 0.5]
    }

    # --- 1. Cas Standard : Changement de config ---
    print("  [1] Test Cas Standard (Changement vers 'stemming')...")
    res_change = choisir_configuration_pretraitement(fiche_test.copy(), "stemming")
    
    assert res_change["config_id"] == "stemming"
    assert res_change["statut"] == "non_calcule" # Reset forcé
    assert res_change["tokens"] == []
    assert res_change["vecteur"] is None
    print("      -> Succès (Mise à jour et Reset effectués).")

    # --- 2. Cas Optimisation : Même config ---
    print("  [2] Test Cas Optimisation (Même config 'standard')...")
    res_meme = choisir_configuration_pretraitement(fiche_test.copy(), "standard")
    
    assert res_meme["config_id"] == "standard"
    assert res_meme["statut"] == "calcule" # Pas de reset
    assert len(res_meme["tokens"]) > 0
    print("      -> Succès (État préservé).")

    # --- 3. Cas d'erreurs ---
    print("  [3] Test Cas d'erreurs...")
    
    # A. Config inconnue
    try:
        choisir_configuration_pretraitement(fiche_test, "config_magique_inexistante")
        print("      -> ÉCHEC : Aurait dû lever ValueError (config inconnue).")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Config inconnue détectée ({e})")

    # B. Config vide
    try:
        choisir_configuration_pretraitement(fiche_test, "")
        print("      -> ÉCHEC : Aurait dû lever ValueError (config vide).")
        assert False
    except ValueError:
        print("      -> Succès : Config vide détectée.")

    print("\n Test validé : La sélection de configuration est robuste.")

test_choisir_configuration_pretraitement()

def choisir_strategie_oov_requete(fiche_requete, strategie_oov):
    """
    Description :
        Définit la stratégie à adopter lorsque des mots de la requête ne sont pas 
        trouvés dans le vocabulaire du corpus (OOV - Out Of Vocabulary).
        
        Stratégies possibles :
        - 'ignorer' : Les mots inconnus sont simplement supprimés du vecteur.
        - 'substitution' : Tentative de remplacement (synonymes, sous-mots FastText).
        - 'signaler' : L'utilisateur sera averti explicitement des mots manquants.

        Si la stratégie change, le statut de calcul est réinitialisé car cela affecte
        la construction du vecteur final.

    Paramètres :
        fiche_requete  dict, la structure de requête.
        strategie_oov  str, le nom de la stratégie ('ignorer', 'substitution', 'signaler').

    Retour :
        dict, la fiche de requête mise à jour.

    Lève :
        ValueError si la fiche est None ou la stratégie inconnue.
    """
    
    # Liste des stratégies autorisées
    STRATEGIES_VALIDES = ["ignorer", "substitution", "signaler"]

    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    if not isinstance(strategie_oov, str):
        raise TypeError(f"La stratégie doit être une chaîne de caractères. Reçu : {type(strategie_oov)}")
        
    if strategie_oov not in STRATEGIES_VALIDES:
        raise ValueError(f"Stratégie OOV inconnue : '{strategie_oov}'. "
                         f"Valeurs possibles : {STRATEGIES_VALIDES}")

    # 2. Mise à jour de la fiche
    ancienne_strat = fiche_requete.get("options_oov")
    
    if ancienne_strat != strategie_oov:
        fiche_requete["options_oov"] = strategie_oov
        
        # Le traitement des OOV se fait au moment de la vectorisation,
        # donc on doit refaire le calcul si on change de méthode.
        fiche_requete["statut"] = "non_calcule"
        # Note : On ne vide pas forcément les tokens ici, car la tokenisation (découpage) 
        # reste valide, c'est l'étape d'après (mapping vocabulaire) qui change.
        fiche_requete["vecteur"] = None

    return fiche_requete


# Tests unitaires Exercice III.1.a (Fin suite)

def test_choisir_strategie_oov_requete():
    print("\n Test : choisir_strategie_oov_requete ")
    
    # Préparation d'une fiche
    fiche_test = {
        "id": "REQ_OOV",
        "texte": "MotInconnu test",
        "options_oov": "ignorer",
        "statut": "calcule",
        "vecteur": [0.0, 1.0]
    }

    # --- 1. Cas Standard : Changer pour 'signaler' ---
    print("  [1] Test Cas Standard (Changement vers 'signaler')...")
    res_signaler = choisir_strategie_oov_requete(fiche_test.copy(), "signaler")
    
    assert res_signaler["options_oov"] == "signaler"
    assert res_signaler["statut"] == "non_calcule" # Reset du calcul
    print("      -> Succès (Mise à jour effectuée).")

    # --- 2. Cas Standard : Changer pour 'substitution' ---
    print("  [2] Test Cas Standard (Changement vers 'substitution')...")
    res_subst = choisir_strategie_oov_requete(fiche_test.copy(), "substitution")
    
    assert res_subst["options_oov"] == "substitution"
    assert res_subst["statut"] == "non_calcule"
    print("      -> Succès.")

    # --- 3. Cas Optimisation : Même stratégie ---
    print("  [3] Test Cas Optimisation (Pas de changement)...")
    res_meme = choisir_strategie_oov_requete(fiche_test.copy(), "ignorer")
    
    assert res_meme["options_oov"] == "ignorer"
    assert res_meme["statut"] == "calcule" # Pas de reset
    print("      -> Succès (État préservé).")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Stratégie invalide
    try:
        choisir_strategie_oov_requete(fiche_test, "supprimer_tout")
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Stratégie invalide détectée ({e})")

    # B. Fiche None
    try:
        choisir_strategie_oov_requete(None, "ignorer")
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError:
        print("      -> Succès : Fiche None détectée.")

    print("\n Test validé : La gestion des stratégies OOV est correcte.")

test_choisir_strategie_oov_requete()

def definir_granularite_corpus(granularite="document"):
    """
    Description :
        Définit et valide le niveau de granularité de la recherche.
        Ce paramètre détermine si le moteur doit comparer la requête à des 
        documents entiers ou à des phrases isolées.

    Paramètres :
        granularite  str, le niveau souhaité ('document' ou 'phrase').
                     Par défaut "document".
                     Accepte les majuscules/minuscules (ex: "Document" -> "document").

    Retour :
        str, la granularité normalisée (en minuscule) et validée.

    Lève :
        ValueError si la granularité n'est pas 'document' ou 'phrase'.
        TypeError si l'entrée n'est pas une chaîne de caractères.
    """
    
    # Liste des granularités acceptées par le moteur
    GRANULARITES_VALIDES = ["document", "phrase"]

    # 1. Vérification du type
    if not isinstance(granularite, str):
        raise TypeError(f"La granularité doit être une chaîne de caractères. Reçu : {type(granularite)}")
    
    # 2. Normalisation (pour être tolérant aux majuscules)
    granularite_norm = granularite.strip().lower()

    # 3. Validation de la valeur
    if granularite_norm not in GRANULARITES_VALIDES:
        raise ValueError(f"Granularité invalide : '{granularite}'. "
                         f"Valeurs possibles : {GRANULARITES_VALIDES}")

    return granularite_norm


# Tests unitaires Exercice III.2.a

def test_definir_granularite_corpus():
    print("\n Test : definir_granularite_corpus ")
    
    # --- 1. Cas Standard : Valeur par défaut ---
    print("  [1] Test Cas Standard (Défaut)...")
    res_defaut = definir_granularite_corpus() # Utilise "document"
    assert res_defaut == "document"
    print("      -> Succès.")

    # --- 2. Cas Standard : Sélection explicite 'phrase' ---
    print("  [2] Test Cas Standard ('phrase')...")
    res_phrase = definir_granularite_corpus("phrase")
    assert res_phrase == "phrase"
    print("      -> Succès.")

    # --- 3. Cas Limite : Tolérance majuscules/espaces ---
    print("  [3] Test Cas Limite (Majuscules)...")
    res_maj = definir_granularite_corpus("  Document ")
    assert res_maj == "document"
    print("      -> Succès (Normalisation effectuée).")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Valeur inconnue
    try:
        definir_granularite_corpus("paragraphe")
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Valeur invalide détectée ({e})")

    # B. Mauvais type
    try:
        definir_granularite_corpus(123)
        print("      -> ÉCHEC : Aurait dû lever TypeError.")
        assert False
    except TypeError:
        print("      -> Succès : Mauvais type détecté.")

    print("\n Test validé : La définition de granularité est correcte.")

test_definir_granularite_corpus()

def definir_portee_corpus(sous_corpus=None, langues=None):
    """
    Description :
        Configure la portée de la recherche en définissant des filtres sur
        une partie spécifique du corpus ou sur certaines langues.
        
    Paramètres :
        sous_corpus  list ou str, identifiant(s) des documents ou catégorie cible.
                     - None : Tout le corpus (défaut).
                     - list : Une liste d'IDs de documents.
                     - str : Un nom de sous-dossier ou de catégorie.
                     
        langues      list ou str, code(s) langue autorisés (ex: 'fr', ['en', 'fr']).
                     - None : Toutes les langues (défaut).
                     - str : Une seule langue (sera convertie en liste).
                     
    Retour :
        dict, un dictionnaire contenant la configuration de portée et un indicateur
        'est_restreint' (bool) signalant si un filtre est actif.

    Lève :
        TypeError si les types des paramètres sont incorrects (ex: int au lieu de str).
    """
    
    # 1. Validation et Normalisation des Langues
    langues_norm = None
    
    if langues is not None:
        # Si l'utilisateur passe une chaîne "fr", on la transforme en liste ["fr"]
        if isinstance(langues, str):
            langues_norm = [langues]
        elif isinstance(langues, list):
            # Vérifie que tous les éléments sont des chaînes
            if not all(isinstance(l, str) for l in langues):
                raise TypeError("La liste des langues doit contenir uniquement des chaînes de caractères.")
            langues_norm = langues
        else:
            raise TypeError(f"Le paramètre 'langues' doit être str ou list. Reçu : {type(langues)}")

    # 2. Validation du Sous-corpus
    # On accepte str (ex: "Sport") ou list (ex: ["doc1", "doc2"])
    if sous_corpus is not None:
        if not isinstance(sous_corpus, (str, list)):
            raise TypeError(f"Le paramètre 'sous_corpus' doit être str ou list. Reçu : {type(sous_corpus)}")

    # 3. Construction du résultat
    # On détermine si la recherche est restreinte (si au moins un filtre n'est pas None)
    est_restreint = (sous_corpus is not None) or (langues_norm is not None)

    config_portee = {
        "sous_corpus": sous_corpus,
        "langues": langues_norm,     # Toujours une liste ou None
        "est_restreint": est_restreint
    }

    return config_portee


# Tests unitaires Exercice III.2.a (Suite)

def test_definir_portee_corpus():
    print("\n Test : definir_portee_corpus ")
    
    # --- 1. Cas Standard : Recherche Globale (Défaut) ---
    print("  [1] Test Cas Standard (Tout le corpus)...")
    res_global = definir_portee_corpus()
    
    assert res_global["sous_corpus"] is None
    assert res_global["langues"] is None
    assert res_global["est_restreint"] is False
    print("      -> Succès (Pas de restriction).")

    # --- 2. Cas Standard : Restriction Langue (String) ---
    print("  [2] Test Cas Standard (Filtre langue unique)...")
    res_lang = definir_portee_corpus(langues="en")
    
    assert res_lang["langues"] == ["en"] # Doit être normalisé en liste
    assert res_lang["est_restreint"] is True
    print("      -> Succès (Langue normalisée).")

    # --- 3. Cas Standard : Restriction Sous-Corpus (Liste) ---
    print("  [3] Test Cas Standard (Sous-corpus liste)...")
    liste_docs = ["D1.txt", "D2.txt"]
    res_sub = definir_portee_corpus(sous_corpus=liste_docs)
    
    assert res_sub["sous_corpus"] == liste_docs
    assert res_sub["est_restreint"] is True
    print("      -> Succès.")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Langue invalide (ex: un nombre)
    try:
        definir_portee_corpus(langues=123)
        print("      -> ÉCHEC : Aurait dû lever TypeError.")
        assert False
    except TypeError as e:
        print(f"      -> Succès : Type langue invalide détecté ({e})")

    # B. Liste de langues corrompue
    try:
        definir_portee_corpus(langues=["fr", 123]) # Mélange str et int
        print("      -> ÉCHEC : Aurait dû lever TypeError.")
        assert False
    except TypeError:
        print("      -> Succès : Liste hétérogène détectée.")

    print("\n Test validé : La configuration de la portée est correcte.")

test_definir_portee_corpus()

def definir_filtres_corpus(filtres=None):
    """
    Description :
        Définit et valide un ensemble de critères restrictifs basés sur les métadonnées
        disponibles dans le corpus spécifique du projet.
        
    Filtres supportés :
        - taille_min / taille_max (int) : Nombre de mots ou caractères.
        - provenance (str ou list) : Origine du document (ex: 'iut', 'univ_etrangere').
        - langue (str ou list) : Code langue (ex: 'en', 'fr').
        
    Paramètres :
        filtres  dict, dictionnaire contenant les critères {clé: valeur}.
                 Par défaut None.

    Retour :
        dict, structure contenant les critères validés et un indicateur 'est_actif'.

    Lève :
        TypeError si 'filtres' n'est pas un dictionnaire.
        ValueError si incohérence dans les tailles (min > max).
    """
    
    # 1. Cas par défaut
    if filtres is None:
        return {"criteres": {}, "est_actif": False}

    if not isinstance(filtres, dict):
        raise TypeError(f"Le paramètre 'filtres' doit être un dictionnaire. Reçu : {type(filtres)}")

    criteres_valides = {}
    
    # 2. Validation : Taille (Numérique et Logique)
    t_min = filtres.get("taille_min")
    t_max = filtres.get("taille_max")
    
    if t_min is not None:
        if not isinstance(t_min, (int, float)): raise TypeError("taille_min doit être un nombre.")
        criteres_valides["taille_min"] = t_min
        
    if t_max is not None:
        if not isinstance(t_max, (int, float)): raise TypeError("taille_max doit être un nombre.")
        criteres_valides["taille_max"] = t_max
        
    if (t_min is not None) and (t_max is not None) and (t_min > t_max):
        raise ValueError(f"Incohérence : taille_min ({t_min}) > taille_max ({t_max}).")

    # 3. Validation : Provenance (String ou Liste de strings)
    prov = filtres.get("provenance")
    if prov is not None:
        if isinstance(prov, str):
            criteres_valides["provenance"] = [prov] # On normalise en liste
        elif isinstance(prov, list):
            if not all(isinstance(p, str) for p in prov):
                raise TypeError("La liste de provenance doit contenir des chaînes.")
            criteres_valides["provenance"] = prov
        else:
            raise TypeError("La provenance doit être une chaîne (str) ou une liste (list).")

    # 4. Validation : Langue (String ou Liste de strings)
    lang = filtres.get("langue")
    if lang is not None:
        if isinstance(lang, str):
            criteres_valides["langue"] = [lang]
        elif isinstance(lang, list):
             if not all(isinstance(l, str) for l in lang):
                raise TypeError("La liste de langues doit contenir des chaînes.")
             criteres_valides["langue"] = lang
        else:
            raise TypeError("Le filtre langue doit être une chaîne (str) ou une liste (list).")

    # 5. Construction du résultat
    est_actif = len(criteres_valides) > 0

    return {
        "criteres": criteres_valides,
        "est_actif": est_actif
    }


# Tests unitaires Exercice III.2.a (Fin - Adapté)

def test_definir_filtres_corpus():
    print("\n Test : definir_filtres_corpus (Version Corpus Réel) ")
    
    # --- 1. Cas Standard : Filtre Provenance et Taille ---
    print("  [1] Test Cas Standard (Provenance IUT + Taille)...")
    mes_filtres = {
        "provenance": "iut",
        "taille_min": 100
    }
    res = definir_filtres_corpus(mes_filtres)
    
    assert res["est_actif"] is True
    assert res["criteres"]["provenance"] == ["iut"] # Normalisation en liste
    assert res["criteres"]["taille_min"] == 100
    print("      -> Succès.")

    # --- 2. Cas Standard : Liste de provenances ---
    print("  [2] Test Cas Standard (Multi-provenances)...")
    filtres_multi = {"provenance": ["iut", "univ_etrangere"]}
    res_multi = definir_filtres_corpus(filtres_multi)
    
    assert "univ_etrangere" in res_multi["criteres"]["provenance"]
    print("      -> Succès.")

    # --- 3. Cas d'erreurs ---
    print("  [3] Test Cas d'erreurs...")
    
    # A. Incohérence Taille
    try:
        definir_filtres_corpus({"taille_min": 500, "taille_max": 10})
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError:
        print("      -> Succès : Incohérence min > max détectée.")

    # B. Mauvais type Provenance
    try:
        definir_filtres_corpus({"provenance": 12345})
        print("      -> ÉCHEC : Aurait dû lever TypeError.")
        assert False
    except TypeError:
        print("      -> Succès : Provenance invalide (int) détectée.")

    print("\n Test validé : Les filtres spécifiques au corpus sont gérés.")

test_definir_filtres_corpus()

def choisir_descripteurs(fiche_requete, descripteurs=["TF-IDF"], 
                         methode_aggregation=None, normalisation_norme=None, 
                         normalisation_avancee=None):
    """
    Description :
        Configure la stratégie de représentation (vectorisation) de la requête.
        Définit quels descripteurs utiliser (Symboliques ou Embeddings) et comment
        les traiter (Agrégation, Normalisation vectorielle, Normalisation statistique).
        
    Paramètres :
        fiche_requete         dict, la structure de requête.
        descripteurs          list, liste des types de descripteurs (ex: ['TF-IDF'], ['Word2Vec']).
        methode_aggregation   str, pour les embeddings : 'moyenne', 'somme_ponderee', 'inference'.
                              None pour les méthodes symboliques (TF-IDF, etc.).
        normalisation_norme   str, normalisation vectorielle : 'l1', 'l2', 'none'.
        normalisation_avancee str, normalisation statistique : 'minmax', 'zscore', 'none'.

    Retour :
        dict, la fiche de requête mise à jour avec une entrée "config_descripteurs".

    Lève :
        ValueError si la fiche est None ou si les descripteurs sont invalides.
    """
    
    # Listes de validation (Constantes)
    DESC_SYMBOLIQUES = ["bow", "tf", "tf-idf", "bm25"]
    DESC_VECTORIELS = ["word2vec", "doc2vec", "fasttext", "glove", "bert"]
    AGG_VALIDES = ["moyenne", "somme", "somme_ponderee", "inference", None]
    NORM_NORME_VALIDES = ["l1", "l2", "none", None]
    NORM_ADV_VALIDES = ["minmax", "zscore", "none", None]

    # 1. Vérifications défensives de base
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")

    # Normalisation de l'entrée descripteurs (str -> list) et minuscules
    if isinstance(descripteurs, str):
        descripteurs = [descripteurs]
    
    desc_norm = [d.lower().strip() for d in descripteurs]
    
    # Vérification validité descripteurs
    tous_possibles = DESC_SYMBOLIQUES + DESC_VECTORIELS
    for d in desc_norm:
        if d not in tous_possibles:
            raise ValueError(f"Descripteur inconnu : '{d}'.")

    # 2. Vérification de la cohérence (Règles métier)
    
    # Règle : Si Embedding, il faut vérifier l'agrégation (sauf si Doc2Vec/Inférence)
    est_embedding = any(d in DESC_VECTORIELS for d in desc_norm)
    if est_embedding:
        if methode_aggregation is not None:
             agg_norm = methode_aggregation.lower()
             if agg_norm not in AGG_VALIDES:
                 raise ValueError(f"Méthode d'agrégation invalide : {methode_aggregation}")
        # Note : On pourrait forcer une valeur par défaut ici, mais on laisse le choix explicite.

    # Règle : Normalisation avancée (MinMax/Zscore) déconseillée pour Symbolique creux
    # (On ne lève pas d'erreur bloquante, mais on s'assure que la valeur est valide)
    norm_adv_valide = normalisation_avancee.lower() if normalisation_avancee else None
    if norm_adv_valide not in NORM_ADV_VALIDES:
         raise ValueError(f"Normalisation avancée invalide : {normalisation_avancee}")

    norm_norme_valide = normalisation_norme.lower() if normalisation_norme else None
    if norm_norme_valide not in NORM_NORME_VALIDES:
        raise ValueError(f"Normalisation de norme invalide : {normalisation_norme}")

    # 3. Construction de la configuration
    nouvelle_config = {
        "types": desc_norm,
        "aggregation": methode_aggregation,
        "norme": norm_norme_valide,
        "norm_avancee": norm_adv_valide
    }

    # 4. Mise à jour et Reset si changement
    ancienne_config = fiche_requete.get("config_descripteurs")
    
    if ancienne_config != nouvelle_config:
        fiche_requete["config_descripteurs"] = nouvelle_config
        # Tout changement ici invalide le vecteur calculé
        fiche_requete["statut"] = "non_calcule"
        fiche_requete["vecteur"] = None
        fiche_requete["resultats"] = []

    return fiche_requete


# Tests unitaires Exercice III.2.b

def test_choisir_descripteurs():
    print("\n Test : choisir_descripteurs ")
    
    fiche_base = {"id": "REQ_DESC", "texte": "test", "statut": "calcule"}

    # --- 1. Cas Standard : TF-IDF avec Norme L2 ---
    print("  [1] Test Cas Standard (Symbolique TF-IDF + L2)...")
    res_tfidf = choisir_descripteurs(fiche_base.copy(), 
                                     descripteurs=["TF-IDF"], 
                                     normalisation_norme="L2")
    
    config = res_tfidf["config_descripteurs"]
    assert config["types"] == ["tf-idf"]
    assert config["norme"] == "l2"
    assert res_tfidf["statut"] == "non_calcule" # Reset car nouvelle config
    print("      -> Succès.")

    # --- 2. Cas Standard : Embedding avec Moyenne ---
    print("  [2] Test Cas Standard (Embedding Word2Vec + Moyenne)...")
    res_w2v = choisir_descripteurs(fiche_base.copy(), 
                                   descripteurs="Word2Vec", # Test string unique
                                   methode_aggregation="moyenne",
                                   normalisation_avancee="minmax")
    
    config_w2v = res_w2v["config_descripteurs"]
    assert config_w2v["types"] == ["word2vec"]
    assert config_w2v["aggregation"] == "moyenne"
    assert config_w2v["norm_avancee"] == "minmax"
    print("      -> Succès.")

    # --- 3. Cas Optimisation : Même configuration ---
    print("  [3] Test Cas Optimisation (Pas de changement)...")
    # On reprend la fiche issue du test 1
    fiche_calculee = res_tfidf.copy()
    fiche_calculee["statut"] = "calcule" # On simule un calcul fait
    
    res_meme = choisir_descripteurs(fiche_calculee, 
                                    descripteurs=["TF-IDF"], 
                                    normalisation_norme="L2")
    
    assert res_meme["statut"] == "calcule" # Pas de reset
    print("      -> Succès (État préservé).")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Descripteur inconnu
    try:
        choisir_descripteurs(fiche_base, descripteurs=["SuperAlgoInconnu"])
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Descripteur inconnu détecté ({e})")

    # B. Agrégation invalide
    try:
        choisir_descripteurs(fiche_base, descripteurs=["word2vec"], methode_aggregation="fusion_nucleaire")
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError:
        print("      -> Succès : Agrégation invalide détectée.")

    print("\n Test validé : La configuration des descripteurs est correcte.")

test_choisir_descripteurs()

# III. Onglet principal : Recherche documentaire
# 2. Paramétrage du scénario de recherche
# c) Choix de la mesure de similarité

def definir_distance(fiche_requete, type_distance="cosinus"):
    """
    Description :
        Associe une mesure de similarité ou une distance mathématique à la requête.
        Vérifie la compatibilité entre la distance demandée et les descripteurs 
        configurés dans la fiche (Symbolique vs Vectoriel).

    Règles de compatibilité (selon l'énoncé) :
        - Symbolique (TF-IDF, BOW...) : Cosinus, Jaccard.
        - Vectoriel (Embeddings) : Cosinus, Euclidienne, Manhattan, Minkowski.
        - Hybride (Symbolique + Vectoriel) : 'combinaison'.

    Paramètres :
        fiche_requete  dict, la structure de requête. Doit contenir 'config_descripteurs'.
        type_distance  str, nom de la mesure (ex: 'cosinus', 'euclidienne').
                       Par défaut "cosinus".

    Retour :
        dict, la fiche mise à jour avec le champ "type_distance".

    Lève :
        ValueError si la fiche est incomplète (pas de descripteurs).
        ValueError si la distance est incompatible avec le type de descripteur.
    """
    
    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")
        
    if "config_descripteurs" not in fiche_requete:
        raise ValueError("Impossible de définir la distance : aucun descripteur n'a été choisi au préalable.")

    # Normalisation
    if not isinstance(type_distance, str):
        raise TypeError("Le type de distance doit être une chaîne de caractères.")
        
    dist_norm = type_distance.strip().lower()

    # 2. Définition des familles
    DESC_SYMBOLIQUES = ["bow", "tf", "tf-idf", "bm25"]
    DESC_VECTORIELS = ["word2vec", "doc2vec", "fasttext", "glove", "bert"]
    
    # Distances autorisées par famille
    ALLOWED_SYMBOLIQUE = ["cosinus", "jaccard"]
    ALLOWED_VECTORIEL = ["cosinus", "euclidienne", "manhattan", "minkowski"]
    
    # Récupération des descripteurs actifs
    types_actifs = fiche_requete["config_descripteurs"]["types"] # Liste
    
    # 3. Validation de la compatibilité
    is_symbolique = any(t in DESC_SYMBOLIQUES for t in types_actifs)
    is_vectoriel = any(t in DESC_VECTORIELS for t in types_actifs)
    is_hybride = is_symbolique and is_vectoriel

    if is_hybride:
        # En hybride, on accepte 'combinaison' ou 'cosinus' (souvent le dénominateur commun)
        if dist_norm not in ["combinaison", "cosinus"]:
             # On pourrait être plus permissif, mais suivons la logique de séparation
             pass 
             # Note: Pour cet exercice, on autorise 'cosinus' comme valeur sûre en hybride.

    elif is_symbolique and not is_vectoriel:
        # Si purement symbolique
        if dist_norm not in ALLOWED_SYMBOLIQUE:
            raise ValueError(f"Incompatibilité : La distance '{dist_norm}' n'est pas adaptée "
                             f"aux descripteurs symboliques {types_actifs}. "
                             f"Utilisez : {ALLOWED_SYMBOLIQUE}")

    elif is_vectoriel and not is_symbolique:
        # Si purement vectoriel
        if dist_norm not in ALLOWED_VECTORIEL:
            raise ValueError(f"Incompatibilité : La distance '{dist_norm}' n'est pas adaptée "
                             f"aux descripteurs vectoriels {types_actifs}. "
                             f"Utilisez : {ALLOWED_VECTORIEL}")

    # 4. Mise à jour et Reset
    ancien_dist = fiche_requete.get("type_distance")
    
    if ancien_dist != dist_norm:
        fiche_requete["type_distance"] = dist_norm
        # Changer la méthode de calcul de score invalide les résultats
        fiche_requete["statut"] = "non_calcule"
        fiche_requete["resultats"] = []

    return fiche_requete


# Tests unitaires Exercice III.2.c

def test_definir_distance():
    print("\n Test : definir_distance ")
    
    # Préparation de fiches avec descripteurs déjà configurés
    fiche_symb = {
        "id": "R_SYMB", "texte": "...", 
        "config_descripteurs": {"types": ["tf-idf"]}, 
        "statut": "calcule"
    }
    
    fiche_vect = {
        "id": "R_VECT", "texte": "...", 
        "config_descripteurs": {"types": ["word2vec"]}, 
        "statut": "calcule"
    }

    # --- 1. Cas Standard : Cosinus (Universel) ---
    print("  [1] Test Cas Standard (Cosinus sur TF-IDF)...")
    res_cos = definir_distance(fiche_symb.copy(), "cosinus")
    assert res_cos["type_distance"] == "cosinus"
    print("      -> Succès.")

    # --- 2. Cas Standard : Euclidienne sur Vectoriel ---
    print("  [2] Test Cas Standard (Euclidienne sur Word2Vec)...")
    res_euc = definir_distance(fiche_vect.copy(), "euclidienne")
    assert res_euc["type_distance"] == "euclidienne"
    print("      -> Succès.")

    # --- 3. Cas Incompatibilité : Euclidienne sur Symbolique ---
    print("  [3] Test Cas Incompatibilité (Euclidienne sur TF-IDF)...")
    try:
        definir_distance(fiche_symb.copy(), "euclidienne")
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Incompatibilité détectée ({e})")

    # --- 4. Cas Incompatibilité : Jaccard sur Vectoriel ---
    print("  [4] Test Cas Incompatibilité (Jaccard sur Word2Vec)...")
    # Note : Bien que mathématiquement possible, l'énoncé le déconseille pour les embeddings
    try:
        definir_distance(fiche_vect.copy(), "jaccard")
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError as e:
        print(f"      -> Succès : Incompatibilité détectée ({e})")

    # --- 5. Cas Erreur : Pas de descripteurs ---
    print("  [5] Test Cas Erreur (Fiche incomplète)...")
    try:
        fiche_vide = {"id": "R_VIDE"}
        definir_distance(fiche_vide, "cosinus")
        print("      -> ÉCHEC : Aurait dû lever ValueError (dependance manquante).")
        assert False
    except ValueError:
        print("      -> Succès : Absence de config descripteurs détectée.")

    print("\n Test validé : La cohérence distance/descripteur est assurée.")

test_definir_distance()

# III. Onglet principal : Recherche documentaire
# 2. Paramétrage du scénario de recherche
# d) Paramètres avancés

def definir_options_avancees(fiche_requete, expansion_requete=False, 
                             multi_langues=False, pre_calcul_normes=True):
    """
    Description :
        Configure les options avancées du moteur de recherche.
        - Expansion de requête : enrichissement automatique (synonymes/embeddings).
        - Multi-langues : stratégie de fusion ou séparation des résultats par langue.
        - Pré-calcul normes : optimisation des calculs de similarité.

    Paramètres :
        fiche_requete      dict, la structure de requête.
        expansion_requete  bool, activer/désactiver l'expansion (Défaut: False).
        multi_langues      bool, activer le mode multilingue (Défaut: False).
        pre_calcul_normes  bool, utiliser les normes pré-calculées (Défaut: True).

    Retour :
        dict, la fiche de requête mise à jour avec le champ "options_avancees".

    Lève :
        ValueError si la fiche est None.
        TypeError si les options ne sont pas des booléens.
    """
    
    # 1. Vérifications défensives
    if fiche_requete is None:
        raise ValueError("La fiche_requete ne peut pas être None.")

    # Vérification des types booléens
    if not isinstance(expansion_requete, bool):
        raise TypeError(f"expansion_requete doit être un booléen. Reçu : {type(expansion_requete)}")
        
    if not isinstance(multi_langues, bool):
        raise TypeError(f"multi_langues doit être un booléen. Reçu : {type(multi_langues)}")
        
    if not isinstance(pre_calcul_normes, bool):
        raise TypeError(f"pre_calcul_normes doit être un booléen. Reçu : {type(pre_calcul_normes)}")

    # 2. Construction de la configuration
    nouvelle_config = {
        "expansion": expansion_requete,
        "mode_multilingue": multi_langues,
        "optimisation_normes": pre_calcul_normes
    }

    # 3. Mise à jour et Gestion d'état
    ancienne_config = fiche_requete.get("options_avancees")
    
    # Si les options changent, on invalide le statut "calculé"
    # Exemple : Si on active l'expansion, le vecteur requête va changer.
    # Exemple : Si on change le mode multilingue, les résultats changent.
    if ancienne_config != nouvelle_config:
        fiche_requete["options_avancees"] = nouvelle_config
        
        fiche_requete["statut"] = "non_calcule"
        fiche_requete["resultats"] = []
        
        # Si l'expansion change, le vecteur change potentiellement
        if ancienne_config and (ancienne_config["expansion"] != expansion_requete):
             fiche_requete["vecteur"] = None

    return fiche_requete


# Tests unitaires Exercice III.2.d

def test_definir_options_avancees():
    print("\n Test : definir_options_avancees ")
    
    fiche_base = {"id": "REQ_ADV", "texte": "test", "statut": "calcule"}

    # --- 1. Cas Standard : Activation Expansion ---
    print("  [1] Test Cas Standard (Expansion=True)...")
    res_exp = definir_options_avancees(fiche_base.copy(), 
                                       expansion_requete=True,
                                       multi_langues=False,
                                       pre_calcul_normes=True)
    
    opts = res_exp["options_avancees"]
    assert opts["expansion"] is True
    assert opts["mode_multilingue"] is False
    assert res_exp["statut"] == "non_calcule" # Reset déclenché
    print("      -> Succès.")

    # --- 2. Cas Standard : Valeurs par défaut ---
    print("  [2] Test Cas Standard (Défaut)...")
    res_defaut = definir_options_avancees(fiche_base.copy())
    
    opts_def = res_defaut["options_avancees"]
    assert opts_def["expansion"] is False
    assert opts_def["optimisation_normes"] is True
    print("      -> Succès.")

    # --- 3. Cas Optimisation : Même configuration ---
    print("  [3] Test Cas Optimisation (Pas de changement)...")
    # On crée une fiche qui a déjà ces options
    fiche_prete = res_exp.copy()
    fiche_prete["statut"] = "calcule" # On simule un calcul terminé
    
    # On réapplique exactement les mêmes options
    res_meme = definir_options_avancees(fiche_prete, 
                                        expansion_requete=True,
                                        multi_langues=False,
                                        pre_calcul_normes=True)
    
    assert res_meme["statut"] == "calcule" # L'état doit être préservé
    print("      -> Succès (État préservé).")

    # --- 4. Cas d'erreurs ---
    print("  [4] Test Cas d'erreurs...")
    
    # A. Mauvais type (int au lieu de bool)
    try:
        definir_options_avancees(fiche_base, expansion_requete=1)
        print("      -> ÉCHEC : Aurait dû lever TypeError.")
        assert False
    except TypeError as e:
        print(f"      -> Succès : Type incorrect détecté ({e})")

    # B. Fiche None
    try:
        definir_options_avancees(None)
        print("      -> ÉCHEC : Aurait dû lever ValueError.")
        assert False
    except ValueError:
        print("      -> Succès : Fiche None détectée.")

    print("\n Test validé : La gestion des options avancées est correcte.")

test_definir_options_avancees()

