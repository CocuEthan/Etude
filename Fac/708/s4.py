import numpy as np
import math

#I  Représentations vectorielles
#a Représentation par indices 

def texte_vers_indices(texte, vocabulaire_direct):
    """
    Description :
        Transforme un texte en une liste d'indices
        basée sur le vocabulaire fourni.
    
    Paramètres :
        texte              str ou list, la phrase brute ou la liste de tokens.
        vocabulaire_direct dict, mapping {mot : index}.
    
    Retour :
        list, liste d'entiers. Les mots inconnus sont notés -1.
    """
    if not texte:
        return []
    if isinstance(texte, str):
        tokens = texte.split()
    else:
        tokens = texte
        
    indices = []
    for mot in tokens:
        idx = vocabulaire_direct.get(mot, -1)
        indices.append(idx)
        
    return indices


def indices_vers_texte(indices, vocabulaire_inverse):
    """
    Description :
        Reconstruit un texte à partir d'une liste d'indices.
    
    Paramètres :
        indices             list, liste d'entiers.
        vocabulaire_inverse dict, mapping {index : mot}.
    
    Retour :
        str, le texte reconstruit. Les indices inconnus sont marqués .
    """
    if not indices:
        return ""
        
    mots = []
    for idx in indices:
        mot = vocabulaire_inverse.get(idx, "<UNK>")
        mots.append(mot)
        
    return " ".join(mots)


def test_conversion_indices():
    print("\n Test : Conversion Texte <-> Indices ")
    
    #  Configuration (Données de l'exemple) 
    vocabulaire_direct = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    vocabulaire_inverse = {0: 'chat', 1: 'chien', 2: 'dort', 3: 'mange', 4: 'maison'}
    
    #  1. Test texte_vers_indices 
    
    # Cas normal : "chat dort" -> [0, 2]
    res1 = texte_vers_indices("chat dort", vocabulaire_direct)
    assert res1 == [0, 2]
    
    # Cas mixte : "chien mange maison" -> [1, 3, 4]
    res2 = texte_vers_indices("chien mange maison", vocabulaire_direct)
    assert res2 == [1, 3, 4]
    
    # Cas mots inconnus : "souris mange fromage" -> [-1, 3, -1]
    res3 = texte_vers_indices("souris mange fromage", vocabulaire_direct)
    assert res3 == [-1, 3, -1]
    
    print(" Test 'texte_vers_indices' validé.")

    #  2. Test indices_vers_texte 
    
    # Cas normal : [1, 2, 0, 3] -> "chien dort chat mange"
    res4 = indices_vers_texte([1, 2, 0, 3], vocabulaire_inverse)
    assert res4 == "chien dort chat mange"
    
    # Cas indice inconnu : [10, 2, 3] -> "<UNK> dort mange"
    # (L'énoncé suggère un token spécial ou vide, ici j'utilise <UNK> pour la clarté)
    res5 = indices_vers_texte([10, 2, 3], vocabulaire_inverse)
    assert "<UNK>" in res5 and "dort" in res5
    
    print(" Test 'indices_vers_texte' validé.")

# Lancer les tests
#test_conversion_indices()

#b One-Hot Encoding

def one_hot_encode_mots(texte, vocabulaire_direct):
    """
    Description :
        Transforme un texte en une liste de vecteurs One-Hot.
        Préserve l'ordre des mots.
    
    Paramètres :
        texte               str ou list, la phrase brute ou la liste de tokens.
        vocabulaire_direct  dict, mapping {mot : index}.
    
    Retour :
        list, une liste de tableaux numpy.
              Chaque vecteur a la taille du vocabulaire.
    """
    if not texte or not vocabulaire_direct:
        return []
    if isinstance(texte, str):
        tokens = texte.split()
    else:
        tokens = texte
        
    taille = len(vocabulaire_direct)
    res = []
    
    for mot in tokens:
        vecteur = np.zeros(taille, dtype=int)
        if mot in vocabulaire_direct:
            index = vocabulaire_direct[mot]
            vecteur[index] = 1
        
        res.append(vecteur)
        
    return res


def one_hot_decode(vecteurs, vocabulaire_inverse):
    """
    Description :
        Reconstruit le texte à partir d'une liste de vecteurs One-Hot.
    
    Paramètres :
        vecteurs             list, liste de tableaux numpy (One-Hot).
        vocabulaire_inverse  dict, mapping {index : mot}.
    
    Retour :
        str, le texte reconstruit.
    """
    if not vecteurs:
        return ""
        
    mots = []
    
    for vec in vecteurs:
        if np.sum(vec) == 0:
            mots.append("<UNK>")
            continue
            
        index = np.argmax(vec)
        mot = vocabulaire_inverse.get(index, "<UNK>")
        mots.append(mot)
        
    return " ".join(mots)


def test_one_hot_encoding():
    print("\n Test : One-Hot Encoding ")
    
    #  Configuration 
    # Vocabulaire de l'énoncé (taille 5)
    vocab_dir = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    vocab_inv = {0: 'chat', 1: 'chien', 2: 'dort', 3: 'mange', 4: 'maison'}
    
    #  1. Test Encodage 
    # "chat maison" -> doit donner [[1,0,0,0,0], [0,0,0,0,1]]
    phrase = "chat maison"
    vecteurs = one_hot_encode_mots(phrase, vocab_dir)
    
    print(f"Phrase : '{phrase}'")
    print("Vecteurs obtenus :")
    for v in vecteurs:
        print(f"  {v}")
    
    # Vérifications
    assert len(vecteurs) == 2
    # chat (index 0)
    assert vecteurs[0][0] == 1 and np.sum(vecteurs[0]) == 1
    # maison (index 4)
    assert vecteurs[1][4] == 1 and np.sum(vecteurs[1]) == 1
    
    #  2. Test Décodage 
    # On reprend les vecteurs générés pour voir si on retombe sur nos pattes
    texte_reconstruit = one_hot_decode(vecteurs, vocab_inv)
    print(f"Décodage : '{texte_reconstruit}'")
    
    assert texte_reconstruit == "chat maison"
    
    #  3. Test Mot Inconnu 
    # "souris" n'est pas dans le vocabulaire -> vecteur nul
    vec_inconnu = one_hot_encode_mots("souris", vocab_dir)
    assert np.sum(vec_inconnu[0]) == 0
    
    # Décodage du vecteur nul -> <UNK>
    decode_inconnu = one_hot_decode(vec_inconnu, vocab_inv)
    assert decode_inconnu == "<UNK>"
    
    print(" Test 'One-Hot Encoding' validé.")


#test_one_hot_encoding()

#c Sac de mots (Bag-of-Words «BoW») binaire 

def bag_of_words_binaire(texte, vocabulaire_direct):
    """
    Description :
        Transforme un texte en vecteur binaire  selon le vocabulaire.
        Indique seulement la PRÉSENCE des mots, sans compter les occurrences.
    
    Paramètres :
        texte               str ou list, le document à vectoriser.
        vocabulaire_direct  dict, mapping {mot : index}.
    
    Retour :
        numpy.array, vecteur de taille |V| contenant des 0 et des 1.
    """
    if not vocabulaire_direct:
        return []
    taille = len(vocabulaire_direct)
    vecteur = np.zeros(taille, dtype=int)
    
    if not texte:
        return vecteur
    if isinstance(texte, str):
        tokens = texte.split()
    else:
        tokens = texte
        
    for mot in tokens:
        if mot in vocabulaire_direct:
            index = vocabulaire_direct[mot]
            vecteur[index] = 1
            
    return vecteur


def bag_of_words_decode(vecteur, vocabulaire_inverse):
    """
    Description :
        Reconstruit la liste des mots présents à partir d'un vecteur binaire.
        Attention : L'ordre d'origine est perdu, les mots sont restitués
        dans l'ordre du dictionnaire (ordre des indices).
    
    Paramètres :
        vecteur              list ou np.array, le vecteur binaire.
        vocabulaire_inverse  dict, mapping {index : mot}.
    
    Retour :
        str, la liste des mots présents séparés par un espace.
    """
    if vecteur is None or len(vecteur) == 0:
        return ""
    presents = []
    for index, valeur in enumerate(vecteur):
        if valeur == 1:
            mot = vocabulaire_inverse.get(index, "<UNK>")
            presents.append(mot)
            
    return " ".join(presents)


def test_bag_of_words_binaire():
    print("\n Test : Bag-of-Words Binaire ")
    
    #  Configuration (Basée sur l'exemple de l'énoncé) 
    # Vocabulaire : ['chat', 'chien', 'dort', 'mange', 'maison']
    vocab_dir = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    vocab_inv = {0: 'chat', 1: 'chien', 2: 'dort', 3: 'mange', 4: 'maison'}
    
    #  1. Test Encodage 
    
    # Cas 1 : "chat dort" -> Indices 0 et 2
    # Attendu : [1, 0, 1, 0, 0]
    phrase1 = "chat dort"
    vec1 = bag_of_words_binaire(phrase1, vocab_dir)
    print(f"Phrase : '{phrase1}' -> {vec1}")
    
    assert vec1[0] == 1 # chat
    assert vec1[2] == 1 # dort
    assert vec1[1] == 0 # chien absent
    assert np.sum(vec1) == 2
    
    # Cas 2 : "chien mange maison" -> Indices 1, 3, 4
    # Attendu : [0, 1, 0, 1, 1]
    phrase2 = "chien mange maison"
    vec2 = bag_of_words_binaire(phrase2, vocab_dir)
    assert np.array_equal(vec2, [0, 1, 0, 1, 1])
    
    # Cas 3 : Mots inconnus et répétitions
    # "chat chat souris" -> Indices 0 (chat). Souris ignoré.
    # En binaire, même si "chat" est là 2 fois, la valeur reste 1.
    phrase3 = "chat chat souris"
    vec3 = bag_of_words_binaire(phrase3, vocab_dir)
    # Attendu : [1, 0, 0, 0, 0]
    assert vec3[0] == 1
    assert np.sum(vec3) == 1
    
    print(" Test 'bag_of_words_binaire' validé.")

    #  2. Test Décodage 
    
    # Vecteur : [1, 0, 1, 0, 0] (chat, dort)
    vec_a_decoder = [1, 0, 1, 0, 0]
    texte_decode = bag_of_words_decode(vec_a_decoder, vocab_inv)
    print(f"Vecteur {vec_a_decoder} -> '{texte_decode}'")
    
    # Note : L'ordre est celui des indices (0 puis 2), donc "chat dort"
    assert "chat" in texte_decode
    assert "dort" in texte_decode
    assert "chien" not in texte_decode
    
    # Vecteur vide : [0, 0, 0, 0, 0]
    assert bag_of_words_decode([0, 0, 0, 0, 0], vocab_inv) == ""
    
    print(" Test 'bag_of_words_decode' validé.")


#test_bag_of_words_binaire()

#2  Représentations pondérées et statistiques 
#a Sac-de-mots (Bag-of-Words «BoW») occurrences

def bag_of_words_occurrences(texte, vocabulaire_direct):
    """
    Description :
        Transforme un texte en vecteur de comptage.
    
    Paramètres :
        texte               str ou list, le document à vectoriser.
        vocabulaire_direct  dict, mapping {mot : index}.
    
    Retour :
        numpy.array, vecteur d'entiers de taille |V|.
    """
    if not vocabulaire_direct:
        return []
    
    taille = len(vocabulaire_direct)
    # Initialisation d'un vecteur de zéros
    vecteur = np.zeros(taille, dtype=int)
    
    if not texte:
        return vecteur
    
    # Tokenisation simple si nécessaire
    if isinstance(texte, str):
        tokens = texte.split()
    else:
        tokens = texte
        
    for mot in tokens:
        if mot in vocabulaire_direct:
            index = vocabulaire_direct[mot]
            vecteur[index] += 1
            
    return vecteur


def bag_of_words_occurrences_decode(vecteur, vocabulaire_inverse):
    """
    Description :
        Reconstruit le texte en répétant les mots selon leur nombre d'occurrences.
        (L'ordre original est perdu, on suit l'ordre du vocabulaire).
    
    Paramètres :
        vecteur              list ou np.array, le vecteur de comptage.
        vocabulaire_inverse  dict, mapping {index : mot}.
    
    Retour :
        str, le texte reconstruit.
    """
    if vecteur is None or len(vecteur) == 0:
        return ""
        
    mots_presents = []
    
    for index, count in enumerate(vecteur):
        if count > 0:
            mot = vocabulaire_inverse.get(index, "<UNK>")
            mots_presents.extend([mot] * int(count))
            
    return " ".join(mots_presents)

def test_bag_of_words_occurrences():
    print("\n Test : Bag-of-Words Occurrences ")
    
    #  Configuration 
    # Vocabulaire : ['chat', 'chien', 'dort', 'mange', 'maison']
    vocab_dir = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    vocab_inv = {0: 'chat', 1: 'chien', 2: 'dort', 3: 'mange', 4: 'maison'}
    
    #  1. Test Encodage (Avec répétitions) 
    
    # Phrase : "chat dort chat"
    # chat (idx 0) : 2 fois
    # dort (idx 2) : 1 fois
    # Attendu : [2, 0, 1, 0, 0]
    phrase1 = "chat dort chat"
    vec1 = bag_of_words_occurrences(phrase1, vocab_dir)
    print(f"Phrase : '{phrase1}' -> {vec1}")
    
    assert vec1[0] == 2
    assert vec1[2] == 1
    assert vec1[1] == 0
    assert np.sum(vec1) == 3
    
    #  2. Test Décodage (Avec répétitions) 
    
    # Vecteur : [2, 1, 0, 0, 0] -> chat(2), chien(1)
    vec_a_decoder = [2, 1, 0, 0, 0]
    texte_decode = bag_of_words_occurrences_decode(vec_a_decoder, vocab_inv)
    print(f"Vecteur {vec_a_decoder} -> '{texte_decode}'")
    
    # Note : L'ordre de sortie suit l'index (0 puis 1) -> "chat chat chien"
    attendu = "chat chat chien"
    assert texte_decode == attendu
    
    #  3. Cas Vide 
    vec_vide = bag_of_words_occurrences("", vocab_dir)
    assert np.sum(vec_vide) == 0
    
    print(" Test 'bag_of_words_occurrences' validé.")


#test_bag_of_words_occurrences()

#b TF (Term Frequency)

def calcul_tf(texte, vocabulaire_direct):
    """
    Description :
        Calcule le vecteur TF d'un document.
        TF(t) = Nombre d'occurrences de t / Nombre total de mots dans le doc.
    
    Paramètres :
        texte               str ou list, le document à vectoriser.
        vocabulaire_direct  dict, mapping {mot : index}.
    
    Retour :
        numpy.array, vecteur de floats de taille |V|.
    """
    if not vocabulaire_direct:
        return []
    
    taille = len(vocabulaire_direct)
    vecteur = np.zeros(taille, dtype=float)
    
    if not texte:
        return vecteur
    if isinstance(texte, str):
        tokens = texte.split()
    else:
        tokens = texte
    
    nb = len(tokens)
    
    if nb == 0:
        return vecteur
        
    for mot in tokens:
        if mot in vocabulaire_direct:
            index = vocabulaire_direct[mot]
            vecteur[index] += 1
            
    vecteur = vecteur / nb
    
    return vecteur

def test_calcul_tf():
    print("\n Test : Calcul TF (Term Frequency) ")
    vocab = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    
    #  Cas 1 : "chat dort" 
    # Total mots = 2. chat=1, dort=1.
    # TF = 1/2 = 0.5
    res1 = calcul_tf("chat dort", vocab)
    print(f"TF 'chat dort' : {res1}")
    
    assert res1[0] == 0.5 
    assert res1[2] == 0.5 
    assert res1[1] == 0.0
    
    #  Cas 2 : "chien mange maison" 
    # Total mots = 3.
    # TF = 1/3 ≈ 0.333
    res2 = calcul_tf("chien mange maison", vocab)
    print(f"TF 'chien mange maison' : {res2}")
    
    assert np.isclose(res2[1], 0.33333333)
    assert np.isclose(res2[3], 0.33333333) 
    assert np.isclose(res2[4], 0.33333333)
    
    #  Cas 3 : Répétition "chat chat chat" 
    # Total = 3. chat=3.
    # TF chat = 3/3 = 1.0
    res3 = calcul_tf("chat chat chat", vocab)
    assert res3[0] == 1.0
    
    print(" Test 'calcul_tf' validé.")


#test_calcul_tf()

#c IDF (Inverse Document Frequency) 

def calcul_idf(corpus, vocabulaire_direct, methode='smooth'):
    """
    Description :
        Calcule le vecteur IDF pour l'ensemble du vocabulaire selon la méthode choisie.
        
    Paramètres :
        corpus              dict, {id : liste de listes de tokens}.
        vocabulaire_direct  dict, {mot : index}.
        methode             str, variante de calcul :
                              'classique', 'smooth', 'smooth_p1', 'logplus', 
                              'max', 'bm25', 'bm25_smooth'.
    
    Retour :
        numpy.array, vecteur de floats de taille |V| contenant les scores IDF.
    """
    if not corpus or not vocabulaire_direct:
        return np.array([])

    N = len(corpus)
    taille = len(vocabulaire_direct)
    df = np.zeros(taille, dtype=float)
    
    for doc in corpus.values():
        unique = set(token for phrase in doc for token in phrase)
        
        for mot in unique:
            if mot in vocabulaire_direct:
                index = vocabulaire_direct[mot]
                df[index] += 1
    idf = np.zeros(taille, dtype=float)
    if methode == 'classique':
        idf = np.log(N / df)
        
    elif methode == 'smooth':
        idf = np.log(N / (df + 1))
        
    elif methode == 'smooth_p1':
        idf = np.log(N / (df + 1)) + 1
        
    elif methode == 'logplus':
        idf = np.log(1 + (N / df))
        
    elif methode == 'max':
        max_df = np.max(df) if len(df) > 0 else 1
        idf = np.log(max_df / (1 + df))
        
    elif methode == 'bm25':
        val = (N - df) / df
        val = np.maximum(val, 1e-10) 
        idf = np.log(val)
        
    elif methode == 'bm25_smooth':
        val = (N - df + 0.5) / (df + 0.5)
        val = np.maximum(val, 1e-10)
        idf = np.log(val)
    else:
        print(f"Méthode '{methode}' inconnue. Utilisation de 'smooth'.")
        idf = np.log(N / (df + 1))
    return idf


def test_calcul_idf():
    print("\n Test : calcul_idf ")
    
    # - Configuration (Exemple du cours) -
    # Doc 1 : chat dort
    # Doc 2 : chien dort
    # Doc 3 : chat mange
    # Doc 4 : chien mange maison
    
    corpus_test = {
        "d1": [["chat", "dort"]],
        "d2": [["chien", "dort"]],
        "d3": [["chat", "mange"]],
        "d4": [["chien", "mange", "maison"]]
    }
    
    # Vocabulaire
    # df attendus :
    # chat : 2 (d1, d3)
    # chien : 2 (d2, d4)
    # dort : 2 (d1, d2)
    # mange : 2 (d3, d4)
    # maison : 1 (d4)
    
    vocab_dir = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    
    # - 1. Test Méthode Classique -
    idf_classique = calcul_idf(corpus_test, vocab_dir, methode='classique')
    
    print(f"IDF Classique : {idf_classique}")
    
    # Vérifications manuelles (log base e par défaut dans numpy)
    # log(4/2) = 0.6931...
    # log(4/1) = 1.3862...
    
    # chat (index 0, df=2)
    assert np.isclose(idf_classique[0], 0.6931, atol=1e-3)
    # maison (index 4, df=1)
    assert np.isclose(idf_classique[4], 1.3862, atol=1e-3)
    
    # - 2. Test Méthode Smooth -
    # log(4 / (2+1)) = log(1.33) = 0.287
    idf_smooth = calcul_idf(corpus_test, vocab_dir, methode='smooth')
    assert np.isclose(idf_smooth[0], np.log(4/3), atol=1e-3)
    
    # - 3. Test Méthode Max -
    # max(df) = 2
    # Pour maison (df=1) : log( 2 / (1+1) ) = log(1) = 0
    idf_max = calcul_idf(corpus_test, vocab_dir, methode='max')
    assert np.isclose(idf_max[4], 0.0, atol=1e-3)
    
    # - 4. Test Méthode BM25 Smooth -
    # Pour chat (df=2, N=4) : log( (4 - 2 + 0.5) / (2 + 0.5) ) = log(2.5 / 2.5) = log(1) = 0
    idf_bm25 = calcul_idf(corpus_test, vocab_dir, methode='bm25_smooth')
    assert np.isclose(idf_bm25[0], 0.0, atol=1e-3)
    
    print(" Test 'calcul_idf' validé.")

#test_calcul_idf()

#d TF-IDF 


def calcul_tf_idf(corpus, vocabulaire_direct, methode_idf='smooth'):
    """
    Description :
        Calcule la matrice TF-IDF pour l'ensemble du corpus.
        TF-IDF = TF * IDF.
    
    Paramètres :
        corpus              dict, {id : liste de listes de tokens}.
        vocabulaire_direct  dict, mapping {mot : index}.
        methode_idf         str, méthode pour le calcul IDF.
    
    Retour :
        dict, {id : numpy.array} où chaque array est le vecteur TF-IDF du document.
    """
    if not corpus or not vocabulaire_direct:
        return {}
    try:
        vecteurIdf = calcul_idf(corpus, vocabulaire_direct, methode=methode_idf)
    except NameError:
        return {}

    matrice = {}

    for id, doc in corpus.items():
        tokens = [mot for phrase in doc for mot in phrase]
        
        try:
            vecteurTf = calcul_tf(tokens, vocabulaire_direct)
        except NameError:
            print("Erreur : La fonction 'calcul_tf' est manquante.")
            return {}      
        vecteurTfIdf = vecteurTf * vecteurIdf  
        matrice[id] = vecteurTfIdf 
    return matrice

def test_calcul_tf_idf():
    print("\n Test : Calcul TF-IDF ")
    
    # - Configuration (Exemple du cours) -
    corpus_test = {
        "d1": [["chat", "dort"]],
        "d2": [["chien", "dort"]],
        "d3": [["chat", "mange"]],
        "d4": [["chien", "mange", "maison"]]
    }
    
    vocab_dir = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    
    # - Exécution -
    # On utilise la méthode 'classique' pour retrouver les chiffres de l'exemple
    matrice = calcul_tf_idf(corpus_test, vocab_dir, methode_idf='classique')
    
    print("Résultats TF-IDF :")
    for doc_id, vec in matrice.items():
        # On arrondit pour l'affichage
        print(f"  {doc_id} : {np.round(vec, 3)}")
        
    # - Vérifications -
    
    # Vérifions le Doc 1 ("chat dort")
    vec_d1 = matrice["d1"]
    
    # chat (index 0) : TF=0.5 * IDF=0.693 = 0.3465
    assert np.isclose(vec_d1[0], 0.3465, atol=1e-3)
    # chien (index 1) : 0
    assert vec_d1[1] == 0.0
    # dort (index 2) : 0.3465
    assert np.isclose(vec_d1[2], 0.3465, atol=1e-3)
    
    # Vérifions le Doc 4 ("chien mange maison")
    # TF = [0, 0.33, 0, 0.33, 0.33]
    # IDF = [..., 0.693, ..., 0.693, 1.386]
    vec_d4 = matrice["d4"]
    
    # maison (index 4) : TF=0.333 * IDF=1.386 = 0.462
    assert np.isclose(vec_d4[4], 0.462, atol=1e-3)
    
    print(" Test 'calcul_tf_idf' validé.")

#test_calcul_tf_idf()

#e BM25 

def calcul_bm25(corpus, vocabulaire_direct, k1=1.5, b=0.75):
    """
    Description :
        Calcule la matrice BM25 pour l'ensemble du corpus.
        BM25 est une amélioration du TF-IDF prenant en compte la saturation
        de la fréquence et la longueur des documents.
    
    Paramètres :
        corpus              dict, {id : liste de listes de tokens}.
        vocabulaire_direct  dict, mapping {mot : index}.
        k1                  float, paramètre de saturation .
        b                   float, paramètre de longueur.
    
    Retour :
        dict, {id : numpy.array} vecteurs BM25.
    """
    if not corpus or not vocabulaire_direct:
        return {}

    N = len(corpus)
    longueurs = {}
    total = 0
    for id, doc in corpus.items():
        tokens = [mot for phrase in doc for mot in phrase]
        l = len(tokens)
        longueurs[id] = l
        total += l
        
    avgdl = total / N if N > 0 else 1
    
    try:
        vecteurIdf = calcul_idf(corpus, vocabulaire_direct, methode='bm25_smooth')
        vecteurIdf = np.maximum(vecteurIdf, 0)
    except NameError:
        print("Erreur : fonction 'calcul_idf' manquante.")
        return {}

    matriceBm25 = {}

    for id, doc in corpus.items():
        
        tokens = [mot for phrase in doc for mot in phrase]
        
        vecteur = np.zeros(len(vocabulaire_direct))
        for mot in tokens:
            if mot in vocabulaire_direct:
                vecteur[vocabulaire_direct[mot]] += 1
        lenD = longueurs[id]
        numerateur = vecteur * (k1 + 1)
        denominateur = vecteur + k1 * (1 - b + b * (lenD / avgdl))
        vecteurBm25 = vecteurIdf * (numerateur / denominateur)
        matriceBm25[id] = vecteurBm25
        
    return matriceBm25

def test_calcul_bm25():
    print("\n Test : Calcul BM25 ")
    
    # - Configuration -
    # Doc 1 : chat dort (len=2)
    # Doc 2 : chien dort (len=2)
    # Doc 3 : chat mange (len=2)
    # Doc 4 : chien mange maison (len=3)
    corpus_test = {
        "d1": [["chat", "dort"]],
        "d2": [["chien", "dort"]],
        "d3": [["chat", "mange"]],
        "d4": [["chien", "mange", "maison"]]
    }
    # Moyenne longueurs (avgdl) = (2+2+2+3)/4 = 2.25
    
    vocab_dir = {'chat': 0, 'chien': 1, 'dort': 2, 'mange': 3, 'maison': 4}
    
    # - Exécution -
    matrice = calcul_bm25(corpus_test, vocab_dir, k1=1.5, b=0.75)
    
    print("Résultats BM25 :")
    for doc_id, vec in matrice.items():
        # On affiche uniquement les valeurs non nulles pour la lisibilité
        non_zeros = {k: round(v, 3) for k, v in zip(vocab_dir.keys(), vec) if v > 0}
        print(f"  {doc_id} : {non_zeros}")
        
    # - Vérifications -
    
    # 1. Structure
    assert len(matrice) == 4
    assert len(matrice["d1"]) == 5
    
    # 2. Logique du poids
    # 'maison' est rare (df=1) -> IDF élevé
    # 'dort' est moyen (df=2) -> IDF plus faible (voire 0 avec BM25 strict sur petit corpus)
    
    vec_d4 = matrice["d4"]
    score_maison = vec_d4[4] # maison
    score_chien = vec_d4[1]  # chien
    
    # Sur ce tout petit corpus, avec BM25 Smooth :
    # IDF(maison) = log((4-1+0.5)/(1+0.5)) = log(2.33) > 0
    # IDF(chien) = log((4-2+0.5)/(2+0.5)) = log(1) = 0
    # Donc 'chien' aura un score de 0 (car IDF=0). C'est normal sur un micro-corpus équilibré.
    
    assert score_maison > score_chien
    
    # 3. Vérification des zéros (mots absents)
    assert matrice["d1"][1] == 0 # chien absent de d1
    
    print(" Test 'calcul_bm25' validé.")

#test_calcul_bm25()

#3 Représentations normalisées
#a Normalisation L1 (somme = 1) 

def normaliser_L1(v):
    """
    Description :
        Normalise un vecteur selon la norme L1 (Somme = 1).
        Transforme le vecteur en distribution de probabilité.
    
    Paramètres :
        v  list ou numpy.array, le vecteur à normaliser.
    
    Retour :
        list, le vecteur normalisé.
    """
    # Conversion en array numpy pour faciliter les calculs
    vecteur = np.array(v, dtype=float)
    
    # Calcul de la somme des composantes (valeur absolue pour être rigoureux, 
    # même si en TF-IDF tout est positif)
    somme = np.sum(np.abs(vecteur))
    
    # Sécurité : Division par zéro
    if somme == 0:
        return vecteur.tolist()
        
    # Normalisation
    res = vecteur / somme
    
    return res.tolist()

def test_normaliser_L1():
    print("\n Test : normaliser_L1 ")
    
    # Cas 1 : Vecteur standard
    # [2, 0, 2] -> Somme = 4 -> [0.5, 0, 0.5]
    v1 = [2, 0, 2]
    res1 = normaliser_L1(v1)
    
    print(f"  Vecteur : {v1}")
    print(f"  Normalisé L1 : {res1}")
    
    assert res1 == [0.5, 0.0, 0.5]
    # La somme doit faire 1
    assert sum(res1) == 1.0
    
    # Cas 2 : Vecteur nul
    v2 = [0, 0, 0]
    res2 = normaliser_L1(v2)
    assert res2 == [0.0, 0.0, 0.0]
    
    # Cas 3 : TF (déjà entre 0 et 1, mais somme != 1)
    # [0.5, 0.5] -> Somme = 1 -> Reste pareil
    v3 = [0.5, 0.5]
    assert normaliser_L1(v3) == [0.5, 0.5]
    
    print(" Test 'normaliser_L1' validé.")

#test_normaliser_L1()

#b Normalisation L2 (norme = 1) 
def normaliser_L2(v):
    """
    Description :
        Normalise un vecteur selon la norme L2.
        La somme des carrés des éléments vaudra 1.
        Indispensable pour la similarité cosinus.
    
    Paramètres :
        v  list ou numpy.array, le vecteur à normaliser.
    
    Retour :
        list, le vecteur normalisé.
    """
    vecteur = np.array(v, dtype=float)
    
    norme = np.sqrt(np.sum(vecteur**2))
    if norme == 0:
        return vecteur.tolist()
    res = vecteur / norme
    return res.tolist()

def test_normaliser_L2():
    print("\n Test : normaliser_L2 ")
    
    # Cas 1 : Vecteur Pythagore (3, 4) -> Norme 5
    # Résultat attendu : (3/5, 4/5) = (0.6, 0.8)
    v1 = [3, 4]
    res1 = normaliser_L2(v1)
    
    print(f"  Vecteur : {v1}")
    print(f"  Normalisé L2 : {res1}")
    
    assert res1 == [0.6, 0.8]
    
    # Vérification : la somme des carrés doit faire 1
    somme_carres = res1[0]**2 + res1[1]**2
    assert np.isclose(somme_carres, 1.0)
    
    # Cas 2 : Vecteur nul
    v2 = [0, 0]
    res2 = normaliser_L2(v2)
    assert res2 == [0.0, 0.0]
    
    # Cas 3 : Vecteur TF-IDF typique
    v3 = [1, 1, 1, 1] # Norme = sqrt(4) = 2
    res3 = normaliser_L2(v3)
    # Attendu : [0.5, 0.5, 0.5, 0.5]
    assert res3 == [0.5, 0.5, 0.5, 0.5]
    
    print(" Test 'normaliser_L2' validé.")

#test_normaliser_L2()

#c Normalisation Min–Max (mise à l’échelle entre 0 et 1) 

def normaliser_minmax(v):
    """
    Description :
        Normalise un vecteur pour que ses valeurs soient comprises entre 0 et 1.
    
    Paramètres :
        v  list ou numpy.array, le vecteur à normaliser.
    
    Retour :
        list, le vecteur mis à l'échelle.
    """
    if not len(v):
        return []

    vecteur = np.array(v, dtype=float)
    
    vMin = np.min(vecteur)
    vMax = np.max(vecteur)

    diff = vMax - vMin
    if diff == 0:
        return np.zeros(len(vecteur), dtype=float).tolist()
        
    res = (vecteur - vMin) / diff
    return res.tolist()

def test_normaliser_minmax():
    
    # Cas 1 : Vecteur standard
    # Min=1, Max=5 -> Diff=4
    v1 = [1, 3, 5]
    res1 = normaliser_minmax(v1)
    
    print(f"  Vecteur : {v1}")
    print(f"  Normalisé MinMax : {res1}")
    
    assert res1 == [0.0, 0.5, 1.0]
    
    # Cas 2 : Vecteur constant (Min = Max)
    # Division par zéro évitée -> tout à 0
    v2 = [2, 2, 2]
    res2 = normaliser_minmax(v2)
    assert res2 == [0.0, 0.0, 0.0]
    
    # Cas 3 : Vecteur négatif
    # Min=-10, Max=10 -> Diff=20
    v3 = [-10, 0, 10]
    res3 = normaliser_minmax(v3)
    assert res3 == [0.0, 0.5, 1.0]
    
    print(" Test 'normaliser_minmax' validé.")

#test_normaliser_minmax()
#d Standardisation (z-score) 

def standardiser_zscore(v):
    """
    Description :
        Standardise un vecteur.
        Chaque valeur est centrée et réduite.
        Formule : (v - moyenne) / ecartType
    
    Paramètres :
        v  list ou numpy.array, le vecteur à standardiser.
    
    Retour :
        list, le vecteur standardisé.
    """
    if not len(v):
        return []

    vecteur = np.array(v, dtype=float)
    
    moyenne = np.mean(vecteur)
    ecartType = np.std(vecteur)
    
    if ecartType == 0:
        return np.zeros(len(vecteur), dtype=float).tolist()
        
    res = (vecteur - moyenne) / ecartType
    return res.tolist()

def test_standardiser_zscore():
    
    # Cas 1 : Vecteur simple
    v1 = [1, 3, 5]
    res1 = standardiser_zscore(v1)
    
    print(f"  Vecteur : {v1}")
    print(f"  Standardisé : {res1}")
    
    assert np.isclose(np.mean(res1), 0.0)
    assert np.isclose(np.std(res1), 1.0)
    
    # Cas 2 : Vecteur constant (Ecart-type = 0)
    v2 = [2, 2, 2]
    res2 = standardiser_zscore(v2)
    assert res2 == [0.0, 0.0, 0.0]
    
    # Cas 3 : Vecteur symétrique
    # [-1, 1] -> Moyenne 0, Ecart-type 1
    v3 = [-1, 1]
    res3 = standardiser_zscore(v3)
    assert res3 == [-1.0, 1.0]
    
    print(" Test 'standardiser_zscore' validé.")
#test_standardiser_zscore()

#4 Représentations basées sur les n-grammes 
#a Construction des dictionnaires d’indexation pour les ngrammes 

def construire_dictionnaire_ngrammes(vocabulaire_ngrammes):
    """
    Description :
        Construit les dictionnaires d'indexation pour les n-grammes.
        Associe chaque n-gramme à un identifiant unique.
    
    Paramètres :
        vocabulaire_ngrammes  list, la liste des n-grammes uniques.
                                Ex: [('le', 'chat'), ('chat', 'dort')]
    
    Retour :
        tuple (dict, dict), le couple .
    """
    if not vocabulaire_ngrammes:
        return {}, {}
    
    ngramme2idx = {}
    idx2ngramme = {} 
    for index, ngramme in enumerate(vocabulaire_ngrammes):
        ngramme2idx[ngramme] = index
        idx2ngramme[index] = ngramme
        
    return ngramme2idx, idx2ngramme

def test_construire_dictionnaire_ngrammes():
    
    # Vocabulaire n-grammes (tuples)
    vocab_ng_test = [("le", "chat"), ("chat", "dort"), ("il", "mange")]
    
    # Action
    n2i, i2n = construire_dictionnaire_ngrammes(vocab_ng_test)
    
    print(f"  Vocabulaire : {vocab_ng_test}")
    print(f"  Direct : {n2i}")
    
    # Vérifications Direct (Tuple -> Int)
    assert n2i[("le", "chat")] == 0
    assert n2i[("il", "mange")] == 2
    
    # Vérifications Inverse (Int -> Tuple)
    assert i2n[0] == ("le", "chat")
    assert i2n[2] == ("il", "mange")
    
    # Cas limite : Vide
    n2i_vide, i2n_vide = construire_dictionnaire_ngrammes([])
    assert n2i_vide == {}
    
    print(" Test 'construire_dictionnaire_ngrammes' validé.")

#test_construire_dictionnaire_ngrammes()

#b Encodage vectoriel des n-grammes  

def _generer_ngrammes_local(texte, n):
    """Génère une liste de tuples n-grammes à partir d'un texte."""
    if not texte:
        return []
    tokens = texte.split() if isinstance(texte, str) else texte
    
    if len(tokens) < n:
        return []
        
    return [tuple(tokens[i : i+n]) for i in range(len(tokens) - n + 1)]


def encoder_bow_ngrammes(texte, n, vocab_ng, dico_direct_ng, type='binaire'):
    """
    Description :
        Encode un texte en vecteur Bag-of-N-grams.
    
    Paramètres :
        texte           str ou list, le texte à encoder.
        n               int, taille des n-grammes.
        vocab_ng        list, liste des n-grammes du vocabulaire.
        dico_direct_ng  dict, mapping {ngramme_tuple : index}.
        type            str, 'binaire' ou 'occurrences'.
    
    Retour :
        numpy.array, vecteur d'entiers.
    """
    taille = len(dico_direct_ng)
    vecteur = np.zeros(taille, dtype=int)
    
    ngrammes = _generer_ngrammes_local(texte, n)
    
    for ng in ngrammes:
        if ng in dico_direct_ng:
            index = dico_direct_ng[ng]
            
            if type == 'binaire':
                vecteur[index] = 1
            else:
                vecteur[index] += 1
                
    return vecteur

def encoder_tf_ngrammes(texte, n, vocab_ng, dico_direct_ng):
    """
    Description :
        Encode un texte en vecteur TF basé sur les n-grammes.
        TF = nb_occurrences_ngramme / nbTotalNgrammes_dans_texte.
    
    Paramètres :
        texte           str ou list, le texte à encoder.
        n               int, taille des n-grammes.
        vocab_ng        list, liste des n-grammes.
        dico_direct_ng  dict, mapping {ngramme_tuple : index}.
    
    Retour :
        numpy.array, vecteur de floats.
    """
    taille = len(dico_direct_ng)
    vecteur = np.zeros(taille, dtype=float)
    ngrammes = _generer_ngrammes_local(texte, n)
    nbTotalNgrammes = len(ngrammes)
    if nbTotalNgrammes == 0:
        return vecteur
    for ng in ngrammes:
        if ng in dico_direct_ng:
            index = dico_direct_ng[ng]
            vecteur[index] += 1
    return vecteur / nbTotalNgrammes


def encoder_tfidf_ngrammes(texte, n, vocab_ng, dico_direct_ng, idf_ng):
    """
    Description :
        Encode un texte en vecteur TF-IDF basé sur les n-grammes.
        TF-IDF = TF(ngramme) * IDF(ngramme).
    
    Paramètres :
        texte           str ou list, le texte à encoder.
        n               int, taille des n-grammes.
        vocab_ng        list, liste des n-grammes.
        dico_direct_ng  dict, mapping {ngramme_tuple : index}.
        idf_ng          numpy.array, le vecteur IDF pré-calculé pour les n-grammes.
    
    Retour :
        numpy.array, vecteur de floats.
    """
    vecteurTf = encoder_tf_ngrammes(texte, n, vocab_ng, dico_direct_ng)
    if idf_ng is not None and len(idf_ng) == len(vecteurTf):
        return vecteurTf * idf_ng
    return vecteurTf


def test_encodage_ngrammes():
    print("\n Test : Encodage Vectoriel N-grammes ")
    
    vocab_ng = [("le", "chat"), ("chat", "dort"), ("le", "chien")]
    dico_ng = {("le", "chat"): 0, ("chat", "dort"): 1, ("le", "chien"): 2}
    idf_ng = np.array([1.0, 1.0, 2.0])
    
    texte = "le chat dort"
    
    #  1. Test BoW Binaire 
    # Attendu : [1, 1, 0]
    res_bow = encoder_bow_ngrammes(texte, 2, vocab_ng, dico_ng, type='binaire')
    print(f"BoW Binaire : {res_bow}")
    assert np.array_equal(res_bow, [1, 1, 0])
    
    #  2. Test BoW Occurrences 
    texte_rep = "le chat dort le chat"
    res_occ = encoder_bow_ngrammes(texte_rep, 2, vocab_ng, dico_ng, type='occurrences')
    print(f"BoW Occurrences ('{texte_rep}') : {res_occ}")
    assert res_occ[0] == 2
    assert res_occ[1] == 1
    
    #  3. Test TF 
    res_tf = encoder_tf_ngrammes(texte, 2, vocab_ng, dico_ng)
    print(f"TF : {res_tf}")
    assert res_tf[0] == 0.5
    assert res_tf[1] == 0.5
    assert res_tf[2] == 0.0
    
    # 4. Test TF-IDF 
    res_tfidf = encoder_tfidf_ngrammes(texte, 2, vocab_ng, dico_ng, idf_ng)
    print(f"TF-IDF : {res_tfidf}")
    assert res_tfidf[0] == 0.5
    
    print(" Test 'encodage_ngrammes' validé.")

#test_encodage_ngrammes()


#c Combinaison des n-grammes

def concatener_vocab_ngrammes(liste_vocab_ng):
    """
    Description :
        Combine plusieurs vocabulaires de n-grammes en une seule structure unifiée 
        avec ses dictionnaires d'indexation.
    
    Paramètres :
        liste_vocab_ng -- list de listes, ex: [vocab_uni, vocab_bi].
                          Chaque vocabulaire est une liste de tuples ou de chaînes.
    
    Retour :
        tuple (vFinal, dicoDirectFinal, dicoInverseFinal).
    """
    if not liste_vocab_ng:
        return [], {}, {}
    
    voc = set()
    
    for vocab in liste_vocab_ng:
        for element in vocab:
            if isinstance(element, str):
                element = (element,)
            voc.add(element)
            
    vFinal = sorted(list(voc))
    dicoDirectFinal = {}
    dicoInverseFinal = {}
    
    for index, ngramme in enumerate(vFinal):
        dicoDirectFinal[ngramme] = index
        dicoInverseFinal[index] = ngramme
    return vFinal, dicoDirectFinal, dicoInverseFinal

def test_concatener_vocab_ngrammes():
    print("\n Test : concatener_vocab_ngrammes ")
    
    # Vocab Unigrammes (chaînes ou tuples, ma fonction gère les deux)
    vocab_uni = ["le", "chat", "dort"]
    
    # Vocab Bigrammes (tuples)
    vocab_bi = [("le", "chat"), ("chat", "dort")]
    
    # Action
    vocab_final, d_direct, d_inverse = concatener_vocab_ngrammes([vocab_uni, vocab_bi])
    
    print(f"  Vocab final : {vocab_final}")
    
    # Vérifications
    
    # 1. Taille : 3 unigrammes + 2 bigrammes = 5
    assert len(vocab_final) == 5
    
    # 2. Présence des éléments (normalisés en tuples)
    assert ("chat",) in vocab_final
    assert ("le", "chat") in vocab_final
    
    # 3. Dictionnaires
    idx_chat = d_direct[("chat",)]
    assert d_inverse[idx_chat] == ("chat",)
    
    # 4. Tri (optionnel mais attendu)
    # "chat" (c) vient avant "le" (l)
    # ("chat",) vient avant ("chat", "dort") car plus court ? Non, tuple comparaison.
    # Python trie tuples élément par élément.
    
    print(" Test 'concatener_vocab_ngrammes' validé.")

#test_concatener_vocab_ngrammes()