import numpy as np
from s4 import bag_of_words_binaire, bag_of_words_occurrences, calcul_tf
import os
from s1_Cocu_Ethan import explorer_corpus
from s2_Cocu_Ethan import detecter_langue_f
from s2_Cocu_Ethan import convertir_vers_minuscule, traiter_ponctuation, traiter_accents
from s3 import segmenter_mots, pipeline_filtrage, pipeline_morphologique
from s3 import pipeline_pretraitement
from s3 import construire_vocabulaire, construire_dictionnaire_vocabulaire
from s4 import calcul_idf
from s3 import generer_ngrammes
from s4 import construire_dictionnaire_ngrammes, encoder_tfidf_ngrammes, calcul_idf

#1 Vectorisation des requêtes et du corpus
#a Vectorisation d’une phrase


def vectoriser_phrase(phrase, vocabulaire_direct, methode="tfidf", **params):
    """
    Description :
        Transforme une phrase en un vecteur numérique
        selon la méthode choisie.
    
    Paramètres :
        phrase              list, la phrase tokenisée.
        vocabulaire_direct  dict, mapping {mot : index}.
        methode             str, méthode de pondération :
                            'bool', 'count', 'tf', 'tfidf', 'bm25'.
        **params            arguments variables pour les méthodes avancées :
                            
    
    Retour :
        numpy.array, le vecteur représentant la phrase.
    """
    if methode == "bool":
        return bag_of_words_binaire(phrase, vocabulaire_direct)
    
    elif methode == "count":
        return bag_of_words_occurrences(phrase, vocabulaire_direct)
        
    elif methode == "tf":
        return calcul_tf(phrase, vocabulaire_direct)

    elif methode == "tfidf":
        vecteurTf = calcul_tf(phrase, vocabulaire_direct)
        
        vecteurIdf = params.get("vecteurIdf")
        
        if vecteurIdf is None:
            return vecteurTf 
        return vecteurTf * vecteurIdf

    elif methode == "bm25":
        vecteurIdf = params.get("vecteurIdf")
        k1 = params.get("k1", 1.5)
        b = params.get("b", 0.75)
        avgdl = params.get("avgdl", 1.0)
        
        if vecteurIdf is None:
            return np.zeros(len(vocabulaire_direct))

        vecteur = bag_of_words_occurrences(phrase, vocabulaire_direct)

        len_d = len(phrase)
        numerateur = vecteur * (k1 + 1)
        denominateur = vecteur + k1 * (1 - b + b * (len_d / avgdl))
        with np.errstate(divide='ignore', invalid='ignore'):
            fraction = numerateur / denominateur
            fraction = np.nan_to_num(fraction) 
            
        return vecteurIdf * fraction

    else:
        return bag_of_words_binaire(phrase, vocabulaire_direct)


def test_vectoriser_phrase():
    print("\n Test : vectoriser_phrase ")
    
    #  Configuration 
    vocab = {"chat": 0, "chien": 1, "mange": 2, "souris": 3}
    phrase = ["chat", "mange", "chat"] # "chat" apparaît 2 fois
    
    # Simulation d'un vecteur IDF (supposons que 'chat' est fréquent, 'souris' rare)
    # chat(0): 0.2, chien(1): 1.0, mange(2): 0.5, souris(3): 1.5
    idf_simule = np.array([0.2, 1.0, 0.5, 1.5])
    
    #  1. Test Booléen 
    v_bool = vectoriser_phrase(phrase, vocab, methode="bool")
    assert np.array_equal(v_bool, [1, 0, 1, 0])
    
    #  2. Test Count 
    v_count = vectoriser_phrase(phrase, vocab, methode="count")
    assert np.array_equal(v_count, [2, 0, 1, 0])
    
    #  3. Test TF 
    v_tf = vectoriser_phrase(phrase, vocab, methode="tf")
    assert np.isclose(v_tf[0], 0.666, atol=1e-2)
    
    #  4. Test TF-IDF 
    v_tfidf = vectoriser_phrase(phrase, vocab, methode="tfidf", vecteurIdf=idf_simule)
    assert np.isclose(v_tfidf[0], v_tf[0] * idf_simule[0])
    
    #  5. Test BM25 
    v_bm25 = vectoriser_phrase(
        phrase, vocab, methode="bm25", 
        vecteurIdf=idf_simule, avgdl=10, k1=1.5, b=0.75)
    assert len(v_bm25) == 4
    assert v_bm25[1] == 0.0
    assert v_bm25[0] > 0.0
    print(" Test 'vectoriser_phrase' validé.")
#test_vectoriser_phrase()


#b. Vectorisation d'un document

# i. Vectorisation basée sur les mots du document
def vectoriser_document_mots(document, vocabulaire_direct, methode="tfidf", **params):
    """
    Description :
        Vectorise un document en considérant toutes ses phrases comme un seul texte.
        Aplatit la structure en une seule liste de mots.
    
    Paramètres :
        document            list, liste de listes de tokens.
        vocabulaire_direct  dict, mapping {mot : index}.
        methode             str, méthode de pondération.
        **params            arguments supplémentaires.
    
    Retour :
        numpy.array, le vecteur globals du document.
    """
    if not document:
        return np.zeros(len(vocabulaire_direct))
    
    tokens = []
    for phrase in document:
        for mot in phrase:
            tokens.append(mot)
    return vectoriser_phrase(tokens, vocabulaire_direct, methode, **params)

# ii. Vectorisation par agrégation des vecteurs des phrases

def vectoriser_document_agrege(document, vocabulaire_direct, methode="tfidf", strategie="moyenne", **params):
    """
    Description :
        Vectorise chaque phrase séparément puis agrège les vecteurs obtenus.
    
    Paramètres :
        document            list, liste de listes de tokens.
        vocabulaire_direct  dict, mapping {mot : index}.
        methode             str, méthode de pondération pour chaque phrase.
        strategie           str, méthode d'agrégation : "moyenne", "somme", "max".
        **params            arguments supplémentaires.
    
    Retour :
        numpy.array, le vecteur agrégé du document.
    """
    taille = len(vocabulaire_direct)
    
    if not document:
        return np.zeros(taille)
        
    vecteur = []
    for phrase in document:
        vec = vectoriser_phrase(phrase, vocabulaire_direct, methode, **params)
        vecteur.append(vec)
    if not vecteur:
        return np.zeros(taille)
    matrice = np.array(vecteur)
    if strategie == "moyenne":
        vecteurRes = np.mean(matrice, axis=0)
        
    elif strategie == "somme":
        vecteurRes = np.sum(matrice, axis=0)
        
    elif strategie == "max":
        vecteurRes = np.max(matrice, axis=0)
        
    else:
        vecteurRes = np.mean(matrice, axis=0)
        
    return vecteurRes


def test_vectorisation_document_strategies():
    print("\n Test : Vectorisation Document")
    
    # Configuration
    vocab = {"chat": 0, "chien": 1, "dort": 2}
    doc = [["chat"], ["chat", "chien"]]
    vec_mots = vectoriser_document_mots(doc, vocab, methode="count")
    
    assert vec_mots[0] == 2
    assert vec_mots[1] == 1
    assert vec_mots[2] == 0 
    
    # Phrase 1 ("chat") -> [1, 0, 0] (en count)
    # Phrase 2 ("chat chien") -> [1, 1, 0] (en count)
    
    # Stratégie Somme
    vec_somme = vectoriser_document_agrege(doc, vocab, methode="count", strategie="somme")
    assert np.array_equal(vec_somme, [2, 1, 0])
    
    # Stratégie Moyenne
    vec_moy = vectoriser_document_agrege(doc, vocab, methode="count", strategie="moyenne")
    assert vec_moy[0] == 1.0
    assert vec_moy[1] == 0.5
    
    # Stratégie Max
    vec_max = vectoriser_document_agrege(doc, vocab, methode="count", strategie="max")
    assert vec_max[0] == 1
    assert vec_max[1] == 1
    
    print(" Test 'vectorisation_document_strategies' validé.")

#test_vectorisation_document_strategies()

#c. Vectorisation du corpus (Fonction générique)

def vectoriser_corpus(corpus, vocabulaire_direct, methode="tfidf", niveau="document_mots", strategie_agregation="moyenne", **params):
    """
    Description :
        Transforme un corpus en une suite de vecteurs selon le niveau de granularité demandé.
        Cette fonction unifiée gère les trois niveaux définis dans la consigne : 
        "phrase", "document_mots", "document_agrege".

    Paramètres :
        corpus                dict, {id : [[mot1, ...], [mot1, ...]]}.
        vocabulaire_direct    dict, mapping {mot : index}.
        methode               str, méthode de pondération ("tfidf", "bm25", "count", etc.).
        niveau                str, le niveau de vectorisation souhaité :
                                - "phrase" : retourne une liste de vecteurs pour chaque document.
                                - "document_mots" : concatène les mots (stratégie à plat).
                                - "document_agrege" : vectorise les phrases puis agrège.
        strategie_agregation  str, si niveau="document_agrege" ("moyenne", "somme", "max").
        **params              arguments variables (vecteurIdf, k1, b, etc.).

    Retour :
        dict, la structure retournée dépend du niveau :
              - "phrase" : {id : [vecteur_phrase_1, vecteur_phrase_2, ...]}
              - "document_..." : {id : vecteur_document}
    """
    matrice = {}
    
    if not corpus:
        return matrice

    for id, doc in corpus.items():
        if niveau == "phrase":
            vecteurs = []
            for phrase in doc:
                vec = vectoriser_phrase(phrase, vocabulaire_direct, methode, **params)
                vecteurs.append(vec)
            matrice[id] = vecteurs
        elif niveau == "document_mots":
            matrice[id] = vectoriser_document_mots(
                doc, vocabulaire_direct, methode, **params
            )
        elif niveau == "document_agrege":
            matrice[id] = vectoriser_document_agrege(
                doc, vocabulaire_direct, methode, strategie=strategie_agregation, **params
            )
            
    return matrice


def test_vectoriser_corpus_generique():
    print("\n Test : vectoriser_corpus (Générique - 3 niveaux) ")
    
    # Configuration
    vocab = {"chat": 0, "chien": 1}
    corpus = {
        "d1": [["chat"], ["chat", "chien"]]
    }
    
    # Test 1 : Niveau Phrase
    res_phrase = vectoriser_corpus(corpus, vocab, methode="count", niveau="phrase")
    assert len(res_phrase["d1"]) == 2
    assert np.array_equal(res_phrase["d1"][0], [1, 0])
    
    # Test 2 : Niveau Document Mots 
    res_mots = vectoriser_corpus(corpus, vocab, methode="count", niveau="document_mots")
    assert np.array_equal(res_mots["d1"], [2, 1])
    
    # Test 3 : Niveau Document Agrégé 
    res_agg = vectoriser_corpus(
        corpus, vocab, methode="count", 
        niveau="document_agrege", strategie_agregation="somme"
    )
    assert np.array_equal(res_agg["d1"], [2, 1])
    
    print(" Test 'vectoriser_corpus_generique' validé.")

#test_vectoriser_corpus_generique()


# e. Construction des métadonnées du corpus

def construire_meta_corpus(chemin_base):
    """
    Description :
        Parcourt le corpus et construit un dictionnaire de métadonnées
        pour chaque fichier trouvé.
        
    Paramètres :
        chemin_base  str, le chemin du dossier racine contenant le corpus brut.
        
    Retour :
        dict, dictionnaire { id : { 'langue':..., 'sous_corpus':..., 'chemin':... } }
    """
    metaCorpus = {}
    dic = explorer_corpus(chemin_base)
    
    if not dic:
        return {}

    i = 0
    
    for cheminDossier, infos in dic.items():
        nomSousCorpus = os.path.basename(cheminDossier)
        if os.path.normpath(cheminDossier) == os.path.normpath(chemin_base):
            nomSousCorpus = "Racine"

        for fichier in infos['contenu']:
            if not fichier.endswith('.txt'):
                continue
            chemin = os.path.join(cheminDossier, fichier)
            id = os.path.splitext(fichier)[0]
            langue = detecter_langue_f(fichier)
            if langue == "inconnue":
                langue = "na"
            elif langue == "français":
                langue = "fr"
            elif langue == "anglais":
                langue = "en"
            metaCorpus[id] = {
                'id': id,
                'titre': id,        
                'langue': langue,
                'sous_corpus': nomSousCorpus,
                'chemin': chemin,
                'position': i
            }
            
            i += 1
            
    return metaCorpus


def test_construire_meta_corpus():
    print("\n Test : construire_meta_corpus ")
    
    # Setup : Création d'une structure temporaire pour le test
    dir_test = "test_metaCorpus"
    dir_ufr = os.path.join(dir_test, "UFR")
    f_txt = os.path.join(dir_ufr, "etu01_fr.txt")
    
    try:
        os.makedirs(dir_ufr, exist_ok=True)
        with open(f_txt, "w") as f: f.write("test")
        
        meta = construire_meta_corpus(dir_test)
        
        assert "etu01_fr" in meta
        donnees = meta["etu01_fr"]
        
        assert donnees["langue"] == "fr"
        assert donnees["sous_corpus"] == "UFR"
        assert donnees["titre"] == "etu01_fr"
        assert donnees["position"] == 0
        assert os.path.normpath(donnees["chemin"]) == os.path.normpath(f_txt)
        
        print(" Test 'construire_meta_corpus' validé.")
        
    except Exception as e:
        print(f" Erreur test meta : {e}")
        
    finally:
        if os.path.exists(f_txt): os.remove(f_txt)
        if os.path.exists(dir_ufr): os.rmdir(dir_ufr)
        if os.path.exists(dir_test): os.rmdir(dir_test)

#test_construire_meta_corpus()

# 2. Mesures de similarité entre vecteurs

# a. Distance Euclidienne (L2)
def calcul_distance_euclidienne(v1, v2):
    """
    Description :
        Calcule la distance "droite" entre deux vecteurs.
        Formule : sqrt(sum((v1 - v2)^2))
    
    Paramètres :
        v1, v2  list ou numpy.array, les deux vecteurs à comparer.
    
    Retour :
        float, la distance euclidienne.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    
    return np.sqrt(np.sum((a - b) ** 2))

# b. Distance Manhattan (L1)
def calcul_distance_manhattan(v1, v2):
    """
    Description :
        Calcule la somme des écarts absolus.
        Moins sensible aux valeurs extrêmes que l'Euclidienne.
        Formule : sum(|v1 - v2|)
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, la distance Manhattan.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    
    return np.sum(np.abs(a - b))

# c. Distance de Minkowski (Lp)
def calcul_distance_minkowski(v1, v2, p):
    """
    Description :
        Généralisation des distances.
        Formule : (sum(|v1 - v2|^p))^(1/p)
    
    Paramètres :
        v1, v2  list ou numpy.array.
        p       int ou float, l'ordre de la distance (p >= 1).
    
    Retour :
        float, la distance Minkowski.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    
    if p < 1:
        return 0.0
        
    somme = np.sum(np.power(np.abs(a - b), p))
    return np.power(somme, 1/p)

# d. Distance de Tchebychev (L_infini)
def calcul_distance_tchebychev(v1, v2):
    """
    Description :
        Mesure l'écart maximal entre deux vecteurs.
        Formule : max(|v1 - v2|)
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, la distance de Tchebychev.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    
    return np.max(np.abs(a - b))

# e. Distance de Bray-Curtis
def calcul_distance_bray_curtis(v1, v2):
    """
    Description :
        Mesure la dissimilarité basée sur les différences relatives.
        Très utilisée pour des données de comptage/fréquence.
        Formule : sum(|v1 - v2|) / sum(v1 + v2)
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, la distance.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    
    numerateur = np.sum(np.abs(a - b))
    denominateur = np.sum(a + b)
    
    if denominateur == 0:
        return 0.0
        
    return numerateur / denominateur

# f. Similarité Cosinus
def calcul_similarite_cosinus(v1, v2):
    """
    Description :
        Mesure l'angle entre deux vecteurs.
        Recommandé pour TF-IDF et textes longs.
        Formule : (v1 . v2) / (||v1|| * ||v2||)
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, score entre -1 et 1.
               1 = vecteurs identiques.
               0 = vecteurs orthogonaux.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    
    produit_scalaire = np.dot(a, b)
    normeA = np.linalg.norm(a)
    normeB = np.linalg.norm(b)
    
    if normeA == 0 or normeB == 0:
        return 0.0
        
    return produit_scalaire / (normeA * normeB)

# g. Distance Cosinus
def calcul_distance_cosinus(v1, v2):
    """
    Description :
        Inverse de la similarité cosinus.
        Formule : 1 - Similarité Cosinus
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, distance cosinus.
    """
    sim = calcul_similarite_cosinus(v1, v2)
    return 1 - sim

# h. Similarité et distance de Jaccard

def calcul_similarite_jaccard(v1, v2):
    """
    Description :
        Calcule la similarité de Jaccard.
        Pour des vecteurs binaires : Intersection / Union.
        Pour des vecteurs pondérés : Somme(Min) / Somme(Max).
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, score entre 0.0 et 1.0.
    """
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    numerateur = np.sum(np.minimum(a, b))
    denominateur = np.sum(np.maximum(a, b))
    if denominateur == 0:
        return 0.0
        
    return numerateur / denominateur


def calcul_distance_jaccard(v1, v2):
    """
    Description :
        Calcule la distance de Jaccard.
        Formule : 1 - Similarité Jaccard.
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, distance entre 0.0 et 1.0.
    """
    sim = calcul_similarite_jaccard(v1, v2)
    return 1.0 - sim


# i. Distance de Hamming

def calcul_distance_hamming(v1, v2):
    """
    Description :
        Compte le nombre de positions où les deux vecteurs diffèrent.
        Adapté pour les vecteurs binaires ou catégoriels.
    
    Paramètres :
        v1, v2  list ou numpy.array.
    
    Retour :
        float, le nombre de différence.
    """
    a = np.array(v1)
    b = np.array(v2)
    if a.shape != b.shape:
        return -1.0
    return np.sum(a != b)


# j. Distance de Jensen-Shannon

def _divergence_kl(p, q):
    """
    Fonction utilitaire locale pour la Divergence de Kullback-Leibler.
    DivKL(P || Q) = sum(pi * log(pi / qi))
    """
    epsilon = 1e-10
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    masque = p > 0
    res = np.sum(p[masque] * np.log(p[masque] / (q[masque] + epsilon)))
    
    return res

def calcul_distance_jensen_shannon(v1, v2):
    """
    Description :
        Calcule la distance de Jensen-Shannon.
        C'est la racine carrée de la divergence JS.
        Symétrique et bornée entre 0 et 1 ou 0 et ln(2).
        
    Paramètres :
        v1, v2  list ou numpy.array.
                Note : Si la somme != 1, la fonction tente de normaliser.
    
    Retour :
        float, la distance JS.
    """
    p = np.array(v1, dtype=float)
    q = np.array(v2, dtype=float)
    sommep = np.sum(p)
    sommeq = np.sum(q)
    if sommep == 0 or sommeq == 0:
        return 0.0 
        
    p = p / sommep
    q = q / sommeq
    m = 0.5 * (p + q)
    divKlPm = _divergence_kl(p, m)
    divKlQm = _divergence_kl(q, m)
    jsDivergence = 0.5 * divKlPm + 0.5 * divKlQm
    jsDivergence = max(0.0, jsDivergence)
    
    return np.sqrt(jsDivergence)


def test_mesures_similarite():
    print("\n Test : Ensemble des mesures de similarité et distances ")
    
    vA = [0, 0]
    vB = [3, 4]
    vC = [1, 1]
    vD = [2, 2] 
    vE = [1, -1]
    vF = [1, 1, 0, 0]
    vG = [1, 0, 1, 0]
    dist1 = [0.5, 0.5]
    dist2 = [1.0, 0.0]
    dist3 = [0.0, 1.0]


    # a. Euclidienne 
    assert calcul_distance_euclidienne(vA, vB) == 5.0
    
    # b. Manhattan 
    assert calcul_distance_manhattan(vA, vB) == 7.0
    
    # c. Minkowski
    assert calcul_distance_minkowski(vA, vB, 1) == 7.0
    assert calcul_distance_minkowski(vA, vB, 2) == 5.0
    
    # d. Tchebychev :
    assert calcul_distance_tchebychev(vA, vB) == 4.0
    
    # e. Bray-Curtis :
    assert calcul_distance_bray_curtis(vA, vB) == 1.0

    # f. Similarité Cosinus
    assert np.isclose(calcul_similarite_cosinus(vC, vD), 1.0)
    assert np.isclose(calcul_similarite_cosinus(vC, vE), 0.0)
    
    # g. Distance Cosinus (1 - Sim)
    assert np.isclose(calcul_distance_cosinus(vC, vD), 0.0)

    # h. Jaccard (Inter / Union)
    assert np.isclose(calcul_similarite_jaccard(vF, vG), 1/3)
    assert np.isclose(calcul_distance_jaccard(vF, vG), 2/3)
    
    # Cas critique Jaccard : Vecteurs nuls
    assert calcul_similarite_jaccard([0,0], [0,0]) == 0.0

    # i. Hamming (Nombre de différences)
    # vF vs vG : diffèrent aux indices 1 et 2 -> 2 erreurs
    assert calcul_distance_hamming(vF, vG) == 2.0
    
    # Cas critique Hamming : Tailles différentes
    assert calcul_distance_hamming([1], [1, 2]) == -1.0
    # j. Jensen-Shannon
    # Identiques
    assert np.isclose(calcul_distance_jensen_shannon(dist1, dist1), 0.0)
    
    # Totalement différents
    res_js = calcul_distance_jensen_shannon(dist2, dist3)
    valeur_attendue = np.sqrt(np.log(2))
    assert np.isclose(res_js, valeur_attendue, atol=1e-3)
    
    # Cas critique JS : Vecteur nul
    assert calcul_distance_jensen_shannon([0, 0], [0.5, 0.5]) == 0.0
    
    print(" Tous les tests de similarité (1 à 10) sont validés avec succès.")

#test_mesures_similarite()


# 3. Recherche documentaire par requête

# a. Représentation de la requête

def pretraiter_requete(texte_requete, config_pretraitement, langue="fr"):
    """
    Description :
        Applique à la requête les mêmes étapes de prétraitement que celles 
        utilisées pour le corpus.
    
    Paramètres :
        texte_requete         str, la phrase brute tapée par l'utilisateur.
        config_pretraitement  dict, paramètres.
        langue                str, la langue de la requête.
    
    Retour :
        list, la liste des tokens prétraités.
    """
    if not texte_requete or not isinstance(texte_requete, str):
        return []
    txt = convertir_vers_minuscule(texte_requete)
    if config_pretraitement.get("accents"):
        txt = traiter_accents(txt, config_pretraitement["accents"])
    if config_pretraitement.get("ponctuation"):
        txt = traiter_ponctuation(txt, config_pretraitement["ponctuation"])
    tokens = segmenter_mots(txt)
    if config_pretraitement.get("filtrage"):
        tokens = pipeline_filtrage(tokens, config_pretraitement["filtrage"], langue=langue)
    if config_pretraitement.get("morphologie"):
        tokens = pipeline_morphologique(tokens, config_pretraitement["morphologie"], langue=langue)
        
    return tokens


def vectoriser_requete(texte_pretraite, vocabulaire_direct, methode="tfidf", requete="phrase", **params):
    """
    Description :
        Transforme la requête prétraitée en un vecteur unique
        selon la nature de la requête.
        Assure la compatibilité avec les fonctions de vectorisation du corpus.
    
    Paramètres :
        texte_pretraite     list, liste des tokens de la requête.
        vocabulaire_direct  dict, mapping {mot : index}.
        methode             str, méthode de pondération.
        requete        str, simulateur de structure :
                            - "phrase" : La requête est vue comme une simple phrase.
                            - "document_mots" : La requête est vue comme un document complet.
                            - "document_agrege" : Idem, mais agrégée.
        **params            arguments
    
    Retour :
        numpy.array, le vecteur final représentant la requête.
    """
    if not texte_pretraite:
        return np.zeros(len(vocabulaire_direct))
    if requete == "phrase":
        return vectoriser_phrase(texte_pretraite, vocabulaire_direct, methode, **params)
    document = [texte_pretraite]
    
    if requete == "document_mots":
        return vectoriser_document_mots(document, vocabulaire_direct, methode, **params)
        
    elif requete == "document_agrege":
        strategie = params.get("strategie_agregation", "moyenne")
        return vectoriser_document_agrege(document, vocabulaire_direct, methode, strategie=strategie, **params)
    
    else:
        return vectoriser_phrase(texte_pretraite, vocabulaire_direct, methode, **params)


def test_traitement_requete():
    print("\n Test : Prétraitement et Vectorisation de Requête ")
    requete_brute = "Les chats mangent... !"
    
    # Configuration 
    config = {
        "accents": {"uniformiser": True},         
        "ponctuation": {"supprimer": True},       
        "filtrage": {"stopwords": True, "longueur_min": 2},
        "morphologie": {"stemming": True}         
    }
    tokens = pretraiter_requete(requete_brute, config, langue="fr")
    print(f"  Requête brute : '{requete_brute}'")
    print(f"  Tokens traités : {tokens}")
    assert "chat" in tokens
    assert "!" not in tokens
    assert "les" not in tokens
    
    #2. Test Vectorisation
    vocab = {"chat": 0, "mang": 1, "souris": 2}
    idf_simule = np.array([1.0, 0.5, 2.0]) # chat=1.0, mang=0.5
    
    # Test TF-IDF
    vecteur = vectoriser_requete(
        tokens, vocab, methode="tfidf", requete="phrase", 
        vecteurIdf=idf_simule
    )
    
    print(f"  Vecteur Requête : {vecteur}")
    
    assert vecteur[0] == 0.5
    assert vecteur[1] == 0.25 
    assert vecteur[2] == 0.0  
    vec_vide = vectoriser_requete([], vocab)
    assert np.sum(vec_vide) == 0
    
    print(" Test 'traitement_requete' validé.")
#test_traitement_requete()

# b. Calcul de similarité avec la requête

def calculer_similarite(vect_requete, vect_corpus, mesure='cosinus'):
    """
    Description :
        Fonction routeur qui calcule la similarité ou la distance entre 
        le vecteur de la requête et un vecteur du corpus selon la mesure choisie.
        
    Paramètres :
        vect_requete  numpy.array, le vecteur de la requête.
        vect_corpus   numpy.array, un vecteur issu du corpus.
        mesure        str, le nom de la métrique :
                      'cosinus', 'distance_cosinus', 'euclidienne', 
                      'manhattan', 'jaccard', 'distance_jaccard', etc.
    
    Retour :
        float, le score calculé.
    """
    m = mesure.lower()
    
    if m == 'cosinus':
        return calcul_similarite_cosinus(vect_requete, vect_corpus)
    
    elif m == 'distance_cosinus':
        return calcul_distance_cosinus(vect_requete, vect_corpus)
        
    elif m == 'euclidienne':
        return calcul_distance_euclidienne(vect_requete, vect_corpus)
        
    elif m == 'manhattan':
        return calcul_distance_manhattan(vect_requete, vect_corpus)
        
    elif m == 'jaccard':
        return calcul_similarite_jaccard(vect_requete, vect_corpus)
        
    elif m == 'distance_jaccard':
        return calcul_distance_jaccard(vect_requete, vect_corpus)
        
    elif m == 'hamming':
        return calcul_distance_hamming(vect_requete, vect_corpus)
        
    elif m == 'jensen-shannon':
        return calcul_distance_jensen_shannon(vect_requete, vect_corpus)
        
    else:
        return 0.0


def calculer_scores_requete(vect_requete, vecteur, mesure='cosinus', niveau='document_mots'):
    """
    Description :
        Compare la requête à l'ensemble du corpus vectorisé.
        Gère les structures simples et les structures imbriquées.
    
    Paramètres :
        vect_requete     numpy.array, le vecteur unique de la requête.
        vecteur  dict, le corpus vectorisé.
                         Format : {id : vecteur} ou {id : [vec_ph1, vec_ph2]}.
        mesure           str, la métrique à utiliser.
        niveau           str, indique la structure.
    
    Retour :
        dict, les scores.
              - Si niveau doc : {id : score}
              - Si niveau phrase : {id : [score_ph1, score_ph2, ...]}
    """
    scores = {}
    
    if not vecteur:
        return scores
        
    for id, contenu in vecteur.items():
        if niveau == 'phrase':
            if isinstance(contenu, list):
                score = []
                for vecteur in contenu:
                    val = calculer_similarite(vect_requete, vecteur, mesure)
                    score.append(val)
                scores[id] = score
            else:
                scores[id] = []
        else:
            val = calculer_similarite(vect_requete, contenu, mesure)
            scores[id] = val
            
    return scores


def test_calcul_scores():
    print("\n Test : Calcul des scores de similarité ")
    
    # 1. Configuration des données
    req = np.array([1, 1])
    
    corpus_doc = {
        "d1": np.array([1, 1]),
        "d2": np.array([1, 0])
    }
    
    corpus_phrase = {
        "d3": [np.array([1, 1]), np.array([0, 0])]
    }
    
    #Test 1 : Niveau Document (Cosinus)
    res_doc = calculer_scores_requete(req, corpus_doc, mesure='cosinus', niveau='document_mots')
    print(f"  Scores Doc (Cosinus) : {res_doc}")
    
    assert np.isclose(res_doc["d1"], 1.0)
    assert np.isclose(res_doc["d2"], 0.707, atol=1e-3)
    
    # Test 2 : Niveau Document
    res_dist = calculer_scores_requete(req, corpus_doc, mesure='euclidienne', niveau='document_mots')
    print(f"  Scores Doc (Euclidienne) : {res_dist}")
    
    assert res_dist["d1"] == 0.0
    assert res_dist["d2"] == 1.0
    
    #Test 3 : Niveau Phrase
    res_ph = calculer_scores_requete(req, corpus_phrase, mesure='cosinus', niveau='phrase')
    print(f"  Scores Phrase : {res_ph}")
    assert len(res_ph["d3"]) == 2
    assert np.isclose(res_ph["d3"][0], 1.0)
    assert res_ph["d3"][1] == 0.0          
    
    print(" Test 'calcul_scores' validé.")

#test_calcul_scores()

# c. Classement et affichage des résultats

def extraire_top_k(scores_dict, k=5, niveau="document"):
    """
    Description :
        Sélectionne les k meilleurs éléments classés selon les scores.
        Gère le niveau document et le niveau phrase.
    
    Paramètres :
        scores_dict  dict, sortie de 'calculer_scores_requete'.
        k            int, nombre de résultats à retourner.
        niveau       str, 'document' ou 'phrase'.
    
    Retour :
        list, liste de tuplestriée par score décroissant.
              Pour le niveau phrase : ((id, index_phrase), score).
    """
    if not scores_dict:
        return []

    tries = []
    if niveau.startswith("document"):
        liste = list(scores_dict.items())
        tries = sorted(liste, key=lambda x: x[1], reverse=True)

    elif niveau == "phrase":
        tabScores = []
        for id, scoresPhrases in scores_dict.items():
            if isinstance(scoresPhrases, list):
                for idx, score in enumerate(scoresPhrases):
                    tabScores.append( ((id, idx), score) )
        
        tries = sorted(tabScores, key=lambda x: x[1], reverse=True)

    else:
        return []

    return tries[:k]

def afficher_metadonnees_resultat(id, score, meta_corpus):
    """
    Description :
        Génère une chaîne de caractères contenant les informations 
        essentielles d'un résultat à partir des métadonnées.
    
    Paramètres :
        id          str, identifiant du document.
        score       float, score de pertinence.
        meta_corpus dict, dictionnaire des métadonnées.

    Retour :
        str : Le bloc de texte formaté avec les infos du résultat.
    """
    lignes = []
    
    lignes.append(f"\n Résultat (Score : {score:.4f}) ")
    
    if meta_corpus and id in meta_corpus:
        infos = meta_corpus[id]
        titre = infos.get('titre', id)
        langue = infos.get('langue', 'na')
        source = infos.get('sous_corpus', 'Inconnu')
        chemin = infos.get('chemin', 'N/A')
        
        lignes.append(f"Document : {titre}")
        lignes.append(f"Langue   : {langue}")
        lignes.append(f"Source   : {source}")
        lignes.append(f"Chemin   : {chemin}")
    else:
        lignes.append(f"Document : {id} (Pas de métadonnées disponibles)")
        
    return "\n".join(lignes)


def highlight_mots_pertinents(texte, requete_tokens, vocabulaire):
    """
    Description :
        Met en évidence dans le texte les mots présents dans la requête.
        Utilise des codes ANSI pour la couleur dans la console.
    
    Paramètres :
        texte           list ou str, le contenu du document.
        requete_tokens  list, les tokens de la requête.
        vocabulaire     dict, le vocabulaire.
    
    Retour :
        str, le texte reconstruit avec surlignage.
    """
    if not texte:
        return ""
    motsTexte = texte if isinstance(texte, list) else texte.split()
    motsCles = set(r.lower() for r in requete_tokens)
    
    motsSurlignes = []
    debut = "\033[1;31m" 
    fin = "\033[0m"
    
    for mot in motsTexte:
        motClean = mot.lower().strip(".,!?;:\"")
        
        if motClean in motsCles:
            motsSurlignes.append(f"{debut}{mot}{fin}")
        else:
            motsSurlignes.append(mot)
            
    return " ".join(motsSurlignes)


def afficher_contenu_document(id, corpus_tokens, niveau="document_mots", idPhrase=None, requete_tokens=None):
    """
    Description :
        Génère une chaîne de caractères représentant le contenu textuel 
        du document ou d'une phrase spécifique.
    
    Paramètres :
        id              str, id du document.
        corpus_tokens   dict, le corpus tokenisé {id: [[mot, mot], ...]}.
        niveau          str, le niveau d'affichage ("phrase" ou autre).
        idPhrase        int, index de la phrase (si niveau="phrase").
        requete_tokens  list, pour le surlignage optionnel.

    Retour :
        str : Le contenu formaté.
    """
    if not corpus_tokens or id not in corpus_tokens:
        return "(Contenu non disponible)"

    doc = corpus_tokens[id]
    lignes = [] 
    if niveau == "phrase" and idPhrase is not None:
        if 0 <= idPhrase < len(doc):
            phraseTokens = doc[idPhrase]
            if requete_tokens:
                texte = highlight_mots_pertinents(phraseTokens, requete_tokens, {})
            else:
                texte = " ".join(phraseTokens)
            
            lignes.append(f"Extrait (Phrase {idPhrase}) : \"{texte}\"")
        else:
            lignes.append("(Phrase introuvable)")
            
    else:
        lignes.append("Contenu :")
        nb_max = 5
        for i, phraseTokens in enumerate(doc):
            if i >= nb_max:
                lignes.append("...")
                break
                
            if requete_tokens:
                texte = highlight_mots_pertinents(phraseTokens, requete_tokens, {})
            else:
                texte = " ".join(phraseTokens)
            
            lignes.append(f"  - {texte}")

    return "\n".join(lignes)

def afficher_resultat_complet(identifiant, score, corpus_tokens, meta_corpus, niveau, requete_tokens=None, afficher_texte=True):
    """
    Description :
        Orchestrateur qui génère la chaîne de caractères complète pour un résultat unique.
        Combine les métadonnées et le contenu.
    
    Retour :
        str : Le texte complet du résultat.
    """
    # Gestion de l'identifiant (cas phrase ou document entier)
    if isinstance(identifiant, tuple):
        id, idPh = identifiant
    else:
        id = identifiant
        idPh = None
    
    res = []

    meta_str = afficher_metadonnees_resultat(id, score, meta_corpus)
    res.append(meta_str)
    
    if afficher_texte:
        contenu_str = afficher_contenu_document(id, corpus_tokens, niveau, idPh, requete_tokens)
        res.append(contenu_str)

    return "\n".join(res)

def afficher_resultats_top_k(tries, corpus_tokens, meta_corpus, niveau, requete_tokens=None):
    """
    Description :
        Génère une chaîne de caractères contenant tous les k meilleurs résultats.
    
    Retour :
        str : Le rapport complet de la recherche.
    """
    if not tries:
        return "Aucun résultat trouvé."
        
    lignes = []
    
    lignes.append(f"\n --- {len(tries)} résultats trouvés --- ")
    
    for identifiant, score in tries:
        texte = afficher_resultat_complet(
            identifiant, score, corpus_tokens, meta_corpus, 
            niveau, requete_tokens, afficher_texte=True
        )
        lignes.append(texte)
        
        lignes.append("-" * 40)

    return "\n".join(lignes)

def test_affichage_resultats():
    print("\n Test : Module d'Affichage et Classement ")
    #Setup
    scores_doc = {"d1": 0.5, "d2": 0.9, "d3": 0.1}
    scores_phrase = {"d1": [0.1, 0.8], "d2": [0.3]}
    
    # 2. Test extraire_top_k
    top_doc = extraire_top_k(scores_doc, k=2, niveau="document_mots")
    assert len(top_doc) == 2
    assert top_doc[0][0] == "d2" 
    
    top_phrase = extraire_top_k(scores_phrase, k=2, niveau="phrase")
    assert top_phrase[0][1] == 0.8
    assert top_phrase[0][0] == ("d1", 1)
    
    # 3. Test highlight
    txt = ["le", "chat", "mange"]
    req = ["chat"]
    hl = highlight_mots_pertinents(txt, req, {})
    assert "\033" in hl or "**" in hl or "chat" in hl
    print(f"  Test Highlight : {hl}")

    print(" Test 'affichage_resultats' validé.")

#test_affichage_resultats()

# 4. Évaluation et visualisation

# a. Analyse des Top-k résultats

def filtrer_par_score(top_k, seuil=0.5):
    """
    Description :
        Filtre la liste des résultats pour ne garder que ceux ayant
        une pertinence supérieure ou égale au seuil.
    
    Paramètres :
        top_k  list, liste de tuples .
        seuil  float, score minimum accepté.
    
    Retour :
        list, la sous-liste filtrée.
    """
    if not top_k:
        return []
    res = []
    for element in top_k:
        score = element[1]
        
        if score >= seuil:
            res.append(element)
            
    return res


def resume_top_k(top_k, meta_corpus):
    """
    Description :
        Génère une liste de dictionnaires récapitulatifs des résultats.
        Croise les scores avec les métadonnées (Langue, Source, etc.).
    
    Paramètres :
        top_k        list, liste de tuples (identifiant, score).
        meta_corpus  dict, dictionnaire des métadonnées {id : {infos...}}.
    
    Retour :
        list, une liste de dictionnaires enrichis contenant rang, score, titre, etc.
    """
    resume = []
    
    if not top_k:
        return resume
        
    rang = 1
    for couple in top_k:
        identifiant = couple[0]
        score = couple[1]
        
        if isinstance(identifiant, tuple):
            id = identifiant[0]
            suffixe = f" (Ph. {identifiant[1]})"
        else:
            id = identifiant
            suffixe = ""
            
        if meta_corpus and id in meta_corpus:
            meta = meta_corpus[id]
            langue = meta.get('langue', 'N/A')
            source = meta.get('sous_corpus', 'Inconnu')
            titre = meta.get('titre', str(id))
        else:
            langue = 'N/A'
            source = 'Inconnu'
            titre = str(id)
        
        info = {
            'rang': rang,
            'score': score,
            'id': id,
            'langue': langue,
            'source': source,
            'detail': suffixe.strip(),
            'titre_complet': f"{titre}{suffixe}"
        }
        resume.append(info)
        rang += 1
        
    return resume


def test_evaluation_resultats():
    print("\n Test : Module d'Évaluation")
    
    # Données 
    resultats = [
        ("doc1", 0.95),
        ("doc2", 0.80),
        ("doc3", 0.40), 
        (("doc4", 2), 0.90)
    ]
    
    # Métadonnées
    meta = {
        "doc1": {"langue": "fr", "sous_corpus": "Biologie", "titre": "Cellules"},
        "doc2": {"langue": "en", "sous_corpus": "Informatique", "titre": "Python"},
        "doc3": {"langue": "fr", "sous_corpus": "Histoire", "titre": "Rois"},
        "doc4": {"langue": "en", "sous_corpus": "News", "titre": "Times"}
    }
    
    # 1. Test Filtrage
    filtres = filtrer_par_score(resultats, seuil=0.5)
    
    print(f"  Avant filtre : {len(resultats)} -> Après : {len(filtres)}")
    
    assert len(filtres) == 3
    
    # Vérification explicite
    ids_restants = []
    for r in filtres:
        if isinstance(r[0], tuple):
            ids_restants.append(r[0][0])
        else:
            ids_restants.append(r[0])
            
    assert "doc3" not in ids_restants
    
    # 2. Test Résumé
    tableau = resume_top_k(filtres, meta)
    
    print(f"\n{'Rg':<3} | {'Score':<6} | {'Lang':<4} | {'Source':<15} | {'Document'}")
    print("-" * 60)
    for ligne in tableau:
        print(f"{ligne['rang']:<3} | {ligne['score']:<6.4f} | {ligne['langue']:<4} | {ligne['source']:<15.15} | {ligne['titre_complet']}")

    assert len(tableau) == 3
    assert tableau[0]['id'] == "doc1"
    assert tableau[0]['source'] == "Biologie"
    assert tableau[2]['id'] == "doc4"
    assert "(Ph. 2)" in tableau[2]['detail']
    
    print("\n Test 'evaluation_resultats' validé.")

#test_evaluation_resultats()

# b. Distribution des scores

def distribution_scores(scores, titre="Distribution des scores"):
    """
    Description :
        Génère un histogramme pour visualiser la répartition des scores.
        
    Paramètres :
        scores  list ou np.array, la liste des scores de similarité.
        titre   str, le titre du graphique.
        
    Retour :
        matplotlib.figure.Figure, la figure générée.
    """
    if not scores or len(scores) == 0:
        return None

    fig = plt.figure(figsize=(8, 5))
    
    plt.hist(scores, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    
    plt.title(titre)
    plt.xlabel("Score de similarité")
    plt.ylabel("Nombre de documents")
    plt.grid(axis='y', alpha=0.5)
    
    plt.tight_layout()
    return fig


def stats_scores(scores):
    """
    Description :
        Calcule les indicateurs statistiques d'une liste de scores.
    
    Paramètres :
        scores  list ou np.array.
    
    Retour :
        dict, contient min, max, moyenne, mediane, q1, q3, ecartType.
    """
    statistiques = {}
    
    if not scores or len(scores) == 0:
        return statistiques
        
    data = np.array(scores, dtype=float)
    
    statistiques["min"] = np.min(data)
    statistiques["max"] = np.max(data)
    statistiques["moyenne"] = np.mean(data)
    statistiques["mediane"] = np.median(data)
    statistiques["ecartType"] = np.std(data)
    statistiques["q1"] = np.percentile(data, 25)
    statistiques["q3"] = np.percentile(data, 75)
    
    return statistiques


def normaliser_scores(scores, methode='minmax'):
    """
    Description :
        Normalise une liste de scores.
    
    Paramètres :
        scores   list, les scores bruts.
        methode  str, 'minmax'  ou 'zscore'.
    
    Retour :
        list, les scores normalisés.
    """
    if not scores:
        return []
        
    data = np.array(scores, dtype=float)
    resultat = []
    
    if methode == 'minmax':
        mini = np.min(data)
        maxi = np.max(data)
        ecart = maxi - mini
        
        if ecart == 0:
            for _ in scores:
                resultat.append(0.0)
        else:
            for x in data:
                norme = (x - mini) / ecart
                resultat.append(norme)
                
    elif methode == 'zscore':
        moyenne = np.mean(data)
        ecartType = np.std(data)
        
        if ecartType == 0:
            for _ in scores:
                resultat.append(0.0)
        else:
            for x in data:
                norme = (x - moyenne) / ecartType
                resultat.append(norme)
    
    else:
        for x in data:
            resultat.append(x)
            
    return resultat


def comparer_distributions_requetes(scores_requetes):
    """
    Description :
        Génère un graphique comparatif des distributions de scores.
    
    Paramètres :
        scores_requetes  dict, { "Nom Requete" : [lscores], ... }
        
    Retour :
        matplotlib.figure.Figure, la figure générée.
    """
    if not scores_requetes:
        return None

    donnees = []
    etiquettes = []
    
    for nom, scores in scores_requetes.items():
        if scores and len(scores) > 0:
            donnees.append(scores)
            etiquettes.append(nom)
            
    if not donnees:
        return None

    fig = plt.figure(figsize=(10, 6))
    plt.boxplot(donnees, labels=etiquettes, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', color='black'),
                medianprops=dict(color='red'))
                
    plt.title("Comparaison des distributions de scores par requête")
    plt.ylabel("Score")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def test_distribution_scores():
    print("\n Test : Module de Distribution et Statistiques des Scores ")
    
    # 1. Données
    scores_a = [0.1, 0.2, 0.15, 0.9, 0.85, 0.1, 0.05, 0.8]
    scores_b = [0.45, 0.5, 0.55, 0.48, 0.52, 0.49]
    
    # 2. Test Statistiques
    stats_a = stats_scores(scores_a)
    print("  Stats Requête A :")
    print(f"    Min: {stats_a['min']:.2f}, Max: {stats_a['max']:.2f}")
    
    assert stats_a['max'] == 0.9
    
    # 3. Test Graphiques
    
    # Histogramme
    fig1 = distribution_scores(scores_a, titre="Test Histo")
    if fig1:
        print("  Graphique 1 (Histogramme) généré avec succès.")
        plt.close(fig1)
    else:
        print("  Erreur Graphique 1")

    # Comparaison
    donnees_comp = {"Req A": scores_a, "Req B": scores_b}
    fig2 = comparer_distributions_requetes(donnees_comp)
    if fig2:
        print("  Graphique 2 (Boxplot) généré avec succès.")
        plt.close(fig2)
    else:
        print("  Erreur Graphique 2")
    
    print(" Test 'distribution_scores' terminé.")

#test_distribution_scores()

# c. Répartition par sous-corpus et langue

def analyse_sous_corpus(top_k, meta_corpus):
    """
    Description :
        Compte le nombre de résultats provenant de chaque sous-corpus.
    
    Paramètres :
        top_k        list, liste des résultats [(id, score), ...].
        meta_corpus  dict, métadonnées {id : {sous_corpus: ...}}.
    
    Retour :
        dict, {nom_sous_corpus : nombre_occurrences}.
    """
    compteur = {}
    
    if not top_k:
        return compteur
        
    for item in top_k:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            id = identifiant[0]
        else:
            id = identifiant
            
        source = "Inconnu"
        if meta_corpus and id in meta_corpus:
            info = meta_corpus[id]
            source = info.get("sous_corpus", "Inconnu")
            
        if source in compteur:
            compteur[source] += 1
        else:
            compteur[source] = 1
            
    return compteur


def repartition_pourcentage(top_k, meta_corpus):
    """
    Description :
        Calcule la proportion (en %) des résultats par langue et sous-corpus.
    
    Paramètres :
        top_k        list, les résultats.
        meta_corpus  dict, les métadonnées.
    
    Retour :
        dict, { "sous_corpus": {source: pct}, "langue": {langue: pct} }.
    """
    res = {"sous_corpus": {}, "langue": {}}
    
    nb = len(top_k)
    if nb == 0:
        return res
        
    nbSource = {}
    nbLangue = {}
    
    for item in top_k:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            id = identifiant[0]
        else:
            id = identifiant
            
        src = "Inconnu"
        lng = "na"
        
        if meta_corpus and id in meta_corpus:
            info = meta_corpus[id]
            src = info.get("sous_corpus", "Inconnu")
            lng = info.get("langue", "na")
            
        if src in nbSource:
            nbSource[src] += 1
        else:
            nbSource[src] = 1
            
        if lng in nbLangue:
            nbLangue[lng] += 1
        else:
            nbLangue[lng] = 1
    for k, v in nbSource.items():
        pct = (v / nb) * 100
        res["sous_corpus"][k] = round(pct, 2)
        
    for k, v in nbLangue.items():
        pct = (v / nb) * 100
        res["langue"][k] = round(pct, 2)
        
    return res


def afficher_repartition_barplot(repartition, titre="Répartition des résultats"):
    """
    Description :
        Génère un diagramme en barres des répartitions.
    
    Paramètres :
        repartition  dict, sortie de repartition_pourcentage.
        titre        str.
    
    Retour :
        matplotlib.figure.Figure.
    """
    if not repartition:
        return None
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    data = repartition.get("sous_corpus", {})
    if data:
        noms = list(data.keys())
        vals = list(data.values())
        ax1.bar(noms, vals, color="skyblue")
        ax1.set_title("Par Sous-Corpus (%)")
        ax1.set_ylabel("%")
        ax1.tick_params(axis='x', rotation=45)
    
    lng = repartition.get("langue", {})
    if lng:
        noms = list(lng.keys())
        vals = list(lng.values())
        ax2.bar(noms, vals, color="lightgreen")
        ax2.set_title("Par Langue (%)")
    
    plt.suptitle(titre)
    plt.tight_layout()
    return fig


def filtrer_top_k_par_categorie(top_k, meta_corpus, categorie="langue", valeur="fr"):
    """
    Description :
        Filtre les résultats pour ne garder que ceux correspondant à un critère.
        Ex: garder seulement les résultats en français.
    
    Paramètres :
        top_k        list, résultats.
        meta_corpus  dict.
        categorie    str, "langue" ou "sous_corpus".
        valeur       str, la valeur attendue.
    
    Retour :
        list, sous-liste filtrée.
    """
    res = []
    if not top_k:
        return res
        
    for item in top_k:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            id = identifiant[0]
        else:
            id = identifiant
            
        if meta_corpus and id in meta_corpus:
            info = meta_corpus[id]
            donnee = info.get(categorie)
            if donnee == valeur:
                res.append(item)
                
    return res


def test_analyse_repartition():
    print("\n Test : 4.c Analyse Répartition (Sous-Corpus et Langue) ")
    
    # Données simulées
    # Top-K fictif
    top_k = [("d1", 0.9), ("d2", 0.8), ("d3", 0.7), ("d4", 0.6)]
    
    # Métadonnées
    meta = {
        "d1": {"sous_corpus": "Sport", "langue": "fr"},
        "d2": {"sous_corpus": "Sport", "langue": "en"},
        "d3": {"sous_corpus": "Politique", "langue": "fr"},
        "d4": {"sous_corpus": "Politique", "langue": "fr"}
    }
    
    # 1. Test Analyse brute
    comptes = analyse_sous_corpus(top_k, meta)
    assert comptes["Sport"] == 2
    assert comptes["Politique"] == 2
    
    # 2. Test Pourcentages
    rep = repartition_pourcentage(top_k, meta)
    print(f"  Répartition : {rep}")
    assert rep["sous_corpus"]["Sport"] == 50.0
    assert rep["langue"]["fr"] == 75.0
    
    # 3. Test Graphique
    fig_rep = afficher_repartition_barplot(rep)
    if fig_rep:
        plt.close(fig_rep)
        print("  Graphique Répartition généré.")
    else:
        print("  Erreur Graphique Répartition.")
    
    # 4. Test Filtrage
    resEn = filtrer_top_k_par_categorie(top_k, meta, "langue", "en")
    assert len(resEn) == 1
    assert resEn[0][0] == "d2"
    
    print(" Test 4.c analyse_repartition validé.")

#test_analyse_repartition()


# 5. Expérimentations exploratoires
# a. Prétraitement globals du corpus pour l'expérimentation exploratoire

def pretraiter_corpus(corpus, config_pretraitement):
    """
    Description :
        Applique le prétraitement sur l'ensemble du corpus selon une configuration donnée.
        Cette fonction garantit que tous les documents subissent exactement les mêmes
        transformations (nettoyage, stop-words, normalisation) avant les expériences.
    
    Paramètres :
        corpus               dict, le corpus initial {id : liste de listes de tokens}.
        config_pretraitement dict, dictionnaire contenant les paramètres :
                             - 'langue'
                             - 'stopwords' 
                             - 'stemming' 
                             - 'lemmatisation' 
                             - 'non_alphabetiques' 
                             - 'longueur_min' 
    
    Retour :
        dict, le corpus prétraité conservant la structure initiale {id : [[tokens...]]}.
    """
    langue = config_pretraitement.get("langue", "fr")
    res = pipeline_pretraitement(corpus, config_pretraitement, langue=langue)
    
    return res


def test_pretraiter_corpus():
    print("\n Test : 5.a Prétraitement globals du corpus ")
    
    # 1. Configuration du corpus de test
    corpus_test = {
        "doc1": [["Le", "chat", "mange", "la", "souris", "."]],
        "doc2": [["123", "chats", "jouent", "!"]]
    }
    
    # 2. Définition d'une configuration de test
    config = {
        "langue": "fr",
        "stopwords": True,          
        "non_alphabetiques": True,  
        "stemming": True,           
        "longueur_min": 2           
    }
    res = pretraiter_corpus(corpus_test, config)
    print(f"  Corpus Original : {corpus_test}")
    print(f"  Corpus Traité   : {res}")
    
    # Analyse Doc 1
    tokens_d1 = res["doc1"][0]
    assert "Le" not in tokens_d1 and "le" not in tokens_d1
    assert "." not in tokens_d1
    assert len(tokens_d1) > 0
    
    # Analyse Doc 2
    tokens_d2 = res["doc2"][0]
    assert "123" not in tokens_d2
    assert "!" not in tokens_d2
    assert "chat" in tokens_d2
    print(" Test 5.a 'pretraiter_corpus' validé.")

#test_pretraiter_corpus()


# b. Impact des 5 configurations de prétraitement

def tester_pretraitements(requete, corpus, configs):
    """
    Description :
        Teste différentes configurations de prétraitement sur le même corpus et la même requête.
        Pour chaque config : 
        1. Prétraite le corpus et la requête.
        2. Reconstruit le vocabulaire.
        3. Vectorise et lance la recherche.
        4. Retourne les métriques.
    
    Paramètres :
        requete  str, la requête utilisateur brute.
        corpus   dict, le corpus brut {id : [[tokens]]}.
        configs  dict, dictionnaire de configurations {nom : parametres}.
    
    Retour :
        dict, résultats par configuration {nom : {vocab_len, top_k}}.
    """
    resultats = {}
    
    for nom, params in configs.items():
        nettoyer = pretraiter_corpus(corpus, params)
        
        lvocab = construire_vocabulaire(nettoyer)
        dvocab, _ = construire_dictionnaire_vocabulaire(lvocab)
        
        idf = calcul_idf(nettoyer, dvocab, methode="smooth")
        
        matrice = vectoriser_corpus(
            nettoyer, 
            dvocab, 
            methode="tfidf", 
            niveau="document_mots", 
            idf=idf
        )
        req = pretraiter_requete(requete, {"filtrage": params, "morphologie": params})
        
        requete = vectoriser_requete(
            req, 
            dvocab, 
            methode="tfidf", 
            requete="phrase", 
            idf=idf
        )
        
        scores = calculer_scores_requete(requete, matrice, mesure="cosinus")
        top = extraire_top_k(scores, k=3, niveau="document")
        
        resultats[nom] = {
            "tailleVocabulaire": len(lvocab),
            "topResultats": top
        }
        
    return resultats


def test_tester_pretraitements():
    print("\n Test : 5.b Comparaison des configurations de prétraitement ")
    
    # Données : Corpus brut
    corpus = {
        "d1": [["Les", "Chats", "aiment", "les", "souris", "."]],
        "d2": [["Le", "chien", "aboie", "!!!", "123"]]
    }
    requete = "le chat"
    
    # Définition des 5 configurations
    configs = {
        "A (Brut)": {
            "stopwords": False, "longueur_min": 0, "non_alphabetiques": False, 
            "stemming": False, "lemmatisation": False
        },
        "B (Filtres)": {
            "stopwords": True, "longueur_min": 2, "non_alphabetiques": True, 
            "stemming": False, "lemmatisation": False
        },
        "D (Stemming)": {
            "stopwords": True, "longueur_min": 2, "non_alphabetiques": True, 
            "stemming": True, "lemmatisation": False
        }
    }
    
    res = tester_pretraitements(requete, corpus, configs)
    vocab_a = res["A (Brut)"]["tailleVocabulaire"]
    vocab_b = res["B (Filtres)"]["tailleVocabulaire"]
    top_d = res["D (Stemming)"]["topResultats"]
    
    print(f"  Vocab A: {vocab_a}, Vocab B: {vocab_b}")
    print(f"  Top D (Stemming) : {top_d}")
    assert vocab_b < vocab_a
    if top_d:
        assert top_d[0][0] == "d1"
        
    print(" Test 5.b 'tester_pretraitements' validé.")

#test_tester_pretraitements()


# c. Impact du type de représentation

def tester_descripteurs(requete_traitee, corpus_traite, vocabulaire_direct, descripteurs):
    """
    Description :
        Compare les résultats de recherche pour différents descripteurs vectoriels
        sur un corpus DÉJÀ prétraité.
    
    Paramètres :
        requete_traitee     list, tokens de la requête.
        corpus_traite       dict, le corpus.
        vocabulaire_direct  dict, mapping {mot: index}.
        descripteurs        list, liste des méthodes à tester ['count', 'tf', 'tfidf', 'bm25'].
    
    Retour :
        dict, {methode : top_k_resultats}.
    """
    resultats = {}
    
    idf = calcul_idf(corpus_traite, vocabulaire_direct, methode="smooth")
    
    bm25 = {"idf": idf, "k1": 1.5, "b": 0.75}
    
    total = 0
    nb = len(corpus_traite)
    for doc in corpus_traite.values():
        for phrase in doc:
            total += len(phrase)
    avgdl = total / nb if nb > 0 else 1
    bm25["avgdl"] = avgdl

    for methode in descripteurs:
        params = {}
        if methode == "tfidf":
            params["idf"] = idf
        elif methode == "bm25":
            params = bm25
            
        matrice = vectoriser_corpus(
            corpus_traite, 
            vocabulaire_direct, 
            methode=methode, 
            niveau="document_mots", 
            **params
        )
        
        req = vectoriser_requete(
            requete_traitee, 
            vocabulaire_direct, 
            methode=methode, 
            **params
        )
        scores = calculer_scores_requete(req, matrice, mesure="cosinus")
        top = extraire_top_k(scores, k=3)
        resultats[methode] = top
        
    return resultats


def test_tester_descripteurs():
    print("\n Test : 5.c Comparaison des descripteurs (BoW, TF-IDF, BM25) ")
    
    # Configuration : Corpus propre
    nettoyer = {
        "d1": [["chat"]],
        "d2": [["chat", "chat"]],
        "d3": [["chien"]]
    }
    req_clean = ["chat"]
    
    # Construction vocabulaire
    vocab = ["chat", "chien"]
    dico, _ = construire_dictionnaire_vocabulaire(vocab)
    
    methodes = ["count", "tf", "tfidf", "bm25"]
    
    res = tester_descripteurs(req_clean, nettoyer, dico, methodes)
    
    # Vérifications
    print(f"  Résultats Count : {res['count']}")
    print(f"  Résultats TF    : {res['tf']}")

    assert "count" in res
    assert len(res["count"]) > 0
    top_doc_d3 = [x for x in res["count"] if x[0] == "d3"]
    if top_doc_d3:
        assert top_doc_d3[0][1] == 0.0
        
    print(" Test 5.c tester_descripteurs validé.")

#test_tester_descripteurs()

# d. Impact des n-grammes

def tester_ngrams(requete, corpus, n_list, vocabulaire_direct=None):
    """
    Description :
        Teste l'impact de la taille des n-grammes.
        sur les résultats de recherche.
    
    Paramètres :
        requete     str, la requête brute.
        corpus      dict, le corpus prétraité {id : [[tokens]]}.
        n_list      list, liste des tailles à tester.
        vocabulaire_direct dict, optionnel.
    
    Retour :
        dict, { n : top_k_resultats }.
    """
    resultats = {}
    if isinstance(requete, str):
        req = requete.split()
    else:
        req = requete

    for n in n_list:
        ngrams = {}
        for id, doc in corpus.items():
            lngrams = []
            for phrase in doc:
                ngs = generer_ngrammes(phrase, n, niveau='phrase')
                lngrams.extend(ngs)
            ngrams[id] = [lngrams]
        tngrams = set()
        for docNg in ngrams.values():
            for phrase in docNg:
                tngrams.update(phrase)
        
        voc = sorted(list(tngrams))
        dico, _ = construire_dictionnaire_ngrammes(voc)
        
        if not dico:
            resultats[n] = []
            continue

        idf = calcul_idf(ngrams, dico, methode="smooth")
        vecteur = {}
        for id, doc in corpus.items():
            tokens = [mot for phrase in doc for mot in phrase]
            vec = encoder_tfidf_ngrammes(tokens, n, voc, dico, idf)
            vecteur[id] = vec
            
        vec = encoder_tfidf_ngrammes(req, n, voc, dico, idf)
        scores = calculer_scores_requete(vec, vecteur, mesure="cosinus")
        top = extraire_top_k(scores, k=3)
        
        resultats[n] = top
        
    return resultats


def test_tester_ngrams():
    print("\n Test : 5.d Impact des N-grammes ")
    
    # Corpus :
    corpus = {
        "d1": [["j'aime", "la", "pomme", "rouge"]],
        "d2": [["une", "pomme", "verte", "et", "un", "ballon", "rouge"]]
    }
    requete = "pomme rouge"
    res = tester_ngrams(requete, corpus, n_list=[1, 2])
    
    # Analyse N=1
    top_n1 = res[1]
    print(f"  N=1 (Mots isolés) : {top_n1}")
    
    # Analyse N=2
    top_n2 = res[2]
    print(f"  N=2 (Expressions) : {top_n2}")
    if top_n2:
        assert top_n2[0][0] == "d1"
        score_d2 = next((item[1] for item in top_n2 if item[0] == "d2"), 0.0)
        assert score_d2 == 0.0
        
    print(" Test 5.d 'tester_ngrams' validé.")

#test_tester_ngrams()


# e. Impact de la métrique de similarité

def comparer_distances(vecteur, mesures=['cosinus', 'euclidienne', 'manhattan', 'jaccard']):
    """
    Description :
        Compare différentes mesures de similarité sur le même corpus vectorisé.
        Calcule la matrice de similarité pour chaque mesure et extrait les paires les plus proches.
        Permet d'observer comment la métrique influence le regroupement des documents.
    
    Paramètres :
        vecteur dict, {id : vecteur}.
        mesures         list, liste des métriques à tester.
    
    Retour :
        dict, {nom_mesure : liste_top_paires}.
    """
    resultats = {}
    
    if not vecteur:
        return resultats
        
    for mesure in mesures:
        matrice, labels = matrice_similarite(vecteur, mesure=mesure)
        tri = "max"
        if "distance" in mesure or mesure in ["euclidienne", "manhattan", "hamming"]:
            tri = "min"
            
        paire = top_paires_similaires(matrice, labels, top=3, tri=tri)
        
        resultats[mesure] = paire
        
    return resultats


def test_comparer_distances():
    print("\n Test : 5.e Impact de la métrique de similarité ")
    
    corpus_vec = {
        "d1": np.array([1, 1]),
        "d2": np.array([10, 10]),
        "d3": np.array([1.1, 1.1])
    }
    
    mesures = ["cosinus", "euclidienne"]
    res = comparer_distances(corpus_vec, mesures)
    top_cos = res["cosinus"]
    print(f"  Cosinus (Direction) : {top_cos}")
    score_d1_d2 = 0.0
    for paire, score in top_cos:
        if set(paire) == {"d1", "d2"}:
            score_d1_d2 = score
    assert np.isclose(score_d1_d2, 1.0)
    top_eucl = res["euclidienne"]
    print(f"  Euclidienne (Proximité) : {top_eucl}")
    
    meilleure_paire_eucl = top_eucl[0][0]
    assert set(meilleure_paire_eucl) == {"d1", "d3"}
    
    print(" Test 5.e 'comparer_distances' validé.")

#test_comparer_distances()

# f. Échelle de la recherche cas requête phrase vs requête document

def comparer_echelle_requete(requete_tokens, corpus_vecteurs, vocabulaire_direct, 
                             methode="tfidf", requete='phrase', 
                             niveau_corpus='document_agrege', 
                             mesures=None, top_k=5, **params):
    """
    Description :
        Compare les résultats de recherche en faisant varier l'échelle de la requête
        et la métrique de similarité.
        Permet d'observer si une requête longue donne de meilleurs
        résultats qu'une requête courte sur un corpus donné.
    
    Paramètres :
        requete_tokens     list, la requête sous forme de liste de tokens.
        corpus_vecteurs    dict, le corpus déjà vectorisé correspondant au niveau_corpus choisi.
        vocabulaire_direct dict, mapping {mot: index}.
        methode            str, méthode de vectorisation pour la requête.
        requete       str, 'phrase' ou 'document_mots'/'document_agrege'.
        niveau_corpus      str, structure du corpus .
        mesures            list, liste des métriques à tester.
        top_k              int, nombre de résultats à extraire.
        **params           arguments supplémentaires.
    
    Retour :
        dict, { nom_mesure : liste_top_k_resultats }.
    """
    resultats = {}
    
    if mesures is None:
        mesures = ['cosinus']
        
    vecteur = vectoriser_requete(
        requete_tokens, 
        vocabulaire_direct, 
        methode=methode, 
        requete=requete, 
        **params
    )
    
    for mesure in mesures:
        scores = calculer_scores_requete(
            vecteur, 
            corpus_vecteurs, 
            mesure=mesure, 
            niveau=niveau_corpus
        )
        meilleurs = extraire_top_k(scores, k=top_k, niveau=niveau_corpus)
        
        resultats[mesure] = meilleurs
        
    return resultats


def test_comparer_echelle_requete():
    print("\n Test : 5.f Échelle de la recherche")
    
    # Configuration
    vocab = {"chat": 0, "dort": 1, "mange": 2}
    
    # Corpus vectorisé 
    corpus_vec_doc = {
        "d1": np.array([0.5, 0.5, 0.0]),
        "d2": np.array([0.5, 0.0, 0.5])
    }
    params = {} 
    
    # Scénario 1 : Requête courte
    req_courte = ["chat"]
    
    res_courte = comparer_echelle_requete(
        req_courte, corpus_vec_doc, vocab, 
        methode="tf", 
        requete="phrase", 
        niveau_corpus="document_agrege",
        mesures=["cosinus"]
    )
    
    print(f"  Résultats Requête Courte ('chat') : {res_courte['cosinus']}")
    
    # Analyse
    assert len(res_courte['cosinus']) == 2
    
    # Scénario 2 : Requête longue
    req_longue = ["chat", "dort"]
    
    res_longue = comparer_echelle_requete(
        req_longue, corpus_vec_doc, vocab, 
        methode="tf", 
        requete="document_mots",
        niveau_corpus="document_agrege",
        mesures=["cosinus", "euclidienne"]
    )
    
    print(f"  Résultats Requête Longue ('chat dort') : {res_longue['cosinus']}")
    
    # Analyse
    top_doc = res_longue['cosinus'][0]
    assert top_doc[0] == "d1"
    assert np.isclose(top_doc[1], 1.0)
    
    # Vérification Euclidienne
    top_eucl = res_longue['euclidienne'][0]
    assert top_eucl[0] == "d1"
    assert np.isclose(top_eucl[1], 0.0)
    
    print(" Test 5.f 'comparer_echelle_requete' validé.")

#test_comparer_echelle_requete()

# g. Impact de la langue

# i. Comparaison des résultats entre langues 

def top_k_mono_langue(requete_tokens, corpus_vecteurs, vocabulaire_direct, 
                      methode="tfidf", niveau_corpus='document_mots', 
                      mesure='cosinus', top_k=5, **params):
    """
    Description :
        Effectue une recherche monolingue complète : vectorisation de la requête
        puis calcul des scores sur un corpus donné.
    
    Paramètres :
        requete_tokens      list, tokens de la requête.
        corpus_vecteurs     dict, le corpus vectorisé dans la langue cible.
        vocabulaire_direct  dict, vocabulaire de la langue cible.
        methode             str, méthode de vectorisation (tfidf, bm25...).
        niveau_corpus       str, 'phrase', 'document_mots', etc.
        mesure              str, métrique de similarité.
        top_k               int, nombre de résultats.
        **params            arguments (vecteur_idf, etc.).
    
    Retour :
        list, liste des résultats triés [(id, score), ...].
    """
    vecteur = vectoriser_requete(
        requete_tokens, 
        vocabulaire_direct, 
        methode=methode,
        requete="phrase",
        **params
    )
    
    scores = calculer_scores_requete(
        vecteur, 
        corpus_vecteurs, 
        mesure=mesure, 
        niveau=niveau_corpus
    )
    resultats = extraire_top_k(scores, k=top_k, niveau=niveau_corpus)
    
    return resultats


def comparer_top_k_langues(topFr, topEn):
    """
    Description :
        Compare les résultats obtenus pour une requête française et sa traduction anglaise.
        Tente d'identifier les documents communs
    
    Paramètres :
        topFr  list, résultats [(id_fr, score), ...].
        topEn  list, résultats [(id_en, score), ...].
    
    Retour :
        dict, statistiques de comparaison.
    """
    stats = {
        "nbFr": len(topFr),
        "nbEn": len(topEn),
        "intersection": 0,
        "communs": []
    }
    
    fr = set()
    for item in topFr:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            identifiant = identifiant[0]
        base = identifiant.split('_')[0]
        fr.add(base)
        
    base = set()
    for item in topEn:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            identifiant = identifiant[0]
            
        base = identifiant.split('_')[0]
        base.add(base)

    communs = fr.intersection(base)
    stats["intersection"] = len(communs)
    stats["communs"] = list(communs)
    
    return stats

def test_comparaison_mono_langue():
    print("\n Test : Comparaison Mono-langue (FR vs EN) ")
    
    # Configuration
    v_fr = {"chat": 0, "mange": 1}
    v_en = {"cat": 0, "eats": 1}
    
    # Corpus Vectorisés (Simulés)
    c_vec_fr = {"d1_fr": np.array([1.0, 0.0])}
    c_vec_en = {"d1_en": np.array([1.0, 0.0])}
    
    # Paramètres simulés
    p_fr = {"vecteur_idf": np.array([1.0, 1.0])}
    p_en = {"vecteur_idf": np.array([1.0, 1.0])}
    
    # Action 1 : Recherche FR
    req_fr = ["chat"]
    res_fr = top_k_mono_langue(
        req_fr, c_vec_fr, v_fr, 
        methode="tfidf", niveau_corpus='document_mots',
        **p_fr
    )
    
    # Action 2 : Recherche EN
    req_en = ["cat"]
    res_en = top_k_mono_langue(
        req_en, c_vec_en, v_en, 
        methode="tfidf", niveau_corpus='document_mots',
        **p_en
    )
    
    # Action 3 : Comparaison
    comp = comparer_top_k_langues(res_fr, res_en)
    
    print(f"  Résultat FR : {res_fr}")
    print(f"  Résultat EN : {res_en}")
    print(f"  Comparaison : {comp}")
    
    # Vérifications
    assert res_fr[0][0] == "d1_fr"
    assert res_en[0][0] == "d1_en"
    assert comp["intersection"] == 1
    assert "d1" in comp["ids_communs"]
    
    print(" Test 'comparaison_mono_langue' validé.")

#test_comparaison_mono_langue()

# ii. Recherche combinée par fusion des top-k

def recherche_multilingue_fusion(requete_fr, requete_en, 
                                 corpus_vect_fr, corpus_vect_en,
                                 vocab_fr, vocab_en,
                                 params_fr, params_en,
                                 methode="tfidf", top_k=5):
    """
    Description :
        Effectue une recherche parallèleet fusionne les résultats
        pour obtenir un classement globals unifié.
        Stratégie de fusion : Moyenne des scores pour un même document ID racine.
    
    Paramètres :
        requete_fr/en       list, tokens.
        corpus_vect_fr/en   dict, corpus vectorisés.
        vocab_fr/en         dict, vocabulaires.
        params_fr/en        dict, paramètres spécifiques à chaque langue.
    
    Retour :
        list, top-k fusionné [(racine, score_moyen), ...].
    """
    
    resFr = top_k_mono_langue(
        requete_fr, corpus_vect_fr, vocab_fr, 
        methode=methode, niveau_corpus='document_mots', 
        top_k=len(corpus_vect_fr),
        **params_fr
    )
    
    resEn = top_k_mono_langue(
        requete_en, corpus_vect_en, vocab_en, 
        methode=methode, niveau_corpus='document_mots', 
        top_k=len(corpus_vect_en),
        **params_en
    )
    
    scores = {}
    
    for identifiant, score in resFr:
        racine = identifiant.split('_')[0]
        
        if racine not in scores:
            scores[racine] = []
        scores[racine].append(score)
        
    for identifiant, score in resEn:
        racine = identifiant.split('_')[0]
        
        if racine not in scores:
            scores[racine] = []
        scores[racine].append(score)
        
    resultats = []
    for racine, lscores in scores.items():
        if len(lscores) > 0:
            moyenne = sum(lscores) / len(lscores)
            resultats.append((racine, moyenne))
            
    tries = sorted(resultats, key=lambda x: x[1], reverse=True)
    return tries[:top_k]

def comparer_top_k_mono_vs_fusion(top_k_mono, top_k_fusion):
    """
    Description :
        Compare les résultats d'une recherche mono-langue
        avec ceux d'une recherche fusionnée.
        Calcule la similarité de Jaccard entre les deux listes de résultats
        pour voir si la fusion apporte de nouveaux documents ou garde les mêmes.
    
    Paramètres :
        top_k_mono    list, liste des résultats mono-langue [(id, score), ...].
        top_k_fusion  list, liste des résultats fusionnés [(id, score), ...].
    
    Retour :
        dict, contient :
              - 'jaccard' : float, taux de chevauchement.
              - 'idsMono' : list, les identifiants trouvés en mono.
              - 'idsFusion' : list, les identifiants trouvés en fusion.
    """
    idsMono = []
    for item in top_k_mono:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            identifiant = identifiant[0] 
        racine = identifiant.split('_')[0]
        idsMono.append(racine)
        
    idsFusion = []
    for item in top_k_fusion:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            identifiant = identifiant[0]
            
        idsFusion.append(identifiant)
    
    setMono = set(idsMono)
    setFusion = set(idsFusion)
    
    inter = len(setMono.intersection(setFusion))
    union = len(setMono.union(setFusion))
    
    jaccard = inter / union if union > 0 else 0.0
    
    return {
        "jaccard": round(jaccard, 2),
        "idsMono": idsMono,
        "idsFusion": idsFusion
    }


def test_recherche_fusion():
    print("\n Test :Recherche Multilingue par Fusion ")
    
    # Configuration
    v_fr = {"chat": 0}
    v_en = {"cat": 0}
    c_vec_fr = {
        "d1_fr": np.array([1.0]), 
        "d2_fr": np.array([1.0])
    }
    c_vec_en = {
        "d1_en": np.array([1.0]),
        "d2_en": np.array([0.0])
    }
    
    p = {"vecteur_idf": np.array([1.0])}
    
    # Action : Fusion
    res_fusion = recherche_multilingue_fusion(
        ["chat"], ["cat"],
        c_vec_fr, c_vec_en,
        v_fr, v_en,
        p, p,
        methode="tfidf"
    )
    
    print(f"  Résultats Fusion : {res_fusion}")
    
    # Vérifications
    assert res_fusion[0][0] == "d1"
    assert np.isclose(res_fusion[0][1], 1.0)
    assert res_fusion[1][0] == "d2"
    assert np.isclose(res_fusion[1][1], 0.5)
    
    # Comparaison Mono vs Fusion
    res_mono_fr = [("d1_fr", 1.0), ("d2_fr", 1.0)]
    comp_fus = comparer_top_k_mono_vs_fusion(res_mono_fr, res_fusion)
    print(f"  Comparaison Fusion vs Mono : {comp_fus}")
    assert comp_fus["jaccard"] == 1.0
    print(" Test 'recherche_fusion' validé.")

#test_recherche_fusion()

# h. Impact du corpus : Recherche locale ou globalse
# i. Recherche locale par sous-corpus

def top_k_local(requete, corpus_sous_corpus, vocabulaire_direct, 
                niveau_corpus='document_agrege', mesure='cosinus', 
                top_k=5, methode="tfidf", **params):
    """
    Description :
        Effectue une recherche limitée à un sous-ensemble du corpus.
        Elle vectorise ce sous-corpus spécifiquement et y cherche la requête.
    
    Paramètres :
        requete             list, tokens de la requête.
        corpus_sous_corpus  dict, le sous-ensemble de documents {id: doc}.
        vocabulaire_direct  dict, le vocabulaire globals.
        niveau_corpus       str, niveau de granularité.
        mesure              str, métrique de similarité.
        top_k               int, nombre de résultats.
        methode             str, méthode de vectorisation.
        **params            arguments (vecteur_idf, etc.).
    
    Retour :
        list, liste des résultats triés [(id, score), ...].
    """
    if not corpus_sous_corpus:
        return []

    matrice = vectoriser_corpus(
        corpus_sous_corpus, 
        vocabulaire_direct, 
        methode=methode, 
        niveau=niveau_corpus, 
        **params
    )
    
    req = "phrase"
    if "document" in niveau_corpus:
        req = "document_mots" 
        
    vecteur = vectoriser_requete(
        requete, 
        vocabulaire_direct, 
        methode=methode, 
        requete=req, 
        **params
    )
    
    scores = calculer_scores_requete(
        vecteur, 
        matrice, 
        mesure=mesure, 
        niveau=niveau_corpus
    )
    
    return extraire_top_k(scores, k=top_k, niveau=niveau_corpus)


def analyse_repartition_local(top_k, meta_corpus):
    """
    Description :
        Analyse la distribution des résultats d'une recherche locale.
        Permet de voir quels documents dominent au sein du sous-groupe.
    
    Paramètres :
        top_k        list, les résultats de la recherche locale.
        meta_corpus  dict, les métadonnées.
    
    Retour :
        list, liste de dictionnaires enrichis pour affichage.
    """
    analyse = []
    if not top_k:
        return analyse
        
    for rang, (identifiant, score) in enumerate(top_k, 1):
        id = identifiant[0] if isinstance(identifiant, tuple) else identifiant
        
        titre = id
        source = "Inconnu"
        
        if meta_corpus and id in meta_corpus:
            titre = meta_corpus[id].get("titre", id)
            source = meta_corpus[id].get("sous_corpus", "Inconnu")
            
        analyse.append({
            "rang": rang,
            "id": id,
            "score": score,
            "titre": titre,
            "source_locale": source
        })
        
    return analyse


def test_recherche_locale():
    print("\n Test : Recherche Locale par Sous-Corpus ")
    
    # Configuration
    vocab = {"sport": 0, "ballon": 1, "politique": 2, "vote": 3}
    
    # Corpus Globals
    corpus_globals = {
        "d1_sport": [["le", "sport", "c'est", "ballon"]],
        "d2_sport": [["ballon", "rond"]],
        "d3_pol":   [["vote", "loi"]],
        "d4_pol":   [["politique", "vote"]]
    }
    
    # Métadonnées simulées
    meta = {
        "d1_sport": {"sous_corpus": "Sport"},
        "d2_sport": {"sous_corpus": "Sport"},
        "d3_pol":   {"sous_corpus": "Politique"},
        "d4_pol":   {"sous_corpus": "Politique"}
    }
    
    sous_corpus_sport = {k: v for k, v in corpus_globals.items() if "sport" in k}
    print(f"  Sous-corpus Sport : {list(sous_corpus_sport.keys())}")
    req = ["ballon"]
    
    res_local = top_k_local(
        req, sous_corpus_sport, vocab,
        niveau_corpus='document_mots',
        mesure='cosinus',
        methode='count',
        top_k=5
    )
    
    print(f"  Résultats Locaux : {res_local}")
    
    # Vérifications
    ids_trouves = [x[0] for x in res_local]
    assert "d3_pol" not in ids_trouves
    assert "d4_pol" not in ids_trouves
    assert "d1_sport" in ids_trouves
    
    # 2. Analyse
    analyse = analyse_repartition_local(res_local, meta)
    assert analyse[0]["source_locale"] == "Sport"
    
    print(" Test 'recherche_locale' validé.")

#test_recherche_locale()

# ii. Recherche globalse sur l'ensemble du corpus

def top_k_globals(requete, corpus_complet, vocabulaire_direct, 
                 niveau_corpus='document_agrege', mesure='cosinus', 
                 top_k=5, methode="tfidf", **params):
    """
    Description :
        Effectue une recherche sur l'ensemble du corpus.
        Cela suppose que 'corpus_complet' contient déjà les vecteurs de TOUS les documents.
    
    Paramètres :
        requete             list, tokens de la requête.
        corpus_complet      dict, le corpus vectorisé complet {id : vecteur}.
        vocabulaire_direct  dict, le vocabulaire globals.
        niveau_corpus       str, niveau de granularité.
        mesure              str, métrique de similarité.
        top_k               int, nombre de résultats.
        methode             str, méthode de vectorisation pour la requête.
        **params            arguments (vecteur_idf, etc.).
    
    Retour :
        list, liste des résultats triés [(id, score), ...].
    """
    req = "phrase"
    if "document" in niveau_corpus:
        req = "document_mots"
        
    vecteur_req = vectoriser_requete(
        requete, 
        vocabulaire_direct, 
        methode=methode, 
        type_requete=req, 
        **params
    )
    
    scores = calculer_scores_requete(
        vecteur_req, 
        corpus_complet, 
        mesure=mesure, 
        niveau=niveau_corpus
    )
    
    resultats = extraire_top_k(scores, k=top_k, niveau=niveau_corpus)
    
    return resultats


def analyse_repartition_globals(top_k, meta_corpus):
    """
    Description :
        Analyse la distribution des résultats d'une recherche globalse.
        Permet de voir si les résultats proviennent de divers sous-corpus ou d'un seul,
        et d'identifier la diversité linguistique.
    
    Paramètres :
        top_k        list, les résultats de la recherche globalse.
        meta_corpus  dict, les métadonnées globalses.
    
    Retour :
        list, liste de dictionnaires enrichis contenant source et langue.
    """
    analyse = []
    if not top_k:
        return analyse
        
    for rang, (identifiant, score) in enumerate(top_k, 1):
        if isinstance(identifiant, tuple):
            id = identifiant[0]
        else:
            id = identifiant
            
        titre = id
        source = "Inconnu"
        langue = "na"
        
        if meta_corpus and id in meta_corpus:
            info = meta_corpus[id]
            titre = info.get("titre", id)
            source = info.get("sous_corpus", "Inconnu")
            langue = info.get("langue", "na")
            
        analyse.append({
            "rang": rang,
            "id": id,
            "score": score,
            "source": source,
            "langue": langue,
            "titre": titre
        })
        
    return analyse


def test_recherche_globalse():
    print("\n Test : Recherche Globalse ")
    
    # Configuration
    vocab = {"code": 0, "loi": 1, "java": 2, "python": 3}
    
    # Corpus Globals Vectorisé
    corpus_vec_globals = {
        "d1_droit": np.array([1.0, 1.0, 0.0, 0.0]), 
        "d2_info":  np.array([1.0, 0.0, 0.0, 1.0]), 
        "d3_info":  np.array([1.0, 0.0, 1.0, 0.0]) 
    }
    
    meta = {
        "d1_droit": {"sous_corpus": "Droit", "langue": "fr"},
        "d2_info":  {"sous_corpus": "Info", "langue": "en"},
        "d3_info":  {"sous_corpus": "Info", "langue": "en"}
    }
    
    # Action
    req = ["code"]
    
    res_globals = top_k_globals(
        req, corpus_vec_globals, vocab,
        niveau_corpus='document_agrege',
        mesure='cosinus',
        methode='tf',
        top_k=5
    )
    
    print(f"  Résultats Globaux : {res_globals}")
    
    # Analyse
    analyse = analyse_repartition_globals(res_globals, meta)
    sources_trouvees = []
    for item in analyse:
        sources_trouvees.append(item["source"])
        
    print(f"  Sources trouvées : {sources_trouvees}")
    
    assert "Droit" in sources_trouvees
    assert "Info" in sources_trouvees
    
    # Vérification scores 
    score1 = analyse[0]["score"]
    score2 = analyse[1]["score"]
    assert np.isclose(score1, score2)
    
    print(" Test  'recherche_globalse' validé.")

#test_recherche_globalse()

# iii. Comparaison entre recherche locale et globalse

def comparer_local_vs_globals(top_k_local, top_k_globals):
    """
    Description :
        Compare les résultats d'une recherche locale 
        et d'une recherche globalse. Identifie les documents qui apparaissent
        dans les deux listes, et ceux qui sont exclusifs à l'une ou l'autre.
    
    Paramètres :
        top_k_local   list, résultats de la recherche locale [(id, score), ...].
        top_k_globals  list, résultats de la recherche globalse [(id, score), ...].
    
    Retour :
        dict, contient les listes d'IDs : 'local', 'globals', 'partages'.
              Pour les partagés, inclut aussi l'écart de rang.
    """
    dictLocal = {}
    rang = 1
    for item in top_k_local:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            identifiant = identifiant[0]
        dictLocal[identifiant] = (rang, item[1])
        rang += 1
        
    dictGlobals = {}
    rang = 1
    for item in top_k_globals:
        identifiant = item[0]
        if isinstance(identifiant, tuple):
            identifiant = identifiant[0]
        dictGlobals[identifiant] = (rang, item[1])
        rang += 1
    idsL = set(dictLocal.keys())
    idsG = set(dictGlobals.keys())
    
    local = []
    for id in idsL:
        if id not in idsG:
            score = dictLocal[id][1]
            local.append((id, score))
            
    globals = []
    for id in idsG:
        if id not in idsL:
            score = dictGlobals[id][1]
            globals.append((id, score))
            
    partages = []
    for id in idsL:
        if id in idsG:
            rangL = dictLocal[id][0]
            rangG = dictGlobals[id][0]
            scoreL = dictLocal[id][1]
            scoreG = dictGlobals[id][1]
            
            ecart = rangG - rangL
            
            partages.append({
                "id": id,
                "rangLocal": rangL,
                "rangGlobals": rangG,
                "ecartRang": ecart,
                "scoreLocal": scoreL,
                "scoreGlobals": scoreG
            })
            
    return {
        "local": local,
        "globals": globals,
        "partages": partages
    }


def visualiser_diff_local_globals(resultats_comparaison, titre="Différence Local vs Globals"):
    """
    Description :
        Génère un graphique montrant la répartition des documents :
        Uniques au Local, Uniques au Globals, et Partagés.
    
    Paramètres :
        resultats_comparaison  dict, retour de la fonction comparer_local_vs_globals.
        titre                  str.
    
    Retour :
        matplotlib.figure.Figure.
    """
    if not resultats_comparaison:
        return None
        
    local = len(resultats_comparaison.get("local", []))
    globals = len(resultats_comparaison.get("seulement_global", []))
    partages = len(resultats_comparaison.get("partages", []))
    
    etiquettes = ["Uniques Local", "Partagés", "Uniques Global"]
    valeurs = [local, partages, globals]
    couleurs = ['skyblue', 'lightgreen', 'salmon']
    
    fig = plt.figure(figsize=(8, 5))
    plt.bar(etiquettes, valeurs, color=couleurs, edgecolor='black')
    
    plt.title(titre)
    plt.ylabel("Nombre de documents (Top-K)")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(valeurs):
        plt.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
        
    plt.tight_layout()
    return fig


def test_comparer_local_globals():
    print("\n Test : Comparaison Local vs Globals ")
    
    # Configuration
    top_local = [("d1", 0.9), ("d2", 0.8)]
    top_globals = [("d1", 0.9), ("d3", 0.85), ("d2", 0.8)]
    
    # Action
    diff = comparer_local_vs_globals(top_local, top_globals)
    
    print(f"  Différences : {diff}")
    
    # Vérifications
    
    ids_partages = [x["id"] for x in diff["partages"]]
    assert "d1" in ids_partages
    assert "d2" in ids_partages
    idsG_only = [x[0] for x in diff["globals"]]
    assert "d3" in idsG_only
    
    info_d2 = next(item for item in diff["partages"] if item["id"] == "d2")
    assert info_d2["rangLocal"] == 2
    assert info_d2["rangGlobals"] == 3
    assert info_d2["ecartRang"] == 1
    
    fig = visualiser_diff_local_globals(diff)
    if fig:
        plt.close(fig)
        print("  Graphique de comparaison généré.")
    
    print(" Test 'comparer_local_vs_globals' validé.")

#test_comparer_local_globals()