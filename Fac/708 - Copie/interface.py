import os
import re
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
from collections import Counter


# =============================================================================
# IMPORTS MODULES
# =============================================================================
try:
    from s2_Cocu_Ethan import lire_document, detecter_langue_f
    from s3 import pipeline_pretraitement, construire_dictionnaire_vocabulaire, tokeniser_corpus
    from s5 import vectoriser_phrase, calculer_similarite 
    from s6 import (generer_nuage_mots_texte, nuage_mots_pondere, 
                    entrainer_modele_word2vec, entrainer_modele_doc2vec,
                    plongement_phrase_par_mots, plongement_document_doc2vec) # Intégration s6
except ImportError as e:
    print(f"ERREUR D'IMPORT : {e}")

# =============================================================================
# STOPWORDS FIXES
# =============================================================================
STOPWORDS_FIXES = {
    # FRANCAIS
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "est", "en", "dans", "pour", "par", "sur",
    "au", "aux", "ce", "ces", "cet", "cette", "qui", "que", "quoi", "dont", "ou", "mais", "donc", "or", "ni", "car",
    "il", "elle", "ils", "elles", "je", "tu", "nous", "vous", "on", "ne", "pas", "plus", "se", "sa", "ses", "son",
    "leur", "leurs", "a", "à", "y", "été", "être", "avoir", "faire", "tout", "tous", "toute", "toutes",
    "comme", "avec", "sans", "sous", "vers", "chez", "vos", "notre", "votre", "nos", "eux", "lui",
    "moi", "toi", "soi", "mon", "ton", "mes", "tes", "ma", "ta", "cela", "ça", "c", "d", "j", "l", "m", "n", "s", "t", "qu",
    # ANGLAIS
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "at", "from", "by", "on", "off", "for",
    "in", "out", "over", "to", "into", "with", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "it", "its", "they", "them", "their", "we", "us", "our", "you", "your", "he", "him", "his",
    "she", "her", "that", "this", "these", "those", "which", "who", "whom", "what", "where", "why", "how",
    "me", "my", "myself", "mine", "yours", "yourself", "ours", "ourselves", "theirs", "themselves",
    "as", "of", "not", "no", "can", "will", "just", "than", "so", "up", "down", "very"
}

# =============================================================================
# BACKEND
# =============================================================================

class MoteurRechercheBackend:
    def __init__(self, logger_callback=None):
        self.corpus_brut = {}       
        self.ids_documents = []     
        self.corpus_tokens = []     
        self.vocabulaire = {}       
        self.matrice_corpus = None  
        self.modele_embeddings = None # Stockage du modèle Word2Vec ou Doc2Vec
        self.config_active = {"descripteur": None, "config_s3": None, "granularite": None}
        self.est_charge = False
        self.historique_scenarios = [] 
        self.logger = logger_callback

    def log(self, message, type_msg="INFO"):
        print(f"[{type_msg}] {message}")
        if self.logger: self.logger(message, type_msg)

    def _nettoyer_interne(self, tokens_bruts):
        propres = []
        for t in tokens_bruts:
            mot = t.lower()
            mot = re.sub(r'[^a-z0-9àâçéèêëîïôûùüÿñæoe]+', '', mot)
            if mot and len(mot) > 1 and mot not in STOPWORDS_FIXES:
                propres.append(mot)
        return propres

    def charger_corpus(self, chemin_cible, mode="dossier_simple", langue="all"):
        chemins_trouves = []
        chemin_cible = os.path.normpath(chemin_cible)
        
        self.log(f"--- CHARGEMENT ---")
        self.log(f"Cible : {chemin_cible}")
        self.log(f"Mode : {mode} | Langue : {langue}")
        
        if not os.path.exists(chemin_cible):
            raise FileNotFoundError(f"Chemin introuvable : {chemin_cible}")

        if mode == "fichier":
            if os.path.isfile(chemin_cible):
                chemins_trouves = [chemin_cible]
            else:
                self.log("Erreur: Le mode 'Fichier' attend un fichier.", "ERROR")
                
        elif mode == "dossier_simple":
            if os.path.isdir(chemin_cible):
                for f in os.listdir(chemin_cible):
                    full_path = os.path.join(chemin_cible, f)
                    if os.path.isfile(full_path) and f.lower().endswith(".txt"):
                        chemins_trouves.append(full_path)

        elif mode == "dossier_recursif":
            if os.path.isdir(chemin_cible):
                for root, dirs, files in os.walk(chemin_cible):
                    for file in files:
                        if file.lower().endswith(".txt"):
                            chemins_trouves.append(os.path.join(root, file))

        if not chemins_trouves:
            raise ValueError(f"Aucun fichier .txt trouvé (Mode: {mode}) dans : {chemin_cible}")

        self.corpus_brut = {}
        self.ids_documents = []
        c_ok = 0
        c_rejet_langue = 0
        
        for p in chemins_trouves:
            path_lower = p.lower()
            garder = True
            
            if langue == "fr":
                if not any(x in path_lower for x in ["_fr", "-fr", ".fr", "\\fr\\", "/fr/"]): garder = False
            elif langue == "en":
                if not any(x in path_lower for x in ["_en", "-en", ".en", "\\en\\", "/en/"]): garder = False

            if not garder:
                c_rejet_langue += 1
                continue

            nom_uniq = os.path.basename(p)
            if nom_uniq in self.corpus_brut:
                nom_uniq = f"{os.path.basename(os.path.dirname(p))}_{nom_uniq}"
            
            try:
                txt = lire_document(p) # s2
                if txt and len(txt.strip()) > 0:
                    self.corpus_brut[nom_uniq] = txt
                    self.ids_documents.append(nom_uniq)
                    c_ok += 1
            except: pass

        self.log(f"Résultat : {c_ok} chargés. ({c_rejet_langue} ignorés pour langue '{langue}')", "SUCCESS")
        
        if c_ok == 0:
            raise ValueError("Aucun document valide chargé.")

        self.est_charge = True
        self.config_active = {"descripteur": None, "config_s3": None, "granularite": None}

    def _segmenter_phrases(self):
        self.log("Segmentation phrases...", "INFO")
        dico = {}
        for did, txt in self.corpus_brut.items():
            phrases = re.split(r'(?<=[.!?])\s+', txt.replace('\n', ' '))
            for i, p in enumerate(phrases):
                if len(p.strip()) > 5: dico[f"{did}#P{i+1}"] = p
        return dico

    def _appliquer_pretraitement_global(self, config_s3, granularite):
        self.log(f"Traitement (Granularité={granularite})...")
        if granularite == "phrase": dico_travail = self._segmenter_phrases()
        else: dico_travail = self.corpus_brut
        self.log(f"Base de travail : {len(dico_travail)} unités.", "INFO")

        self.ids_documents = list(dico_travail.keys())
        self.corpus_tokens = []

        for doc_id in self.ids_documents:
            texte = dico_travail[doc_id]
            tokens_bruts = re.findall(r"\w+", texte)
            if config_s3.get("stopwords", True):
                tokens_propres = self._nettoyer_interne(tokens_bruts)
            else:
                tokens_propres = [t.lower() for t in tokens_bruts]
            self.corpus_tokens.append(tokens_propres)

        all_w = [w for d in self.corpus_tokens for w in d]
        v_res = construire_dictionnaire_vocabulaire(sorted(list(set(all_w)))) # s3
        self.vocabulaire = v_res[0] if isinstance(v_res, tuple) else v_res
        self.log(f"Vocabulaire Final : {len(self.vocabulaire)} mots.", "SUCCESS")
        
        self.config_active["config_s3"] = config_s3
        self.config_active["granularite"] = granularite
        self.matrice_corpus = None; self.config_active["descripteur"] = None

    def _construire_matrice(self, methode):
        """Redéfinition pour inclure les embeddings Word2Vec et Doc2Vec"""
        self.log(f"Vectorisation ({methode})...")
        
        # Cas des modèles de plongement sémantique
        if methode == "word2vec":
            self.log("Entraînement du modèle Word2Vec...")
            self.modele_embeddings = entrainer_modele_word2vec(self.corpus_tokens) # s6
            vecs = [plongement_phrase_par_mots(t, self.modele_embeddings) for t in self.corpus_tokens]
        elif methode == "doc2vec":
            self.log("Entraînement du modèle Doc2Vec...")
            self.modele_embeddings = entrainer_modele_doc2vec(self.corpus_tokens) # s6
            vecs = [plongement_document_doc2vec(t, self.modele_embeddings) for t in self.corpus_tokens]
        else:
            # Méthodes classiques (BoW, TF-IDF, etc.)
            if len(self.vocabulaire) < 1:
                self.matrice_corpus = np.empty((len(self.ids_documents), 0))
                return
            vecs = []
            for t in self.corpus_tokens:
                vecs.append(vectoriser_phrase(t, self.vocabulaire, methode=methode)) # s5
        
        self.matrice_corpus = np.array(vecs)
        self.config_active["descripteur"] = methode

    def rechercher(self, fiche_requete, k=10):
        """Adaptation pour traiter les vecteurs de requêtes par embedding et gérer les distances"""
        if not self.est_charge: raise RuntimeError("Corpus vide")
        
        # 1. Configuration ( inchangé )
        cfg_s3 = fiche_requete["config_pretraitement"]
        gran = fiche_requete["granularite"]
        desc = fiche_requete["config_descripteurs"]["types"][0]

        if (cfg_s3 != self.config_active["config_s3"]) or (gran != self.config_active["granularite"]):
            self._appliquer_pretraitement_global(cfg_s3, gran)
        if desc != self.config_active["descripteur"]:
            self._construire_matrice(desc)

        # 2. Traitement de la requête ( inchangé )
        txt_req = fiche_requete["texte"]
        toks_req_bruts = re.findall(r"\w+", txt_req)
        
        if cfg_s3.get("stopwords", True): toks_req = self._nettoyer_interne(toks_req_bruts)
        else: toks_req = [t.lower() for t in toks_req_bruts]
        
        if not toks_req:
            toks_req = [t.lower() for t in toks_req_bruts]

        # Calcul du vecteur requête
        if desc == "word2vec":
            vec_req = plongement_phrase_par_mots(toks_req, self.modele_embeddings)
        elif desc == "doc2vec":
            vec_req = plongement_document_doc2vec(toks_req, self.modele_embeddings)
        else:
            vec_req = vectoriser_phrase(toks_req, self.vocabulaire, methode=desc)

        # 3. CALCUL DES SCORES (CORRECTION ICI)
        type_dist = fiche_requete["type_distance"]
        scores = []
        
        try:
            # On parcourt chaque document de la matrice pour comparer 1 à 1 avec s5.py
            for doc_vec in self.matrice_corpus:
                # doc_vec est une ligne de la matrice (un document)
                val = calculer_similarite(vec_req, doc_vec, mesure=type_dist) # s5
                scores.append(val)
            
            scores = np.array(scores)

            
            if type_dist in ["euclidienne", "manhattan", "distance_cosinus", "distance_jaccard", "hamming"]:
                scores = -scores

        except Exception as e:
            self.log(f"Erreur Maths: {e}", "ERROR")
            return []

        # 4. Formatage des résultats 
        res = []
        limit = min(len(scores), len(self.ids_documents))
        for i in range(limit):
            sc = float(scores[i])
            if np.isnan(sc): sc = 0.0
            
            if sc > -99999:
                uid = self.ids_documents[i]
                
                # Récupération du texte pour l'aperçu
                if gran == "phrase":
                    dparent = uid.split("#")[0]
                    contenu_parent = self.corpus_brut.get(dparent, '')
                    full_text_display = f"[PHRASE {uid}] issue de {dparent}\n\n{contenu_parent}"
                    apercu = f"[PHRASE] {contenu_parent[:60]}..."
                else:
                    full_text_display = self.corpus_brut.get(uid, "")
                    apercu = full_text_display[:150].replace("\n", " ") + "..."
                
                score_affichage = sc
                if type_dist in ["euclidienne", "manhattan", "distance_cosinus", "distance_jaccard", "hamming"]:
                    score_affichage = -sc 

                res.append((uid, sc, f"{score_affichage:.4f} | {apercu}", full_text_display))

        res.sort(key=lambda x: x[1], reverse=True)
        
        top_k_clean = [(uid, sc, apercu, txt) for (uid, sc, apercu, txt) in res[:k]]

        self.historique_scenarios.append({
            "id": len(self.historique_scenarios)+1, 
            "requete": fiche_requete["texte"],
            "config": {"desc": desc, "gran": gran, "lang": "N/A"},
            "resultats": top_k_clean, 
            "scores_bruts": scores
        })
        
        return [(r[0], r[1], r[2], r[3]) for r in top_k_clean]
    def generer_nuage_resultats(self, top_k):
        txt = ""
        for (uid, _, _, _) in top_k:
            doc_id = uid.split("#")[0]
            if doc_id in self.corpus_brut: txt += self.corpus_brut[doc_id] + " "
        return generer_nuage_mots_texte(txt, stopwords=STOPWORDS_FIXES) # s6

    def generer_nuage_unique(self, uid):
        doc_id = uid.split("#")[0]
        if doc_id in self.corpus_brut: 
            return generer_nuage_mots_texte(self.corpus_brut[doc_id], stopwords=STOPWORDS_FIXES)
        return None

    def get_comparaison_data(self, indices):
        return [self.historique_scenarios[i] for i in indices if i < len(self.historique_scenarios)]

    def calculer_stats_lexicales(self):
        """Calcule la richesse lexicale et le taux de hapax sur le corpus chargé."""
        # Si le corpus n'est pas encore tokenisé, on lance une tokenisation par défaut
        if not self.corpus_tokens and self.est_charge:
            # On utilise une config par défaut (stopwords=True, niveau document) pour les stats
            self._appliquer_pretraitement_global({"stopwords": True}, "document")

        if not self.corpus_tokens:
            return None

        # Aplatir tous les documents en une seule liste de mots
        all_tokens = [mot for doc in self.corpus_tokens for mot in doc]
        N = len(all_tokens) # Nombre total de mots (tokens)

        if N == 0:
            return {"TTR": 0, "Hapax": 0, "Vocab": 0, "Total": 0}

        # Comptage des fréquences
        compteur = Counter(all_tokens)
        V = len(compteur) # Taille du vocabulaire (Types)
        
        # Hapax : mots qui n'apparaissent qu'une seule fois
        nb_hapax = sum(1 for count in compteur.values() if count == 1)

        # Calcul des ratios
        # TTR (Type-Token Ratio) : Richesse lexicale
        ttr = V / N 
        
        # Taux de Hapax (Proportion de mots uniques dans le vocabulaire)
        taux_hapax = nb_hapax / V 

        return {
            "TTR": ttr,
            "Hapax": taux_hapax,
            "Vocab": V,
            "Total": N,
            "NbHapax": nb_hapax
        }
# =============================================================================
# FRONTEND
# =============================================================================
class InterfaceMoteurRecherche:
    def __init__(self, root):
        self.root = root
        self.root.title("Moteur de Recherche")
        self.root.geometry("1450x950")
        
        # Variable pour stocker le chemin du dernier dossier chargé
        self.dernier_chemin_corpus = "" 
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", font=('Segoe UI', 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

        self.v_mode = tk.StringVar(master=self.root, value="dossier_simple")
        self.v_lang = tk.StringVar(master=self.root, value="all") 
        
        self.moteur = MoteurRechercheBackend(logger_callback=self.ajouter_log)
        self.map_desc = {
            "TF-IDF": "tfidf", 
            "BM25": "bm25", 
            "BoW (Count)": "count", 
            "BoW (Bin)": "binary", 
            "TF": "tf",
            "Word2Vec": "word2vec", 
            "Doc2Vec": "doc2vec"
        }
        self.map_dist = {"Cosinus": "cosinus", "Jaccard": "jaccard", "Euclidienne": "euclidienne", "Manhattan": "manhattan"}

        self.main_split = tk.PanedWindow(root, orient=tk.VERTICAL)
        self.main_split.pack(fill=tk.BOTH, expand=True)

        self.panneau_haut = tk.PanedWindow(self.main_split, orient=tk.HORIZONTAL)
        self.main_split.add(self.panneau_haut, height=750)
        
        self.sidebar = tk.Frame(self.panneau_haut, bg="#f4f4f4", width=280, padx=10, pady=10)
        self.panneau_haut.add(self.sidebar)
        self.contenu = tk.Frame(self.panneau_haut, bg="white")
        self.panneau_haut.add(self.contenu)

        self.frame_logs = tk.LabelFrame(self.main_split, text="Journal d'exécution", bg="#2b2b2b", fg="white")
        self.main_split.add(self.frame_logs, height=200)
        self.txt_logs = scrolledtext.ScrolledText(self.frame_logs, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_logs.pack(fill=tk.BOTH, expand=True)
        self.txt_logs.tag_config("ERROR", foreground="#ff4444")
        self.txt_logs.tag_config("WARNING", foreground="orange")
        self.txt_logs.tag_config("SUCCESS", foreground="#00ccff")

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(side=tk.BOTTOM, fill=tk.X)

        self._init_sidebar()
        self._init_contenu()
        self.ajouter_log("Système prêt.", "INFO")

    def _start_work(self):
        self.root.config(cursor="watch"); self.progress.start(10); self.root.update()

    def _stop_work(self):
        self.root.config(cursor=""); self.progress.stop(); self.root.update()

    def ajouter_log(self, message, tag="INFO"):
        self.txt_logs.insert(tk.END, f"[{tag}] {message}\n", tag if tag in ["ERROR","WARNING","SUCCESS"] else "INFO"); self.txt_logs.see(tk.END)

    def _init_sidebar(self):
        lf_src = ttk.LabelFrame(self.sidebar, text=" 1. SOURCE & FILTRES ")
        lf_src.pack(fill=tk.X, pady=5, ipadx=5, ipady=5)
        
        tk.Radiobutton(lf_src, text="Fichier unique", variable=self.v_mode, value="fichier").pack(anchor="w")
        tk.Radiobutton(lf_src, text="Dossier (Racine)", variable=self.v_mode, value="dossier_simple").pack(anchor="w")
        tk.Radiobutton(lf_src, text="Dossier (Récursif)", variable=self.v_mode, value="dossier_recursif").pack(anchor="w")
        
        ttk.Separator(lf_src, orient='horizontal').pack(fill='x', pady=8)
        ttk.Label(lf_src, text="Filtre Langue :").pack(anchor="w")
        self.cb_lang = ttk.Combobox(lf_src, values=["Tous (Mixte)", "Français (_fr)", "Anglais (_en)"], state="readonly")
        self.cb_lang.current(0); self.cb_lang.pack(fill=tk.X, pady=2)

        btn_load = tk.Button(self.sidebar, text="📂 CHARGER CORPUS", bg="#007acc", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", command=self.action_charger)
        btn_load.pack(fill=tk.X, pady=15)
        
        self.lbl_info = tk.Label(self.sidebar, text="Aucun corpus chargé", bg="#e0e0e0", fg="#333", relief="sunken")
        self.lbl_info.pack(fill=tk.X, pady=5)
        tk.Button(self.sidebar, text="Vider Logs", command=lambda: self.txt_logs.delete('1.0', tk.END)).pack(side=tk.BOTTOM, fill=tk.X)

    def _init_contenu(self):
        self.onglets = ttk.Notebook(self.contenu)
        self.onglets.pack(fill=tk.BOTH, expand=True)
        
        # Onglet 1 : Recherche
        self.tab_recherche = tk.Frame(self.onglets, bg="white")
        self.onglets.add(self.tab_recherche, text=" 🔍 RECHERCHE ")
        self._build_tab_search(self.tab_recherche)

        # Onglet 2 : Exploration et Stats
        self.tab_corpus = tk.Frame(self.onglets, bg="white")
        self.onglets.add(self.tab_corpus, text=" 📁 EXPLORATION CORPUS ")
        self._build_tab_corpus(self.tab_corpus)

        # Onglet 3 : Comparaison
        self.tab_comparaison = tk.Frame(self.onglets, bg="white")
        self.onglets.add(self.tab_comparaison, text=" 📊 COMPARAISON ")
        self._build_tab_compare(self.tab_comparaison)

    def _build_tab_search(self, parent):
        pan = tk.PanedWindow(parent, orient=tk.HORIZONTAL)
        pan.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        gauche = tk.Frame(pan, bg="white"); pan.add(gauche, minsize=600)
        droite = tk.LabelFrame(pan, text="Visualisation Lexicale", bg="white"); pan.add(droite)
        fr_conf = tk.LabelFrame(gauche, text="Paramètres de Recherche", bg="#f8f9fa", padx=5, pady=5)
        fr_conf.pack(fill=tk.X, pady=5)
        opts = {'padx': 5, 'pady': 5, 'sticky': 'w'}
        tk.Label(fr_conf, text="Descripteur:", bg="#f8f9fa").grid(row=0, column=0, **opts)
        self.cb_desc = ttk.Combobox(fr_conf, values=list(self.map_desc.keys()), state="readonly", width=15); self.cb_desc.current(0); self.cb_desc.grid(row=0, column=1, **opts)
        tk.Label(fr_conf, text="Distance:", bg="#f8f9fa").grid(row=0, column=2, **opts)
        self.cb_dist = ttk.Combobox(fr_conf, values=list(self.map_dist.keys()), state="readonly", width=15); self.cb_dist.current(0); self.cb_dist.grid(row=0, column=3, **opts)
        tk.Label(fr_conf, text="Nettoyage:", bg="#f8f9fa").grid(row=1, column=0, **opts)
        self.cb_prep = ttk.Combobox(fr_conf, values=["Standard", "Brut"], state="readonly", width=15); self.cb_prep.current(0); self.cb_prep.grid(row=1, column=1, **opts)
        tk.Label(fr_conf, text="Granularité:", bg="#f8f9fa").grid(row=1, column=2, **opts)
        self.cb_gran = ttk.Combobox(fr_conf, values=["Document", "Phrase"], state="readonly", width=15); self.cb_gran.current(0); self.cb_gran.grid(row=1, column=3, **opts)
        fr_req = tk.Frame(gauche, bg="white", pady=10); fr_req.pack(fill=tk.X)
        tk.Label(fr_req, text="Requête:", font=("Segoe UI", 11, "bold"), bg="white").pack(side=tk.LEFT)
        self.ent_req = tk.Entry(fr_req, font=("Segoe UI", 11), bd=2, relief="groove"); self.ent_req.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        tk.Label(fr_req, text="Top K:", bg="white").pack(side=tk.LEFT)
        self.spin_k = tk.Spinbox(fr_req, from_=1, to=50, width=3, font=("Segoe UI", 11)); self.spin_k.pack(side=tk.LEFT, padx=5); self.spin_k.delete(0, "end"); self.spin_k.insert(0,5)
        btn_go = tk.Button(fr_req, text="LANCER", bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), command=self.action_rechercher)
        btn_go.pack(side=tk.LEFT, padx=10)
        cols = ("#", "ID", "Score", "Aperçu")
        self.tree = ttk.Treeview(gauche, columns=cols, show="headings"); self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.heading("#", text="#"); self.tree.column("#", width=40, stretch=False)
        self.tree.heading("ID", text="Identifiant"); self.tree.column("ID", width=180, stretch=False)
        self.tree.heading("Score", text="Sim."); self.tree.column("Score", width=80, stretch=False)
        self.tree.heading("Aperçu", text="Contenu (Double-clic pour voir tout)"); self.tree.column("Aperçu", width=400)
        sb = ttk.Scrollbar(gauche, orient="vertical", command=self.tree.yview); sb.place(relx=1, rely=0, relheight=1, anchor='ne'); self.tree.configure(yscrollcommand=sb.set)
        self.tree.tag_configure('odd', background='#f9f9f9'); self.tree.tag_configure('even', background='#ffffff')
        self.tree.bind("<Double-1>", self.on_double_click_result)
        fr_vb = tk.Frame(droite, bg="white"); fr_vb.pack(fill=tk.X)
        tk.Button(fr_vb, text="☁️ Nuage Global", command=self.action_nuage_global).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(fr_vb, text="📄 Nuage Document", command=self.action_nuage_doc).pack(side=tk.LEFT, padx=5, pady=5)
        self.canvas_frame = tk.Frame(droite, bg="white"); self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def _build_tab_corpus(self, parent):
        pan_corpus = tk.PanedWindow(parent, orient=tk.HORIZONTAL, bg="white")
        pan_corpus.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Partie Gauche : Arborescence ---
        frame_tree = tk.LabelFrame(pan_corpus, text="Structure de l'Arborescence", bg="white", font=("Segoe UI", 10, "bold"))
        pan_corpus.add(frame_tree, width=700)
        
        self.txt_arborescence = scrolledtext.ScrolledText(frame_tree, font=("Consolas", 10), bg="#f8f9fa")
        self.txt_arborescence.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Partie Droite : Statistiques ---
        frame_stats = tk.LabelFrame(pan_corpus, text="Statistiques Détaillées", bg="white", font=("Segoe UI", 10, "bold"))
        pan_corpus.add(frame_stats)

        self.tree_stats = ttk.Treeview(frame_stats, columns=("Propriété", "Valeur"), show="headings", height=15)
        self.tree_stats.heading("Propriété", text="Indicateur")
        self.tree_stats.heading("Valeur", text="Donnée")
        self.tree_stats.column("Propriété", width=250)
        self.tree_stats.column("Valeur", width=150)
        self.tree_stats.pack(fill=tk.X, padx=10, pady=10)

        btn_refresh = tk.Button(frame_stats, text="🔄 ACTUALISER L'ANALYSE", bg="#17a2b8", fg="white", 
                               font=("Segoe UI", 10, "bold"), command=self.action_analyser_corpus)
        btn_refresh.pack(pady=20)

    def _build_tab_compare(self, parent):
        tk.Label(parent, text="Historique des Scénarios", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=10)
        self.listbox_hist = tk.Listbox(parent, selectmode=tk.MULTIPLE, height=8, font=("Consolas", 10))
        self.listbox_hist.pack(fill=tk.X, padx=20)
        btn = tk.Button(parent, text="COMPARER LA SÉLECTION", bg="#ff9800", fg="white", font=("Segoe UI", 10, "bold"), command=self.action_comparer)
        btn.pack(pady=10)
        self.frame_comp_res = tk.Frame(parent, bg="white"); self.frame_comp_res.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def action_charger(self):
        self._start_work()
        try:
            mode = self.v_mode.get()
            raw_lang = self.cb_lang.get()
            lang = "fr" if "Français" in raw_lang else "en" if "Anglais" in raw_lang else "all"
            
            path = filedialog.askopenfilename() if mode == "fichier" else filedialog.askdirectory()
                
            if path:
                self.dernier_chemin_corpus = path
                self.moteur.charger_corpus(path, mode, lang)
                self.lbl_info.config(text=f"CORPUS : {len(self.moteur.ids_documents)} docs", fg="green")
                
                self.action_analyser_corpus()
                messagebox.showinfo("Succès", "Chargement terminé.")
        except Exception as e: messagebox.showerror("Erreur", str(e))
        finally: self._stop_work()

    def action_analyser_corpus(self):
        if not self.dernier_chemin_corpus or not os.path.exists(self.dernier_chemin_corpus):
            self.ajouter_log("Analyse impossible : aucun chemin valide.", "WARNING")
            return

        self._start_work()
        try:
            from s1_Cocu_Ethan import afficher_structure, statistiques_structure
            
            # 1. Mise à jour de l'arborescence (Visuel)
            arbo = afficher_structure(self.dernier_chemin_corpus)
            self.txt_arborescence.delete('1.0', tk.END)
            self.txt_arborescence.insert(tk.END, arbo if arbo != 0 else "Erreur de structure.")

            # 2. Nettoyage du tableau
            self.tree_stats.delete(*self.tree_stats.get_children())

            # --- ANALYSE DES DOSSIERS ET FICHIERS (ETUDIANTS) ---
            nb_sous_corpus = 0
            etudiants_ids = set() # Pour stocker les "XX" uniques
            compteur_langues = Counter()
            
            # Regex pour capter : etu(XX)_(lang).txt
            # On cherche "etu" suivi de chiffres, un underscore, des lettres, et .txt
            pattern_etu = re.compile(r"etu(\d+)_([a-zA-Z]+)\.txt")

            for root, dirs, files in os.walk(self.dernier_chemin_corpus):
                # Chaque dossier rencontré (sauf la racine) est un sous-corpus potentiel
                if root != self.dernier_chemin_corpus:
                    nb_sous_corpus += 1
                
                for fichier in files:
                    # Analyse du nom de fichier
                    match = pattern_etu.match(fichier)
                    if match:
                        # Si le fichier respecte le format etuXX_lang.txt
                        id_etu = match.group(1) # Le XX
                        langue = match.group(2) # Le lang
                        
                        etudiants_ids.add(id_etu)
                        compteur_langues[langue] += 1
                    elif fichier.endswith(".txt"):
                        # Cas fallback si le nom n'est pas standard mais c'est du texte
                        compteur_langues["inconnu"] += 1

            # --- INSERTION DANS LE TABLEAU ---
            
            # A. Structure
            self.tree_stats.insert("", tk.END, values=("--- STRUCTURE ---", ""))
            self.tree_stats.insert("", tk.END, values=("Sous-corpus (Dossiers)", nb_sous_corpus))
            
            # B. Étudiants (Identifiés par le motif etuXX)
            self.tree_stats.insert("", tk.END, values=("--- ETUDIANTS ---", ""))
            self.tree_stats.insert("", tk.END, values=("Nombre d'étudiants (XX)", len(etudiants_ids)))
            
            # Afficher quelques IDs pour vérifier
            liste_ids = sorted(list(etudiants_ids))
            if liste_ids:
                resume_ids = ", ".join(liste_ids[:5]) + ("..." if len(liste_ids) > 5 else "")
                self.tree_stats.insert("", tk.END, values=("IDs détectés", resume_ids))

            # C. Langues
            self.tree_stats.insert("", tk.END, values=("--- LANGUES ---", ""))
            for lang, count in compteur_langues.items():
                self.tree_stats.insert("", tk.END, values=(f"Langue '{lang}'", f"{count} fichiers"))

            # D. Stats Lexicales (Appel Backend)
            stats_lex = self.moteur.calculer_stats_lexicales()
            if stats_lex:
                self.tree_stats.insert("", tk.END, values=("--- ANALYSE LEXICALE ---", ""))
                self.tree_stats.insert("", tk.END, values=("Total Tokens", stats_lex['Total']))
                self.tree_stats.insert("", tk.END, values=("Richesse (TTR)", f"{stats_lex['TTR']:.4f}"))
                self.tree_stats.insert("", tk.END, values=("Taux Hapax", f"{stats_lex['Hapax']:.2%}"))

            self.ajouter_log(f"Analyse terminée : {len(etudiants_ids)} étudiants trouvés.", "SUCCESS")

        except Exception as e:
            self.ajouter_log(f"Erreur Analyse: {e}", "ERROR")
            import traceback
            traceback.print_exc()
        finally:
            self._stop_work()
    def action_rechercher(self):
        txt = self.ent_req.get()
        if not txt: return
        self._start_work()
        try:
            cfg = {"stopwords":True, "non_alphabetiques":True, "longueur_min":3}
            if self.cb_prep.get() == "Brut": cfg = {"stopwords":False, "non_alphabetiques":False, "longueur_min":0}
            
            fiche = {
                "texte": txt, 
                "config_pretraitement": cfg, 
                "config_descripteurs": {"types": [self.map_desc[self.cb_desc.get()]]}, 
                "type_distance": self.map_dist[self.cb_dist.get()], 
                "granularite": self.cb_gran.get().lower()
            }
            res = self.moteur.rechercher(fiche, k=int(self.spin_k.get()))
            for i in self.tree.get_children(): self.tree.delete(i)
            self.stored_results = {}
            for i, (uid, s, apercu, full_txt) in enumerate(res):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", iid=uid, values=(i+1, uid, f"{s:.4f}", apercu), tags=(tag,))
                self.stored_results[uid] = full_txt
            self._update_hist()
            self.action_nuage_global(res)
        except Exception as e: self.ajouter_log(f"Erreur Recherche: {e}", "ERROR")
        finally: self._stop_work()

    def on_double_click_result(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id and item_id in self.stored_results:
            top = tk.Toplevel(self.root); top.title(f"Contenu : {item_id}"); top.geometry("600x400")
            txt = scrolledtext.ScrolledText(top, font=("Segoe UI", 11)); txt.pack(fill=tk.BOTH, expand=True); txt.insert(tk.END, self.stored_results[item_id])

    def _update_hist(self):
        self.listbox_hist.delete(0, tk.END)
        for s in self.moteur.historique_scenarios:
            self.listbox_hist.insert(tk.END, f"Scenario #{s['id']} | Req: '{s['requete']}' | {s['config']['desc'].upper()} | {s['config']['gran']}")

    def _afficher_fig(self, fig, target=None):
        if target is None: target = self.canvas_frame
        plt.close('all'); 
        for w in target.winfo_children(): w.destroy()
        if not fig: return
        cv = FigureCanvasTkAgg(fig, master=target); cv.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        cv.get_tk_widget().bind("<Configure>", lambda e: (fig.set_size_inches(e.width/100, e.height/100), cv.draw()))

    def _afficher_fig_scrollable(self, fig, target_frame):
        plt.close('all')
        for w in target_frame.winfo_children(): w.destroy()
        canvas_tk = tk.Canvas(target_frame, bg="white")
        h_scroll = ttk.Scrollbar(target_frame, orient="horizontal", command=canvas_tk.xview)
        v_scroll = ttk.Scrollbar(target_frame, orient="vertical", command=canvas_tk.yview)
        scrollable_frame = tk.Frame(canvas_tk, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas_tk.configure(scrollregion=canvas_tk.bbox("all")))
        canvas_tk.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_tk.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        canvas_tk.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        target_frame.grid_rowconfigure(0, weight=1); target_frame.grid_columnconfigure(0, weight=1)
        cv = FigureCanvasTkAgg(fig, master=scrollable_frame); cv.draw(); cv.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def action_nuage_global(self, res=None):
        if not res and self.moteur.historique_scenarios: res = self.moteur.historique_scenarios[-1]["resultats"]
        if res: self._afficher_fig(self.moteur.generer_nuage_resultats(res))

    def action_nuage_doc(self):
        sel = self.tree.selection()
        if sel: self._afficher_fig(self.moteur.generer_nuage_unique(sel[0]))

    def action_comparer(self):
        try:
            # 1. Validation de la sélection
            selection = self.listbox_hist.curselection()
            if not selection:
                messagebox.showinfo("Info", "Veuillez sélectionner des requêtes dans l'historique.")
                return
                
            indices = [int(i) for i in selection]
            if len(indices) < 2:
                messagebox.showwarning("Attention", "Sélectionnez au moins 2 scénarios pour comparer.")
                return

            # 2. Récupération des données
            scenarios = self.moteur.get_comparaison_data(indices)
            if not scenarios:
                self.ajouter_log("Aucune donnée de comparaison disponible.", "WARNING")
                return

            nb_scenarios = len(scenarios)
            
            # --- CORRECTION MAJEURE : MODE SCROLLABLE ---
            # On définit une taille FIXE et GRANDE (10x12 pouces) pour garantir la lisibilité.
            # On utilise constrained_layout pour éviter que les textes ne se chevauchent.
            fig = plt.figure(figsize=(10, 12), dpi=100, constrained_layout=True)
            
            gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.2])

            # --- GRAPH 1 : BOXPLOT (HAUT) ---
            ax_box = fig.add_subplot(gs[0, 0])
            
            data_scores = []
            labels = []
            for sc in scenarios:
                scores = [s for s in sc["scores_bruts"] if np.isfinite(s) and s > -999]
                if not scores: scores = [0]
                data_scores.append(scores)
                labels.append(f"#{sc['id']}")

            box = ax_box.boxplot(data_scores, patch_artist=True)
            colors = plt.cm.viridis(np.linspace(0.3, 0.8, len(data_scores)))
            for patch, color in zip(box['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
                
            ax_box.set_xticklabels(labels, fontweight='bold')
            ax_box.set_title("Distribution des Scores", fontsize=12, fontweight='bold')
            ax_box.grid(True, linestyle=':', alpha=0.6)

            # --- GRAPH 2 : HEATMAP (BAS) ---
            ax_heat = fig.add_subplot(gs[1, 0])
            
            matrice_sim = np.zeros((nb_scenarios, nb_scenarios))
            for i in range(nb_scenarios):
                set_i = set(res[0] for res in scenarios[i]["resultats"]) 
                for j in range(nb_scenarios):
                    set_j = set(res[0] for res in scenarios[j]["resultats"])
                    inter = len(set_i.intersection(set_j))
                    union = len(set_i.union(set_j))
                    matrice_sim[i, j] = inter / union if union > 0 else 0

            im = ax_heat.imshow(matrice_sim, cmap="coolwarm", vmin=0, vmax=1, aspect='auto')
            
            for i in range(nb_scenarios):
                for j in range(nb_scenarios):
                    val = matrice_sim[i, j]
                    c_text = "white" if (val > 0.6 or val < 0.4) else "black"
                    ax_heat.text(j, i, f"{val:.2f}", ha="center", va="center", color=c_text, fontweight='bold')

            ax_heat.set_xticks(range(nb_scenarios))
            ax_heat.set_yticks(range(nb_scenarios))
            ax_heat.set_xticklabels([f"S#{sc['id']}" for sc in scenarios], rotation=0, fontweight='bold')
            ax_heat.set_yticklabels([f"S#{sc['id']}" for sc in scenarios], fontweight='bold')
            ax_heat.set_title("Similarité (Jaccard)", fontsize=12, fontweight='bold')

            plt.colorbar(im, ax=ax_heat, fraction=0.05, pad=0.04)

            # --- AFFICHAGE VIA LA MÉTHODE SCROLLABLE ---
            # Cela placera le grand graphique dans une zone avec ascenseurs
            self._afficher_fig_scrollable(fig, target_frame=self.frame_comp_res)
            
            self.ajouter_log("Comparaison affichée (Mode Scrollable).", "SUCCESS")

        except Exception as e:
            self.ajouter_log(f"Erreur Comparaison : {e}", "ERROR")
            print(e)
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceMoteurRecherche(root)
    root.mainloop()
