import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import adjusted_rand_score

from s1_Cocu_Ethan import explorer_corpus
from s2_Cocu_Ethan import lire_document
from s3 import pipeline_pretraitement, construire_vocabulaire, construire_dictionnaire_vocabulaire
from s4 import calcul_idf
from s5 import vectoriser_corpus
from s6 import (entrainer_modele_word2vec, entrainer_modele_doc2vec, 
                plongement_document_par_mots, plongement_document_doc2vec)
from Exercice_2 import executer_kmeans

####################
# 1. Calcul
####################

def calculer_ari_projet(labels_reels, affectations_predites):
    """Calcule l'Adjusted Rand Index entre les vraies classes et les clusters."""
    return adjusted_rand_score(labels_reels, affectations_predites)

def executer_benchmark_complet(matrices, labels_reels, k=3):
    """Compare toutes les approches et retourne un DataFrame de synthèse."""
    resultats = []
    print(f"\n{'Approche':<15} | {'ARI Score':<10}")
    print("-" * 30)
    
    for nom, X in matrices.items():
        points = X.tolist()
        if len(points) < k: 
            print(f"{nom:<15} | IGNORÉ (pas assez de données)")
            continue
            
        indices_init = np.random.choice(len(points), k, replace=False)
        centres_init = [points[i] for i in indices_init]
        
        _, affectations, _, _ = executer_kmeans(points, centres_init)
        
        score = calculer_ari_projet(labels_reels, affectations)
        resultats.append({"Approche": nom, "ARI": score})
        print(f"{nom:<15} | {score:<10.4f}")
        
    return pd.DataFrame(resultats)

####################
# 2. MAIN
####################

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    nom_dossier_source = os.path.join(base_path, "Corpus_Textes", "Cas_2_Textes_Complets")
    
    config_pretraitement = {
        "minuscules": True, "accents": True, "ponctuation": True,
        "stopwords": True, "longueur_min": 2, "morphologie": None
    }

    print(f"--- 708 : Analyse du corpus ---")
    
    structure_corpus = explorer_corpus(nom_dossier_source)
    tous_fichiers = []
    for dossier, infos in structure_corpus.items():
        for f in infos['contenu']:
            if f.lower().endswith('.txt'):
                tous_fichiers.append(os.path.join(dossier, f))

    if not tous_fichiers:
        print("Erreur : Aucun fichier .txt trouvé.")
        exit()

    textes_bruts = {}
    labels_reels_dict = {}
    
    for chemin in tous_fichiers:
        nom_f = os.path.basename(chemin)
        contenu = lire_document(chemin)
        if contenu.strip():
            textes_bruts[nom_f] = contenu
            
            nom_lower = nom_f.lower()
            if "fr" in nom_lower: labels_reels_dict[nom_f] = 0
            elif "en" in nom_lower or "an" in nom_lower: labels_reels_dict[nom_f] = 1
            else: labels_reels_dict[nom_f] = 2

    print(f"Prétraitement de {len(textes_bruts)} documents...")
    corpus_tokens = {}
    
    for nom_f, contenu in textes_bruts.items():
        tokens_valides = []
        try:
            res_pipeline = pipeline_pretraitement({nom_f: contenu}, config_pretraitement)
            if isinstance(res_pipeline, dict) and nom_f in res_pipeline:
                tokens_valides = res_pipeline[nom_f]
        except Exception:
            pass

        if not tokens_valides or not isinstance(tokens_valides, list):
            contenu_propre = re.sub(r'[^\w\s]', ' ', contenu.lower())
            tokens_valides = [mot for mot in contenu_propre.split() if len(mot) > 2]

        if len(tokens_valides) > 0:
            corpus_tokens[nom_f] = tokens_valides

    labels_reels = [labels_reels_dict[nom] for nom in corpus_tokens.keys()]
    tokens_fr = [tokens for nom, tokens in corpus_tokens.items() if labels_reels_dict[nom] == 0]
    tokens_an = [tokens for nom, tokens in corpus_tokens.items() if labels_reels_dict[nom] == 1]

    print(f" -> Documents valides conservés : {len(corpus_tokens)}")
    print(f" -> Dont {len(tokens_fr)} Français et {len(tokens_an)} Anglais.")

    if len(corpus_tokens) == 0:
        print("Erreur critique : Impossible d'extraire des mots des documents.")
        exit()

    print("\nEntraînement des modèles Word2Vec/Doc2Vec...")
    entrainement_fr = tokens_fr if len(tokens_fr) > 0 else list(corpus_tokens.values())
    entrainement_an = tokens_an if len(tokens_an) > 0 else list(corpus_tokens.values())

    m_w2v_fr = entrainer_modele_word2vec(entrainement_fr, min_count=1)
    m_w2v_an = entrainer_modele_word2vec(entrainement_an, min_count=1)
    m_d2v_fr = entrainer_modele_doc2vec(entrainement_fr, min_count=1)
    m_d2v_an = entrainer_modele_doc2vec(entrainement_an, min_count=1)

    corpus_fmt = {k: [v] for k, v in corpus_tokens.items()}
    vocab = construire_vocabulaire(corpus_fmt)
    dico = construire_dictionnaire_vocabulaire(vocab)
    
    idf = calcul_idf(corpus_fmt, dico)

    print("Génération des représentations vectorielles...")
    mats = {}
    mats['bagofword'] = np.array(list(vectoriser_corpus(corpus_fmt, dico, methode="count").values()))
    mats['bm25'] = np.array(list(vectoriser_corpus(corpus_fmt, dico, methode="bm25", vecteurIdf=idf).values()))
    
    mats['word2vecFR'] = np.array([plongement_document_par_mots(t, m_w2v_fr) for t in corpus_tokens.values()])
    mats['word2vecAN'] = np.array([plongement_document_par_mots(t, m_w2v_an) for t in corpus_tokens.values()])
    mats['Doc2vecFR'] = np.array([plongement_document_doc2vec(t, m_d2v_fr) for t in corpus_tokens.values()])
    mats['doc2vecAn'] = np.array([plongement_document_doc2vec(t, m_d2v_an) for t in corpus_tokens.values()])

    print("\nLancement du K-Means (k=3)...")
    df_res = executer_benchmark_complet(mats, labels_reels, k=3)

    df_res.sort_values("ARI").plot(kind='barh', x='Approche', y='ARI', color='teal', edgecolor='black')
    plt.title("Comparaison de la pureté des clusters (Adjusted Rand Index)")
    plt.xlabel("Score ARI")
    plt.tight_layout()
    plt.show()