import numpy as np
import os
from gensim.models import KeyedVectors, Word2Vec, FastText
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from s3 import segmenter_mots, pipeline_filtrage 
from collections import Counter, defaultdict
from scipy.sparse import vstack, csr_matrix, issparse
import pickle
import glob
import shutil
from wordcloud import WordCloud
#Séance 6: Embeddings, visualisation lexicale et gestion des descripteurs
#2. Niveaux de plongement et granularité des représentations
#a. Plongement de mots
#i. Apprentissage d’un modèle de plongement sur le corpus

def entrainer_modele_word2vec(corpus, taille_vecteur=100, fenetre=5, min_count=2, epochs=10):
    """
    Description :
        Entraîne un modèle Word2Vec sur le corpus fourni.
        Le modèle apprend à associer un vecteur dense à chaque mot.

    Paramètres :
        corpus          list of list of str : Le corpus prétraité.
                        C'est une liste de phrases, où chaque phrase est une liste de mots.
                        Exemple : [['le', 'chat', 'dort'], ['le', 'chien', 'aboie']]
        taille_vecteur  int : Dimension des vecteurs de sortie (ex: 100, 300).
        fenetre         int : La distance maximale entre le mot courant et le mot prédit.
        min_count       int : Ignore les mots dont la fréquence totale est inférieure à ce seuil.
        epochs          int : Nombre d'itérations sur le corpus.

    Retour :
        gensim.models.Word2Vec : L'objet modèle entraîné.
    """

    # Initialisation
    model = Word2Vec(
        sentences=corpus,
        vector_size=taille_vecteur,
        window=fenetre,
        min_count=min_count,
        epochs=epochs,
        sg=0,        
        workers=4 
    )
    
    return model

def test_entrainer_modele_word2vec_complet():
    print("\n Test 1 : Cas Normal (Dimension et Vocabulaire) ")
    
    corpus_simple = [
        ["le", "chat", "mange"],
        ["le", "chien", "dort"],
        ["le", "chat", "joue"]
    ]
    dim = 10
    
    # Entraînement
    modele = entrainer_modele_word2vec(
        corpus_simple, 
        taille_vecteur=dim, 
        fenetre=2, 
        min_count=1, 
        epochs=5
    )
    
    mot_test = "chat"
    
    # Vérifie que le mot est dans le vocabulaire (wv = word vectors)
    assert mot_test in modele.wv, f"ERREUR : '{mot_test}' devrait être dans le vocabulaire."
    print(f" Le mot '{mot_test}' est bien présent.")

    # Vérifie la dimension du vecteur
    vecteur = modele.wv[mot_test]
    assert len(vecteur) == dim, f"ERREUR : Dimension {len(vecteur)} reçue, {dim} attendue."
    print(f" La dimension des vecteurs est correcte ({dim}).")


    # TEST 2 : Cas Limite (Le filtre min_count)
    print("\n Test 2 : Cas Limite (Filtre min_count) ")
    
    corpus_filtre = [
        ["mot", "commun"],
        ["mot", "commun", "rare"] 
    ]
    modele_filtre = entrainer_modele_word2vec(corpus_filtre, min_count=2, taille_vecteur=5)
    
    assert "commun" in modele_filtre.wv, "ERREUR : 'commun' devrait être gardé."
    assert "rare" not in modele_filtre.wv, "ERREUR : 'rare' aurait dû être filtré (min_count)."    
    print(f" Le filtrage min_count fonctionne ('rare' a été ignoré).")


    # TEST 3 : Robustesse (Corpus Vide)
    try:
        modele_vide = entrainer_modele_word2vec([], taille_vecteur=5)
        assert len(modele_vide.wv) == 0, "ERREUR : Le vocabulaire devrait être vide."
        print(" La fonction a géré le corpus vide sans planter.")
    except Exception as e:
        print(f" La fonction a planté sur un corpus vide : {e}")

    print("\n Tous les tests sont validés avec succès ! ")

#test_entrainer_modele_word2vec_complet()

def charger_modele_preentraine(chemin, type_modele='word2vec'):
    """
    Description :
        Charge un modèle de plongements pré-entraîné (Word2Vec ou FastText).
        
    Paramètres :
        chemin       str : Le chemin vers le fichier du modèle.
        type_modele  str : 'word2vec' ou 'fasttext'.
    
    Retour :
        Objet modèle  permettant d'accéder aux vecteurs.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Le fichier modèle est introuvable : {chemin}")


    try:
        if type_modele == 'word2vec':
            binaire = chemin.endswith('.bin')
            modele = KeyedVectors.load_word2vec_format(chemin, binary=binaire)
            
        elif type_modele == 'fasttext':
            modele = FastText.load_fasttext_format(chemin).wv
            
        else:
            raise ValueError(f"Type de modèle inconnu : {type_modele}")
        return modele

    except Exception as e:
        return None


def test_charger_modele_preentraine():
    print("\n Test : Chargement Modèle Pré-entraîné ")
    
    fich_test = "test_vectors.txt"
    # Format standard Word2Vec (Texte)
    # Ligne N : mot valeur1 valeur2 ...
    contenu_faux_modele = """3 4
chat 0.1 0.2 0.3 0.4
chien 0.5 0.6 0.7 0.8
maison 0.9 0.0 0.1 0.2
"""
    # Création du fichier temporaire
    with open(fich_test, "w", encoding="utf-8") as f:
        f.write(contenu_faux_modele)

    try:
        # 1. Test chargement Word2Vec
        modele = charger_modele_preentraine(fich_test, type_modele='word2vec')
        
        # 2. Vérifications
        assert modele is not None, "Le modèle n'a pas été chargé."
        assert "chat" in modele, "Le mot 'chat' devrait être reconnu."
        vecteur = modele['chat']
        print(f"Vecteur récupéré pour 'chat' : {vecteur}")
        assert len(vecteur) == 4, "La dimension devrait être 4."
        
        print(" Test de chargement validé.")
        
    except Exception as e:
        print(f" Erreur pendant le test : {e}")
        
    finally:
        if os.path.exists(fich_test):
            os.remove(fich_test)

#test_charger_modele_preentraine()

#ii. Utilisation de modèles de plongements pré-entraînés

def get_vecteur_mot(token, modele_embeddings, strategie_oov='ignore'):
    """
    Description :
        Retourne le vecteur associé à un mot.
        Gère les cas où le mot n'est pas dans le vocabulaire.

    Paramètres :
        token              str : Le mot à vectoriser.
        modele_embeddings  object : L'objet Gensim.
        strategie_oov      str : 'ignore', 'zeros', ou 'random'.
                                 'ignore' -> Retourne None.
                                 'zeros'  -> Retourne un vecteur de zéros.
                                 'random' -> Retourne un vecteur aléatoire.

    Retour :
        numpy.array ou None : Le vecteur du mot.
    """
    if hasattr(modele_embeddings, 'wv'):
        wv = modele_embeddings.wv
    else:
        wv = modele_embeddings
    if token in wv:
        return wv[token]
    dim = wv.vector_size
    
    if strategie_oov == 'ignore':
        return None
        
    elif strategie_oov == 'zeros':
        return np.zeros(dim)
        
    elif strategie_oov == 'random':
        return np.random.uniform(-0.1, 0.1, dim)
        
    else:
        return None



def test_get_vecteur_mot():
    class MockModel:
        def __init__(self):
            self.vector_size = 4
            self.data = {
                "chat": np.array([0.1, 0.2, 0.3, 0.4])
            }
        
        # Permet de faire "if 'chat' in model"
        def __contains__(self, key):
            return key in self.data
            
        # Permet de faire "model['chat']"
        def __getitem__(self, key):
            return self.data[key]

    mock_model = MockModel()
    
    
    # Cas 1 : Mot connu
    vec = get_vecteur_mot("chat", mock_model)
    assert vec is not None, "Le mot 'chat' devrait retourner un vecteur."
    assert np.array_equal(vec, np.array([0.1, 0.2, 0.3, 0.4]))
    print(" Cas Mot Connu : Validé.")
    # Cas 2 : OOV - Stratégie 'ignore'
     
    vec_ignore = get_vecteur_mot("inconnu", mock_model, strategie_oov='ignore')
    assert vec_ignore is None, "La stratégie 'ignore' doit retourner None."
    print(" Cas OOV 'ignore' : Validé.")

    
    # Cas 3 : OOV - Stratégie 'zeros'
 
    vec_zeros = get_vecteur_mot("inconnu", mock_model, strategie_oov='zeros')
    assert isinstance(vec_zeros, np.ndarray), "Doit retourner un array numpy."
    assert np.all(vec_zeros == 0), "Tous les éléments doivent être à 0."
    assert len(vec_zeros) == 4, "La dimension doit être respectée (4)."
    print(" Cas OOV 'zeros' : Validé.")

     
    # Cas 4 : OOV - Stratégie 'random'
    
    vec_rand = get_vecteur_mot("inconnu", mock_model, strategie_oov='random')
    assert isinstance(vec_rand, np.ndarray), "Doit retourner un array numpy."
    assert len(vec_rand) == 4, "La dimension doit être respectée."
    assert not np.all(vec_rand == 0), "Le vecteur aléatoire ne doit pas être vide."
    print(" Cas OOV 'random' : Validé.")

#test_get_vecteur_mot()

#b. Plongement de phrases


def plongement_phrase_par_mots(phrase, modele_embeddings, strategie_agregation='moyenne', strategie_oov='ignore'):
    """
    Description :
        Calcule le vecteur d'une phrase en agrégeant les vecteurs de ses mots.

    Paramètres :
        phrase              list of str : La phrase tokenisée .
        modele_embeddings   object : Le modèle Word2Vec/FastText.
        strategie_agregation str : 'moyenne' ou 'somme'.
        strategie_oov       str : Comment gérer les mots inconnus.

    Retour :
        numpy.array : Le vecteur résultant pour la phrase.
    """
    if hasattr(modele_embeddings, 'vector_size'):
        dim = modele_embeddings.vector_size
    elif hasattr(modele_embeddings, 'wv'):
        dim = modele_embeddings.wv.vector_size
    else:
        try:
            dim = len(modele_embeddings['le'])
        except:
            dim = 100 
            
    collectes = []

    for mot in phrase:
        vec = get_vecteur_mot(mot, modele_embeddings, strategie_oov=strategie_oov)
        
        if vec is not None:
            collectes.append(vec)
            
    if not collectes:
        return np.zeros(dim)
    
    matrice = np.array(collectes)
    
    if strategie_agregation == 'moyenne':
        return np.mean(matrice, axis=0)
        
    elif strategie_agregation == 'somme':
        return np.sum(matrice, axis=0)
        
    else:
        return np.zeros(dim)



def test_plongement_phrase_par_mots():
    
    # 1. Création d'un faux modèle 
    class MockModel:
        def __init__(self):
            self.vector_size = 2 
            self.wv = self 
            self.data = {
                "chat": np.array([1.0, 2.0]),
                "chien": np.array([3.0, 4.0])
            }
        def __contains__(self, key): return key in self.data
        def __getitem__(self, key): return self.data[key]

    mock = MockModel()
    # Cas 1 : Agrégation 'moyenne' (Cas standard)
    
    phrase = ["chat", "chien"]
    vec_moy = plongement_phrase_par_mots(phrase, mock, strategie_agregation='moyenne')
    
    print(f"Vecteur Moyenne obtenu : {vec_moy}")
    assert np.array_equal(vec_moy, np.array([2.0, 3.0])), "La moyenne est incorrecte."
    print(" Agrégation 'moyenne' validée.")
 
    # Cas 2 : Agrégation 'somme'
     
    vec_somme = plongement_phrase_par_mots(phrase, mock, strategie_agregation='somme')
    print(f"Vecteur Somme obtenu : {vec_somme}")
    assert np.array_equal(vec_somme, np.array([4.0, 6.0])), "La somme est incorrecte."
    print(" Agrégation 'somme' validée.")

    
    # Cas 3 : Phrase avec mot inconnu (OOV 'ignore')
    
    phrase_oov = ["chat", "dinosaure"] 
    vec_oov = plongement_phrase_par_mots(phrase_oov, mock, strategie_agregation='moyenne', strategie_oov='ignore')
    
    assert np.array_equal(vec_oov, np.array([1.0, 2.0])), "Le mot inconnu aurait dû être ignoré."
    print(" Gestion OOV dans la phrase validée.")
 
    # Cas 4 : Phrase totalement inconnue ou vide
     
    vec_vide = plongement_phrase_par_mots(["rien"], mock, strategie_agregation='moyenne', strategie_oov='ignore')
    assert np.all(vec_vide == 0), "Une phrase sans vecteurs valides doit retourner des zéros."
    assert len(vec_vide) == 2, "La dimension du vecteur nul doit être correcte."
    print(" Cas phrase vide/inconnue validé.")

#test_plongement_phrase_par_mots()

def similarite_phrases(phrase1, phrase2, modele_embeddings, strategie_agregation='moyenne', strategie_oov='ignore', mesure='cosinus'):
    """
    Description :
        Calcule la similarité entre deux phrases via leurs embeddings.

    Paramètres :
        phrase1, phrase2    list of str : Les deux phrases tokenisées.
        modele_embeddings   object : Le modèle Word2Vec/FastText.
        strategie_agregation str : 'moyenne' ou 'somme'.
        strategie_oov       str : 'ignore', 'zeros', 'random'.
        mesure              str : 'cosinus' ou 'euclidienne'.

    Retour :
        float : Score de similarité.
    """
    v1 = plongement_phrase_par_mots(phrase1, modele_embeddings, strategie_agregation, strategie_oov)
    v2 = plongement_phrase_par_mots(phrase2, modele_embeddings, strategie_agregation, strategie_oov)
    nv1 = np.linalg.norm(v1)
    nv2 = np.linalg.norm(v2)
    
    if nv1 == 0 or nv2 == 0:
        return 0.0

    if mesure == 'cosinus':
        temp = np.dot(v1, v2)
        sim = temp / (nv1 * nv2)
        return float(sim)
        
    elif mesure == 'euclidienne':
        dist = np.linalg.norm(v1 - v2)
        return 1.0 / (1.0 + dist)
        
    else:
        return 0.0



def test_similarite_phrases():
   
    # 1. Mock Model
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            self.data = {
                "chat": np.array([1.0, 0.0]),
                "chien": np.array([0.0, 1.0]),
                "minou": np.array([1.0, 0.0])
            }
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
        
    mock = MockModel()

    # Cas 1 : Phrases identiques (ou synonymes parfaits)
    p1 = ["chat"]
    p2 = ["minou"]
    sim_perfect = similarite_phrases(p1, p2, mock, mesure='cosinus')
    
    print(f"Sim 'chat' vs 'minou' : {sim_perfect:.4f}")
    assert np.isclose(sim_perfect, 1.0), "La similarité devrait être 1.0"
    print(" Cas Identique validé.")

    
    # Cas 2 : Phrases orthogonales (totalement différentes dans cet espace)
    
    p3 = ["chien"]
    sim_ortho = similarite_phrases(p1, p3, mock, mesure='cosinus')
    
    print(f"Sim 'chat' vs 'chien' (ici orthogonaux) : {sim_ortho:.4f}")
    assert np.isclose(sim_ortho, 0.0), "La similarité devrait être 0.0"
    print(" Cas Différent validé.") 
    # Cas 3 : Phrase vide (Sécurité)
     
    p_vide = []
    sim_vide = similarite_phrases(p1, p_vide, mock)
    assert sim_vide == 0.0, "La similarité avec une phrase vide doit être 0."
    print(" Cas Vide validé.")

#test_similarite_phrases()

def top_k_phrases_similaires(phrase, corpus_phrases, modele_embeddings, strategie_agregation='moyenne', strategie_oov='ignore',  k=5):
    """
    Description :
        Retourne les k phrases les plus proches sémantiquement d'une phrase requête
        dans un corpus donné.

    Paramètres :
        phrase              list of str : La requête tokenisée .
        corpus_phrases      list of lists : Le corpus.
        modele_embeddings   object : Le modèle Word2Vec/FastText.
        strategie_agregation str : 'moyenne' ou 'somme'.
        strategie_oov       str : 'ignore', 'zeros', 'random'.
        k                   int : Nombre de résultats à retourner.

    Retour :
        list of tuples : Une liste de tuple triée par pertinence.
    """
    
    resultats = []
    for p in corpus_phrases:
        score = similarite_phrases(
            phrase, 
            p, 
            modele_embeddings, 
            strategie_agregation=strategie_agregation, 
            strategie_oov=strategie_oov,
            mesure='cosinus'
        )
        resultats.append((score, p))
        
    trier = sorted(resultats, key=lambda x: x[0], reverse=True)
    return trier[:k]

def test_top_k_phrases_similaires():
    print("\n Test : Top-K Phrases Similaires ")
    
    # 1. Création du Mock Model
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            self.data = {
                "manger": np.array([1.0, 0.1]),
                "pomme":  np.array([0.9, 0.0]),
                "ordinateur": np.array([0.0, 1.0]),
                "clavier":    np.array([0.1, 0.9]), 
                "fruit":      np.array([0.8, 0.2])
            }
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
    
    mock = MockModel()
    
    corpus = [
        ["le", "clavier", "est", "cassé"],
        ["je", "veux", "une", "pomme"],     
        ["il", "faut", "manger"],           
        ["ordinateur", "rapide"]     
    ]
    requete = ["je", "veux", "un", "fruit"] 

    top_resultats = top_k_phrases_similaires(
        requete, 
        corpus, 
        mock, 
        k=2, 
        strategie_oov='ignore'
    )
    
    print(f"Requête : {requete}")
    print(f"Résultats (Top 2) :")
    for i, (score, phrase) in enumerate(top_resultats):
        print(f"  {i+1}. Score={score:.4f} -> {phrase}")

    # 5. Vérifications
    # Le mot "fruit" est proche de [0.8, 0.2]
    # "pomme" [0.9, 0.0] et "manger" [1.0, 0.1] devraient sortir en premier
    
    phrase_gagnante = top_resultats[0][1]
    
    # On vérifie que la meilleure phrase contient des mots du thème nourriture
    mots_cles_nourriture = ["pomme", "manger"]
    assert any(mot in phrase_gagnante for mot in mots_cles_nourriture), "Le résultat devrait être lié à la nourriture."
    
    assert len(top_resultats) == 2, "On a demandé k=2."
    
    print(" Le classement sémantique fonctionne correctement.")

#test_top_k_phrases_similaires()

#c. Plongement de documents
#i. Agrégation des vecteurs de mots ou de phrases
def plongement_document_par_mots(document, modele_embeddings, strategie_agregation='moyenne', strategie_oov='ignore'):
    """
    Description :
        Calcule le vecteur d'un document entier en agrégeant les vecteurs de TOUS ses mots.
        
    Paramètres :
        document            list : Le document tokenisé. 
                            Peut être une liste de mots ['le', 'chat'] 
                            OU une liste de phrases [['le', 'chat'], ['il', 'dort']].
        modele_embeddings   object : Le modèle Word2Vec/FastText.
        strategie_agregation str : 'moyenne' ou 'somme'.
        strategie_oov       str : 'ignore', 'zeros', 'random'.

    Retour :
        numpy.array : Le vecteur résultant pour le document.
    """
    
    mots = []
    if document and isinstance(document[0], list):
        for phrase in document:
            mots.extend(phrase)
    else:
        mots = document
    if hasattr(modele_embeddings, 'vector_size'):
        dim = modele_embeddings.vector_size
    elif hasattr(modele_embeddings, 'wv'):
        dim = modele_embeddings.wv.vector_size
    else:
        try:
            dim = len(modele_embeddings['le'])
        except:
            dim = 100
    collectes = []
    for mot in mots:
        vec = get_vecteur_mot(mot, modele_embeddings, strategie_oov=strategie_oov)
        if vec is not None:
            collectes.append(vec)
            
    if not collectes:
        return np.zeros(dim)
        
    matrice = np.array(collectes)
    
    if strategie_agregation == 'moyenne':
        return np.mean(matrice, axis=0)
    elif strategie_agregation == 'somme':
        return np.sum(matrice, axis=0)
    else:
        return np.zeros(dim)



def test_plongement_document_par_mots():
    print("\n Test : Plongement Document (Par Mots) ")
    
    # 1. Mock Model
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            self.data = {
                "chat": np.array([1.0, 2.0]),
                "chien": np.array([3.0, 4.0]),
                "maison": np.array([10.0, 10.0])
            }
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
    
    mock = MockModel()
    # Cas 1 : Document structuré en phrases 
    doc_phrases = [["chat"], ["chien"]]
    
    vecDoc = plongement_document_par_mots(doc_phrases, mock, strategie_agregation='moyenne')
    
    print(f"Vecteur Doc (structuré) : {vecDoc}")
    assert np.array_equal(vecDoc, np.array([2.0, 3.0])), "L'aplatissement ou la moyenne a échoué."
    print(" Cas Document structuré (Phrases) validé.")
    # Cas 2 : Document plat 
    
    doc_plat = ["chat", "chien"]
    vec_plat = plongement_document_par_mots(doc_plat, mock, strategie_agregation='moyenne')
    assert np.array_equal(vec_plat, np.array([2.0, 3.0])), "La liste plate devrait donner le même résultat."
    print(" Cas Document plat validé.")

    
    # Cas 3 : Stratégie 'somme' sur long document
 
    doc_long = ["maison", "maison"]
    vec_somme = plongement_document_par_mots(doc_long, mock, strategie_agregation='somme')
    assert np.array_equal(vec_somme, np.array([20.0, 20.0]))
    print(" Agrégation 'somme' validée.")

#test_plongement_document_par_mots()

def plongement_document_par_phrases(document, modele_embeddings,strategie_agregation_phrase='moyenne', strategie_agregation_doc='moyenne', strategie_oov='ignore'):
    """
    Description :
        Calcule le vecteur d'un document en deux étapes :
        1. Agrégation des mots pour obtenir des vecteurs de phrases.
        2. Agrégation des vecteurs de phrases pour obtenir le vecteur du document.

    Paramètres :
        document                 list of lists : Le document .
        modele_embeddings        object : Le modèle Word2Vec/FastText.
        strategie_agregation_phrase str : 'moyenne' ou 'somme'.
        strategie_agregation_doc    str : 'moyenne' ou 'somme'.
        strategie_oov            str : 'ignore', 'zeros', 'random'.

    Retour :
        numpy.array : Le vecteur résultant pour le document.
    """
    
    if hasattr(modele_embeddings, 'vector_size'):
        dim = modele_embeddings.vector_size
    elif hasattr(modele_embeddings, 'wv'):
        dim = modele_embeddings.wv.vector_size
    else:
        try: dim = len(modele_embeddings['le'])
        except: dim = 100
    if not document or not isinstance(document, list):
        return np.zeros(dim)
        
    if isinstance(document[0], str):
        document = [document]
    vphrases = []
    
    for phrase in document:
        ecPhrase = plongement_phrase_par_mots(
            phrase, 
            modele_embeddings, 
            strategie_agregation=strategie_agregation_phrase, 
            strategie_oov=strategie_oov
        )
        vphrases.append(ecPhrase)
        
    if not vphrases:
        return np.zeros(dim)
        
    matrice = np.array(vphrases)
    
    if strategie_agregation_doc == 'moyenne':
        return np.mean(matrice, axis=0)
        
    elif strategie_agregation_doc == 'somme':
        return np.sum(matrice, axis=0)
        
    else:
        return np.zeros(dim)



def test_plongement_document_par_phrases():
    print("\n Test : Plongement Document (Hiérarchique) ")
    
    # 1. Mock Model
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            self.data = {
                "chat": np.array([2.0, 2.0]),
                "chien": np.array([4.0, 4.0]),
                "oiseau": np.array([10.0, 10.0])
            }
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
    
    mock = MockModel()
    doc = [["chat"], ["chien"]]
    # Cas 1 : Moyenne des Phrases
    vec_moy = plongement_document_par_phrases(
        doc, mock, 
        strategie_agregation_phrase='moyenne', 
        strategie_agregation_doc='moyenne'
    )
    print(f"Vecteur Hiérarchique (Moyenne) : {vec_moy}")
    assert np.array_equal(vec_moy, np.array([3.0, 3.0]))
    print(" Cas Moyenne/Moyenne validé.")

    # Cas 2 : Somme des Phrases
    vec_som = plongement_document_par_phrases(
        doc, mock, 
        strategie_agregation_phrase='moyenne', 
        strategie_agregation_doc='somme'
    )
    assert np.array_equal(vec_som, np.array([6.0, 6.0]))
    print(" Cas Moyenne/Somme validé.")


    # Cas 3 : Robustesse (Liste plate par erreur)
  
    doc_plat = ["chat", "chien"]
    vec_plat = plongement_document_par_phrases(doc_plat, mock)
    # Résultat attendu : Vecteur de la phrase "chat chien" -> Moyenne(2, 4) = 3
    assert np.array_equal(vec_plat, np.array([3.0, 3.0]))
    print(" Cas Robustesse (Liste plate) validé.")

#test_plongement_document_par_phrases()
#ii. Apprentissage d’un modèle de plongement de documents (Doc2Vec)

def entrainer_modele_doc2vec(corpus, taille_vecteur=100, fenetre=5, min_count=2, epochs=20):
    """
    Description :
        Entraîne un modèle Doc2Vec sur le corpus fourni.
        Apprend des vecteurs uniques pour chaque document.

    Paramètres :
        corpus          list of lists : Liste de documents tokenisés.
                        Ex: [['le', 'chat'], ['le', 'chien']]
        taille_vecteur  int : Dimension du vecteur de document.
        fenetre         int : Taille de la fenêtre de contexte.
        min_count       int : Fréquence minimale des mots pour être pris en compte.
        epochs          int : Nombre d'itérations d'entraînement.

    Retour :
        gensim.models.doc2vec.Doc2Vec : Le modèle entraîné.
    """
    documents_tagues = [
        TaggedDocument(words=doc, tags=[i]) 
        for i, doc in enumerate(corpus)
    ]
    modele = Doc2Vec(
        documents_tagues,
        vector_size=taille_vecteur,
        window=fenetre,
        min_count=min_count,
        epochs=epochs,
        dm=1,       
        workers=4
    )
    
    return modele



def test_entrainer_modele_doc2vec():
    print("\n Test : Entraînement Doc2Vec ")
    
    # 1. Corpus factice
    corpus_test = [
        ["le", "chat", "dort", "sur", "le", "canapé"],      
        ["le", "chien", "aboie", "dans", "le", "jardin"],    
        ["il", "fait", "beau", "aujourd'hui"],               
        ["les", "oiseaux", "chantent"]                     
    ]
    
    taille = 10
    modele = entrainer_modele_doc2vec(corpus_test, taille_vecteur=taille, min_count=1, epochs=10)
    
    # a) Vérifier qu'on peut récupérer le vecteur d'un document connu 
    vecDoc_0 = modele.dv[0]
    print(f"Vecteur du document 0 (taille {len(vecDoc_0)}) : {vecDoc_0}")
    
    assert len(vecDoc_0) == taille, f"La taille devrait être {taille}."
    
    # b) Vérifier l'inférence (prédire le vecteur d'un NOUVEAU document)
    nouveau_doc = ["le", "chat", "joue"]
    vec_nouveau = modele.infer_vector(nouveau_doc)
    
    assert len(vec_nouveau) == taille, "L'inférence doit retourner un vecteur de la bonne taille."
    print(" Inférence sur nouveau document réussie.")
    
    # c) Test de similarité (Document 0 vs Document 1)
    sim = modele.dv.similarity(0, 1)
    print(f"Similarité entre Doc 0 et Doc 1 : {sim:.4f}")
    
    print(" Test Doc2Vec validé.")

#test_entrainer_modele_doc2vec()

def plongement_document_doc2vec(document, modele_doc2vec):
    """
    Description :
        Infère le vecteur d'un document ou d'une requête
        à l'aide d'un modèle Doc2Vec déjà entraîné.

    Paramètres :
        document         list : Le document tokenisé .
                                Peut aussi accepter une liste de phrases .
        modele_doc2vec   object : Le modèle Gensim Doc2Vec entraîné.

    Retour :
        numpy.array : Le vecteur du document.
    """
    
    lmots = []
    
    if document and isinstance(document, list):
        if isinstance(document[0], list):
            for phrase in document:
                lmots.extend(phrase)
        else:
            lmots = document
    else:
        lmots = []
    return modele_doc2vec.infer_vector(lmots)


def test_plongement_document_doc2vec():
    print("\n Test : Inférence Doc2Vec ")
    
    data = ["le", "chat", "mange", "la", "souris"]
    tagged_data = [TaggedDocument(words=data, tags=[0])]

    model = Doc2Vec(tagged_data, vector_size=5, min_count=1, epochs=5)
    
    # Cas 1 : Document standard 
 
    doc_nouveau = ["le", "chat", "joue"]
    vec = plongement_document_doc2vec(doc_nouveau, model)
    
    print(f"Vecteur inféré (taille {len(vec)}) : {vec}")
    assert len(vec) == 5, "La dimension du vecteur doit correspondre au modèle (5)."
    assert isinstance(vec, np.ndarray), "Le résultat doit être un array Numpy."
    print(" Inférence standard validée.")

 
    # Cas 2 : Document structuré

    doc_phrases = [["le", "chat"], ["dort", "ici"]]
    ecPhrases = plongement_document_doc2vec(doc_phrases, model)
    
    assert len(ecPhrases) == 5, "L'aplatissement des phrases a échoué."
    # On vérifie juste que ce n'est pas un vecteur nul 
    assert not np.all(ecPhrases == 0), "Le vecteur ne devrait pas être nul."
    print(" Inférence avec structure de phrases validée.")


    # Cas 3 : Document vide ou inconnu
    
    doc_inconnu = ["kjhzefkjzh", "blabla"] 
    vec_inc = plongement_document_doc2vec(doc_inconnu, model)
    assert len(vec_inc) == 5
    print(" Inférence sur mots inconnus validée.")

#test_plongement_document_doc2vec()

#iii. Utilisation des vecteurs de documents pour la recherche

def similarite_documents(doc1, doc2, modele_embeddings, mesure='cosinus'):
    """
    Description :
        Calcule la similarité entre deux documents.
        S'adapte automatiquement au type de modèle fourni 
        ou accepte directement des vecteurs numpy pré-calculés.

    Paramètres :
        doc1, doc2          : Le document  OU le vecteur.
        modele_embeddings   : Le modèle  OU None si vecteurs fournis.
        mesure              : 'cosinus' ou 'euclidienne'.

    Retour :
        float : Score de similarité.
    """
    
    if isinstance(doc1, np.ndarray):
        v1 = doc1
    else:
        if isinstance(modele_embeddings, Doc2Vec):
            v1 = plongement_document_doc2vec(doc1, modele_embeddings)
        else:
            v1 = plongement_document_par_mots(doc1, modele_embeddings, strategie_agregation='moyenne')

    if isinstance(doc2, np.ndarray):
        v2 = doc2
    else:
        if isinstance(modele_embeddings, Doc2Vec):
            v2 = plongement_document_doc2vec(doc2, modele_embeddings)
        else:
            v2 = plongement_document_par_mots(doc2, modele_embeddings, strategie_agregation='moyenne')
    nv1 = np.linalg.norm(v1)
    nv2 = np.linalg.norm(v2)
    
    if nv1 == 0 or nv2 == 0:
        return 0.0
    if mesure == 'cosinus':
        return float(np.dot(v1, v2) / (nv1 * nv2))
        
    elif mesure == 'euclidienne':
        dist = np.linalg.norm(v1 - v2)
        return 1.0 / (1.0 + dist)
        
    else:
        return 0.0



def test_similarite_documents():
    print("\n Test : Similarité Documents (Universelle) ")
    
    # 1. Cas : Vecteurs déjà calculés 
    vec_a = np.array([1.0, 0.0])
    vec_b = np.array([0.0, 1.0])
    sim_direct = similarite_documents(vec_a, vec_b, modele_embeddings=None)
    
    print(f"Test Numpy direct (Orthogonal) : {sim_direct}")
    assert sim_direct == 0.0, "Vecteurs orthogonaux = 0."
    print(" Cas Numpy validé.")

    # 2. Cas : Modèle Word2Vec 
    class MockWord2Vec:
        def __init__(self):
            self.wv = self
            self.vector_size = 2
            self.data = {"chat": np.array([1, 0]), "chien": np.array([1, 0])} # Synonymes parfaits ici
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
    
    mock_w2v = MockWord2Vec()
    doc_1 = ["chat"]
    doc_2 = ["chien"]
    
    sim_w2v = similarite_documents(doc_1, doc_2, mock_w2v)
    print(f"Test Word2Vec (Synonymes) : {sim_w2v}")
    assert sim_w2v == 1.0, "Devrait être 1.0 (vecteurs identiques)."
    print(" Cas Word2Vec validé.")

    # 3. Cas : Modèle Doc2Vec 
    class MockDoc2Vec(Doc2Vec): # Hérite de Doc2Vec pour passer le isinstance
        def __init__(self):
            pass
        def infer_vector(self, doc):
            if "pomme" in doc: return np.array([1.0, 0.0])
            return np.array([0.0, 1.0])

    mock_d2v = MockDoc2Vec()
    doc_pomme = ["je", "mange", "une", "pomme"]
    doc_autre = ["je", "dors"]
    
    sim_d2v = similarite_documents(doc_pomme, doc_autre, mock_d2v)
    print(f"Test Doc2Vec (Différents) : {sim_d2v}")
    assert sim_d2v == 0.0, "Devrait être 0.0 (vecteurs orthogonaux simulés)."
    print(" Cas Doc2Vec validé.")

#test_similarite_documents()

def top_k_documents_similaires(document, corpus, modele_embeddings, k=5, mesure='cosinus'):
    """
    Description :
        Retourne les k documents du corpus les plus proches sémantiquement 
        du document requête.

    Paramètres :
        document            list : Le document requête .
        corpus              list of lists : La liste de tous les documents du corpus.
        modele_embeddings   object : Le modèle .
        k                   int : Le nombre de résultats souhaités.
        mesure              str : 'cosinus' ou 'euclidienne'.

    Retour :
        list of tuples : [(score, document), (score, document), ...] triés par pertinence.
    """
    
    resultats = []
    for i, doc_cible in enumerate(corpus):
        score = similarite_documents(
            document, 
            doc_cible, 
            modele_embeddings, 
            mesure=mesure
        )
        resultats.append((score, doc_cible))
    trier = sorted(resultats, key=lambda x: x[0], reverse=True)
    return trier[:k]


def test_top_k_documents_similaires():
    print("\n Test : Top-K Documents Similaires ")
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            self.data = {
                "cpu": np.array([1.0, 0.0]),
                "ram": np.array([0.9, 0.1]),
                "tarte": np.array([0.0, 1.0]),
                "four": np.array([0.1, 0.9])
            }
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
        
    mock = MockModel()
    
    corpus = [
        ["tarte", "aux", "pommes"], 
        ["cpu", "et", "ram"],       
        ["four", "chaud"],          
        ["disque", "dur"]           
    ]
    
    requete = ["changer", "ma", "ram"]
    
    # 4. Recherche (k=2)
    # On s'attend à trouver le Doc 1 ("cpu et ram") en premier.
    resultats = top_k_documents_similaires(requete, corpus, mock, k=2)
    
    print(f"Requête : {requete}")
    print("Résultats obtenus :")
    for i, (score, doc) in enumerate(resultats):
        print(f"  {i+1}. Score={score:.4f} -> {doc}")
        
    meilleur_doc = resultats[0][1]
    assert "cpu" in meilleur_doc or "ram" in meilleur_doc, "Le 1er résultat doit être informatique."
    
    # Vérifier que le nombre de résultats est respecté
    assert len(resultats) <= 2, "Ne doit pas retourner plus de k résultats."
    
    print(" Classement sémantique validé.")

#test_top_k_documents_similaires()

#3. Visualisation lexicale et interprétation des contenus
#a. Les nuages de mots comme outil d’analyse exploratoire
#b. Création de nuages de mots à partir d’un texte

def generer_nuage_mots_texte(texte, stopwords=None, largeur=600, hauteur=300, couleur_fond='white'):
    """
    Description :
        Génère un nuage de mots à partir d'un texte brut et retourne
        l'objet Figure correspondant.

    Paramètres :
        texte        str : Le texte source (ou liste de chaînes).
        stopwords    list/set : Liste de mots à exclure.
        largeur      int : Largeur de l'image.
        hauteur      int : Hauteur de l'image.
        couleur_fond str : Couleur de fond.

    Retour :
        matplotlib.figure.Figure : L'objet graphique (ou None si texte vide).
    """
    
    if isinstance(texte, list):
        txt = " ".join(texte)
    else:
        txt = texte

    if not txt or len(txt.strip()) == 0:
        return None

    wc = WordCloud(
        width=largeur, 
        height=hauteur, 
        background_color=couleur_fond, 
        stopwords=stopwords, 
        collocations=False   
    )

    wc.generate(txt)

    fig = plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear') 
    plt.axis("off") 
    plt.title("Nuage de Mots (Fréquences Brutes)", fontsize=14)
    
    return fig

def test_generer_nuage_mots_texte():
    print("\n[TEST] Nuage de Mots (Texte Brut)")
    
    # Texte factice répétant certains mots pour tester la taille
    texte_test = """
    Python est un langage de programmation. Python est super.
    Le code est important. Le code doit être propre.
    Programmation, programmation, algorithme, moteur de recherche.
    """
    
    # Liste de mots à exclure (stopwords)
    stop = set(["est", "un", "le", "de", "doit", "être"])
    
    print("Une fenêtre graphique va s'ouvrir...")
    print("1. Vérifiez que 'PYTHON', 'PROGRAMMATION' et 'CODE' sont les plus gros.")
    print("2. Vérifiez que 'est' et 'le' sont absents (stopwords).")
    
    # --- MODIFICATION ICI ---
    # 1. On capture le résultat dans la variable 'fig'
    fig = generer_nuage_mots_texte(
        texte_test, 
        stopwords=stop, 
        largeur=800, 
        hauteur=400, 
        couleur_fond='white'
    )
    
    # 2. On vérifie si la figure a bien été créée et on l'affiche
    if fig:
        fig.show()
        # plt.show() bloque l'exécution jusqu'à la fermeture de la fenêtre
        plt.show() 
    else:
        print("Erreur : Le nuage de mots n'a pas été généré.")
    
    print("Test terminé (après fermeture de la fenêtre).")


#test_generer_nuage_mots_texte()

def nuage_mots_document(document, pretraitement=True):
    """
    Description :
        Génère un nuage de mots pour un document donné.
        Peut appliquer un prétraitement  avant l'affichage
        pour éviter que les stopwords ne polluent le visuel.

    Paramètres :
        document      str ou list : Le document .
        pretraitement bool : Si True, applique tokenisation + suppression stopwords.
                             Si False, utilise le texte tel quel.
    
    Retour :
        Affiche le graphique.
    """
    texte = document
    stopwords_fr = {
        "le", "la", "les", "de", "du", "des", "et", "ou", "est", "sont", 
        "un", "une", "pour", "dans", "par", "sur", "au", "aux", "ce", "se", 
        "que", "qui", "ne", "pas", "il", "elle", "ils", "elles", "mais"
    }

    if pretraitement:
        
        if isinstance(document, str):
            tokens = segmenter_mots(document)
        else:
            tokens = document
        propre = pipeline_filtrage(tokens, stopwords_fr)
        texte = " ".join(propre)
        
    else:
        if isinstance(document, list):
            texte = " ".join(document)

    generer_nuage_mots_texte(texte, stopwords=None) 



def test_nuage_mots_document():
    print("\n Test : Nuage de Mots avec/sans Prétraitement ")
    
    doc_sale = """
    Le chat est dans la cuisine. Le chat mange de la nourriture.
    Il est content. La cuisine est belle. Chat, chien, cuisine.
    """
    
    print("\n1. Test SANS prétraitement :")
    print("ATTENDU : Vous devriez voir des gros 'Le', 'La', 'est'...")
    nuage_mots_document(doc_sale, pretraitement=False)
    
    print("\n2. Test AVEC prétraitement :")
    print("ATTENDU : 'Le', 'La', 'est' doivent disparaître.")
    print("Les mots clés 'chat', 'cuisine', 'mange' doivent ressortir.")
    nuage_mots_document(doc_sale, pretraitement=True)

#test_nuage_mots_document()

def nuage_mots_sous_corpus(liste_documents, stopwords=None):
    """
    Description :
        Concatène tous les textes d'un sous-corpus et produit un nuage de mots global.
        Permet de visualiser les thèmes dominants d'un groupe de documents.

    Paramètres :
        liste_documents : list. Une liste de documents.
                          Chaque document peut être une chaîne (str) 
                          ou une liste de tokens (list of str).
        stopwords       : list/set. Mots à exclure.

    Retour :
        Affiche le graphique.
    """
    
    morceaux_texte = []
    
    for doc in liste_documents:
        if isinstance(doc, list):
            morceaux_texte.append(" ".join(doc))
        elif isinstance(doc, str):
            morceaux_texte.append(doc)
            
    texte_global = " ".join(morceaux_texte)
    
    generer_nuage_mots_texte(texte_global, stopwords=stopwords, largeur=800, hauteur=400)



def test_nuage_mots_sous_corpus():
    print("\n Test : Nuage de Mots (Sous-Corpus) ")
    
    # Scénario : Un sous-corpus de 3 documents parlant d'astronomie
    # Doc 1 : Texte brut
    # Doc 2 : Liste de tokens
    # Doc 3 : Texte brut
    sous_corpus_astro = [
        "La planète Mars est rouge.",
        ["Mars", "est", "une", "planète", "voisine"],
        "Les missions vers Mars augmentent."
    ]
    
    # Stopwords basiques
    mots_vides = {"la", "le", "les", "est", "une", "vers"}
    
    print("Affichage du nuage cumulé...")
    print("Le mot 'Mars' devrait être le plus gros (présent 3 fois).")
    print("Le mot 'planète' devrait être moyen (présent 2 fois).")
    
    nuage_mots_sous_corpus(sous_corpus_astro, stopwords=mots_vides)

#test_nuage_mots_sous_corpus()
#c. Nuages de mots pondérés par des scores (TF, TF-IDF, etc.)
def nuage_mots_pondere(poid, largeur=800, hauteur=400, couleur_fond='white'):
    """
    Description :
        Génère un nuage de mots à partir d'un dictionnaire {mot: score}
        et retourne l'objet Figure.

    Paramètres :
        poid : dict. Dictionnaire associant chaque mot à son poids.
        largeur       : int. Largeur de l'image.
        hauteur       : int. Hauteur de l'image.
        couleur_fond  : str. Couleur de fond.

    Retour :
        matplotlib.figure.Figure : L'objet graphique (ou None si dico vide).
    """
    
    if not poid:
        return None

    wc = WordCloud(
        width=largeur,
        height=hauteur,
        background_color=couleur_fond
    )
    
    wc.generate_from_frequencies(poid)
    fig = plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title("Nuage de Mots Pondéré (ex: TF-IDF)", fontsize=14)
    
    return fig

def test_nuage_mots_pondere():
    print("\n[TEST] Nuage de Mots Pondéré (TF-IDF Simulés)")
    
    scores_tfidf = {
        "ornithorynque": 0.95,  
        "kangourou": 0.50,     
        "australie": 0.40,     
        "zoo": 0.20,            
        "le": 0.01,             
        "et": 0.01
    }
    
    print("Une fenêtre va s'ouvrir...")
    print("Vérifiez que 'ORNITHORYNQUE' domine l'image.")
    print("Vérifiez que 'le' est minuscule ou invisible.")
    
    fig_pondere = nuage_mots_pondere(scores_tfidf)
    
    if fig_pondere:
        fig_pondere.show()
        plt.show() 
        print("Test terminé (fenêtre fermée).")
    else:
        print("Erreur : Le graphique n'a pas été généré.")

#test_nuage_mots_pondere()

def comparer_nuages_documents(doc1, doc2, scores1, scores2):
    """
    Description :
        Génère une figure contenant deux nuages de mots côte à côte 
        pour comparer visuellement deux documents et retourne l'objet Figure.

    Paramètres :
        doc1, doc2       : Textes originaux (informatif/fallback).
        scores1, scores2 : Dictionnaires {mot: poids}.
    
    Retour :
        matplotlib.figure.Figure : L'objet graphique contenant les deux nuages.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    if scores1:
        wc1 = WordCloud(width=400, height=300, background_color='white')
        wc1.generate_from_frequencies(scores1)
        axes[0].imshow(wc1, interpolation='bilinear')
        axes[0].set_title("Document 1", fontsize=14, fontweight='bold')
    else:
        axes[0].text(0.5, 0.5, "Pas de données (Scores vides)", ha='center')
    axes[0].axis("off")

    if scores2:
        wc2 = WordCloud(width=400, height=300, background_color='white')
        wc2.generate_from_frequencies(scores2)
        axes[1].imshow(wc2, interpolation='bilinear')
        axes[1].set_title("Document 2", fontsize=14, fontweight='bold')
    else:
        axes[1].text(0.5, 0.5, "Pas de données (Scores vides)", ha='center')
    axes[1].axis("off")

    plt.tight_layout()
    return fig


def test_comparer_nuages_documents():
    print("\n[TEST] Comparaison Visuelle (Côte à Côte)")
    
    scores_vacances = {
        "soleil": 0.9, "plage": 0.85, "mer": 0.8,
        "sable": 0.7, "repos": 0.6, "été": 0.5
    }
    
    scores_bureau = {
        "réunion": 0.95, "projet": 0.8, "urgent": 0.75,
        "email": 0.7, "client": 0.6, "rapport": 0.55
    }
    
    print("Une fenêtre graphique va s'ouvrir avec deux nuages distincts.")
    print("Gauche : Mots liés à la plage.")
    print("Droite : Mots liés au travail.")
    
    fig_comparaison = comparer_nuages_documents(None, None, scores_vacances, scores_bureau)

    if fig_comparaison:
        fig_comparaison.show()
        plt.show() 
        print("Test terminé (fenêtre fermée).")
    else:
        print("Erreur : Le graphique n'a pas été généré.")

#test_comparer_nuages_documents()

#d. Visualisation des résultats de recherche par des nuages de mots
def nuage_document_resultat(document, poids):
    """
    Description :
        Affiche un nuage de mots pour un document spécifique retourné par le moteur,
        en mettant en évidence les mots importants selon les poids fournis (ex: TF-IDF).

    Paramètres :
        document : str ou list. Le contenu du document (texte ou tokens).
        poids    : dict. Dictionnaire {mot: score}. 
                   Peut être le vecteur TF-IDF de ce document transformé en dict.

    Retour :
        Affiche le graphique.
    """
    mots = []
    if isinstance(document, list):
        mots = document
    elif isinstance(document, str):
        mots = document.lower().split() 
    poid = {}
    setMot = set(mots)
    
    for mot, score in poids.items():
        if mot in setMot and score > 0:
            poid[mot] = score
            
    if not poid:
        from collections import Counter
        poid = dict(Counter(mots))

    nuage_mots_pondere(poid, largeur=600, hauteur=300, couleur_fond='#f0f0f0')



def test_nuage_document_resultat():
    print("\n Test : Nuage Résultat de Recherche ")
    
    # Scénario : Le moteur a trouvé ce document suite à une requête sur "l'espace"
    document_trouve = ["la", "fusée", "décolle", "vers", "la", "lune", "et", "l'espace"]
    
    # Le moteur (TF-IDF ou autre) a donné ces scores d'importance :
    # "fusée", "lune", "espace" sont très importants.
    # "la", "et", "vers" ont des scores nuls ou très faibles (stopwords).
    poids_moteur = {
        "fusée": 0.8,
        "lune": 0.75,
        "espace": 0.9,
        "décolle": 0.5,
        "mars": 0.2,   # Mot présent dans le dico global mais ABSENT du doc (ne doit pas s'afficher)
        "la": 0.01     # Mot présent mais poids faible (sera petit)
    }
    
    print("Vérification visuelle :")
    print("- 'ESPACE', 'FUSÉE', 'LUNE' doivent être gros.")
    print("- 'MARS' ne doit PAS apparaître (car pas dans le document).")
    
    nuage_document_resultat(document_trouve, poids_moteur)

#test_nuage_document_resultat()

def nuage_mots_resultats_recherche(documents, scores=None):
    """
    Description :
        Génère un nuage de mots global à partir d'une liste de documents retournés 
        par une requête (Top-K).
        Les mots sont pondérés par le score de similarité du document qui les contient.

    Paramètres :
        documents : list. Liste de str (textes) ou list (tokens) représentant les résultats.
        scores    : list (optionnel). Liste des scores de similarité (float) correspondant 
                    aux documents. Si None, tous les documents ont un poids de 1.

    Retour :
        matplotlib.figure.Figure : L'objet graphique généré par nuage_mots_pondere.
    """    
    if scores is None:
        scores = [1.0] * len(documents)
    
    if len(documents) != len(scores):
        return None

    poids_globaux = Counter()

    for doc, score in zip(documents, scores):
        mots = []
        if isinstance(doc, list):
            mots = doc
        elif isinstance(doc, str):
            mots = doc.lower().split()
            
        for mot in mots:
            poids_globaux[mot] += score

    fig = nuage_mots_pondere(
        dict(poids_globaux), 
        largeur=800, 
        hauteur=400, 
        couleur_fond='white'
    )
    
    if fig:
        ax = fig.gca()
        ax.set_title(f"Nuage global des {len(documents)} résultats (pondéré par similarité)", fontsize=14)
        
    return fig


def nuage_mots_top_k_documents(requete, corpus, modele_embeddings, k=5):
    """
    Description :
        1. Effectue une recherche sémantique pour trouver les k documents les plus proches.
        2. Affiche un nuage de mots pondéré par la pertinence de ces résultats.

    Paramètres :
        requete           list : La requête tokenisée (ex: ['je', 'cherche', ...]).
        corpus            list : Le corpus complet.
        modele_embeddings object : Le modèle Word2Vec/Doc2Vec.
        k                 int : Nombre de résultats à utiliser pour le nuage.

    Retour :
        Affiche le graphique.
    """
    
    resultats = top_k_documents_similaires(
        requete, 
        corpus, 
        modele_embeddings, 
        k=k,
        mesure='cosinus'
    )
    
    if not resultats:
        return
    scores = [res[0] for res in resultats]
    documents = [res[1] for res in resultats]
    nuage_mots_resultats_recherche(documents, scores)




def test_nuage_mots_top_k_documents():
    print("\n Test : Pipeline Complet (Recherche + Visualisation) ")
    
    # 1. Simulation du corpus et du modèle (Mock)
    # Thème A : Nature (Forêt, Arbre)
    # Thème B : Ville (Voiture, Rue)
    corpus = [
        ["forêt", "arbre", "vert", "nature"],     # Doc 0
        ["ville", "voiture", "goudron", "rue"],   # Doc 1
        ["feuille", "bois", "arbre", "racine"],   # Doc 2
        ["immeuble", "béton", "ville"]            # Doc 3
    ]
    
    # On simule un modèle Word2Vec qui connait ces mots
    # Ici, on triche un peu pour le test : on définit juste une fonction top_k factice
    # ou on utilise un MockModel simple comme avant.
    
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            # Vecteurs simplifiés : Nature ~ [1,0], Ville ~ [0,1]
            self.data = {
                "nature": np.array([1.0, 0.0]), "arbre": np.array([1.0, 0.1]),
                "ville": np.array([0.0, 1.0]), "rue": np.array([0.1, 1.0]),
                "requete": np.array([1.0, 0.0]) # La requête sera "nature"
            }
        # Fallback pour les mots inconnus (pour éviter KeyError)
        def __contains__(self, k): return True 
        def __getitem__(self, k): return self.data.get(k, np.zeros(2))
            
    mock = MockModel()
    
    # 2. La Requête
    # On cherche "nature" (qui est proche de Doc 0 et Doc 2)
    requete = ["requete"] # Simule "je cherche la nature"
    
    print("Action : Recherche des 2 docs les plus proches de 'nature'...")
    print("Attendu : Un nuage affichant 'ARBRE', 'FORÊT', 'BOIS' en gros.")
    
    # 3. Exécution
    # Note : Cela va appeler tes vraies fonctions top_k et nuage_mots
    # Assure-toi que s6_embeddings.top_k_documents_similaires est bien importée
    
    try:
        nuage_mots_top_k_documents(requete, corpus, mock, k=2)
        print(" Pipeline exécuté sans erreur.")
    except Exception as e:
        print(f" Erreur lors de l'exécution : {e}")
        print("Vérifiez que les fonctions de s6_embeddings sont bien accessibles.")

test_nuage_mots_top_k_documents()

def nuage_requete_vs_document(requete, document, poids_entree):
    """
    Description :
        Génère un nuage de mots comparatif (Vert=Match, Rouge=Manquant)
        et retourne l'objet Figure.

    Paramètres :
        requete      : str ou list. La requête utilisateur.
        document     : str ou list. Le document retrouvé.
        poids_entree : dict. Les scores {mot: poids} du document.

    Retour :
        matplotlib.figure.Figure : L'objet graphique.
    """
    
    # 1. Normalisation en ensembles (Sets)
    def normaliser_set(data):
        if isinstance(data, str):
            return set(data.lower().split())
        return set([m.lower() for m in data])

    setRequete = normaliser_set(requete)
    setDocument = normaliser_set(document)
    
    pfinal = {}
    maxScore = 0 

    if poids_entree:
        for mot, score in poids_entree.items():
            if mot in setDocument: # Sécurité
                pfinal[mot] = score
                if score > maxScore: maxScore = score
    
    if maxScore == 0: maxScore = 1.0

    for mot in setRequete:
        if mot not in setDocument:
            pfinal[mot] = maxScore 
        else:
            if mot in pfinal:
                pfinal[mot] *= 1.2
            else:
                pfinal[mot] = maxScore
    def couleur_custom(word, font_size, position, orientation, random_state=None, **kwargs):
        word_lower = word.lower()
        
        if word_lower in setRequete and word_lower in setDocument:
            return "green"  
        elif word_lower in setRequete:
            return "red"    
        else:
            return "grey"  
            
    if not pfinal:
        return None

    wc = WordCloud(
        width=800, 
        height=400, 
        background_color="white",
        color_func=couleur_custom,
        prefer_horizontal=0.9
    )
    
    wc.generate_from_frequencies(pfinal)
        
    fig = plt.figure(figsize=(10, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    
    plt.title(f"Analyse Lexicale : Requête vs Document", fontsize=14)
    plt.text(400, 420, "Légende : VERT = Match | ROUGE = Manquant | GRIS = Contexte", 
             fontsize=10, color='black', ha='center')
    
    return fig

def test_nuage_requete_vs_document():
    print("\n[TEST] Nuage Comparatif (Recouvrement) ")
    
    # Scénario :
    # L'utilisateur cherche une recette de "Tarte aux pommes cannelle".
    requete = ["tarte", "aux", "pommes", "cannelle"]
    
    # Le moteur trouve un document qui parle de "Tarte aux pommes" mais pas de cannelle.
    # Il parle aussi de sucre, farine, four (contexte).
    document = ["recette", "de", "la", "tarte", "aux", "pommes", "sucre", "farine", "four"]
    
    # Poids simulés (TF-IDF) du document
    poids = {
        "tarte": 0.8,
        "pommes": 0.7,
        "sucre": 0.5,
        "farine": 0.4,
        "four": 0.3,
        "recette": 0.2
        # Note : "cannelle" n'est pas dans les poids car pas dans le doc
    }
    
    print("Vérification visuelle attendue (Une fenêtre va s'ouvrir) :")
    print("1. 'TARTE', 'POMMES', 'AUX' -> EN VERT (Présents dans les deux)")
    print("2. 'CANNELLE' -> EN ROUGE (Mot de la requête manquant dans le doc)")
    print("3. 'SUCRE', 'FARINE'... -> EN GRIS (Contexte du document)")
    
    # --- MODIFICATION ICI ---
    # 1. Capture de la figure retournée
    fig_comparatif = nuage_requete_vs_document(requete, document, poids)

    # 2. Affichage explicite
    if fig_comparatif:
        fig_comparatif.show()
        plt.show() # Bloque jusqu'à la fermeture de la fenêtre
        print("Test terminé (fenêtre fermée).")
    else:
        print("Erreur : Le graphique n'a pas été généré.")

#test_nuage_requete_vs_document()

#4. Expansion de requête à l’aide des plongements vectoriels
#a. Principe de l’expansion de requête

def termes_expansion(requete, modele_embeddings, k=5):
    """
    Description :
        Pour chaque mot de la requête, extrait les k termes les plus proches
        dans l'espace vectoriel.

    Paramètres :
        requete           list : La requête tokenisée.
        modele_embeddings object : Le modèle Word2Vec/FastText/KeyedVectors.
        k                 int : Nombre de synonymes à chercher par mot.

    Retour :
        dict : Un dictionnaire { "mot_original": [("synonyme1", score), ("synonyme2", score)...] }
    """
    
    if hasattr(modele_embeddings, 'wv'):
        wv = modele_embeddings.wv
    else:
        wv = modele_embeddings

    res = {}

    for mot in requete:
        if mot in wv:
            try:
                voisins = wv.most_similar(mot, topn=k)
                res[mot] = voisins
            except Exception as e:
                res[mot] = []
        else:
            res[mot] = []

    return res



def test_termes_expansion():
    print("\n Test : Extraction des termes d'expansion ")
    
    # 1. Mock Model 
    class MockVectors:
        def __contains__(self, key):
            return key in ["chat", "manger"]
            
        def most_similar(self, key, topn=3):
            if key == "chat":
                return [("félin", 0.9), ("minou", 0.85), ("animal", 0.7)][:topn]
            elif key == "manger":
                return [("nourriture", 0.88), ("repas", 0.82), ("dîner", 0.75)][:topn]
            return []

    # Wrapper pour simuler l'objet Gensim complet
    class MockModel:
        def __init__(self):
            self.wv = MockVectors()

    mock = MockModel()
    
    requete = ["chat", "inconnu"]
    expansions = termes_expansion(requete, mock, k=2)
    # Cas A : Mot connu ("chat")
    print(f"Expansion pour 'chat' : {expansions['chat']}")
    assert len(expansions['chat']) == 2, "Doit retourner 2 synonymes."
    assert expansions['chat'][0][0] == "félin", "Le premier synonyme doit être 'félin'."
    
    # Cas B : Mot inconnu ("inconnu")
    print(f"Expansion pour 'inconnu' : {expansions['inconnu']}")
    assert expansions['inconnu'] == [], "Doit retourner une liste vide pour les mots inconnus."
    
    print(" Extraction des expansions validée.")

#test_termes_expansion()

def construire_requete_etendue(requete, termes_expanses, alpha=1.0, beta=0.5):
    """
    Description :
        Construit une représentation vectorielle pondérée de la requête,
        combinant les termes originaux et les termes d'expansion.
        
        Poids final d'un mot = (alpha si dans requête) + (beta * similarité si dans expansion)

    Paramètres :
        requete         list : La requête originale tokenisée.
        termes_expanses dict : Le dictionnaire retourné par termes_expansion()
                               { 'chat': [('félin', 0.9), ...] }
        alpha           float : Poids des termes originaux.
        beta            float : Facteur de pondération des expansions.

    Retour :
        dict : Un dictionnaire { "mot": poids_total } prêt pour la recherche.
    """
    
    vecRequete = defaultdict(float)
    
    for mot in requete:
        vecRequete[mot] += alpha
    for mot_origine, voisins in termes_expanses.items():
        
        for (synonyme, similarite) in voisins:
            poids = beta * similarite
            vecRequete[synonyme] += poids
            
    return dict(vecRequete)



def test_construire_requete_etendue():
    print("\n Test : Construction Requête Étendue  ")
    requete = ["chat", "manger"]
    
    termes_expanses = {
        "chat": [("félin", 0.9), ("minou", 0.8)],
        "manger": [("nourriture", 0.85), ("repas", 0.5)]
    }
    
    alpha = 1.0  
    beta = 0.5   

    vecteur_final = construire_requete_etendue(requete, termes_expanses, alpha, beta)
    
    print(f"Vecteur pondéré final : {vecteur_final}")
    
    
    # Pour "chat" : Présent dans requête -> 1.0
    assert vecteur_final["chat"] == 1.0
    
    # Pour "félin" : Expansion de chat (sim 0.9) * beta (0.5) -> 0.45
    assert abs(vecteur_final["félin"] - 0.45) < 0.001
    
    # Pour "minou" : Expansion de chat (sim 0.8) * beta (0.5) -> 0.40
    assert abs(vecteur_final["minou"] - 0.40) < 0.001
    
    # Pour "repas" : Expansion de manger (sim 0.5) * beta (0.5) -> 0.25
    assert abs(vecteur_final["repas"] - 0.25) < 0.001
    
    print(" Calcul des pondérations validé.")

#test_construire_requete_etendue()

def recherche_avec_expansion(requete, corpus, modele_embeddings, k=5, alpha=1.0, beta=0.5, mesure='cosinus'):
    """
    Description :
        Effectue une recherche documentaire en utilisant l'expansion de requête.
        1. Étend la requête avec des synonymes.
        2. Construit un vecteur pondéré (Requête + Expansion).
        3. Compare ce vecteur aux documents du corpus.

    Paramètres :
        requete           list : La requête tokenisée .
        corpus            list : Liste des documents.
        modele_embeddings object : Le modèle Word2Vec/Doc2Vec.
        k                 int : Nombre de documents à retourner.
        alpha, beta       float : Poids (Original vs Expansion).
        mesure            str : 'cosinus' ou 'euclidienne'.

    Retour :
        list : Top-K résultats [(score, document), ...]
    """
    
    synonymes = termes_expansion(requete, modele_embeddings, k=3)
    dictPoid = construire_requete_etendue(requete, synonymes, alpha, beta)
    dim = 0
    if hasattr(modele_embeddings, 'vector_size'):
        dim = modele_embeddings.vector_size
    else:
        dim = modele_embeddings.wv.vector_size
        
    vecRequete = np.zeros(dim)
    
    for mot, poids in dictPoid.items():
        if mot in modele_embeddings.wv:
            vec = modele_embeddings.wv[mot]
            vecRequete += vec * poids
    resultats = []
    
    for doc in corpus:
        score = similarite_documents(
            vecRequete, 
            doc,            
            modele_embeddings, 
            mesure=mesure
        )
        resultats.append((score, doc))
    trier = sorted(resultats, key=lambda x: x[0], reverse=True)
    return trier[:k]



def test_recherche_avec_expansion():
    print("\n Test : Recherche avec Expansion (Avant/Après) ")
    
    class MockModel:
        def __init__(self):
            self.vector_size = 2
            self.wv = self
            self.data = {
                "auto":    np.array([1.0, 0.0]),
                "voiture": np.array([0.9, 0.1]), 
                "vélo":    np.array([0.0, 1.0]), 
            }
        
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
        def most_similar(self, key, topn=3):
            if key == "auto": return [("voiture", 0.9)]
            return []

    mock = MockModel()
    
    # 2. Corpus
    corpus = [
        ["j'aime", "ma", "voiture"], 
        ["je", "fais", "du", "vélo"]
    ]
    
    requete = ["auto"] 
    
    # 3. Recherche SANS expansion (Simulation mentale)
    
    print(f"Requête utilisateur : {requete}")
    print("Lancement de la recherche étendue...")
    
    resultats = recherche_avec_expansion(requete, corpus, mock, k=1, alpha=1.0, beta=0.5)
    
    meilleur_score, meilleur_doc = resultats[0]
    print(f"Meilleur résultat : {meilleur_doc} (Score: {meilleur_score:.4f})")
    
    # Vérification
    assert "voiture" in meilleur_doc, "Le système aurait dû trouver le document parlant de voiture."
    assert meilleur_score > 0, "Le score doit être positif."
    
    print(" Le moteur a trouvé le synonyme grâce à l'expansion.")

#test_recherche_avec_expansion()

#c. Visualisation de l’espace sémantique pour l’expansion de requête
def mots_plus_proches(mot, modele_embeddings, k=20):
    """
    Description :
        Retourne les k mots les plus proches d'un mot donné dans l'espace sémantique,
        accompagnés de leur score de similarité .

    Paramètres :
        mot               str : Le mot de référence.
        modele_embeddings object : Le modèle Word2Vec/FastText/KeyedVectors.
        k                 int : Nombre de voisins à retourner.

    Retour :
        list of tuples : [(mot_voisin, score), ...] triés par score décroissant.
                         Retourne [] si le mot est inconnu.
    """
    if hasattr(modele_embeddings, 'wv'):
        wv = modele_embeddings.wv
    else:
        wv = modele_embeddings
        
    if mot not in wv:
        return []
        
    try:
        return wv.most_similar(mot, topn=k)
    except Exception as e:
        return []



def test_mots_plus_proches():
    print("\n Test : Voisinage Sémantique ")
    
    # 1. Mock Model
    class MockVectors:
        def __contains__(self, key): return key == "roi"
        def most_similar(self, key, topn=5):
            if key == "roi":
                return [
                    ("reine", 0.85), 
                    ("prince", 0.75), 
                    ("monarque", 0.70), 
                    ("royaume", 0.65), 
                    ("couronne", 0.60)
                ][:topn]
            return []
            
    class MockModel:
        def __init__(self): self.wv = MockVectors()
        
    mock = MockModel()
    
    # 2. Test sur mot connu
    mot_test = "roi"
    k_test = 3
    voisins = mots_plus_proches(mot_test, mock, k=k_test)
    
    print(f"Voisins de '{mot_test}' (Top {k_test}) :")
    for v, score in voisins:
        print(f"  - {v} ({score:.4f})")
        
    assert len(voisins) == k_test
    assert voisins[0][0] == "reine"
    
    # 3. Test sur mot inconnu
    voisins_inconnu = mots_plus_proches("blabla", mock)
    assert len(voisins_inconnu) == 0
    print(" Gestion mot inconnu validée.")

#test_mots_plus_proches()

def nuage_expansion_requete(mot, modele_embeddings, k=20):
    """
    Description :
        Génère un nuage de mots visualisant le "voisinage sémantique" d'un mot.
        Permet de voir quels termes seront utilisés pour l'expansion de la requête.

    Paramètres :
        mot               str : Le mot pivot de la requête.
        modele_embeddings object : Le modèle vectoriel.
        k                 int : Nombre de voisins à afficher.

    Retour :
        Affiche le graphique.
    """
    
    
    voisins = mots_plus_proches(mot, modele_embeddings, k=k)
    
    if not voisins:
        print(f"Pas d'expansion possible (le mot '{mot}' est probablement inconnu).")
        return
    dictPoid = dict(voisins)
    
    meilleur_score = voisins[0][1]
    dictPoid[mot] = meilleur_score * 1.1
    nuage_mots_pondere(dictPoid, largeur=600, hauteur=400, couleur_fond="white")



def test_nuage_expansion_requete():
    print("\n Test : Visualisation Expansion ")
    
    # 1. Mock Model
    class MockModel:
        def __init__(self):
            self.wv = self
        def __contains__(self, k): return True
        def most_similar(self, key, topn=5):
            return [
                ("pc", 0.90),
                ("machine", 0.80),
                ("processeur", 0.75),
                ("écran", 0.70),
                ("clavier", 0.60)
            ][:topn]

    mock = MockModel()
    
    print("Action : Affichage de l'expansion pour 'ordinateur'.")
    print("Vérifiez que 'ORDINATEUR' est le plus gros, entouré de 'PC', 'MACHINE'...")
    
    nuage_expansion_requete("ordinateur", mock, k=5)

#test_nuage_expansion_requete()

def comparer_expansion_requete(mot, modele_embeddings1, modele_embeddings2, k=20):
    """
    Description :
        Génère une figure comparant deux nuages de mots côte à côte 
        pour voir comment deux modèles interprètent le même mot.
        Retourne l'objet Figure.

    Paramètres :
        mot                str : Le mot à analyser.
        modele_embeddings1 object : Le premier modèle.
        modele_embeddings2 object : Le deuxième modèle.
        k                  int : Nombre de voisins à afficher.

    Retour :
        matplotlib.figure.Figure : L'objet graphique.
    """
    
    voisins1 = mots_plus_proches(mot, modele_embeddings1, k=k)
    voisins2 = mots_plus_proches(mot, modele_embeddings2, k=k)
    
    dict1 = dict(voisins1) if voisins1 else {}
    dict2 = dict(voisins2) if voisins2 else {}
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    if dict1:
        wc1 = WordCloud(width=400, height=300, background_color="white", colormap="viridis")
        wc1.generate_from_frequencies(dict1)
        axes[0].imshow(wc1, interpolation="bilinear")
        axes[0].set_title(f"Modèle 1 : Voisins de '{mot}'", fontsize=14, fontweight='bold')
    else:
        axes[0].text(0.5, 0.5, f"Mot '{mot}' inconnu\ndans Modèle 1", ha='center')
    axes[0].axis("off")

    if dict2:
        wc2 = WordCloud(width=400, height=300, background_color="white", colormap="plasma")
        wc2.generate_from_frequencies(dict2)
        axes[1].imshow(wc2, interpolation="bilinear")
        axes[1].set_title(f"Modèle 2 : Voisins de '{mot}'", fontsize=14, fontweight='bold')
    else:
        axes[1].text(0.5, 0.5, f"Mot '{mot}' inconnu\ndans Modèle 2", ha='center')
    axes[1].axis("off")

    plt.tight_layout()
    return fig

def test_comparer_expansion_requete():
    print("\n[TEST] Comparaison de Modèles (Polysémie) ")
    
    # Mock pour simuler le comportement des modèles (Word2Vec/Doc2Vec)
    class MockModel:
        def __init__(self, data):
            self.wv = self
            self.data = data
        def __contains__(self, k): return True
        def most_similar(self, key, topn=5):
            return self.data.get(key, [])[:topn]

    # Données simulées
    data_couleurs = {
        "orange": [("rouge", 0.9), ("jaune", 0.85), ("vert", 0.6), ("couleur", 0.5)]
    }
    data_telecom = {
        "orange": [("sfr", 0.9), ("bouygues", 0.85), ("réseau", 0.8), ("mobile", 0.7)]
    }
    
    modele_couleur = MockModel(data_couleurs)
    modele_telecom = MockModel(data_telecom)
    
    print("Action : Ouverture de la fenêtre comparative.")
    print("Gauche : Univers des couleurs (Rouge, Jaune...)")
    print("Droite : Univers des télécoms (SFR, Réseau...)")
    
    # --- MODIFICATION ICI ---
    # 1. Capture du résultat
    fig_compare = comparer_expansion_requete("orange", modele_couleur, modele_telecom, k=5)

    # 2. Affichage explicite
    if fig_compare:
        fig_compare.show()
        plt.show() # Bloque l'exécution jusqu'à la fermeture de la fenêtre
        print("Test terminé.")
    else:
        print("Erreur : Graphique non généré.")

# Lancement du test
#test_comparer_expansion_requete()
#5. Gestion des descripteurs et indexation
#a. Structuration des descripteurs (pré-indexation)


def initialiser_fiche_unite(id, type, texte, config):
    """
    Description :
        Crée une structure de données standardisée  pour une unité linguistique.
        Cette fiche servira de conteneur central pour tous les
        descripteurs et métadonnées futurs.

    Paramètres :
        id    : str ou int. Identifiant unique.
        type  : str. "document" ou "phrase".
        texte       : str ou list. Le contenu.
        config      : dict ou str. La configuration de prétraitement utilisée.

    Retour :
        dict : La fiche initialisée avec des conteneurs vides pour les descripteurs.
    """
    
    longueur = 0
    if isinstance(texte, list):
        longueur = len(texte)
    elif isinstance(texte, str):
        longueur = len(texte.split())
    
    fiche = {
        "id": id,
        "type": type,       
        
        #  Contenu 
        "texte": texte,           
        "config_id": config,      
        "descripteurs": {},       
        
        "parametres_calcul": {},
         
        "metadonnees": {
            "longueur": longueur,
            "langue": None,      
            "sous_corpus": None  
        },
        "statut": "initialisé" 
    }
    
    return fiche



def test_initialiser_fiche_unite():
    print("\n Test : Initialisation Fiche Unité ")
    texte_doc = ["le", "chat", "mange", "la", "souris"]
    config_doc = "config_standard_v1"
    fiche_doc = initialiser_fiche_unite("doc_1", "document", texte_doc, config_doc)
    print("Fiche Document créée :")
    print(fiche_doc)
    
    assert fiche_doc["type"] == "document"
    assert fiche_doc["metadonnees"]["longueur"] == 5
    assert fiche_doc["descripteurs"] == {} # Doit être vide au début
    print(" Structure Document validée.")

    # 2. Cas d'une Phrase
    texte_phrase = "Ceci est une phrase."
    fiche_phrase = initialiser_fiche_unite(101, "phrase", texte_phrase, config="brut")
    
    assert fiche_phrase["type"] == "phrase"
    assert fiche_phrase["id"] == 101
    print(" Structure Phrase validée.")

#test_initialiser_fiche_unite()

def initialiser_dictionnaire_global():
    """
    Description :
        Crée la structure de données principale vide.
        Cette structure servira de conteneur unique pour tout le projet.

    Retour :
        dict : La structure initialisée avec les sections 'documents', 'phrases' et 'meta'.
    """
    dico = {
        "documents": {}, 
        "phrases": {},   
        
        "meta": {
            "nom_projet": "Moteur de Recherche Vectoriel",
            "total_docs": 0,
            "total_phrases": 0,
        }
    }
    return dico


def test_initialiser_dictionnaire_global():
    print("\n Test : Fonction initialiser_dictionnaire_global ")
    dico_test = initialiser_dictionnaire_global()
    
    # 2. Vérifications structurelles
    assert isinstance(dico_test, dict), "Le résultat doit être un dictionnaire."
    
    # Vérifie la présence des clés principales
    assert "documents" in dico_test, "La clé 'documents' est manquante."
    assert "phrases" in dico_test, "La clé 'phrases' est manquante."
    assert "meta" in dico_test, "La clé 'meta' est manquante."
    
    # 3. Vérifications des valeurs initiales
    # Les conteneurs doivent être vides au départ
    assert len(dico_test["documents"]) == 0, "La section documents doit être vide."
    assert len(dico_test["phrases"]) == 0, "La section phrases doit être vide."
    
    # Les compteurs doivent être à 0
    assert dico_test["meta"]["total_docs"] == 0, "Le compteur total_docs doit être à 0."
    assert dico_test["meta"]["total_phrases"] == 0, "Le compteur total_phrases doit être à 0."
    
    # Vérifie le nom du projet
    assert dico_test["meta"]["nom_projet"] == "Moteur de Recherche Vectoriel"
    
    print(" initialiser_dictionnaire_global : Structure validée avec succès.")

#test_initialiser_dictionnaire_global()

def ajouter_fiche(dico, fiche):
    """
    Description :
        Insère une fiche unité dans le dictionnaire global.
        La fiche est rangée automatiquement dans 'documents' ou 'phrases' selon son type.
        Les compteurs globaux sont mis à jour.

    Paramètres :
        dico : dict. L'index global à modifier.
        fiche       : dict. La fiche unité à insérer.

    Retour :
        None (Modification en place).
    """
    if not isinstance(fiche, dict) or "id" not in fiche or "type" not in fiche:
        return

    id = fiche["id"]
    type = fiche["type"]

    if type == "document":
        if id not in dico["documents"]:
            dico["meta"]["total_docs"] += 1
        
        dico["documents"][id] = fiche

    elif type == "phrase":
        if id not in dico["phrases"]:
            dico["meta"]["total_phrases"] += 1
            
        dico["phrases"][id] = fiche

def test_ajouter_fiche():
    print("\n Test : Fonction ajouter_fiche ")
    dico_test = initialiser_dictionnaire_global()
    
    #  Cas 1 : Ajout d'un DOCUMENT valide 
    fiche_doc = {"id": "doc_01", "type": "document", "contenu": "test doc"}
    ajouter_fiche(dico_test, fiche_doc)
    
    assert "doc_01" in dico_test["documents"], "Le document doc_01 devrait être présent."
    assert dico_test["meta"]["total_docs"] == 1, "Le compteur docs devrait être à 1."
    
    #  Cas 2 : Ajout d'une PHRASE valide 
    fiche_phrase = {"id": "ph_01", "type": "phrase", "contenu": "test phrase"}
    ajouter_fiche(dico_test, fiche_phrase)
    
    assert "ph_01" in dico_test["phrases"], "La phrase ph_01 devrait être présente."
    assert dico_test["meta"]["total_phrases"] == 1, "Le compteur phrases devrait être à 1."
    
    #  Cas 3 : Mise à jour (Même ID) 
    fiche_doc_update = {"id": "doc_01", "type": "document", "contenu": "Mise à jour"}
    ajouter_fiche(dico_test, fiche_doc_update)
    
    assert dico_test["documents"]["doc_01"]["contenu"] == "Mise à jour", "Le contenu aurait dû être mis à jour."
    assert dico_test["meta"]["total_docs"] == 1, "Le compteur ne doit pas s'incrémenter lors d'une mise à jour."
    
    #  Cas 4 : Gestion d'erreur (Fiche invalide) 
    fiche_invalide = {"type": "document", "contenu": "pas d'id"}
    ajouter_fiche(dico_test, fiche_invalide)
    assert dico_test["meta"]["total_docs"] == 1 
    
    # Fiche avec type inconnu
    fiche_type_inconnu = {"id": "x", "type": "alien", "contenu": "E.T."}
    ajouter_fiche(dico_test, fiche_type_inconnu)
    assert "x" not in dico_test["documents"]
    assert "x" not in dico_test["phrases"]
    
    print(" ajouter_fiche : Insertion, mise à jour et gestion d'erreurs validées.")

#test_ajouter_fiche()


def filtrer_fiches(dico, langue=None, config_id=None, type=None):
    """
    Description :
        Extrait une liste de fiches du dictionnaire global correspondant aux critères fournis.
        Les critères à None sont ignorés .

    Paramètres :
        dico : dict. L'index global.
        langue      : str. Code langue stocké dans métadonnées.
        config_id   : str. ID de la configuration de prétraitement.
        type  : str. 'document' ou 'phrase'.

    Retour :
        list : Une liste de dictionnaires.
    """
    resultats = []
    source = []
    
    if type == "document":
        source = [dico["documents"]]
    elif type == "phrase":
        source = [dico["phrases"]]
    elif type is None:
        source = [dico["documents"], dico["phrases"]]
    else:
        return []

    for source in source:
        for fiche in source.values():
            
            if config_id is not None:
                if fiche.get("config_id") != config_id:
                    continue
            if langue is not None:
                meta = fiche.get("metadonnees", {})
                if meta.get("langue") != langue:
                    continue

            resultats.append(fiche)

    return resultats

def test_filtrer_fiches():
    print("\n Test : Fonction filtrer_fiches ")
    
    index_test = {
        "documents": {
            "d1": {"id": "d1", "type": "document", "config_id": "c1", "metadonnees": {"langue": "fr"}},
            "d2": {"id": "d2", "type": "document", "config_id": "c2", "metadonnees": {"langue": "en"}},
            "d3": {"id": "d3", "type": "document", "config_id": "c1", "metadonnees": {"langue": "en"}}
        },
        "phrases": {
            "p1": {"id": "p1", "type": "phrase", "config_id": "c1", "metadonnees": {"langue": "fr"}}
        },
        "meta": {}
    }
    
    # 2. Test filtre sur TYPE (Uniquement les phrases)
    res_phrases = filtrer_fiches(index_test, type="phrase")
    assert len(res_phrases) == 1
    assert res_phrases[0]["id"] == "p1"
    print(" Filtre Type : OK")

    # 3. Test filtre sur CONFIG (Tous les éléments avec config c1)
    res_conf = filtrer_fiches(index_test, config_id="c1")
    assert len(res_conf) == 3
    print(" Filtre Config : OK")

    # 4. Test filtre sur LANGUE (Tous les éléments en Anglais)
    res_lang = filtrer_fiches(index_test, langue="en")
    assert len(res_lang) == 2
    for r in res_lang:
        assert r["metadonnees"]["langue"] == "en"
    print(" Filtre Langue : OK")

    # 5. Test COMBO (Documents + Anglais + Config c1)
    # Seul d3 correspond à ces 3 critères
    res_combo = filtrer_fiches(index_test, type="document", langue="en", config_id="c1")
    assert len(res_combo) == 1
    assert res_combo[0]["id"] == "d3"
    print(" Filtre Combiné : OK")
    
    # 6. Test Aucun résultat
    res_vide = filtrer_fiches(index_test, langue="zh") # Chinois (inexistant)
    assert len(res_vide) == 0
    print(" Filtre Vide : OK")

#test_filtrer_fiches()

def initialiser_vocabulaire_embeddings(modele_embeddings):
    """
    Description :
        Extrait tous les vecteurs de mots du modèle
        et les stocke dans un dictionnaire standard Python.
        
        Cela permet :
        1. De découpler le reste du code de la librairie Gensim.
        2. D'accélérer les recherches simples.
        3. De faciliter l'expansion de requête .

    Paramètres :
        modele_embeddings : Objet Gensim.

    Retour :
        dict : Un dictionnaire { "mot": numpy.array([...]) }.
    """
    if hasattr(modele_embeddings, 'wv'):
        kv = modele_embeddings.wv
    else:
        kv = modele_embeddings

    dict = {}
    try:
        lmots = kv.index_to_key
    except AttributeError:
        if hasattr(kv, 'vocab'):
            lmots = list(kv.vocab.keys())
        else:
            lmots = list(kv.keys()) if isinstance(kv, dict) else []

    compteur = 0
    for mot in lmots:
        try:
            vecteur = kv[mot]
            dict[mot] = vecteur
            compteur += 1
        except KeyError:
            continue

    return dict

def test_initialiser_vocabulaire_embeddings():
    print("\n Test : Fonction initialiser_vocabulaire_embeddings ")
    
    # 1. Création d'un Mock 
    class MockKeyedVectors:
        def __init__(self):
            self.index_to_key = ["chat", "chien", "maison"]
            self.vectors_data = {
                "chat": np.array([1.0, 0.0]),
                "chien": np.array([0.9, 0.1]),
                "maison": np.array([0.0, 1.0])
            }
            
        def __getitem__(self, key):
            return self.vectors_data[key]

    class MockModel:
        def __init__(self):
            self.wv = MockKeyedVectors()

    modele_test = MockModel()

    print("Extraction des vecteurs...")
    dico_resultat = initialiser_vocabulaire_embeddings(modele_test)

    # 3. Vérifications
    # Vérifier le type
    assert isinstance(dico_resultat, dict), "Le résultat doit être un dictionnaire."
    
    # Vérifier la taille
    assert len(dico_resultat) == 3, "Le dictionnaire doit contenir 3 mots."
    
    # Vérifier le contenu
    assert "chat" in dico_resultat
    assert np.array_equal(dico_resultat["chat"], np.array([1.0, 0.0]))
    
    # Vérifier l'indépendance (optionnel mais bon pour la compréhension)
    # Si je supprime le modèle, le dictionnaire doit survivre
    del modele_test
    assert "chien" in dico_resultat
    
    print(" Extraction du vocabulaire validée.")

#test_initialiser_vocabulaire_embeddings()
#b. Calcul des descripteurs
#i. Principe général du calcul des descripteurs
#ii. Calcul des descripteurs symboliques

def appliquer_normalisation(vecteur, methode):
    """Applique une normalisation L1 ou L2 sur un vecteur numpy."""
    if methode is None:
        return vecteur
    
    norm = 0
    if methode == 'l1':
        norm = np.sum(np.abs(vecteur))
    elif methode == 'l2':
        norm = np.sqrt(np.sum(vecteur**2))
        
    if norm > 0:
        return vecteur / norm
    return vecteur

def calculer_bow_fiches(fiches, vocabulaire, type_bow="binaire", config_id=None, normalisation=None):
    """
    Calcule et stocke les vecteurs Bag-Of-Words directement dans les fiches.
    """
    if isinstance(vocabulaire, list):
        index = {mot: i for i, mot in enumerate(vocabulaire)}
    else:
        index = vocabulaire
        
    taille = len(index)

    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id:
            continue

        tokens = fiche.get("texte", [])
        if isinstance(tokens, str): tokens = tokens.split()
        vecteur = np.zeros(taille)
        for mot in tokens:
            if mot in index:
                vecteur[index[mot]] += 1
        
        if type_bow == "binaire":
            vecteur = (vecteur > 0).astype(float)

        vecteur = appliquer_normalisation(vecteur, normalisation)

        nom = f"bow_{type_bow}"
        fiche["descripteurs"][nom] = vecteur
        fiche["parametres_calcul"][nom] = {
            "type": type_bow, 
            "norm": normalisation, 
            "vocab_len": taille
        }
        
        fiche["statut"] = "calculé"

def calculer_tf_fiches(fiches, vocabulaire, config_id=None, normalisation=None):
    """
    Calcule et stocke les vecteurs TF.
    """
    calculer_bow_fiches(fiches, vocabulaire, type_bow="frequence", config_id=config_id, normalisation=None)
    
    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id: continue
        
        if "bow_frequence" in fiche["descripteurs"]:
            brute = fiche["descripteurs"]["bow_frequence"]
            transformer = appliquer_normalisation(brute, normalisation)
            fiche["descripteurs"]["tf"] = transformer
            fiche["parametres_calcul"]["tf"] = {"source": "bow_frequence", "norm": normalisation}
            fiche["statut"] = "calculé"


def calculer_tfidf_fiches(fiches, idf_vecteur, config_id=None, normalisation=None):
    """
    Calcule et stocke TF-IDF en utilisant le vecteur TF déjà présent dans la fiche.
    """
    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id: continue

        if "tf" in fiche["descripteurs"]:
            transformer = fiche["descripteurs"]["tf"]
            transformeridf = transformer * idf_vecteur
            transformeridf = appliquer_normalisation(transformeridf, normalisation)
            fiche["descripteurs"]["tfidf"] = transformeridf
            fiche["parametres_calcul"]["tfidf"] = {"source": "tf", "norm": normalisation}
            fiche["statut"] = "calculé"

def calculer_bm25_fiches(fiches, vocabulaire, stats_corpus, parametres_bm25, config_id=None, normalisation=None):
    """
    Calcule et stocke BM25.
    """
    if isinstance(vocabulaire, list):
        index = {mot: i for i, mot in enumerate(vocabulaire)}
    else:
        index = vocabulaire
        
    k1 = parametres_bm25.get("k1", 1.5)
    b = parametres_bm25.get("b", 0.75)
    avgdl = stats_corpus.get("avgdl", 10)
    idf_vecteur = stats_corpus.get("idf_vecteur", np.ones(len(index)))

    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id: continue

        tokens = fiche.get("texte", [])
        dl = len(tokens)
        transformer = np.zeros(len(index))
        for mot in tokens:
            if mot in index:
                transformer[index[mot]] += 1
        numerateur = transformer * (k1 + 1)
        denominateur = transformer + k1 * (1 - b + b * (dl / avgdl))
        vecbm25 = idf_vecteur * (numerateur / np.maximum(denominateur, 1e-6))
        vecbm25 = appliquer_normalisation(vecbm25, normalisation)
        fiche["descripteurs"]["bm25"] = vecbm25
        fiche["parametres_calcul"]["bm25"] = {
            "k1": k1, "b": b, "avgdl": avgdl, "norm": normalisation
        }
        fiche["statut"] = "calculé"

def test_calcul_descripteurs_direct():
    print("\n Test : Calculs avec stockage direct dans les fiches ")
    
    vocab = ["chat", "chien"]
    fiche = {
        "id": "doc1", 
        "type": "document", 
        "config_id": "c1", 
        "texte": ["chat", "chat", "chien"],
        "descripteurs": {}, 
        "parametres_calcul": {}, 
        "statut": "init"
    }
    
    calculer_bow_fiches([fiche], vocab, type_bow="binaire", config_id="c1")
    print(f"Descripteurs stockés : {fiche['descripteurs'].keys()}")
    assert "bow_binaire" in fiche["descripteurs"]
    assert fiche["descripteurs"]["bow_binaire"][0] == 1.0 # chat présent
    assert fiche["statut"] == "calculé"
    
    print(" Test validé : Les descripteurs sont bien ajoutés au dictionnaire.")

#test_calcul_descripteurs_direct()

#iii. Calcul des descripteurs vectoriels (embeddings)

def calculer_embeddings_phrases(fiches, modele_embeddings, config_id=None):
    """
    Description :
        Calcule le vecteur de chaque phrase en faisant la moyenne des vecteurs
        des mots qui la composent. Stocke le résultat directement dans la fiche.

    Paramètres :
        fiches            : list. Liste de fiches .
        modele_embeddings : object. Modèle Gensim.
        config_id         : str. Pour filtrer sur une config précise.
    """
    if hasattr(modele_embeddings, 'wv'):
        wv = modele_embeddings.wv
        vector_size = modele_embeddings.vector_size
    else:
        wv = modele_embeddings
        vector_size = getattr(modele_embeddings, 'vector_size', 100) 
    for fiche in fiches:
        if fiche.get("type") != "phrase": 
            continue
        if config_id and fiche.get("config_id") != config_id: 
            continue

        tokens = fiche.get("texte", [])
        if isinstance(tokens, str): tokens = tokens.split()
        vecMots = []
        for mot in tokens:
            if mot in wv:
                vecMots.append(wv[mot])
        
        if vecMots:
            vecMoyen = np.mean(vecMots, axis=0)
            norm = np.linalg.norm(vecMoyen)
            if norm > 0:
                vecMoyen = vecMoyen / norm
        else:
            vecMoyen = np.zeros(vector_size)
        nom = "embedding_moyenne"
        fiche["descripteurs"][nom] = vecMoyen
        
        fiche["parametres_calcul"][nom] = {
            "methode": "mean_pooling",
            "dim": vector_size,
            "nb_mots_trouves": len(vecMots)
        }
        fiche["statut"] = "calculé"

def test_calculer_embeddings_phrases():
    print("\n Test : Calcul Embeddings Phrases (Moyenne) ")
    class MockWV:
        def __init__(self):
            self.vector_size = 2
            self.data = {
                "chat": np.array([1.0, 0.0]),
                "dort": np.array([0.0, 1.0])
            }
        def __contains__(self, key): return key in self.data
        def __getitem__(self, key): return self.data[key]
        
    class MockModel:
        def __init__(self): self.wv = MockWV()
        
    mock_model = MockModel()

    # 2. Fiche Phrase Test
    fiche_phrase = {
        "id": "p1", 
        "type": "phrase", 
        "texte": ["chat", "dort", "inconnu"],
        "descripteurs": {}, 
        "parametres_calcul": {},
        "statut": "init"
    }
    
    calculer_embeddings_phrases([fiche_phrase], mock_model)    
    desc = fiche_phrase["descripteurs"]["embedding_moyenne"]
    print(f"Vecteur calculé : {desc}")
    
    # Vérifions la moyenne (après normalisation)

    assert len(desc) == 2
    assert desc[0] > 0 and desc[1] > 0
    assert np.isclose(desc[0], desc[1]) 
    # Vérifions les métadonnées
    params = fiche_phrase["parametres_calcul"]["embedding_moyenne"]
    assert params["nb_mots_trouves"] == 2
    print(" Calcul embedding phrase validé.")

#test_calculer_embeddings_phrases()

def calculer_embeddings_documents_mots(fiches, modele_embeddings, config_id=None):
    """
    Description :
        Calcule le vecteur de chaque document en faisant la moyenne des vecteurs
        des mots qui le composent.
        
        Cette approche est une baseline très robuste.
        Elle transforme une liste de mots de longueur variable en un vecteur de taille fixe.

    Paramètres :
        fiches            : list. Liste de fiches.
        modele_embeddings : object. Modèle Gensim.
    """
    
    if hasattr(modele_embeddings, 'wv'):
        wv = modele_embeddings.wv
    else:
        wv = modele_embeddings
    vector_size = getattr(wv, 'vector_size', 100)

    compteur = 0
    for fiche in fiches:
        if fiche.get("type") != "document": 
            continue
        if config_id and fiche.get("config_id") != config_id: 
            continue
        tokens = fiche.get("texte", [])
        if isinstance(tokens, str): tokens = tokens.split()
        vecMots = []
        ignores = 0
        
        for mot in tokens:
            if mot in wv:
                vecMots.append(wv[mot])
            else:
                ignores += 1
        if vecMots:
            vecDoc = np.mean(vecMots, axis=0)
            norm = np.linalg.norm(vecDoc)
            if norm > 0:
                vecDoc = vecDoc / norm
        else:
            vecDoc = np.zeros(vector_size)
        nom = "doc_embedding_moyenne"
        fiche["descripteurs"][nom] = vecDoc
        fiche["parametres_calcul"][nom] = {
            "methode": "mean_pooling_words",
            "dim": vector_size,
            "mots_utilises": len(vecMots),
            "ignores": ignores
        }
        fiche["statut"] = "calculé"
        compteur += 1
        


def test_calculer_embeddings_documents_mots():
    print("\n Test : Calcul Embeddings Documents (Agrégation) ")
    
    # 1. Mock Modèle (Dimension 3 pour changer)
    class MockModel:
        def __init__(self):
            self.vector_size = 3
            self.wv = self
            self.data = {
                "ia":    np.array([1.0, 0.0, 0.0]),
                "futur": np.array([0.0, 1.0, 0.0])
            }
        def __contains__(self, k): return k in self.data
        def __getitem__(self, k): return self.data[k]
        
    mock = MockModel()
    
    # 2. Fiche Document
    doc = {
        "id": "doc_science",
        "type": "document",
        "texte": ["l'", "ia", "est", "le", "futur"],
        "descripteurs": {},
        "parametres_calcul": {},
        "statut": "init"
    }
    calculer_embeddings_documents_mots([doc], mock)    
    vec = doc["descripteurs"]["doc_embedding_moyenne"]
    infos = doc["parametres_calcul"]["doc_embedding_moyenne"]
    
    print(f"Vecteur Document : {vec}")
    print(f"Infos : {infos}")
    
    assert len(vec) == 3
    assert infos["mots_utilises"] == 2
    assert infos["ignores"] == 3 
    assert vec[0] > 0 and vec[1] > 0
    
    print(" Agrégation document validée.")

#test_calculer_embeddings_documents_mots()

def calculer_embeddings_documents_phrases(fiches, modele_embeddings, config_id=None):
    """
    Description :
        Calcule le vecteur de chaque document en agrégeant les vecteurs de ses PHRASES.
        C'est une approche hiérarchique (Word -> Sentence -> Document).

    Prérequis :
        - Les fiches 'phrase' doivent déjà avoir un vecteur 'embedding_moyenne'.
        - Les fiches 'document' doivent avoir une liste 'idsPhrases' permettant
          de retrouver leurs phrases constituantes.
    
    Paramètres :
        fiches            : list. L'ensemble des fiches (documents ET phrases).
        modele_embeddings : object. Pour récupérer la dimension des vecteurs.
    """
    map = {}
    
    for fiche in fiches:
        if fiche.get("type") == "phrase":
            if "embedding_moyenne" in fiche.get("descripteurs", {}):
                map[fiche["id"]] = fiche["descripteurs"]["embedding_moyenne"]
    if hasattr(modele_embeddings, 'vector_size'):
        dim = modele_embeddings.vector_size
    elif hasattr(modele_embeddings, 'wv'):
        dim = modele_embeddings.wv.vector_size
    else:
        dim = 100
    compteur = 0
    for fiche in fiches:
        if fiche.get("type") != "document": 
            continue
        if config_id and fiche.get("config_id") != config_id: 
            continue
        idsPhrases = fiche.get("idsPhrases", [])
        
        vecteursCollection = []
        for pid in idsPhrases:
            if pid in map:
                vecteursCollection.append(map[pid])
        
        if vecteursCollection:
            vecDoc = np.mean(vecteursCollection, axis=0)
            
            norm = np.linalg.norm(vecDoc)
            if norm > 0:
                vecDoc = vecDoc / norm
        else:
            vecDoc = np.zeros(dim)

        nom = "doc_embedding_hierarchique"
        fiche["descripteurs"][nom] = vecDoc
        fiche["parametres_calcul"][nom] = {
            "methode": "mean_pooling_sentences",
            "dim": dim,
            "nbPhrases_utilisees": len(vecteursCollection)
        }
        fiche["statut"] = "calculé"
        compteur += 1

def test_calculer_embeddings_documents_phrases():
    print("\n Test : Calcul Hiérarchique (Doc <- Phrases) ")
    
    class MockModel:
        def __init__(self): self.vector_size = 2
    mock = MockModel()
    phrase1 = {
        "id": "p1", "type": "phrase",
        "descripteurs": {"embedding_moyenne": np.array([1.0, 0.0])}
    }
    phrase2 = {
        "id": "p2", "type": "phrase",
        "descripteurs": {"embedding_moyenne": np.array([0.0, 1.0])}
    }
    doc = {
        "id": "d1", "type": "document",
        "idsPhrases": ["p1", "p2"], 
        "descripteurs": {}, "parametres_calcul": {}, "statut": "init"
    }
    tout_le_monde = [phrase1, phrase2, doc]
    calculer_embeddings_documents_phrases(tout_le_monde, mock)
    
    # 4. Vérification
    # Moyenne([1,0], [0,1]) = [0.5, 0.5]. Normalisé -> [0.707, 0.707]
    vec = doc["descripteurs"]["doc_embedding_hierarchique"]
    infos = doc["parametres_calcul"]["doc_embedding_hierarchique"]
    
    print(f"Vecteur Document Hiérarchique : {vec}")
    
    assert len(vec) == 2
    assert infos["nbPhrases_utilisees"] == 2
    assert np.isclose(vec[0], 0.707, atol=0.01)
    
    print(" Agrégation hiérarchique validée.")

#test_calculer_embeddings_documents_phrases()

def calculer_embeddings_documents_doc2vec(fiches, modele_doc2vec, config_id=None):
    """
    Description :
        Utilise un modèle Doc2Vec pré-entraîné pour inférer le vecteur d'un document
        à partir de sa liste de tokens.
        
        Contrairement à la moyenne des mots, Doc2Vec tente de capturer
        le contexte global du paragraphe/document.

    Paramètres :
        fiches         : list. Liste des fiches documents.
        modele_doc2vec : object. Modèle Gensim Doc2Vec entraîné.
        config_id      : str. Filtre optionnel.
    """
    vector_size = getattr(modele_doc2vec, 'vector_size', 100)
    compteur = 0

    for fiche in fiches:
       
        if fiche.get("type") != "document": 
            continue
        if config_id and fiche.get("config_id") != config_id: 
            continue
        tokens = fiche.get("texte", [])
        if isinstance(tokens, str): tokens = tokens.split()
        
        try:
            vecDoc = modele_doc2vec.infer_vector(tokens)
            norm = np.linalg.norm(vecDoc)
            if norm > 0:
                vecDoc = vecDoc / norm
                
        except Exception as e:
            print(f"Erreur inférence Doc2Vec sur {fiche.get('id')}: {e}")
            vecDoc = np.zeros(vector_size)
        nom = "doc2vec"
        fiche["descripteurs"][nom] = vecDoc
        
        fiche["parametres_calcul"][nom] = {
            "methode": "doc2vec_inference",
            "dim": vector_size,
        }
        fiche["statut"] = "calculé"
        compteur += 1

def test_calculer_embeddings_documents_doc2vec():
    print("\n Test : Inférence Doc2Vec ")
    
    # 1. Mock du Modèle Doc2Vec 
    class MockDoc2Vec:
        def __init__(self):
            self.vector_size = 4
        
        def infer_vector(self, tokens):
            val = len(tokens)
            return np.array([val, val*0.1, 1.0, 0.0])

    mock_model = MockDoc2Vec()
    
    doc = {
        "id": "doc_inconnu",
        "type": "document",
        "texte": ["ceci", "est", "un", "test"],
        "descripteurs": {},
        "parametres_calcul": {},
        "statut": "init"
    }
    calculer_embeddings_documents_doc2vec([doc], mock_model)
    vec = doc["descripteurs"]["doc2vec"]
    print(f"Vecteur Doc2Vec inféré : {vec}")
    
    # Le mock retourne [4, 0.4, 1.0, 0.0] avant normalisation
    assert len(vec) == 4
    assert vec[0] > 0 
    assert np.isclose(np.linalg.norm(vec), 1.0) 
    print(" Inférence Doc2Vec validée.")

#test_calculer_embeddings_documents_doc2vec()

#c. Indexation des descripteurs
#i. Indexation symbolique et vectorielle (vues matricielles)


def construire_index_symbolique(fiches, typeDescripteur, config_id=None):
    """
    Description :
        Construit une vue matricielle à partir d'une liste de fiches.
        Utilise une matrice creuse pour stocker efficacement les données.

    Paramètres :
        fiches           : list. Liste des fiches .
        typeDescripteur : str. Le nom du descripteur à indexer.
        config_id        : str. Filtre sur la configuration de prétraitement.

    Retour :
        dict : Structure d'index contenant :
               - 'matrice': scipy.sparse.csr_matrix
               - 'mapping': dict {idFiche -> index_ligne}
               - 'ids': list [idFiche]
               - 'meta': dict (infos sur le descripteur)
    """
    collectes = []
    ids = []
    mapping = {}
    meta = {} 

    index = 0
    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id:
            continue
        
        descripteurs = fiche.get("descripteurs", {})
        if typeDescripteur not in descripteurs:
            continue
            
        vecteur = descripteurs[typeDescripteur]
        
        if not meta:
            params = fiche.get("parametres_calcul", {}).get(typeDescripteur, {})
            meta = params
        
        collectes.append(vecteur)
        
        cur = fiche["id"]
        ids.append(cur)
        mapping[cur] = index
        index += 1

    if not collectes:
        return None
    try:
        matrice_sparse = csr_matrix(collectes)
    except Exception as e:
        return None
    symbolique = {
        "type": "symbolique",
        "descripteur_cible": typeDescripteur,
        "matrice": matrice_sparse,  
        "mapping": mapping,          
        "ids": ids,        
        "meta": meta            
    }
    
    return symbolique

def test_construire_index_symbolique():
    print("\n Test : Construction Index Symbolique (Sparse) ")
    d1 = {"id": "d1", "config_id": "c1", "descripteurs": {"tfidf": np.array([1., 0., 0., 1.])}}
    d2 = {"id": "d2", "config_id": "c1", "descripteurs": {"tfidf": np.array([0., 1., 1., 0.])}}
    d3 = {"id": "d3", "config_id": "c2", "descripteurs": {"tfidf": np.array([1., 1., 1., 1.])}}
    corpus = [d1, d2, d3]
    
    index = construire_index_symbolique(corpus, "tfidf", config_id="c1")
    
    # 3. Vérifications
    assert index is not None
    
    # Vérif Matrice
    matrice = index["matrice"]
    assert matrice.shape == (2, 4)
    # Vérifions que c'est bien une matrice creuse
    assert isinstance(matrice, csr_matrix)
    
    # Vérif Mapping
    assert index["mapping"]["d1"] == 0
    assert index["mapping"]["d2"] == 1 
    assert "d3" not in index["mapping"] 
    dense_check = matrice.toarray()
    assert dense_check[0, 0] == 1.0 
    print(" Index symbolique construit et validé.")

#test_construire_index_symbolique()


def construire_index_embeddings(fiches, type_embeddings, config_id=None):
    """
    Description :
        Construit une vue matricielle pour les embeddings.
        Utilise une matrice dense car les embeddings ne contiennent pas de zéros.

    Paramètres :
        fiches          : list. Liste des fiches.
        type_embeddings : str. Nom du descripteur.
        config_id       : str. Filtre.

    Retour :
        dict : Structure d'index contenant :
               - 'matrice': numpy.ndarray
               - 'mapping': dict {idFiche -> index_ligne}
               - 'ids': list [idFiche]
               - 'meta': dict
    """
    collectes = []
    ids = []
    mapping = {}
    meta = {}
    
    index = 0
    
    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id:
            continue
            
        descripteurs = fiche.get("descripteurs", {})
        if type_embeddings not in descripteurs:
            continue
            
        vecteur = descripteurs[type_embeddings]
        
        if not isinstance(vecteur, (np.ndarray, list)):
            continue
            
        if not meta:
            meta = fiche.get("parametres_calcul", {}).get(type_embeddings, {})

        collectes.append(vecteur)
        
        cur = fiche["id"]
        ids.append(cur)
        mapping[cur] = index
        index += 1

    if not collectes:
        return None
    try:
        matrice = np.array(collectes)
    except Exception as e:
        return None

    indVectoriel = {
        "type": "indVectoriel",
        "descripteur_cible": type_embeddings,
        "matrice": matrice,
        "mapping": mapping,
        "ids": ids,
        "meta": meta
    }
    
    return indVectoriel


def test_construire_index_embeddings():
    print("\n Test : Construction Index Vectoriel (Dense) ")
    d1 = {"id": "d1", "config_id": "c1", "descripteurs": {"doc2vec": np.array([0.5, 0.5])}}
    d2 = {"id": "d2", "config_id": "c1", "descripteurs": {"doc2vec": np.array([-0.1, 0.9])}}
    d3 = {"id": "d3", "config_id": "c1", "descripteurs": {}}
    
    corpus = [d1, d2, d3]
    index = construire_index_embeddings(corpus, "doc2vec", config_id="c1")
    
    # 3. Vérifications
    assert index is not None
    
    matrice = index["matrice"]
    # On attend 2 documents (d3 ignoré) x 2 dimensions
    assert matrice.shape == (2, 2)
    
    # Vérification que c'est bien du numpy standard
    assert isinstance(matrice, np.ndarray)
    
    # Vérification Mapping
    assert index["mapping"]["d1"] == 0
    assert index["mapping"]["d2"] == 1
    
    print(" Index vectoriel construit et validé.")

#test_construire_index_embeddings()

def mettre_a_jour_index_embeddings(index_embeddings, fiche):
    """
    Description :
        Ajoute dynamiquement une nouvelle fiche à un index vectoriel existant.
        Met à jour la matrice , la liste des IDs et le mapping.

    Paramètres :
        index_embeddings : dict. La structure d'index.
        fiche            : dict. La fiche unité contenant le vecteur à ajouter.

    Retour :
        bool : True si la mise à jour a réussi, False sinon.
    """
    nomripteur = index_embeddings.get("descripteur_cible")
    if not nomripteur:
        return False
    if nomripteur not in fiche.get("descripteurs", {}):
        print(f"Erreur : La fiche {fiche.get('id')} ne contient pas le descripteur '{nomripteur}'.")
        return False

    nouveau_vecteur = fiche["descripteurs"][nomripteur]
    idFiche = fiche["id"]
    matrices = index_embeddings["matrice"]
    dim = matrices.shape[1]
    if not isinstance(nouveau_vecteur, np.ndarray):
        nouveau_vecteur = np.array(nouveau_vecteur)
    if len(nouveau_vecteur) != dim:
        return False

    if idFiche in index_embeddings["mapping"]:
        return False
    try:
        index_embeddings["matrice"] = np.vstack([matrices, nouveau_vecteur])
    except Exception as e:
        return False
    nouvelle = len(index_embeddings["ids"])
    index_embeddings["ids"].append(idFiche)
    index_embeddings["mapping"][idFiche] = nouvelle    
    return True

def test_mettre_a_jour_index_embeddings():
    print("\n Test : Mise à jour Incrémentale Index ")
    matrice_init = np.array([
        [1.0, 0.0],
        [0.0, 1.0] 
    ])
    index = {
        "descripteur_cible": "vec",
        "matrice": matrice_init,
        "ids": ["docA", "docB"],
        "mapping": {"docA": 0, "docB": 1}
    }
    
    nouvelle_fiche = {
        "id": "docC",
        "descripteurs": {"vec": np.array([0.5, 0.5])}
    }
    print("Avant maj :", index["matrice"].shape)
    succes = mettre_a_jour_index_embeddings(index, nouvelle_fiche)
    print("Après maj :", index["matrice"].shape)
    
    # 4. Vérifications
    assert succes is True
    assert index["matrice"].shape == (3, 2), "La matrice doit avoir 3 lignes."
    assert index["mapping"]["docC"] == 2, "Le docC doit être à la ligne 2."
    assert index["ids"][2] == "docC"
    
    # Vérification du contenu du vecteur ajouté
    assert np.allclose(index["matrice"][2], [0.5, 0.5])
    
    print(" Mise à jour incrémentale validée.")

#test_mettre_a_jour_index_embeddings()

def mettre_a_jour_index_symbolique(symbolique, fiche):
    """
    Description :
        Ajoute dynamiquement une nouvelle fiche à un index symbolique.
        Utilise vstack pour empiler le nouveau vecteur creux ou dense.

    Paramètres :
        symbolique : dict. La structure d'index existante.
        fiche            : dict. La fiche unité à ajouter.

    Retour :
        bool : True si succès, False sinon.
    """
    nomripteur = symbolique.get("descripteur_cible")
    if not nomripteur:
        return False

    if nomripteur not in fiche.get("descripteurs", {}):
        return False

    newVect = fiche["descripteurs"][nomripteur]
    idFiche = fiche["id"]
    
    matrices = symbolique["matrice"]
    nbcol = matrices.shape[1]

    try:
        if not issparse(newVect):
            vecSparse = csr_matrix(newVect)
        else:
            vecSparse = newVect
            
        if vecSparse.shape[1] != nbcol:
            if vecSparse.shape[0] == 1 and vecSparse.shape[1] == nbcol:
                pass
            elif vecSparse.shape[0] == nbcol and vecSparse.shape[1] == 1:
                
                vecSparse = vecSparse.T
            elif vecSparse.shape[1] != nbcol:
                return False
                
    except Exception as e:
        return False

    if idFiche in symbolique["mapping"]:
        return False    
    try:
        newMatrice = vstack([matrices, vecSparse]).tocsr()
        symbolique["matrice"] = newMatrice
    except Exception as e:
        return False

    nouvelle = len(symbolique["ids"])
    symbolique["ids"].append(idFiche)
    symbolique["mapping"][idFiche] = nouvelle    
    return True

def test_mettre_a_jour_index_symbolique():
    print("\n Test : Mise à jour Incrémentale Symbolique ")
    data_init = csr_matrix([
        [1, 0, 1],
        [0, 1, 0]
    ])
    index = {
        "descripteur_cible": "bow",
        "matrice": data_init,
        "ids": ["docA", "docB"],
        "mapping": {"docA": 0, "docB": 1}
    }
    
    nouveau_vec = np.array([1, 1, 1])
    fiche = {
        "id": "docC",
        "descripteurs": {"bow": nouveau_vec}
    }
    succes = mettre_a_jour_index_symbolique(index, fiche)
    
    # 4. Vérifications
    assert succes is True
    assert index["matrice"].shape == (3, 3)
    assert index["ids"][-1] == "docC"
    
    # Vérifions une valeur précise dans la matrice sparse
    assert index["matrice"][2, 1] == 1
    
    print(" Ajout sparse validé.")

#test_mettre_a_jour_index_symbolique()

#ii. Indexation opérationnelle
#1) Pré-calculs liés aux mesures de similarité vectorielles


def precalculer_normes_embeddings(index_embeddings):
    """
    Description :
        Calcule à l'avance la norme Euclidienne de chaque vecteur de la matrice.
        Stocke ces normes dans l'index pour accélérer le calcul du Cosinus plus tard.
        
        Optimisation : Si les vecteurs sont déjà normalisés, cette étape
        permet de le vérifier ou de traiter ceux qui ne le sont pas.

    Paramètres :
        index_embeddings : dict. Structure d'index contenant une clé 'matrice'.

    Retour :
        None (Ajoute la clé 'normes' dans l'index).
    """
    if "matrice" not in index_embeddings:
        return

    matrice = index_embeddings["matrice"]
    
    try:
        normes = np.linalg.norm(matrice, axis=1, ord=2)
        index_embeddings["normes"] = normes
        
    except Exception as e:
        return None

def test_precalculer_normes_embeddings():
    print("\n Test : Pré-calcul des Normes ")
    
    matrice = np.array([
        [3.0, 4.0],
        [1.0, 0.0]
    ])
    
    index = {
        "matrice": matrice,
        "ids": ["docA", "docB"]
    }
    
    precalculer_normes_embeddings(index)
    assert "normes" in index, "La clé 'normes' doit être présente."
    normes = index["normes"]
    
    print(f"Normes calculées : {normes}")
    
    # Vérif Doc A
    assert np.isclose(normes[0], 5.0), "La norme de [3, 4] doit être 5."
    # Vérif Doc B
    assert np.isclose(normes[1], 1.0), "La norme de [1, 0] doit être 1."
    
    print(" Pré-calcul validé.")

#test_precalculer_normes_embeddings()

def precalculer_normes_symboliques(symbolique):
    """
    Description :
        Calcule les normes Euclidiennes des vecteurs d'une matrice creuse.
        Stocke le résultat pour accélérer le calcul de similarité Cosinus.

        Méthode :
        Pour une matrice creuse, on évite de la densifier. On utilise :
        Norme = sqrt( somme( carrés des éléments ) ) par ligne.

    Paramètres :
        symbolique : dict. Structure contenant 'matrice'.

    Retour :
        None (Modification en place).
    """
    if "matrice" not in symbolique:
        return

    matrice = symbolique["matrice"]

    if not issparse(matrice):
        symbolique["normes"] = np.linalg.norm(matrice, axis=1)
        return
    try:
        carres = matrice.power(2)
        sommes = carres.sum(axis=1)
        normes = np.sqrt(np.array(sommes).flatten())
        symbolique["normes"] = normes

    except Exception as e:
        return None

def test_precalculer_normes_symboliques():
    print("\n Test : Pré-calcul Normes Symboliques (Sparse) ")
    data = csr_matrix([
        [3.0, 0.0, 4.0],
        [0.0, 1.0, 0.0]
    ])
    
    index = {
        "matrice": data,
        "ids": ["docA", "docB"]
    }
    
    precalculer_normes_symboliques(index)    
    assert "normes" in index
    normes = index["normes"]
    
    print(f"Normes calculées : {normes}")
    
    # Vérification des valeurs
    assert np.isclose(normes[0], 5.0)
    assert np.isclose(normes[1], 1.0)
    
    # Vérification de la forme (doit être un array 1D, pas une matrice colonne)
    assert normes.shape == (2,) or normes.shape == (2)
    
    print(" Pré-calcul sparse validé.")

#test_precalculer_normes_symboliques()

#2) Pré-calculs spécifiques aux modèles symboliques

def construire_inverse(fiches, typeDescripteur, config_id=None):
    """
    Description :
        Construit un index inversé associant chaque terme
        à la liste des documents qui le contiennent, avec leur pondération.
        
        Structure de retour :
        {
            index_terme_0: [(id_doc_A, poids), (id_doc_B, poids)],
            index_terme_1: [(id_doc_C, poids)],
            ...
        }

    Paramètres :
        fiches           : list. Liste des fiches documents.
        typeDescripteur : str. Le nom du descripteur (ex: 'tff', 'bow_binaire').
        config_id        : str. Filtre sur la configuration.

    Retour :
        dict : L'index inversé.
    """
    
    inverse = {}
    nb = 0

    for fiche in fiches:
        if config_id and fiche.get("config_id") != config_id:
            continue
            
        descripteurs = fiche.get("descripteurs", {})
        if typeDescripteur not in descripteurs:
            continue
            
        vecteur = descripteurs[typeDescripteur]
        id_doc = fiche["id"]
        nb += 1
        i = []
        valeurs = []

        if issparse(vecteur):
            _, i = vecteur.nonzero()
            valeurs = vecteur.data
            
        elif isinstance(vecteur, np.ndarray):
            i = np.nonzero(vecteur)[0]
            valeurs = vecteur[i]
            
        elif isinstance(vecteur, list):
            vecArr = np.array(vecteur)
            i = np.nonzero(vecArr)[0]
            valeurs = vecArr[i]
        for i, j in enumerate(i):
            poids = values = valeurs[i]
            cle = int(j)
            
            if cle not in inverse:
                inverse[cle] = []
            inverse[cle].append((id_doc, poids))

    return inverse

def test_construire_inverse():
    print("\n Test : Construction Index Inversé ")
    d1 = {
        "id": "D1", "config_id": "c1", 
        "descripteurs": {"bow": np.array([1, 1, 0, 0])}
    }
    d2 = {
        "id": "D2", "config_id": "c1", 
        "descripteurs": {"bow": np.array([0, 0, 1, 0])}
    }
    d3 = {
        "id": "D3", "config_id": "c1", 
        "descripteurs": {"bow": np.array([1, 0, 1, 0])}
    }

    corpus = [d1, d2, d3]
    idx_inv = construire_inverse(corpus, "bow", config_id="c1")
    
    # 3. Vérifications
    
    # Test pour le terme "chat" (index 0)
    assert 0 in idx_inv
    docs_chat = [entry[0] for entry in idx_inv[0]]
    assert "D1" in docs_chat
    assert "D3" in docs_chat
    assert "D2" not in docs_chat
    
    # Test pour le terme "blanc" (index 2)
    # Présent dans D2 et D3
    assert 2 in idx_inv
    docs_blanc = [entry[0] for entry in idx_inv[2]]
    assert "D2" in docs_blanc
    assert "D3" in docs_blanc
    
    # Vérification des poids
    # Dans D1, le poids de "chat" (index 0) est 1
    found_weight = False
    for id, weight in idx_inv[0]:
        if id == "D1":
            assert weight == 1
            found_weight = True
    assert found_weight
    
    print(" Index inversé validé.")

#test_construire_inverse()

#d. Persistance

def sauvegarder_fiches(fichier, dictionnaire_global):
    """
    Description :
        Sauvegarde le dictionnaire global sur le disque.
        
        Utilise le format 'pickle' qui est idéal pour conserver les types de données
        sans avoir besoin de conversions manuelles.

    Paramètres :
        fichier             : str. Le chemin du fichier de destination.
        dictionnaire_global : dict. L'objet à sauvegarder.

    Retour :
        bool : True si succès, False en cas d'erreur d'écriture.
    """
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError as e:
            return False

    try:
        with open(fichier, 'wb') as f:
            pickle.dump(dictionnaire_global, f)
            
        taille = os.path.getsize(fichier) / (1024 * 1024)
        return True
        
    except Exception as e:
        return False

def test_sauvegarder_fiches():
    print("\n Test : Sauvegarde sur disque (Pickle) ")
    
    data_test = {
        "documents": {
            "d1": {
                "id": "d1", 
                "texte": "test persistence", 
                "vecteur": np.array([0.1, 0.2, 0.3])
            }
        },
        "meta": {"projet": "Test Persistance"}
    }
    
    nomf = "test_data_fiches.pkl"
    succes = sauvegarder_fiches(nomf, data_test)
    
    # 3. Vérifications
    assert succes is True
    assert os.path.exists(nomf), "Le fichier n'a pas été créé."
    
    # Petite vérification de la taille (ne doit pas être vide)
    assert os.path.getsize(nomf) > 0
    
    print(" Fichier créé avec succès.")
    if os.path.exists(nomf):
        os.remove(nomf)
        print("  (Fichier test nettoyé)")

#test_sauvegarder_fiches()

def sauvegarder_fiche_unitaire(fichier, fiche):
    """
    Description :
        Sauvegarde une fiche unique à la fin d'un fichier existant,
        UNIQUEMENT si son statut est 'calculé'.
        
        Cela permet de créer un journal des modifications ou d'ajouter des documents
        au fil de l'eau sans réécrire toute la base de données.

    Paramètres :
        fichier : str. Chemin du fichier de destination.
        fiche   : dict. La fiche unité à sauvegarder.

    Retour :
        bool : True si sauvegardé, False sinon.
    """
    if fiche.get("statut") != "calculé":
        return False

    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError:
            pass 

    try:
        with open(fichier, 'ab') as f:
            pickle.dump(fiche, f)
            
        return True

    except Exception as e:
        return False


def test_sauvegarder_fiche_unitaire():
    print("\n Test : Sauvegarde Unitaire (Append) ")
    fichier_test = "test_journal_fiches.pkl"
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)
    
    # Cas 1 : Fiche valide (calculée)
    fiche_valide = {"id": "doc1", "statut": "calculé", "data": "A"}
    res1 = sauvegarder_fiche_unitaire(fichier_test, fiche_valide)
    
    # Cas 2 : Fiche invalide (init)
    fiche_invalide = {"id": "doc2", "statut": "init", "data": "B"}
    res2 = sauvegarder_fiche_unitaire(fichier_test, fiche_invalide)
    
    # Cas 3 : Autre fiche valide
    fiche_valide_2 = {"id": "doc3", "statut": "calculé", "data": "C"}
    res3 = sauvegarder_fiche_unitaire(fichier_test, fiche_valide_2)

    # Vérifications
    assert res1 is True
    assert res2 is False
    assert res3 is True
    
    donnees_relues = []
    with open(fichier_test, 'rb') as f:
        while True:
            try:
                obj = pickle.load(f)
                donnees_relues.append(obj)
            except EOFError:
                break
    
    print(f"Objets relus : {len(donnees_relues)}")
    assert len(donnees_relues) == 2 # doc1 et doc3 uniquement
    assert donnees_relues[0]["id"] == "doc1"
    assert donnees_relues[1]["id"] == "doc3"
    
    print(" Sauvegarde unitaire incrémentale validée.")
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_sauvegarder_fiche_unitaire()

def sauvegarder_fiches_calculees(dico, dossier_sortie):
    """
    Description :
        Parcourt tout le dictionnaire global.
        Pour chaque fiche ayant le statut 'calculé', génère un nom de fichier unique
        et appelle la fonction de sauvegarde unitaire.

    Paramètres :
        dico    : dict. L'index global contenant les fiches.
        dossier_sortie : str. Le dossier où stocker les fichiers.

    Retour :
        int : Le nombre total de fiches sauvegardées.
    """
    if not os.path.exists(dossier_sortie):
        try:
            os.makedirs(dossier_sortie)
        except OSError as e:
            return 0
    compteur = 0
    sources = [dico.get("documents", {}), dico.get("phrases", {})]
    for source in sources:
        for idFiche, fiche in source.items():
            if fiche.get("statut") == "calculé":
                type = fiche.get("type", "inconnu")
                nomf = f"{type}_{idFiche}.pkl"
                ch = os.path.join(dossier_sortie, nomf)
                if os.path.exists(ch):
                    try:
                        os.remove(ch)
                    except OSError:
                        pass

                succes = sauvegarder_fiche_unitaire(ch, fiche)
                
                if succes:
                    compteur += 1
    return compteur
def test_sauvegarder_fiches_calculees():
    print("\n Test : Sauvegarde en Masse (Parcours Global) ")
    dossier_test = "test_output_fiches"
    dico_test = {
        "documents": {
            "d1": {"id": "d1", "type": "document", "statut": "calculé", "data": "A"}, # OK
            "d2": {"id": "d2", "type": "document", "statut": "init", "data": "B"}     # Ignoré
        },
        "phrases": {
            "p1": {"id": "p1", "type": "phrase", "statut": "calculé", "data": "C"}    # OK
        },
        "meta": {}
    }
    nb = sauvegarder_fiches_calculees(dico_test, dossier_test)
    
    # 3. Vérifications
    assert nb == 2, f"Attendu 2 sauvegardes, obtenu {nb}."
    
    fichier_d1 = os.path.join(dossier_test, "document_d1.pkl")
    fichier_p1 = os.path.join(dossier_test, "phrase_p1.pkl")
    fichier_d2 = os.path.join(dossier_test, "document_d2.pkl")
    
    assert os.path.exists(fichier_d1), "Le fichier d1 manque."
    assert os.path.exists(fichier_p1), "Le fichier p1 manque."
    assert not os.path.exists(fichier_d2), "Le fichier d2 ne devrait pas exister (statut init)."
    
    print(" Sauvegarde en masse validée.")
    import shutil
    if os.path.exists(dossier_test):
        shutil.rmtree(dossier_test)
        print("  (Dossier test nettoyé)")

#test_sauvegarder_fiches_calculees()

def sauvegarder_index_symbolique(fichier, symbolique):
    """
    Description :
        Sauvegarde une structure d'index symbolique
        sur le disque.
        
        Utilise le format Pickle pour préserver le type exact de la matrice
        et les dictionnaires de mapping associés.

    Paramètres :
        fichier          : str. Chemin du fichier de destination.
        symbolique : dict. La structure d'index.

    Retour :
        bool : True si succès, False sinon.
    """
    if not isinstance(symbolique, dict):
        return False
    
    if "matrice" not in symbolique or "mapping" not in symbolique:
        return False
    matrice = symbolique["matrice"]
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError:
            pass
    try:
        with open(fichier, 'wb') as f:
            pickle.dump(symbolique, f)
            
        taille = os.path.getsize(fichier) / (1024 * 1024)
        return True

    except Exception as e:
        return False

def test_sauvegarder_index_symbolique():
    print("\n Test : Sauvegarde Index Symbolique ")
    fichier_test = "test_index_symb.pkl"
    matrice = csr_matrix([
        [1, 0, 2],
        [0, 1, 0]
    ])
    
    index_test = {
        "type": "symbolique",
        "descripteur_cible": "tff",
        "matrice": matrice,
        "mapping": {"d1": 0, "d2": 1},
        "ids": ["d1", "d2"],
        "vocabulaire": {"chat": 0, "chien": 1, "mange": 2}
    }
    succes = sauvegarder_index_symbolique(fichier_test, index_test)
    assert succes is True
    
    with open(fichier_test, 'rb') as f:
        index_relu = pickle.load(f)
        
    matrice_relue = index_relu["matrice"]
    
    # Vérifications
    assert issparse(matrice_relue), "La matrice relue doit rester sparse."
    assert matrice_relue.shape == (2, 3)
    assert index_relu["mapping"]["d1"] == 0
    # Vérification d'une valeur dans la matrice
    assert matrice_relue[0, 2] == 2
    
    print(" Sauvegarde et rechargement de l'index symbolique validés.")
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_sauvegarder_index_symbolique()

def sauvegarder_index_embeddings(fichier, index_embeddings):
    """
    Description :
        Sauvegarde une structure d'index vectoriel sur le disque.
        
        Permet de persister les embeddings pré-calculés et les structures associées.

    Paramètres :
        fichier          : str. Chemin du fichier de destination.
        index_embeddings : dict. La structure d'index.

    Retour :
        bool : True si succès, False sinon.
    """
    if not isinstance(index_embeddings, dict):
        return False
    
    if "matrice" not in index_embeddings or "mapping" not in index_embeddings:
        return False

    matrice = index_embeddings["matrice"]
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError:
            pass
    try:
        with open(fichier, 'wb') as f:
            pickle.dump(index_embeddings, f)
            
        taille = os.path.getsize(fichier) / (1024 * 1024)
        
        dims = matrice.shape if hasattr(matrice, 'shape') else ("?", "?")
        return True

    except Exception as e:
        return False

def test_sauvegarder_index_embeddings():
    print("\n Test : Sauvegarde Index Vectoriel (Dense) ")
    
    fichier_test = "test_index_emb.pkl"
    
    matrice = np.array([
        [0.1, 0.2, 0.3],
        [0.9, 0.8, 0.7]
    ])
    
    index_test = {
        "type": "indVectoriel",
        "descripteur_cible": "doc2vec",
        "matrice": matrice,
        "mapping": {"d1": 0, "d2": 1},
        "ids": ["d1", "d2"],
        "normes": np.array([0.37, 1.39]) 
    }
    
    succes = sauvegarder_index_embeddings(fichier_test, index_test)
    assert succes is True
    with open(fichier_test, 'rb') as f:
        index_relu = pickle.load(f)
        
    matrice_relue = index_relu["matrice"]
    
    # Vérifications
    assert isinstance(matrice_relue, np.ndarray), "Doit être un array Numpy."
    assert np.allclose(matrice_relue, matrice), "Les valeurs doivent être identiques."
    assert index_relu["mapping"]["d2"] == 1
    assert "normes" in index_relu
    
    print(" Sauvegarde et rechargement de l'index vectoriel validés.")
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_sauvegarder_index_embeddings()


def sauvegarder_normes_embeddings(fichier, index_embeddings):
    """
    Description :
        Sauvegarde uniquement le tableau des normes pré-calculées sur le disque.
        
        Utilité :
        Permet de recharger rapidement ces valeurs critiques pour le calcul de similarité
          sans avoir forcément besoin de charger toute la matrice 
        lourde des vecteurs si on ne fait que des statistiques ou des vérifications.

    Paramètres :
        fichier          : str. Chemin du fichier de destination.
        index_embeddings : dict. La structure d'index contenant la clé 'normes'.

    Retour :
        bool : True si succès, False sinon.
    """
    if not isinstance(index_embeddings, dict) or "normes" not in index_embeddings:
        return False
    
    normes = index_embeddings["normes"]
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError:
            pass
    try:
        with open(fichier, 'wb') as f:
            pickle.dump(normes, f)
            
        taille_ko = os.path.getsize(fichier) / 1024
        return True

    except Exception as e:
        return False

def test_sauvegarder_normes_embeddings():
    print("\n Test : Sauvegarde Normes ")  
    fichier_test = "test_normes.pkl"
    index_test = {
        "matrice": np.zeros((3, 10)),
        "normes": np.array([1.0, 5.4, 0.99]) 
    }
    succes = sauvegarder_normes_embeddings(fichier_test, index_test)
    assert succes is True
    
    with open(fichier_test, 'rb') as f:
        normes_relues = pickle.load(f)
    
    # Vérifications
    assert isinstance(normes_relues, np.ndarray)
    assert len(normes_relues) == 3
    assert np.isclose(normes_relues[1], 5.4)
    
    print(" Sauvegarde des normes validée.")
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_sauvegarder_normes_embeddings()


def sauvegarder_normes_symboliques(fichier, symbolique):
    """
    Description :
        Sauvegarde sur disque uniquement le tableau des normes pré-calculées 
        associé à un index symbolique.
        
        Cela permet de charger ces valeurs indépendamment de la matrice creuse complète,
        ce qui est utile pour des vérifications rapides ou pour alléger la mémoire
        si on utilise une stratégie de chargement paresseux.

    Paramètres :
        fichier          : str. Chemin du fichier de destination.
        symbolique : dict. La structure d'index contenant la clé 'normes'.

    Retour :
        bool : True si succès, False sinon.
    """
    if not isinstance(symbolique, dict):
        return False

    if "normes" not in symbolique:
        return False

    normes = symbolique["normes"]
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError:
            pass
    try:
        with open(fichier, 'wb') as f:
            pickle.dump(normes, f)
            
        taille_ko = os.path.getsize(fichier) / 1024
        return True

    except Exception as e:
        return False

def test_sauvegarder_normes_symboliques():
    print("\n Test : Sauvegarde Normes Symboliques ")
    
    fichier_test = "test_normes_symb.pkl"
    index_test = {
        "type": "symbolique",
        "normes": np.array([1.414, 1.0, 5.0])
    }
    succes = sauvegarder_normes_symboliques(fichier_test, index_test)
    assert succes is True

    with open(fichier_test, 'rb') as f:
        normes_relues = pickle.load(f)
        
    assert isinstance(normes_relues, np.ndarray)
    assert len(normes_relues) == 3
    assert np.isclose(normes_relues[0], 1.414)
    
    print(" Sauvegarde des normes symboliques validée.")
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_sauvegarder_normes_symboliques()


def sauvegarder_inverse(fichier, inverse):
    """
    Description :
        Sauvegarde sur disque la structure d'index inversé.
        Format : Dictionnaire { id : [(id_doc, poids), ...] }
        
        Cette sauvegarde est critique : elle permet au moteur de démarrer instantanément
        en sachant déjà quels documents contiennent quels mots, sans avoir à 
        reparcourir tout le corpus.

    Paramètres :
        fichier       : str. Le chemin du fichier de destination.
        inverse : dict. L'index inversé construit précédemment.

    Retour :
        bool : True si succès, False sinon.
    """
    if not isinstance(inverse, dict):
        return False
    
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        try:
            os.makedirs(dossier)
        except OSError:
            pass

    try:
        with open(fichier, 'wb') as f:
            pickle.dump(inverse, f)
            
        taille_ko = os.path.getsize(fichier) / 1024
        nb = len(inverse)
        return True

    except Exception as e:
        return False

def test_sauvegarder_inverse():
    print("\n Test : Sauvegarde Index Inversé ")
    
    fichier_test = "test_inv_index.pkl"
    index_test = {
        0: [("docA", 0.5), ("docB", 0.2)],
        1: [("docB", 0.9)]
    }
    succes = sauvegarder_inverse(fichier_test, index_test)
    assert succes is True
    with open(fichier_test, 'rb') as f:
        index_relu = pickle.load(f)
        
    # Vérifications
    assert isinstance(index_relu, dict)
    assert len(index_relu) == 2
    
    # Vérification de la structure interne (Tuple conservation)
    entree_terme_0 = index_relu[0]
    assert entree_terme_0[0] == ("docA", 0.5)
    
    print(" Sauvegarde de l'index inversé validée.")
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_sauvegarder_inverse()

def mettre_a_jour_inverse_persistant(fichier, index_partiel):
    """
    Description :
        Met à jour un index inversé stocké sur disque avec de nouvelles données.
        
        Stratégie "Load-Merge-Store" :
        1. Charge l'index principal depuis le disque.
        2. Fusionne les listes de documents pour chaque terme.
        3. Réécrit l'index consolidé sur le disque.

    Paramètres :
        fichier       : str. Chemin du fichier .pkl existant.
        index_partiel : dict. Petit index inversé contenant uniquement les nouvelles entrées.

    Retour :
        bool : True si succès.
    """
    index = {}
    if os.path.exists(fichier):
        try:
            with open(fichier, 'rb') as f:
                index = pickle.load(f)
        except Exception as e:
            index = {}
    compteur = 0
    
    for terme, post in index_partiel.items():
        if terme not in index:
            index[terme] = post
            compteur += len(post)
        else:
            postExist = index[terme]
            idsExistants = {id for id, _ in postExist}
            
            for id, poids in post:
                if id not in idsExistants:
                    postExist.append((id, poids))
                    idsExistants.add(id) 
                    compteur += 1
            index[terme] = postExist
    try:
        with open(fichier, 'wb') as f:
            pickle.dump(index, f)            
        return True
        
    except Exception as e:
        return False
    
def test_mettre_a_jour_inverse_persistant():
    print("\n Test : Mise à jour Index Inversé Persistant ")
    
    fichier_test = "test_inv_persistant.pkl"
    index_initial = {0: [("docA", 1.0)]}
    with open(fichier_test, 'wb') as f:
        pickle.dump(index_initial, f)
    index_delta = {
        0: [("docB", 0.5)],
        1: [("docB", 0.8)]
    }
    
    mettre_a_jour_inverse_persistant(fichier_test, index_delta)
    with open(fichier_test, 'rb') as f:
        index_final = pickle.load(f)
    
    # Le terme 0 doit avoir 2 docs
    assert len(index_final[0]) == 2
    assert index_final[0][1][0] == "docB"
    
    # Le terme 1 doit exister
    assert 1 in index_final
    assert index_final[1][0] == ("docB", 0.8)
    
    print(" Fusion persistante validée.")
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_mettre_a_jour_inverse_persistant()

#e. Rechargement

def charger_fiches(fichier):
    """
    Description :
        Charge les fiches depuis le disque et reconstruit le dictionnaire global.
        
        Cette fonction est polyvalente :
        - Elle peut charger un Snapshot (un seul gros dictionnaire).
        - Elle peut charger un Journal (plusieurs fiches à la suite dans le même fichier).
        
    Paramètres :
        fichier : str. Chemin du fichier .pkl à charger.

    Retour :
        dict : Le dictionnaire global structuré {'documents': {}, 'phrases': {}, 'meta': {}}.
               Retourne une structure vide si le fichier n'existe pas.
    """
    dico = {
        "documents": {},
        "phrases": {},
        "meta": {}
    }

    if not os.path.exists(fichier):
        return dico
    
    compteurObjets = 0
    compteurFiches = 0

    try:
        with open(fichier, 'rb') as f:
            while True:
                try:
                    objet = pickle.load(f)
                    compteurObjets += 1

                    if isinstance(objet, dict) and "documents" in objet and "phrases" in objet:
                        dico = objet
                        nbDocs = len(objet.get("documents", {}))
                        nbPhras = len(objet.get("phrases", {}))
                        break

                    elif isinstance(objet, dict) and "id" in objet and "type" in objet:
                        type = objet["type"]
                        id = objet["id"]
                        
                        cle = type + "s" 
                        
                        if cle in dico:
                            dico[cle][id] = objet
                            compteurFiches += 1
                        else:
                            pass
                    
                    
                except EOFError:
                    break

    except Exception as e:
        return dico
    return dico

def test_charger_fiches():
    print("\n Test : Rechargement des Fiches ")
    
    fichier_snapshot = "test_load_snapshot.pkl"
    fichier_journal = "test_load_journal.pkl"
    
    #  Cas 1 : Snapshot 
    # On crée un faux snapshot
    data_snap = {
        "documents": {"d1": {"id": "d1", "type": "document"}},
        "phrases": {},
        "meta": {}
    }
    with open(fichier_snapshot, 'wb') as f:
        pickle.dump(data_snap, f)
        
    res_snap = charger_fiches(fichier_snapshot)
    assert "d1" in res_snap["documents"]
    print(" Chargement Snapshot OK.")

    #  Cas 2 : Journal (Append) 
    # On crée un fichier avec 2 fiches à la suite
    f1 = {"id": "d2", "type": "document", "contenu": "A"}
    f2 = {"id": "p1", "type": "phrase", "contenu": "B"}
    
    with open(fichier_journal, 'wb') as f:
        pickle.dump(f1, f)
        pickle.dump(f2, f)
        
    res_journal = charger_fiches(fichier_journal)
    
    # Vérifications
    assert "d2" in res_journal["documents"]
    assert "p1" in res_journal["phrases"]
    assert res_journal["documents"]["d2"]["contenu"] == "A"
    
    print(" Chargement Journal OK.")
    
    
    for f in [fichier_snapshot, fichier_journal]:
        if os.path.exists(f):
            os.remove(f)

#test_charger_fiches()

def charger_fiche_unitaire(fichier):
    """
    Description :
        Charge une fiche unique depuis un fichier disque.
        
        Gestion de l'historique :
        Comme la fonction de sauvegarde utilise le mode append,
        le fichier peut contenir plusieurs versions de la fiche.
        Cette fonction lit tout le fichier et retourne la DERNIÈRE version trouvée.

    Paramètres :
        fichier : str. Chemin du fichier .pkl.

    Retour :
        dict : La fiche chargée, ou None si le fichier est introuvable ou vide.
    """
    if not os.path.exists(fichier):
        print(f"Erreur : Le fichier '{fichier}' n'existe pas.")
        return None

    ficheResultat = None
    
    try:
        with open(fichier, 'rb') as f:
            while True:
                try:
                    obj = pickle.load(f)
                    ficheResultat = obj
                except EOFError:
                    break
                    
        return ficheResultat

    except Exception as e:
        return None

def test_charger_fiche_unitaire():
    print("\n Test : Chargement Fiche Unitaire ")
    
    fichier_test = "test_fiche_solo.pkl"
    
    v1 = {"id": "d1", "statut": "calculé", "valeur": 10}
    v2 = {"id": "d1", "statut": "calculé", "valeur": 20}
    
    with open(fichier_test, 'wb') as f:
        pickle.dump(v1, f)
        pickle.dump(v2, f)
        
    fiche_chargee = charger_fiche_unitaire(fichier_test)
    
    # 3. Vérifications
    assert fiche_chargee is not None
    assert fiche_chargee["id"] == "d1"
    
    # on doit avoir récupéré v2 , pas v1
    assert fiche_chargee["valeur"] == 20
    
    print(" Chargement unitaire (avec gestion historique) validé.")
    
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_charger_fiche_unitaire()

def charger_fiches_depuis_dossier(dossier):
    """
    Description :
        Parcourt un dossier contenant des fichiers de fiches individuels (.pkl),
        les charge un par un et reconstruit le dictionnaire global structuré.

    Paramètres :
        dossier : str. Le chemin du dossier contenant les fichiers.

    Retour :
        dict : Le dictionnaire global {'documents': {}, 'phrases': {}, 'meta': {}}.
    """
    dico = {
        "documents": {},
        "phrases": {},
        "meta": {}
    }

    if not os.path.exists(dossier):
        return dico

    pattern = os.path.join(dossier, "*.pkl")
    lfichier = glob.glob(pattern)
    
    
    nbsucces = 0
    
    for chemin in lfichier:
        fiche = charger_fiche_unitaire(chemin)
        
        if fiche and "id" in fiche and "type" in fiche:
            type = fiche["type"]
            id = fiche["id"]
            
            cle = type + "s"
            
            if cle in dico:
                dico[cle][id] = fiche
                nbsucces += 1
            else:
                pass
                
    nbDocs = len(dico["documents"])
    nbPhras = len(dico["phrases"])

    return dico



def test_charger_fiches_depuis_dossier():
    print("\n Test : Rechargement depuis Dossier ")
    
    dossier_test = "test_input_folder"
    
    # 1. Préparation : Création dossier et fichiers
    if os.path.exists(dossier_test):
        shutil.rmtree(dossier_test)
    os.makedirs(dossier_test)
    
    # Création manuelle de 2 fichiers
    f1 = {"id": "d10", "type": "document", "data": "Doc 10"}
    f2 = {"id": "p50", "type": "phrase", "data": "Phrase 50"}
    
    import pickle
    with open(os.path.join(dossier_test, "doc_d10.pkl"), 'wb') as f:
        pickle.dump(f1, f)
    with open(os.path.join(dossier_test, "phrase_p50.pkl"), 'wb') as f:
        pickle.dump(f2, f)
        
    # 2. Exécution
    global_resultat = charger_fiches_depuis_dossier(dossier_test)
    
    # 3. Vérifications
    assert "d10" in global_resultat["documents"]
    assert "p50" in global_resultat["phrases"]
    assert global_resultat["documents"]["d10"]["data"] == "Doc 10"
    
    print(" Rechargement dossier validé.")
    
    
    if os.path.exists(dossier_test):
        shutil.rmtree(dossier_test)

#test_charger_fiches_depuis_dossier()

def integrer_fiche_chargee(dico, fiche):
    """
    Description :
        Intègre une fiche chargée depuis le disque dans le dictionnaire global en mémoire.
        Gère les cas de doublons et vérifie la cohérence des configurations.

        Logique de fusion :
        1. Si l'ID n'existe pas : Ajout simple.
        2. Si l'ID existe :
           - Vérifie que le 'config_id' est identique.
           - Si oui : Fusionne les descripteurs.
           - Si non : Rejette la fiche pour éviter la corruption des données.

    Paramètres :
        dico : dict. Le dictionnaire principal {'documents':..., 'phrases':...}.
        fiche       : dict. La fiche unitaire à intégrer.

    Retour :
        bool : True si intégration réussie, False si rejetée (erreur ou conflit).
    """
    if not isinstance(fiche, dict):
        return False
    
    id = fiche.get("id")
    type = fiche.get("type")
    
    if not id or not type:
        return False

    cle = type + "s" 
    if cle not in dico:
        dico[cle] = {}

    cible = dico[cle]

    if id not in cible:
        cible[id] = fiche
        return True

    fiche = cible[id]

    nouveau = fiche.get("config_id")
    ancienne = fiche.get("config_id")

    if nouveau and ancienne and nouveau != ancienne:
        return False
    descn = fiche.get("descripteurs", {})
    desco = fiche.get("descripteurs", {})
    
    desco.update(descn)
    
    nouveauParametre = fiche.get("parametres_calcul", {})
    ancienParametre = fiche.get("parametres_calcul", {})
    ancienParametre.update(nouveauParametre)
    
    if fiche.get("statut") == "calculé":
        fiche["statut"] = "calculé"
        
    return True

def test_integrer_fiche_chargee():
    print("\n Test : Intégration et Cohérence ")
    
    dico = {
        "documents": {
            "d1": {
                "id": "d1", "type": "document", "config_id": "c1",
                "descripteurs": {"tf": [1, 0]}
            }
        },
        "phrases": {}
    }
    
    # 2. Test Insertion
    f_new = {"id": "d2", "type": "document", "config_id": "c1", "descripteurs": {}}
    res1 = integrer_fiche_chargee(dico, f_new)
    assert res1 is True
    assert "d2" in dico["documents"]
    
    # 3. Test Fusion 
    f_update = {
        "id": "d1", "type": "document", "config_id": "c1", # Config identique OK
        "descripteurs": {"bert": [0.5, 0.5]},
        "statut": "calculé"
    }
    res2 = integrer_fiche_chargee(dico, f_update)
    assert res2 is True
    assert "tf" in dico["documents"]["d1"]["descripteurs"]
    assert "bert" in dico["documents"]["d1"]["descripteurs"]
    
    # 4. Test Conflit
    f_conflict = {
        "id": "d1", "type": "document", 
        "config_id": "c99", 
        "descripteurs": {}
    }
    res3 = integrer_fiche_chargee(dico, f_conflict)
    assert res3 is False
    
    print(" Intégration intelligente validée.")

#test_integrer_fiche_chargee()

def charger_index_symbolique(fichier):
    """
    Description :
        Charge un index symbolique depuis un fichier disque.
        Reconstruit la matrice creuse et les mappings.

    Paramètres :
        fichier : str. Chemin du fichier .pkl à charger.

    Retour :
        dict : La structure d'index complète, ou None en cas d'erreur.
    """
    if not os.path.exists(fichier):
        return None
    try:
        with open(fichier, 'rb') as f:
            symbolique = pickle.load(f)

        if not isinstance(symbolique, dict) or "matrice" not in symbolique:
            return None

        matrice = symbolique["matrice"]
        dims = matrice.shape if hasattr(matrice, "shape") else ("?", "?")
        
        typeMat = "Sparse" if issparse(matrice) else "Dense (Attention)"
        return symbolique

    except Exception as e:
        return None

def test_charger_index_symbolique():
    print("\n Test : Rechargement Index Symbolique ")
    
    fichier_test = "test_load_index_symb.pkl"
    
    matrice_init = csr_matrix([[1, 0], [0, 1]])
    index_init = {
        "matrice": matrice_init,
        "mapping": {"d1": 0, "d2": 1},
        "ids": ["d1", "d2"],
        "descripteur_cible": "tff"
    }
    
    with open(fichier_test, 'wb') as f:
        pickle.dump(index_init, f)
        
    index_relu = charger_index_symbolique(fichier_test)
    
    # 3. Vérifications
    assert index_relu is not None
    
    # Vérification que c'est toujours du Sparse
    assert issparse(index_relu["matrice"])
    
    # Vérification du contenu
    assert index_relu["mapping"]["d2"] == 1
    assert index_relu["descripteur_cible"] == "tff"
    
    print(" Index symbolique rechargé avec succès.")
    
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_charger_index_symbolique()

def charger_index_embeddings(fichier):
    """
    Description :
        Charge un index vectoriel depuis un fichier disque.
        Reconstruit la matrice Numpy et les mappings associés.

    Paramètres :
        fichier : str. Chemin du fichier .pkl à charger.

    Retour :
        dict : La structure d'index complète, ou None en cas d'erreur.
    """
    if not os.path.exists(fichier):
        return None


    try:
        with open(fichier, 'rb') as f:
            indVectoriel = pickle.load(f)

        if not isinstance(indVectoriel, dict) or "matrice" not in indVectoriel:
            return None

        matrice = indVectoriel["matrice"]
        dims = matrice.shape if hasattr(matrice, "shape") else ("?", "?")

        return indVectoriel

    except Exception as e:
        return None

def test_charger_index_embeddings():
    print("\n Test : Rechargement Index Vectoriel ")
    
    fichier_test = "test_load_index_emb.pkl"
    matrice_init = np.array([
        [0.1, 0.2, 0.3],
        [0.9, 0.8, 0.7]
    ])
    
    index_init = {
        "type": "indVectoriel",
        "descripteur_cible": "doc2vec",
        "matrice": matrice_init,
        "mapping": {"d1": 0, "d2": 1},
        "ids": ["d1", "d2"],
        "normes": np.linalg.norm(matrice_init, axis=1)
    }
    with open(fichier_test, 'wb') as f:
        pickle.dump(index_init, f)
        
    index_relu = charger_index_embeddings(fichier_test)
    
    # 3. Vérifications
    assert index_relu is not None
    
    # Vérification du type 
    matrice_relue = index_relu["matrice"]
    assert isinstance(matrice_relue, np.ndarray)
    assert matrice_relue.shape == (2, 3)
    
    # Vérification des valeurs (égalité à epsilon près pour les flottants)
    assert np.allclose(matrice_relue, matrice_init)
    
    # Vérification mapping
    assert index_relu["mapping"]["d2"] == 1
    assert "normes" in index_relu
    
    print(" Index vectoriel rechargé et vérifié.")
    
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_charger_index_embeddings()

def verifier_coherence(dictionnaire_global):
    """
    Description :
        Parcourt le dictionnaire global pour vérifier l'intégrité des données.
        
        Contrôles effectués :
        1. Unicité des IDs (pas de chevauchement Documents/Phrases).
        2. Cohérence Clé/ID (la clé du dico doit être égale à fiche['id']).
        3. Présence des champs obligatoires (id, type, config_id, statut).
        4. Logique du statut (si 'calculé', des descripteurs doivent exister).

    Paramètres :
        dictionnaire_global : dict. La base de données en mémoire.

    Retour :
        bool : True si tout est cohérent, False si des erreurs sont détectées.
    """
    print("Démarrage de la vérification de cohérence...")
    
    erreurs = []
    warnings = []
    
    docs = dictionnaire_global.get("documents", {})
    phrases = dictionnaire_global.get("phrases", {})
    
    idsDocs = set(docs.keys())
    idsPhrases = set(phrases.keys())
    doublons = idsDocs.intersection(idsPhrases)
    if doublons:
        erreurs.append(f"CRITIQUE : {len(doublons)} IDs sont présents à la fois dans documents et phrases (ex: {list(doublons)[:3]}).")

    total = 0
    
    for categorie, dictionnaire in [("Document", docs), ("Phrase", phrases)]:
        for cle, fiche in dictionnaire.items():
            total += 1
            f = fiche.get("id")
            
            if cle != f:
                erreurs.append(f"{categorie} '{cle}' : ID interne différent ('{f}').")
            
            champsRequis = ["id", "type", "config_id", "statut"]
            for champ in champsRequis:
                if champ not in fiche:
                    erreurs.append(f"{categorie} '{cle}' : Champ obligatoire manquant '{champ}'.")
            
            attendu = categorie.lower() 
            if fiche.get("type") != attendu:
                erreurs.append(f"{categorie} '{cle}' : Type incorrect '{fiche.get('type')}' (attendu '{attendu}').")

            statut = fiche.get("statut")
            descripteurs = fiche.get("descripteurs", {})
            
            if statut == "calculé":
                if not descripteurs:
                    warnings.append(f"{categorie} '{cle}' : Statut 'calculé' mais aucun descripteur présent.")
                elif len(descripteurs) == 0:
                     warnings.append(f"{categorie} '{cle}' : Statut 'calculé' mais liste descripteurs vide.")
            
            elif statut == "init":
                if descripteurs:
                    warnings.append(f"{categorie} '{cle}' : Statut 'init' mais contient déjà des descripteurs.")

    if erreurs:
        return False
    
    if warnings:
        return True

    return True

def test_verifier_coherence():
    print("\n Test : Vérification de Cohérence ")
    
    dico_sale = {
        "documents": {
            "d1": {"id": "d1", "type": "document", "config_id": "c1", "statut": "init"}, 
            "d2": {"id": "d99", "type": "document", "config_id": "c1", "statut": "init"}, 
            "d3": {"id": "d3", "type": "phrase", "config_id": "c1", "statut": "init"}  
        },
        "phrases": {
            "d1": {"id": "d1", "type": "phrase", "config_id": "c1", "statut": "init"},    
            "p1": {"id": "p1", "type": "phrase", "statut": "calculé"}                      
        }
    }
    
    valide = verifier_coherence(dico_sale)
    assert valide is False, "Le test aurait dû échouer."
    
    dicoPropre = {
        "documents": {
            "d1": {"id": "d1", "type": "document", "config_id": "c1", "statut": "init", "descripteurs": {}}
        },
        "phrases": {
            "p1": {"id": "p1", "type": "phrase", "config_id": "c1", "statut": "calculé", "descripteurs": {"vec": [1]}}
        }
    }
    
    valide = verifier_coherence(dicoPropre)
    assert valide is True, "Le test aurait dû réussir."
    
    print("\n Fonction de vérification validée.")

#test_verifier_coherence()

def gestion_vecteurs_absents(fiche, strategie='ignore', typeDescripteur=None):
    """
    Description :
        Vérifie la présence de vecteurs dans une fiche et applique une stratégie
        si le vecteur est manquant.
        
        Permet d'éviter les crashs lors des calculs de similarité (NoneType error).

    Paramètres :
        fiche            : dict. La fiche unité à vérifier.
        strategie        : str. 'ignore' (défaut), 'alerte', ou 'recalcul'.
        typeDescripteur : str. Vérifie un descripteur précis (ex: 'tff').
                           Si None, vérifie si la liste des descripteurs est vide.

    Retour :
        bool : True si le vecteur est PRÉSENT (la fiche est exploitable).
               False si le vecteur est ABSENT (la fiche doit être écartée).
    """
    idFiche = fiche.get("id", "?")
    descripteurs = fiche.get("descripteurs", {})
    manquant = False
    
    if typeDescripteur:
        if typeDescripteur not in descripteurs:
            manquant = True
        elif descripteurs[typeDescripteur] is None:
             manquant = True
    else:
        if not descripteurs:
            manquant = True

    if not manquant:
        return True

    if strategie == 'ignore':
        return False
        
    elif strategie == 'alerte':
        return False
        
    elif strategie == 'recalcul':
        fiche['statut'] = 'init'
        if typeDescripteur and typeDescripteur in descripteurs:
            del descripteurs[typeDescripteur]
        return False
    
    else:
        return False

def test_gestion_vecteurs_absents():
    print("\n Test : Gestion des Vecteurs Absents ")
    
    # Cas 1 : Fiche complète (Doit retourner True)
    f_ok = {"id": "d1", "descripteurs": {"tf": [1, 0]}}
    assert gestion_vecteurs_absents(f_ok, 'alerte', 'tf') is True
    
    # Cas 2 : Fiche vide, stratégie 'ignore' (Doit retourner False, silence)
    f_vide = {"id": "d2", "descripteurs": {}}
    res_ignore = gestion_vecteurs_absents(f_vide, 'ignore')
    assert res_ignore is False
    
    # Cas 3 : Fiche vide, stratégie 'alerte' (Doit imprimer et retourner False)
    print("Test Alerte (doit afficher un warning ci-dessous) :")
    gestion_vecteurs_absents(f_vide, 'alerte')
    
    # Cas 4 : Fiche vide, stratégie 'recalcul' (Doit modifier le statut)
    f_recalc = {"id": "d3", "statut": "calculé", "descripteurs": {}}
    gestion_vecteurs_absents(f_recalc, 'recalcul')
    
    assert f_recalc["statut"] == "init", "Le statut aurait dû repasser à 'init'."
    
    print(" Gestion des absences validée.")

#test_gestion_vecteurs_absents()

def charger_normes_embeddings(fichier):
    """
    Description :
        Charge depuis le disque le tableau des normes d'embeddings pré-calculées.
        
        Utilité :
        Permet d'initialiser rapidement le diviseur pour le calcul de similarité Cosinus
        sans avoir besoin de recalculer np.linalg.norm() sur la grosse matrice.

    Paramètres :
        fichier : str. Chemin du fichier .pkl contenant les normes.

    Retour :
        numpy.ndarray : Le tableau des normes, ou None en cas d'erreur.
    """
    if not os.path.exists(fichier):
        return None


    try:
        with open(fichier, 'rb') as f:
            normes = pickle.load(f)
        return normes

    except Exception as e:
        return None

def test_charger_normes_embeddings():
    print("\n Test : Rechargement Normes Embeddings ")
    
    fichier_test = "test_load_normes.pkl"
    normes_init = np.array([0.5, 1.2, 3.3])
    
    with open(fichier_test, 'wb') as f:
        pickle.dump(normes_init, f)
        
    normes_relues = charger_normes_embeddings(fichier_test)
    
    # 3. Vérifications
    assert normes_relues is not None
    assert isinstance(normes_relues, np.ndarray)
    assert len(normes_relues) == 3
    assert np.allclose(normes_relues, normes_init)
    
    print(" Normes rechargées avec succès.")
    
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_charger_normes_embeddings()
def charger_normes_symboliques(fichier):
    """
    Description :
        Charge depuis le disque le tableau des normes symboliques pré-calculées.
        
        Utilité :
        Ces normes sont indispensables pour normaliser les scores de similarité 
        (Cosinus = Produit Scalaire / (Norme_A * Norme_B)).
        Les charger séparément permet d'être opérationnel très vite.

    Paramètres :
        fichier : str. Chemin du fichier .pkl.

    Retour :
        numpy.ndarray : Le tableau des normes, ou None si échec.
    """
    if not os.path.exists(fichier):
        return None
    try:
        with open(fichier, 'rb') as f:
            normes = pickle.load(f)
        if isinstance(normes, np.ndarray):
            shape = normes.shape if hasattr(normes, "shape") else "?"

        return normes

    except Exception as e:
        return None

def test_charger_normes_symboliques():
    print("\n Test : Rechargement Normes Symboliques ")
    
    fichier_test = "test_load_normes_symb.pkl"
    donnees_init = np.array([1.41, 2.0, 0.5])
    with open(fichier_test, 'wb') as f:
        pickle.dump(donnees_init, f)
    resultat = charger_normes_symboliques(fichier_test)
    
    # 3. Vérifications
    assert resultat is not None
    assert isinstance(resultat, np.ndarray)
    assert len(resultat) == 3
    # Vérification de la valeur du 2ème élément
    assert np.isclose(resultat[1], 2.0)
    
    print(" Normes symboliques rechargées avec succès.")
    
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_charger_normes_symboliques()

def charger_inverse(fichier):
    """
    Description :
        Charge un index inversé depuis le disque.
        Restaure la structure { id : [(id_doc, poids), ...] }.
        
        Cette opération est critique pour le démarrage rapide du moteur :
        elle évite de devoir reparcourir tous les documents pour reconstruire 
        les associations terme-documents.

    Paramètres :
        fichier : str. Chemin du fichier .pkl à charger.

    Retour :
        dict : L'index inversé, ou None en cas d'erreur.
    """
    if not os.path.exists(fichier):
        return None

    try:
        with open(fichier, 'rb') as f:
            inverse = pickle.load(f)

        if not isinstance(inverse, dict):
            return None

        nb = len(inverse)
        poids = "N/A"
        if nb > 0:
            terme = list(inverse.values())[0]
            if terme and isinstance(terme[0], (list, tuple)):
                if len(terme[0]) > 1:
                    poids = "Présents"
                else:
                    poids = "Absents (Booléen)"
        return inverse

    except Exception as e:
        return None

def test_charger_inverse():
    print("\n Test : Rechargement Index Inversé ")
    
    fichier_test = "test_load_inv_index.pkl"
    index_init = {
        0: [("docA", 0.5), ("docB", 0.2)],
        1: [("docB", 0.9)]
    }
    
    with open(fichier_test, 'wb') as f:
        pickle.dump(index_init, f)
        
    # 2. Exécution du chargement
    index_relu = charger_inverse(fichier_test)
    
    # 3. Vérifications
    assert index_relu is not None
    assert isinstance(index_relu, dict)
    assert len(index_relu) == 2
    
    # Vérification du contenu profond
    postings_terme_0 = index_relu[0]
    assert len(postings_terme_0) == 2
    assert postings_terme_0[0] == ("docA", 0.5)
    
    print(" Index inversé rechargé et vérifié.")
    
    
    if os.path.exists(fichier_test):
        os.remove(fichier_test)

#test_charger_inverse()

def charger_inverse_mise_a_jour(index, fichier):
    """
    Description :
        Charge un index inversé depuis le disque et le FUSIONNE
        avec l'index actuellement en mémoire.
        
        Utilité :
        Permet d'intégrer des mises à jour stockées sur disque  dans le moteur actif sans écraser
        le travail en cours ni reconstruire toute la structure.

    Paramètres :
        index : dict. L'index inversé en mémoire.
                        Modifié en place.
        fichier       : str. Chemin du fichier .pkl à charger.

    Retour :
        bool : True si la fusion a réussi, False sinon.
    """
    if not os.path.exists(fichier):
        return False
    try:
        with open(fichier, 'rb') as f:
            index = pickle.load(f)

        if not isinstance(index, dict):
            return False

        nbMots = 0
        nbLiens = 0
        for id, post in index.items():
            
            if id not in index:
                index[id] = post
                nbMots += 1
                nbLiens += len(post)
            
            else:
                postings = index[id]
                idsExistants = {id for id, _ in postings}
                
                for id, poids in post:
                    if id not in idsExistants:
                        postings.append((id, poids))
                        idsExistants.add(id) 
                        nbLiens += 1
        return True

    except Exception as e:
        return False

def test_charger_inverse_mise_a_jour():
    print("\n Test : Fusion Index Disque -> Mémoire ")
    
    fichier_update = "test_update_index.pkl"
    index_memoire = {
        0: [("docA", 1.0)]
    }
    
    index = {
        0: [("docB", 0.5)],
        1: [("docC", 0.9)]
    }
    with open(fichier_update, 'wb') as f:
        pickle.dump(index, f)
        
    # 3. Exécution de la fusion
    succes = charger_inverse_mise_a_jour(index_memoire, fichier_update)
    assert succes is True
    
    # 4. Vérifications
    
    # Le terme 0 doit maintenant avoir docA ET docB
    assert len(index_memoire[0]) == 2
    ids_0 = [p[0] for p in index_memoire[0]]
    assert "docA" in ids_0 and "docB" in ids_0
    
    # Le terme 1 doit avoir été créé
    assert 1 in index_memoire
    assert index_memoire[1][0] == ("docC", 0.9)
    
    print(" Fusion Disque vers Mémoire validée.")
    
    
    if os.path.exists(fichier_update):
        os.remove(fichier_update)

#test_charger_inverse_mise_a_jour()

