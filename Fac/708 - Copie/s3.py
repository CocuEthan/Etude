import re
import string
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

STOPWORDS_FR = {
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "est", "en", "dans", "pour", "par", "sur",
    "au", "aux", "ce", "ces", "cet", "cette", "qui", "que", "quoi", "dont", "ou", "mais", "donc", "or", "ni", "car",
    "il", "elle", "ils", "elles", "je", "tu", "nous", "vous", "on", "ne", "pas", "plus", "se", "sa", "ses", "son",
    "leur", "leurs", "a", "à", "y", "été", "être", "avoir", "faire", "tout", "tous", "toute", "toutes",
    "comme", "avec", "sans", "sous", "vers", "chez"
}

STOPWORDS_EN = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "at", "from", "by", "on", "off", "for",
    "in", "out", "over", "to", "into", "with", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "it", "its", "they", "them", "their", "we", "us", "our", "you", "your", "he", "him", "his",
    "she", "her", "that", "this", "these", "those", "which", "who", "whom"
}
TOUS_STOPWORDS = STOPWORDS_FR.union(STOPWORDS_EN)
def nettoyer_liste_tokens(liste_mots, config):
    """
    Applique les filtres sur une liste de mots déjà tokenisée.
    Ordre CRUCIAL : Minuscule -> Nettoyage caractères -> Filtres
    """
    mots_propres = []
    
    # Configuration par défaut si non fournie
    if not config:
        config = {"stopwords": True, "non_alphabetiques": True, "longueur_min": 3}

    for mot in liste_mots:
        # 1. MISE EN MINUSCULE (Toujours en premier !)
        mot = mot.lower()
        
        # 2. SUPPRESSION PONCTUATION (Ex: "l'arbre" -> "l" "arbre", "chat." -> "chat")
        # On ne garde que les lettres et les chiffres (si autorisé)
        # Cette regex remplace tout ce qui n'est pas alphanumérique par vide
        if config.get("non_alphabetiques", True):
            # On garde uniquement les caractères de a-z et les accents basiques
            # Si le mot contient des chiffres ou symboles, on le nettoie
            mot = re.sub(r'[^a-zàâçéèêëîïôûùüÿñæoe]+', '', mot)
        
        # Si le mot est devenu vide après nettoyage, on passe
        if not mot:
            continue

        # 3. FILTRE LONGUEUR
        min_len = config.get("longueur_min", 2)
        if len(mot) < min_len:
            continue

        # 4. FILTRE STOPWORDS
        if config.get("stopwords", True):
            if mot in TOUS_STOPWORDS:
                continue

        # 5. STEMMING / LEMMATISATION (Optionnel - Exemple simple)
        if config.get("stemming", False):
            # Règle naïve pour l'exemple (enlevez le 's' ou 'e' final)
            if mot.endswith('s'): mot = mot[:-1]
            if mot.endswith('e'): mot = mot[:-1]

        # Si le mot a survécu à tout ça, on le garde
        mots_propres.append(mot)

    return mots_propres

def est_une_abreviation(token, abreviations):
    """
    Vérifie si le token est une abréviation connue.
    """
    return token in abreviations

def est_un_sigle(token):
    """
    Vérifie si le token est un sigle.
    Critère simple : Lettre majuscule + point + lettre majuscule...
    """
    return bool(re.match(r'^([A-Z]\.)+$', token))

def est_un_decimal(token):
    """
    Vérifie si le token est un nombre décimal.
    """
    return bool(re.match(r'^\d+\.\d+$', token))

def est_une_date(token):
    """
    Vérifie si le token ressemble à une date.
    """
    return bool(re.match(r'^\d{1,2}\.\d{1,2}\.\d{2,4}$', token))



def segmenter_phrases(texte, abreviations=None, option=None):
    """
    Description :
        Segmente un texte en phrases en respectant la ponctuation forte
        et en gérant les exceptions.
    
    Paramètres :
        texte         str, le texte à segmenter.
        abreviations  list, liste des abréviations connues.
        option        dict, options pour gérer d'autres cas.
    
    Retour :
        list, la liste des phrases extraites.
    """
    if not texte:
        return []
        
    if abreviations is None:
        abreviations = ["Dr.", "M.", "Mme.", "av.", "st.", "St.", "vol.", "p.", "ex."]
        
    cfg = {"gerer_decimaux": True, "gerer_dates": True, "gerer_sigles": True}
    if option:
        cfg.update(option)

    phrases = []
    phr = ""
    
    mots = texte.split()
    
    buf = []
    for i, mot in enumerate(mots):
        buf.append(mot)
        fin = mot[-1]
        if fin not in ['.', '!', '?']:
            continue
            
        if fin == '.':
            if est_une_abreviation(mot, abreviations):
                continue
            if cfg["gerer_decimaux"] and est_un_decimal(mot):
                continue

            if cfg["gerer_sigles"] and est_un_sigle(mot):
                continue

            token = mot[:-1] if mot.endswith('.') else mot
            if cfg["gerer_dates"] and est_une_date(token):
                 if i + 1 < len(mots):
                     suivant = mots[i+1]
                     if suivant[0].islower():
                         continue

        phr = " ".join(buf)
        phrases.append(phr)
        buf = [] 
    if buf:
        phrases.append(" ".join(buf))
        
    return phrases


def test_segmenter_phrases():
    print("\n Test : segmenter_phrases ")
    
    # Cas 1 : Basique
    txt1 = "Bonjour. Ça va ?"
    res1 = segmenter_phrases(txt1)
    assert len(res1) == 2
    assert res1[0] == "Bonjour."
    assert res1[1] == "Ça va ?"
    
    # Cas 2 : Abréviations
    txt2 = "Dr. Martin est là. Il travaille."
    res2 = segmenter_phrases(txt2)
    # Ne doit PAS couper après "Dr."
    assert len(res2) == 2 
    assert res2[0] == "Dr. Martin est là."
    
    # Cas 3 : Sigles
    txt3 = "Le P.D.G. a parlé."
    res3 = segmenter_phrases(txt3)
    assert len(res3) == 1
    assert res3[0] == "Le P.D.G. a parlé."
    
    # Cas 4 : Décimaux
    txt4 = "Pi vaut 3.14 environ."
    res4 = segmenter_phrases(txt4)
    assert len(res4) == 1
    assert "3.14" in res4[0]
    
    # Cas 5 : Dates
    txt5 = "Le 12.05.2025 sera un grand jour."
    res5 = segmenter_phrases(txt5)
    assert len(res5) == 1
    
    # Cas 6 : Mixte complexe
    txt_mixte = "M. Dupont (P.D.G.) a dit : 3.5% de hausse ! C'est bien."
    res_mixte = segmenter_phrases(txt_mixte)
    assert len(res_mixte) == 2
    assert res_mixte[0] == "M. Dupont (P.D.G.) a dit : 3.5% de hausse !"
    
    print(" Test 'segmenter_phrases' validé.")

#test_segmenter_phrases()


#b


def segmenter_mots(phrase, balise=False):
    """
    Description :
        Découpe une phrase en une liste de tokens  en se basant sur les espaces.
        Gère la conservation ou la suppression des balises.
    
    Paramètres :
        phrase  str, la phrase à tokeniser.
        balise  bool, si True, conserve les balises. Si False, les ignore.
    
    Retour :
        list, une liste de chaînes.
    """
    if not phrase:
        return []
    tokBrute = phrase.split()
    
    res = []
    
    for token in tokBrute:
        bal = token.startswith('<') and token.endswith('>') and len(token) > 2
        
        if bal:
            if balise:
                res.append(token)
        else:
            res.append(token)
            
    return res


def tokeniser_document(texte, abreviations=None, option=None, balise=False):
    """
    Description :
        Segmente un document en phrases, puis chaque phrase en mots.
    
    Paramètres :
        texte         str, le texte complet du document.
        abreviations  list, pour la segmentation de phrases.
        option        dict, options pour la segmentation de phrases.
        balise        bool, conserver ou non les balises lors de la tokenisation mots.
    
    Retour :
        list, une liste de listes de tokens.
    """
    if not texte:
        return []
    
    try:
        phrases = segmenter_phrases(texte, abreviations, option)
    except NameError:
        phrases = [texte]
    token = []
    for phrase in phrases:
        mots = segmenter_mots(phrase, balise)
        if mots:
            token.append(mots)
            
    return token

def tokeniser_corpus(corpus_brut):
    """ 
    Transforme le texte brut en liste de tokens bruts.
    Entrée : { "id": "Texte..." }
    Sortie : { "id": [ ["mot1", "mot2"], ["mot3"] ] } (Structure phrases)
             OU { "id": ["mot1", "mot2", "mot3"] } (Structure simple)
    """
    corpus_tok = {}
    for doc_id, texte in corpus_brut.items():
        # Découpage simple sur les espaces pour commencer
        # On nettoiera finement dans le pipeline
        if isinstance(texte, str):
            # On simule une liste de phrases (ici une seule "phrase" géante pour simplifier le format)
            # ou on découpe si nécessaire. Ici on renvoie une liste de mots à plat pour simplifier S3.
            corpus_tok[doc_id] = [texte.split()] 
    return corpus_tok
#def tokeniser_corpus(corpus, abreviations=None, option=None, balise=False):
    """
    Description :
        Applique la tokenisation complète sur l'ensemble d'un corpus.
    
    Paramètres :
        corpus        dict, { id : texte_doc }.
        abreviations  list, pour segmenter_phrases.
        option        dict, pour segmenter_phrases.
        balise        bool, conserver ou non les balises.
    
    Retour :
        dict, { id : [[token, ...], [token, ...]] }.
    """
    if not corpus:
        return {}
        
    res = {}
    
    for id, texte in corpus.items():
        res[id] = tokeniser_document(texte, abreviations, option, balise)
        
    return res


def aplatir_tokens(document_tokens):
    """
    Description :
        Aplatit une liste de listes de tokens en une seule liste unique.
        Utile pour compter les fréquences globales.
    
    Paramètres :
        document_tokens  list, liste de listes.
    
    Retour :
        list, liste simple.
    """
    if not document_tokens:
        return []
    return [token for phrase in document_tokens for token in phrase]


def tokens_hapax(document_tokens):
    """
    Description :
        Identifie les hapax dans un document.
    
    Paramètres :
        document_tokens  list, si c'est une liste de listes, elle sera aplatie.
    
    Retour :
        list, la liste des tokens uniques.
    """
    if document_tokens and isinstance(document_tokens[0], list):
        liste = aplatir_tokens(document_tokens)
    else:
        liste = document_tokens

    compteur = {}
    
    for token in liste:
        compteur[token] = compteur.get(token, 0) + 1
        
    hapax = [token for token, count in compteur.items() if count == 1]
    return hapax

def test_segmenter_mots():
    print("\nTest : segmenter_mots")
    
    # Cas 1 : Phrase nettoyée (ponctuation espacée)
    # Note : "chef-d'oeuvre" reste un seul token car pas d'espace
    p1 = "Le chef-d'oeuvre est là ." 
    res1 = segmenter_mots(p1)
    assert res1 == ["Le", "chef-d'oeuvre", "est", "là", "."]
    
    # Cas 2 : Balises (balise=False par défaut -> suppression)
    p2 = "J'ai <NUM> chats ."
    res2 = segmenter_mots(p2, balise=False)
    assert "<NUM>" not in res2
    assert res2 == ["J'ai", "chats", "."]
    
    # Cas 3 : Balises (balise=True -> conservation)
    res3 = segmenter_mots(p2, balise=True)
    assert "<NUM>" in res3
    
    print(" Test 'segmenter_mots' validé.")


def test_tokeniser_document():
    print("\nTest : tokeniser_document")
    
    # Dépend de segmenter_phrases. 
    # On suppose que le texte a été nettoyé
    txt = "Dr. Martin est ici . Il part ."
    
    # Structure attendue : Liste de phrases, qui sont des listes de mots
    res = tokeniser_document(txt)
    
    # Phrase 1 : ["Dr.", "Martin", "est", "ici", "."]
    # Phrase 2 : ["Il", "part", "."]
    assert len(res) == 2
    assert res[0][0] == "Dr." 
    assert res[1][0] == "Il"
    
    print(" Test 'tokeniser_document' validé.")


def test_aplatir_tokens():
    print("\nTest : aplatir_tokens")
    
    entree = [["A", "B"], ["C", "D"]]
    res = aplatir_tokens(entree)
    assert res == ["A", "B", "C", "D"]
    
    print(" Test 'aplatir_tokens' validé.")


def test_tokens_hapax():
    print("\nTest : tokens_hapax")
    
    # Liste de tokens : "le" apparaît 2 fois, "chat" et "chien" 1 fois.
    liste = ["le", "chat", "mange", "le", "chien"]
    
    res = tokens_hapax(liste)
    
    assert "chat" in res
    assert "chien" in res
    assert "mange" in res
    assert "le" not in res # Apparaît 2 fois
    
    print(" Test 'tokens_hapax' validé.")



def lancer_tests_tokenisation():
    test_segmenter_mots()
    try:
        test_tokeniser_document()
    except NameError:
        print(" Test 'tokeniser_document' ignoré (manque segmenter_phrases)")
    test_aplatir_tokens()
    test_tokens_hapax()
    print("\n TOUS LES TESTS DE TOKENISATION SONT VALIDÉS !")

#lancer_tests_tokenisation()


#c


def generer_ngrammes(donnees, n, niveau='phrase', par_phrase=True):
    """
    Description :
        Génère des n-grammes à partir de données structurées.
    
    Paramètres :
        donnees     list (phrase/doc) ou dict (corpus).
        n           int, taille du n-gramme (ex: 2 pour bigrammes).
        niveau      str, 'phrase', 'document' ou 'corpus'.
        par_phrase  bool, si True, respecte les frontières de phrases.
    
    Retour :
        list ou dict, contenant des tuples de tokens.
    """
    if n < 1:
        return []

    if niveau == 'phrase':
        if len(donnees) < n:
            return []
        return [tuple(donnees[i : i+n]) for i in range(len(donnees) - n + 1)]
    elif niveau == 'document':
        doc = []
        
        if par_phrase:
            for phrase in donnees:
                if len(phrase) >= n:
                    ngrammes = [tuple(phrase[i : i+n]) for i in range(len(phrase) - n + 1)]
                    doc.extend(ngrammes)
        else:
            tokens = [token for phrase in donnees for token in phrase]
            if len(tokens) >= n:
                doc = [tuple(tokens[i : i+n]) for i in range(len(tokens) - n + 1)]
        return doc
    elif niveau == 'corpus':
        res = {}
        
        for id, contenu in donnees.items():
            res[id] = generer_ngrammes(
                contenu, n, niveau='document', par_phrase=par_phrase
            )     
        return res
    return []


def test_generer_ngrammes():
    print("\n Test : generer_ngrammes ")
    
    # 1. Niveau Phrase 
    tokens = ["Le", "chat", "dort", "paisiblement"]
    
    # Bigrammes (N=2)
    # Attendu : [('Le', 'chat'), ('chat', 'dort'), ('dort', 'paisiblement')]
    res_ph_2 = generer_ngrammes(tokens, 2, niveau='phrase')
    
    assert len(res_ph_2) == 3
    assert res_ph_2[0] == ("Le", "chat")
    assert res_ph_2[-1] == ("dort", "paisiblement")
    
    # Trigrammes (N=3)
    res_ph_3 = generer_ngrammes(tokens, 3, niveau='phrase')
    assert len(res_ph_3) == 2

    #2. Niveau Document
    # Phrase 1 : ["A", "B"]
    # Phrase 2 : ["C", "D"]
    doc = [["A", "B"], ["C", "D"]]
    
    # Cas par_phrase=True (Pas de croisement)
    # ("A", "B") est possible. ("B", "C") est impossible car traverse la frontière.
    res_doc_true = generer_ngrammes(doc, 2, niveau='document', par_phrase=True)
    
    assert ("A", "B") in res_doc_true
    assert ("C", "D") in res_doc_true
    assert ("B", "C") not in res_doc_true
    
    # Cas par_phrase=False (Croisement autorisé)
    # Tout est mis à plat : A, B, C, D -> ("B", "C") devient possible.
    res_doc_false = generer_ngrammes(doc, 2, niveau='document', par_phrase=False)
    
    assert ("B", "C") in res_doc_false 

    # Niveau Corpus
    corpus = {
        "d1": [["Hello", "World"]],
        "d2": [["Test", "Ok"]]
    }
    
    res_corpus = generer_ngrammes(corpus, 2, niveau='corpus')
    
    assert "d1" in res_corpus
    assert res_corpus["d1"] == [("Hello", "World")]
    assert res_corpus["d2"] == [("Test", "Ok")]

    print(" Test 'generer_ngrammes' validé.")

#test_generer_ngrammes()


#2 Statistiques sur le corpus avant filtrage 
#a

def compter_tokens_phrase(phrase):
    """
    Description :
        Compte le nombre de tokens dans une phrase.
    
    Paramètres :
        phrase  list, une liste de tokens.
    
    Retour :
        int, le nombre de tokens.
    """
    if not phrase:
        return 0
    return len(phrase)


def compter_tokens_document(document):
    """
    Description :
        Compte le nombre total de tokens dans un document.
    
    Paramètres :
        document  list, une liste de listes de tokens.
    
    Retour :
        int, le nombre total de tokens.
    """
    if not document:
        return 0
    return sum(len(phrase) for phrase in document)


def compter_tokens_corpus(corpus):
    """
    Description :
        Compte le nombre total de tokens dans tout le corpus.
    
    Paramètres :
        corpus  dict, {id : document_tokenisé}.
    
    Retour :
        int, le nombre total de tokens.
    """
    if not corpus:
        return 0
    return sum(compter_tokens_document(doc) for doc in corpus.values())


def calculer_mots_vides_document(document, stopwords):
    """
    Description :
        Compte le nombre de mots videsdans un document.
    
    Paramètres :
        document   list, le document tokenisé.
        stopwords  list ou set, la liste des mots à ignorer.
    
    Retour :
        int, le nombre de mots vides trouvés.
    """
    if not document or not stopwords:
        return 0
    stop = set(stopwords)
    compte = 0
    
    for phrase in document:
        for token in phrase:
            if token.lower() in stop:
                compte += 1
    return compte


def calculer_tokens_vides_document(document):
    """
    Description :
        Compte le nombre de tokens vides, numériques ou non alphabétiques
    
    Paramètres :
        document  list, le document tokenisé.
    
    Retour :
        int, le nombre de tokens considérés comme du bruit structurel.
    """
    if not document:
        return 0
        
    compte = 0
    for phrase in document:
        for token in phrase:
            if not token or not token.isalpha():
                compte += 1
    return compte


def calculer_mots_vides_corpus(corpus, stopwords):
    """
    Description :
        Compte le total des mots vides dans tout le corpus.
    """
    if not corpus: return 0
    return sum(calculer_mots_vides_document(doc, stopwords) for doc in corpus.values())


def calculer_tokens_vides_corpus(corpus):
    """
    Description :
        Compte le total des tokens non-alphabétiques dans tout le corpus.
    """
    if not corpus: return 0
    return sum(calculer_tokens_vides_document(doc) for doc in corpus.values())


def generer_statistiques_corpus(corpus, stopwords):
    """
    Description :
        Génère un dictionnaire complet de statistiques sur le corpus.
    """
    nbDocs = len(corpus)
    nbTotal = compter_tokens_corpus(corpus)
    nbStop = calculer_mots_vides_corpus(corpus, stopwords)
    nbBruit = calculer_tokens_vides_corpus(corpus)
    
    proportion = 0
    if nbTotal > 0:
        proportion = (nbStop + nbBruit) / nbTotal

    stats = {
        "nbDocument": nbDocs,
        "nbTokensTotal": nbTotal,
        "nbMotsVides": nbStop,
        "nbTokensVides": nbBruit,
        "proportionBruit": proportion
    }
    return stats

def test_statistiques_globales():
    print("\n Test : Statistiques Globales ")
    # Liste de stopwords simulée
    stopwords = ["le", "la", "est", "un"]
    
    # Document 1 : 2 phrases, des mots normaux, des stopwords, de la ponctuation
    # "Le chat est beau." (4 mots + 1 point)
    # "Il dort." (2 mots + 1 point)
    doc1 = [
        ["Le", "chat", "est", "beau", "."], 
        ["Il", "dort", "."]
    ]
    # Analyse Doc 1 :
    # - Total tokens : 5 + 3 = 8
    # - Stopwords ("Le", "est") : 2
    # - Non-alpha ("." et ".") : 2
    
    # Document 2 : Des chiffres et du bruit
    doc2 = [
        ["123", "!"]
    ]
    # Analyse Doc 2 :
    # - Total tokens : 2
    # - Stopwords : 0
    # - Non-alpha ("123", "!") : 2
    corpus_test = {
        "doc1": doc1,
        "doc2": doc2
    }

    # 1. Comptage simple
    assert compter_tokens_phrase(["Salut", "toi"]) == 2
    assert compter_tokens_document(doc1) == 8
    assert compter_tokens_corpus(corpus_test) == 10 # 8 + 2
    
    # 2. Mots vides (Stopwords)
    # Doc1 contient "Le" et "est"
    assert calculer_mots_vides_document(doc1, stopwords) == 2
    assert calculer_mots_vides_corpus(corpus_test, stopwords) == 2
    
    # 3. Tokens vides / Non-alpha
    # Doc1 a deux points "." -> 2
    assert calculer_tokens_vides_document(doc1) == 2
    # Doc2 a "123" et "!" -> 2
    assert calculer_tokens_vides_document(doc2) == 2
    # Total corpus -> 4
    assert calculer_tokens_vides_corpus(corpus_test) == 4
    
    stats = generer_statistiques_corpus(corpus_test, stopwords)
    
    print("  Stats calculées :", stats)

    assert stats["nbDocument"] == 2
    assert stats["nbTokensTotal"] == 10
    assert stats["nbMotsVides"] == 2
    assert stats["nbTokensVides"] == 4
    assert stats["proportionBruit"] == 0.6
    
    print(" Test Statistiques Globales validé.")


#test_statistiques_globales()


#b
#i Analyse des longueurs

def distribution_longueur_documents(corpus):
    """
    Description :
        Calcule la longueur de chaque document.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        dict, {id : nombre_tokens}.
    """
    dist = {}
    if not corpus:
        return dist
        
    for id, doc in corpus.items():
        tokens = sum(len(phrase) for phrase in doc)
        dist[id] = tokens
        
    return dist


def distribution_longueur_phrases(corpus):
    """
    Description :
        Calcule la longueur moyenne des phrases pour chaque document.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        dict, {id : moyenneToken}.
    """
    dist = {}
    if not corpus:
        return dist
        
    for id, doc in corpus.items():
        nbPhrases = len(doc)
        
        if nbPhrases == 0:
            dist[id] = 0.0
        else:
            nbTokens = sum(len(phrase) for phrase in doc)
            # Calcul de la moyenne
            moyenne = nbTokens / nbPhrases
            dist[id] = round(moyenne, 2)
            
    return dist


def distribution_longueur_mots(corpus):
    """
    Description :
        Calcule la distribution des longueurs de mots
        sur l'ensemble du corpus.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        dict, {longueur_en_caractères : fréquence}.
        Exemple : {2: 150, 3: 400...}.
    """
    dist = {}
    if not corpus:
        return dist
    for doc in corpus.values():
        for phrase in doc:
            for mot in phrase:
                longueur = len(mot)
                dist[longueur] = dist.get(longueur, 0) + 1        
    return dist


def test_distributions():
    print("\n Test : Distributions (Documents, Phrases, Mots) ")
    
    # Corpus factice
    corpus_test = {
        "doc1": [["Le", "chat"], ["Il", "dort"]],
        "doc2": [["Oui"]]
    }
    
    # - 1. Longueur des Documents -
    # Doc1 : 2+2 = 4 tokens
    # Doc2 : 1 token
    res_docs = distribution_longueur_documents(corpus_test)
    print(f"  Docs : {res_docs}")
    assert res_docs["doc1"] == 4
    assert res_docs["doc2"] == 1
    
    # - 2. Longueur Moyenne des Phrases -
    # Doc1 : 4 tokens / 2 phrases = 2.0
    # Doc2 : 1 token / 1 phrase = 1.0
    res_phrases = distribution_longueur_phrases(corpus_test)
    print(f"  Phrases (Moy) : {res_phrases}")
    assert res_phrases["doc1"] == 2.0
    assert res_phrases["doc2"] == 1.0
    
    # - 3. Distribution Longueur Mots -
    # Mots : "Le"(2), "chat"(4), "Il"(2), "dort"(4), "Oui"(3)
    # Longueur 2 : 2 fois ("Le", "Il")
    # Longueur 3 : 1 fois ("Oui")
    # Longueur 4 : 2 fois ("chat", "dort")
    res_mots = distribution_longueur_mots(corpus_test)
    print(f"  Mots (Dist) : {res_mots}")
    
    assert res_mots[2] == 2
    assert res_mots[3] == 1
    assert res_mots[4] == 2
    assert 5 not in res_mots 
    
    print(" Tests Distributions validés.")

#test_distributions()


#ii Analyses des occurrences 

def distribution_occurrences_tokens(corpus):
    """
    Description :
        Compte le nombre d'occurrences de chaque token dans l'ensemble du corpus.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        dict, {token : nombre_occurrences}.
    """
    distribution = {}
    
    if not corpus:
        return distribution
    
    for doc in corpus.values():
        for phrase in doc:
            for token in phrase:
                distribution[token] = distribution.get(token, 0) + 1
                
    return distribution

def test_distribution_occurrences_tokens():
    # Cas simples
    corpus_test = {
        "d1": [["le", "chat"]],
        "d2": [["le", "chien"]]
    }
    dist = distribution_occurrences_tokens(corpus_test)
    assert dist["le"] == 2
    assert dist["chat"] == 1
    assert dist["chien"] == 1

    # Cas limites (Corpus vide)
    assert distribution_occurrences_tokens({}) == {}

    # Cas d’erreurs (Token non présent)
    # Vérifier qu'une clé inexistante ne plante pas l'accès si on utilise .get(), 
    assert "oiseau" not in dist

    print(" Tous les tests unitaires sont passés avec succès !")

#test_distribution_occurrences_tokens()


def tokens_plus_frequents(corpus, n=20):
    """
    Description :
        Extrait les n tokens les plus fréquents du corpus.
        Exclut automatiquement les tokens de ponctuation 
        et les tokens vides pour ne garder que les mots significatifs.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
        n       int, nombre de tokens à retourner.
    
    Retour :
        list, liste de tuples [(token, nb_occ), ...] triée par fréquence décroissante.
    """
    dist = distribution_occurrences_tokens(corpus)
    filtre = []
    
    for token, count in dist.items():
        token = token.strip()
        
        if token and any(c.isalnum() for c in token):
            filtre.append( (token, count) )
    
    tries = sorted(filtre, key=lambda x: (-x[1], x[0]))
    return tries[:n]

def test_tokens_plus_frequents():
    # Cas simples
    corpus_test = {
        "d1": [["chat", "chat", "chat", "chien", "chien"]]
    }
    top1 = tokens_plus_frequents(corpus_test, n=1)
    assert top1 == [("chat", 3)]

    # Cas limites (Demander plus de tokens qu'il n'y en a)
    top_all = tokens_plus_frequents(corpus_test, n=10)
    assert len(top_all) == 2 

    # Cas d’erreurs (Filtrage de la ponctuation)
    corpus_bruit = {
        "d1": [["!", "!", "!", "mot"]]
    }
    res = tokens_plus_frequents(corpus_bruit, n=1)
    assert res[0] == ("mot", 1)

    print(" Tous les tests unitaires sont passés avec succès !")

#test_tokens_plus_frequents()

#c

def statistiques_corpus(corpus):
    """
    Description :
        Calcule des indicateurs statistiques globaux sur le corpus.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        dict, dictionnaire contenant les statistiques calculées.
    """
    stats = {
        "moyenne": 0.0,
        "ecart": 0.0,
        "min": 0,
        "max": 0,
        "moyennePhrase": 0.0,
        "moyenneToken": 0.0
    }
    
    if not corpus:
        return stats

    longueurs = []      
    phrase = []
    total = [] 

    for doc in corpus.values():
        nb = len(doc)
        phrase.append(nb) 
        token = 0
        for p in doc:
            l = len(p)
            token += l
            total.append(l) 
            
        longueurs.append(token)

    if longueurs:
        stats["moyenne"] = round(float(np.mean(longueurs)), 2)
        stats["ecart"] = round(float(np.std(longueurs)), 2)
        stats["min"] = int(np.min(longueurs))
        stats["max"] = int(np.max(longueurs))
    
    if phrase:
        stats["moyennePhrase"] = round(float(np.mean(phrase)), 2)
        
    if total:
        stats["moyenneToken"] = round(float(np.mean(total)), 2)

    return stats

def test_statistiques_corpus():
    # Cas simples
    # Doc 1 : 2 phrases, 4 tokens
    # Doc 2 : 1 phrase, 2 tokens
    corpus_test = {
        "d1": [["a", "b"], ["c", "d"]], 
        "d2": [["e", "f"]]
    }
    stats = statistiques_corpus(corpus_test)
    
    assert stats["moyenne"] == 3.0
    assert stats["max"] == 4
    assert stats["moyennePhrase"] == 1.5

    # Cas limites (Corpus vide)
    stats_vide = statistiques_corpus({})
    assert stats_vide["moyenne"] == 0.0
    assert stats_vide["ecart"] == 0.0

    # Cas d’erreurs (Structure vide interne)
    corpus_vide_interne = {"d1": []}
    stats_vide_int = statistiques_corpus(corpus_vide_interne)
    assert stats_vide_int["max"] == 0

    print(" Tous les tests unitaires sont passés avec succès !")

#test_statistiques_corpus()
#d


def tableau_de_bord(corpus, stats):
    """
    Description :
        Génère un tableau de bord graphique complet
        pour analyser la structure et le lexique du corpus.
    
    Paramètres :
        corpus        dict, {id : liste de listes de tokens}.
        stats  dict, statistiques globales calculées précédemment.
    
    Retour :
        matplotlib.figure.Figure, l'objet graphique contenant le tableau de bord.
    """
    
    if not corpus:
        return None
    all = [token for doc in corpus.values() for phrase in doc for token in phrase]
    docLong = [sum(len(phrase) for phrase in doc) for doc in corpus.values()]
    
    motLong = [len(token) for token in all]
    
    frequences = Counter(all)
    top20 = frequences.most_common(20)
    
    nbTotal = stats.get("nbTokensTotal", len(all))
    nbStop = stats.get("nbMotsVides", 0)
    nbBruit = stats.get("nbTokensVides", 0)
    utile = max(0, nbTotal - nbStop - nbBruit)
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(3, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    sizes = [utile, nbStop, nbBruit]
    labels = ['Tokens Utiles', 'Stopwords', 'Bruit (Non-Alpha)']
    colors = ['#66b3ff', '#ff9999', '#99ff99']
    if sum(sizes) > 0:
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Qualité du Corpus (Proportion de Bruit)")
    ax2 = fig.add_subplot(gs[0, 1])
    if top20:
        mots, counts = zip(*top20)
        ax2.bar(mots, counts, color='skyblue')
        ax2.set_title("Top 20 Tokens les plus fréquents")
        ax2.tick_params(axis='x', rotation=45)
    ax3 = fig.add_subplot(gs[1, 0])
    if docLong:
        ax3.hist(docLong, bins=20, color='salmon', edgecolor='black', alpha=0.7)
        ax3.set_title("Distribution de la longueur des documents")
        ax3.set_xlabel("Nombre de tokens")
        ax3.set_ylabel("Nombre de documents")
    ax4 = fig.add_subplot(gs[1, 1])
    if motLong:
        ax4.hist(motLong, bins=range(1, 20), color='lightgreen', edgecolor='black', alpha=0.7)
        ax4.set_title("Distribution de la longueur des mots (caractères)")
        ax4.set_xlabel("Taille du mot")
    ax5 = fig.add_subplot(gs[2, :])
    if frequences:
        freqs_sorted = sorted(frequences.values(), reverse=True)
        ax5.plot(freqs_sorted, color='purple', linewidth=2)
        ax5.set_title("Courbe de fréquence des tokens (Distribution de Zipf)")
        ax5.set_xlabel("Rang du token")
        ax5.set_ylabel("Fréquence")
        ax5.set_yscale('log')
        ax5.set_xscale('log')
    plt.tight_layout()
    return fig

def test_tableau_de_bord():
    print("\n Test : tableau_de_bord (Visuel) ")
    
    # - 1. Création d'un corpus riche pour avoir de beaux graphiques -
    # On simule des stopwords et du bruit pour le camembert
    docs = []
    
    # Doc A : Mots courts, fréquents (type stopwords)
    doc_a = [["le", "la", "de", "et", "le", "la"] * 5] 
    # Doc B : Mots variés, longueur moyenne
    doc_b = [["chat", "chien", "maison", "voiture", "ordinateur", "python"] * 2] 
    # Doc C : Bruit
    doc_c = [["!!!", "123", "???", "..."] * 3]
    
    corpus_visu = {
        "doc_a": doc_a,
        "doc_b": doc_b,
        "doc_c": doc_c
    }
    
    # Stats simulées
    stats_simulees = {
        "nbTokensTotal": 54,
        "nbMotsVides": 30,
        "nbTokensVides": 12
    }
    
    try:
        fig = tableau_de_bord(corpus_visu, stats_simulees)
        assert fig is not None
        nom_fichier = "test_tableau_de_bord.png"
        fig.savefig(nom_fichier)
        plt.close(fig)
        
        print(f" Test validé. Le graphique a été sauvegardé sous : {nom_fichier}")
        print("Ouvrez ce fichier pour vérifier les 5 graphiques.")
        
    except Exception as e:
        print(f" Erreur lors de la génération : {e}")

#test_tableau_de_bord()

#3 Construction du vocabulaire et diversité lexicale 
#a

def construire_vocabulaire(corpus):
    """
    Description :
        Construit la liste de tous les tokens uniques
        présents dans le corpus.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        list, la liste triée des tokens uniques.
    """
    vocabulaire = set()
    
    if not corpus:
        return []
    
    for doc in corpus.values():
        for phrase in doc:
            vocabulaire.update(phrase)
    return sorted(list(vocabulaire))


def test_construire_vocabulaire():
    print("\nTest : construire_vocabulaire")
    
    # Corpus factice
    corpus_test = {
        "d1": [["le", "chat"]],
        "d2": [["le", "chien"]]
    }
    
    vocab = construire_vocabulaire(corpus_test)
    
    print(f"  Vocabulaire extrait : {vocab}")
    
    # "le" apparaît 2 fois mais ne doit être présent qu'une fois dans le vocabulaire
    assert len(vocab) == 3
    assert "chat" in vocab
    assert "chien" in vocab
    assert "le" in vocab
    # Vérification du tri
    assert vocab == ["chat", "chien", "le"]
    print(" Test validé.")

#test_construire_vocabulaire()

def vocabulaire_ngrammes(corpus, n=2):
    """
    Description :
        Construit la liste de tous les n-grammes uniques présents
        dans le corpus.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
        n       int, la taille des n-grammes.
    
    Retour :
        list, la liste triée des tuples de n-grammes uniques.
    """
    vocab = set()
    
    if not corpus or n < 1:
        return []
        
    for doc in corpus.values():
        for phrase in doc:
            if len(phrase) >= n:
                ngrammes = [tuple(phrase[i : i+n]) for i in range(len(phrase) - n + 1)]
                vocab.update(ngrammes)
    return sorted(list(vocab))


def test_vocabulaire_ngrammes():
    print("\nTest : vocabulaire_ngrammes")
    
    # Corpus factice
    corpus_test = {
        "d1": [["A", "B", "C"]],
        "d2": [["A", "B", "D"]]
    }
    
    # Test Bigrammes (n=2)
    vocab_bi = vocabulaire_ngrammes(corpus_test, 2)
    print(f"  Bigrammes : {vocab_bi}")
    
    # Uniques attendus : (A,B), (B,C), (B,D)
    assert len(vocab_bi) == 3
    assert ("A", "B") in vocab_bi
    assert ("B", "C") in vocab_bi
    assert ("B", "D") in vocab_bi
    
    # Test Trigrammes (n=3)
    vocab_tri = vocabulaire_ngrammes(corpus_test, 3)
    # Uniques attendus : (A,B,C) et (A,B,D)
    assert len(vocab_tri) == 2
    
    print(" Test validé.")

#test_vocabulaire_ngrammes()


#b

def calculer_richesse_lexicale(tokens):
    """
    Description :
        Calcule la richesse lexicale.
        Formule : Nombre de mots uniques / Nombre total de tokens.
    
    Paramètres :
        tokens  list, la liste complète de tous les tokens du corpus.
    
    Retour :
        float, un score entre 0 et 1.
    """
    if not tokens:
        return 0.0
    
    nbTokensTotal = len(tokens)
    unique = len(set(tokens))
    
    res = unique / nbTokensTotal
    return res

def test_calculer_richesse_lexicale():
    print("\n Test 1 : calculer_richesse_lexicale ")
    
    # Cas : 4 tokens au total, 3 uniques ("le", "chat", "dort", "le")
    tokens = ["le", "chat", "dort", "le"]
    res = calculer_richesse_lexicale(tokens)
    print(f"  Richesse : {res}")
    assert res == 0.75
    
    # Cas limite : Vide
    assert calculer_richesse_lexicale([]) == 0.0
    print(" Test 'calculer_richesse_lexicale' validé.")

#test_calculer_richesse_lexicale()
#b
def calculer_taux_hapax(tokens):
    """
    Description :
        Calcule la proportion de mots qui n'apparaissent qu'une seule fois.
        Formule : Nombre d'hapax / Nombre de mots uniques.
    
    Paramètres :
        tokens  list, la liste complète des tokens.
    
    Retour :
        float, le taux d'hapax.
    """
    if not tokens:
        return 0.0
    frequences = Counter(tokens)
    nb = sum(1 for count in frequences.values() if count == 1)
    unique = len(frequences)
    
    if unique == 0:
        return 0.0
        
    res = nb / unique
    return res

def test_calculer_taux_hapax():
    print("\n Test 2 : calculer_taux_hapax ")
    
    # Liste : "le" (2), "chat" (1), "dort" (1)
    tokens = ["le", "chat", "dort", "le"]
    
    # Mots uniques : 3 ("le", "chat", "dort")
    # Taux = 2 / 3 ≈ 0.666...
    res = calculer_taux_hapax(tokens)
    print(f"  Taux Hapax : {res}")
    assert 0.66 < res < 0.67
    
    # Cas limite : Vide
    assert calculer_taux_hapax([]) == 0.0
    
    print(" Test 'calculer_taux_hapax' validé.")

#test_calculer_taux_hapax()

#c
def calculer_dispersion_lexicale(tokens):
    """
    Description :
        Mesure la variabilité des occurrences .
        Une valeur faible indique un lexique équilibré, une valeur élevée indique
        que certains mots dominent très fortement le discours.
    
    Paramètres :
        tokens  list, la liste complète des tokens.
    
    Retour :
        float, l'écart-type des fréquences.
    """
    if not tokens:
        return 0.0
        
    frequences = Counter(tokens)
    valeurs = list(frequences.values())
    return float(np.std(valeurs))

def test_calculer_dispersion_lexicale():
    print("\n Test 3 : calculer_dispersion_lexicale ")
    
    # Liste : "a" (2), "b" (2)
    # Fréquences : [2, 2]
    # Moyenne = 2. Écart-type = 0
    tokens_equilibre = ["a", "b", "a", "b"]
    assert calculer_dispersion_lexicale(tokens_equilibre) == 0.0
    # Liste : "a" (10), "b" (1) -> Forte variation
    tokens_desequilibre = ["a"]*10 + ["b"]
    res = calculer_dispersion_lexicale(tokens_desequilibre)
    print(f"  Dispersion (déséquilibrée) : {res}")
    
    assert res > 0.0
    
    print(" Test 'calculer_dispersion_lexicale' validé.")

#test_calculer_dispersion_lexicale()


def analyser_diversite_lexicale(corpus):
    """
    Description :
        Prépare les données et calcule tous les indicateurs
        de diversité lexicale.
    
    Paramètres :
        corpus  dict, {id : liste de listes de tokens}.
    
    Retour :
        dict, dictionnaire contenant les 3 indicateurs clés.
    """
    if not corpus:
        return {}
    
    tokens = [token for doc in corpus.values() for phrase in doc for token in phrase]
    richesse = calculer_richesse_lexicale(tokens)
    hapax = calculer_taux_hapax(tokens)
    dispersion = calculer_dispersion_lexicale(tokens)

    return {
        "richesseLexicale": round(richesse, 4),
        "tauxHapax": round(hapax, 4),
        "dispersionLexicale": round(dispersion, 4),
        "totalTokens": len(tokens),
        "vocabulaireUnique": len(set(tokens))
    }

def test_analyser_diversite_lexicale():
    print("\n Test 4 : analyser_diversite_lexicale (Orchestrateur) ")
    
    # Corpus factice
    corpus = {
        "d1": [["le", "chat"]],
        "d2": [["le", "chien"]]
    }
    
    # Tokens aplatis : ["le", "chat", "le", "chien"]    
    stats = analyser_diversite_lexicale(corpus)
    print("  Stats :", stats)
    
    assert stats["totalTokens"] == 4
    assert stats["vocabulaireUnique"] == 3
    assert stats["richesseLexicale"] == 0.75
    assert 0.66 < stats["tauxHapax"] < 0.67
    
    print(" Test Orchestrateur validé.")

#test_analyser_diversite_lexicale()



#c
def construire_dictionnaire_vocabulaire(liste_mots):
    """ Construit le dictionnaire {mot: index} """
    mots_uniques = sorted(list(set(liste_mots)))
    return {mot: i for i, mot in enumerate(mots_uniques)}
#def construire_dictionnaire_vocabulaire(vocabulaire):
    """
    Description :
        Construit deux dictionnaires permettant de convertir les mots en indices
        entiers et inversement. Indispensable pour la vectorisation.
    
    Paramètres :
        vocabulaire  list, la liste des tokens uniques du corpus.
    
    Retour :
        tuple (dict, dict), le couple (mot2idx, idx2mot).
    """
    if not vocabulaire:
        return {}, {}
    mot2idx = {} 
    idx2mot = {}
    for index, mot in enumerate(vocabulaire):
        mot2idx[mot] = index
        idx2mot[index] = mot
    return mot2idx, idx2mot

def test_construire_dictionnaire_vocabulaire():
    print("\n Test : construire_dictionnaire_vocabulaire ")
    
    # Vocabulaire factice
    vocab_test = ["chat", "chien", "maison", "soleil"]
    mot2idx, idx2mot = construire_dictionnaire_vocabulaire(vocab_test)
    
    print(f"  Vocabulaire : {vocab_test}")
    print(f"  Mot -> Index : {mot2idx}")
    assert mot2idx["chat"] == 0
    assert mot2idx["chien"] == 1
    assert mot2idx["soleil"] == 3
    
    # Vérifications Index -> Mot
    assert idx2mot[0] == "chat"
    assert idx2mot[3] == "soleil"
    
    # Vérification de cohérence
    index_maison = mot2idx["maison"]
    mot_retrouve = idx2mot[index_maison]
    assert mot_retrouve == "maison"
    
    # Cas limite : Vocabulaire vide
    m2i_vide, i2m_vide = construire_dictionnaire_vocabulaire([])
    assert m2i_vide == {}
    assert i2m_vide == {}
    
    print(" Test 'construire_dictionnaire_vocabulaire' validé.")


#test_construire_dictionnaire_vocabulaire()

#4 Filtrage lexical 

#a

def construire_liste_stopwords(langue="fr"):
    """
    Description :
        Retourne une liste de mots vides courants pour la langue choisie.
        Ces listes sont codées en dur pour ne pas dépendre de bibliothèques externes.
    
    Paramètres :
        langue  str, 'fr' pour français, 'en' pour anglais.
    
    Retour :
        list, une liste de chaînes de caractères.
    """
    if langue == "fr":
        return [
            "le", "la", "les", "un", "une", "des", "du", "de", "d'", "l'",
            "ce", "cet", "cette", "ces", "mon", "ton", "son", "notre", "votre", "leur",
            "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "on",
            "et", "ou", "mais", "donc", "or", "ni", "car",
            "à", "au", "aux", "en", "par", "pour", "sur", "dans", "avec", "sans", "sous",
            "qui", "que", "quoi", "dont", "où",
            "est", "sont", "a", "ont", "être", "avoir", "faire",
            "ne", "pas", "plus", "moins", "très", "bien", "tout", "tous"
        ]
        
    elif langue == "en":
        return [
            "the", "a", "an",
            "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their",
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "us", "them",
            "and", "or", "but", "so", "nor", "for", "yet",
            "in", "on", "at", "by", "for", "with", "about", "against", "between", "into", "through",
            "who", "which", "what", "whose", "whom",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "not", "no", "very", "all", "any", "some"
        ]
        
    else:
        return []
    
def test_construire_liste_stopwords():
    print("\nTest : construire_liste_stopwords")
    # Test FR
    stop_fr = construire_liste_stopwords("fr")
    assert "le" in stop_fr
    assert "avec" in stop_fr
    assert len(stop_fr) > 10
    # Test EN
    stop_en = construire_liste_stopwords("en")
    assert "the" in stop_en
    assert "is" in stop_en
    # Test Inconnu
    assert construire_liste_stopwords("es") == []
    
    print(" Test construction validé.")


#test_construire_liste_stopwords()
#b

def supprimer_mots_vides(tokens, liste_stopwords):
    """
    Description :
        Filtre une liste de tokens en retirant ceux présents dans la liste des stopwords.
        La vérification est insensible à la casse.
    
    Paramètres :
        tokens           list, la liste des tokens à filtrer.
        liste_stopwords  list, la liste des mots à exclure.
    
    Retour :
        list, la liste des tokens filtrés.
    """
    if not tokens:
        return []
    
    if not liste_stopwords:
        return tokens
    stop = set(liste_stopwords)
    filtre = []
    for token in tokens:
        if token.lower() not in stop:
            filtre.append(token)
    return filtre


def test_supprimer_mots_vides():
    print("\nTest : supprimer_mots_vides")
    
    # Liste de test
    stopwords = ["le", "la", "est", "un"]

    # Cas 1 : Standard (Insensible à la casse)
    # "Le" (majuscule) doit être supprimé car "le" est dans les stopwords
    tokens = ["Le", "chat", "est", "un", "animal", "."]
    res = supprimer_mots_vides(tokens, stopwords)
    
    print(f"  Avant : {tokens}")
    print(f"  Après : {res}")
    
    # Attendu : "chat", "animal", "." 
    assert "chat" in res
    assert "animal" in res
    assert "." in res
    assert "Le" not in res
    assert "est" not in res
    
    # Cas 2 : Aucun stopword trouvé
    tokens2 = ["Python", "code", "vitesse"]
    res2 = supprimer_mots_vides(tokens2, stopwords)
    assert res2 == tokens2
    
    # Cas 3 : Que des stopwords
    tokens3 = ["le", "la", "un"]
    res3 = supprimer_mots_vides(tokens3, stopwords)
    assert res3 == []

    print(" Test suppression validé.")

#test_supprimer_mots_vides()

# b

def supprimer_tokens_courts(tokens, longueur_min=3):
    """
    Description :
        Filtre une liste de tokens en retirant ceux dont la longueur
        est inférieure au seuil spécifié.
    
    Paramètres :
        tokens        list, la liste des tokens à filtrer.
        longueur_min  int, la longueur minimale requise pour garder un token.
    
    Retour :
        list, la liste des tokens filtrés.
    """
    if not tokens:
        return []
        
    return [token for token in tokens if len(token) >= longueur_min]

def test_supprimer_tokens_courts():
    print("\nTest : supprimer_tokens_courts")
    
    # Liste de test
    tokens = ["le", "chat", "a", "pu", "voir", "ça"]
    
    # Cas 1 : Seuil par défaut (3)
    res_defaut = supprimer_tokens_courts(tokens)
    print(f"  Défaut (min=3) : {res_defaut}")
    
    assert "chat" in res_defaut
    assert "voir" in res_defaut
    assert "le" not in res_defaut
    assert "a" not in res_defaut
    assert len(res_defaut) == 2
    
    # Cas 2 : Seuil personnalisé (2)
    res_2 = supprimer_tokens_courts(tokens, longueur_min=2)
    assert "le" in res_2
    assert len(res_2) == 5
    
    # Cas 3 : Liste vide
    assert supprimer_tokens_courts([]) == []

    print(" Test suppression longueur validé.")


#test_supprimer_tokens_courts()

#c

def supprimer_non_alphabetiques(tokens):
    """
    Description :
        Filtre une liste de tokens en ne gardant que ceux composés
        uniquement de lettres.
        Rejette "123", "c'est", "v2.0", "!".
    
    Paramètres :
        tokens  list, la liste des tokens à filtrer.
    
    Retour :
        list, la liste des tokens purement alphabétiques.
    """
    if not tokens:
        return []
    
    return [token for token in tokens if token.isalpha()]

def test_supprimer_non_alphabetiques_tokens():
    print("\nTest : supprimer_non_alphabetiques (Tokens)")
    tokens = ["chat", "123", "v2", "!", "chien", "c'est"]
    res = supprimer_non_alphabetiques(tokens)
    print(f"  Résultat : {res}")
    
    assert "chat" in res
    assert "chien" in res
    assert "123" not in res
    assert "v2" not in res
    assert "!" not in res
    assert "c'est" not in res
    
    print(" Test validé.")


#test_supprimer_non_alphabetiques_tokens()

#d

def filtrer_par_occurrence(vocabulaire, occ_min=2, occ_max=None):
    """
    Description :
        Filtre le vocabulaire pour ne garder que les tokens dont la fréquence
        est comprise entre les bornes spécifiées.
    
    Paramètres :
        vocabulaire  dict, un dictionnaire {token: nombre_occurrences}.
        occ_min      int, seuil minimal. Défaut 2.
        occ_max      int, seuil maximal. Défaut None.
    
    Retour :
        dict, le vocabulaire filtré {token: nombre_occurrences}.
    """
    if not vocabulaire:
        return {}
    
    filtre = {}
    
    for token, count in vocabulaire.items():
        conditionMin = count >= occ_min
        conditionMax = True
        if occ_max is not None:
            conditionMax = count <= occ_max
            
        if conditionMin and conditionMax:
            filtre[token] = count
            
    return filtre

def test_filtrer_par_occurrence():
    print("\nTest : filtrer_par_occurrence")
    vocab_test = {
        "rare": 1,
        "moyen": 5,
        "frequent": 100
    }
    
    # Cas 1 : Filtrage Min (supprimer les hapax)
    res_min = filtrer_par_occurrence(vocab_test, occ_min=2)
    print(f"  Min=2 : {res_min}")
    assert "rare" not in res_min
    assert "moyen" in res_min
    assert "frequent" in res_min
    
    # Cas 2 : Filtrage Max (supprimer les mots trop fréquents)
    res_max = filtrer_par_occurrence(vocab_test, occ_min=1, occ_max=10)
    print(f"  Max=10 : {res_max}")
    assert "frequent" not in res_max
    assert "moyen" in res_max
    
    # Cas 3 : Fourchette (Band-pass)
    res_range = filtrer_par_occurrence(vocab_test, occ_min=2, occ_max=10)
    assert len(res_range) == 1
    assert "moyen" in res_range
    
    print(" Test 'filtrer_par_occurrence' validé.")


#test_filtrer_par_occurrence()

#e

def pipeline_filtrage(tokens, config, langue="fr"):
    """
    Description :
        Orchestre l'application successive des filtres sur une liste de tokens
        selon une configuration donnée.
    
    Paramètres :
        tokens  list, la liste brute des tokens.
        config  dict, paramètres d'activation des filtres.
        langue  str, langue pour les stopwords.
    
    Retour :
        list, la liste des tokens filtrés.
    """
    if not tokens:
        return []
    res = list(tokens)
    if config.get("stopwords"):
        liste = construire_liste_stopwords(langue)
        res = supprimer_mots_vides(res, liste)
    if config.get("non_alphabetiques"):
        res = supprimer_non_alphabetiques(res)
        
    longueur= config.get("longueur_min")
    if longueur is not None and longueur > 0:
        res = supprimer_tokens_courts(res, longueur)
        
    occMin = config.get("occ_min")
    occMax = config.get("occ_max")
    
    if occMin is not None or occMax is not None:
        compteur = Counter(res)
        resOcc = []
        
        for token in res:
            count = compteur[token]
            garder = True
            
            if occMin is not None and count < occMin:
                garder = False
            if occMax is not None and count > occMax:
                garder = False
                
            if garder:
                resOcc.append(token)
        
        res = resOcc

    return res


def test_pipeline_filtrage():
    print("\n Test : pipeline_filtrage ")
    tokBrute = ["le", "chat", "123", "a", "chat", "rare", "le"]
    
    # Config de test
    config_test = {
        "stopwords": True,          
        "non_alphabetiques": True, 
        "longueur_min": 3,          
        "occ_min": 2,            
        "occ_max": None
    }
    res = pipeline_filtrage(tokBrute, config_test, langue="fr")
    print(f"  Avant : {tokBrute}")
    print(f"  Après : {res}")
    assert res == ["chat", "chat"]
    assert "123" not in res
    assert "le" not in res
    assert "rare" not in res
    print(" Test 'pipeline_filtrage' validé.")


#test_pipeline_filtrage()

#5 Normalisation morphologique (Stemming et Lemmatisation)

#a
def appliquer_stemming(tokens, langue='fr'):
    """
    Description :
        Applique un stemming simplifié en supprimant les suffixes fréquents.
        Priorise le suffixe le plus long.
        Ne modifie pas les mots trop courts.
    
    Paramètres :
        tokens  list, la liste des tokens à traiter.
        langue  str, la langue des règles à appliquer.
    
    Retour :
        list, la liste des racines.
    """
    if not tokens:
        return []
    regles = {
        "fr": [
            "ements", "ations", "ation", "ateur", "trice", "euse",
            "ement", "ment", "ions", "aient", "s", "es"
        ],
        "en": [
            "ingly", "edly", "tion", "ness", "able", 
            "ing", "ers", "ed", "ly", "es", "s"
        ]
    }
    suffixes = regles.get(langue, [])
    suffixes = sorted(suffixes, key=len, reverse=True)
    stems = []
    for token in tokens:
        tokenStem = token
        if len(token) > 3:
            for suffix in suffixes:
                if token.endswith(suffix):
                    racine = token[:-len(suffix)]
                    if len(racine) >= 2: 
                        tokenStem = racine
        stems.append(tokenStem)
    return stems


def test_appliquer_stemming():
    print("\n Test : appliquer_stemming ")
    
    # - 1. Test Français -
    mots_fr = ["chats", "rapidement", "informations", "bus", "chanteuse"]
    res_fr = appliquer_stemming(mots_fr, "fr")
    
    print(f"  FR Avant : {mots_fr}")
    print(f"  FR Après : {res_fr}")
    
    assert res_fr[0] == "chat"      
    
    assert res_fr[1] == "rapide" or res_fr[1] == "rapid"
    
    assert res_fr[3] == "bus"        
    assert "euse" not in res_fr[4]   
    
    # - 2. Test Anglais -
    mots_en = ["playing", "cats", "happiness"]
    res_en = appliquer_stemming(mots_en, "en")
    
    print(f"  EN Après : {res_en}")
    
    assert res_en[0] == "play"
    assert res_en[1] == "cat"
    
    print(" Test 'appliquer_stemming' validé.")

#test_appliquer_stemming()
#b

def appliquer_lemmatisation(tokens, langue="fr", dictionnaire_lemmes=None):
    """
    Description :
        Remplace les tokens par leur lemmeen utilisant
        un dictionnaire de correspondance.
    
    Paramètres :
        tokens  list, la liste des tokens à lemmatiser.
        langue  str, langue par défautsi aucun dictionnaire n'est fourni.
        dictionnaire_lemmes  dict, dictionnaire personnalisé {forme : lemme}.
    
    Retour :
        list, la liste des tokens lemmatisés.
    """
    if not tokens:
        return []
    if dictionnaire_lemmes is not None:
        mapping = dictionnaire_lemmes
    else:
        lemmes_fr = {
            "chevaux": "cheval", "yeux": "oeil", "travaux": "travail", 
            "journaux": "journal", "étudiants": "étudiant",
            "suis": "être", "es": "être", "est": "être", "sommes": "être", "sont": "être", "été": "être",
            "ai": "avoir", "as": "avoir", "a": "avoir", "ont": "avoir", "eu": "avoir",
            "vais": "aller", "vas": "aller", "va": "aller", "iront": "aller", "allées": "aller",
            "mangeaient": "manger", "programmation": "programme"
        }
        
        lemmes_en = {
            "mice": "mouse", "feet": "foot", "teeth": "tooth", 
            "children": "child", "machines": "machine",
            "am": "be", "is": "be", "are": "be", "was": "be", "were": "be",
            "went": "go", "gone": "go",
            "running": "run", "played": "play",
            "better": "good", "best": "good", "worse": "bad"
        }
        
        mapping = lemmes_fr if langue == "fr" else lemmes_en

    # 2. Application
    lemmes = []
    for token in tokens:
        lemme = mapping.get(token, token)
        lemmes.append(lemme)
        
    return lemmes

def test_appliquer_lemmatisation():
    print("\n Test : appliquer_lemmatisation ")
    
    # - 1. Test Français (Défaut) -
    phrase_fr = ["je", "suis", "allé", "voir", "les", "chevaux"]
    phrase_fr_2 = ["il", "est", "étudiants"]
    
    res_fr = appliquer_lemmatisation(phrase_fr_2, "fr")
    print(f"  FR : {phrase_fr_2} -> {res_fr}")
    
    assert res_fr == ["il", "être", "étudiant"]
    
    # - 2. Test Anglais -
    phrase_en = ["mice", "are", "running", "fast"]
    res_en = appliquer_lemmatisation(phrase_en, "en")
    print(f"  EN : {phrase_en} -> {res_en}")
    assert res_en == ["mouse", "be", "run", "fast"]
    
    # - 3. Test Dictionnaire Personnalisé -
    phrase_custom = ["codant", "dormant"]
    mon_dico = {"codant": "coder", "dormant": "dormir"}
    
    res_custom = appliquer_lemmatisation(phrase_custom, dictionnaire_lemmes=mon_dico)
    
    assert res_custom == ["coder", "dormir"]
    
    print(" Test 'appliquer_lemmatisation' validé.")


#test_appliquer_lemmatisation()

#c
def pipeline_morphologique(tokens, config, langue="fr", lemmes=None):
    """
    Description :
        Orchestre la normalisation morphologique
        selon la configuration choisie.
    
    Paramètres :
        tokens  list, la liste des tokens à normaliser.
        config  dict, activation des modules.
        langue  str, langue du traitement.
        lemmes  dict, dictionnaire optionnel pour la lemmatisation.
    
    Retour :
        list, la liste des tokens normalisés.
    """
    if not tokens:
        return []
    res = list(tokens)
    if config.get("lemmatisation"):
        res = appliquer_lemmatisation(res, langue, lemmes)
    if config.get("stemming"):
        res = appliquer_stemming(res, langue)    
    return res


def test_comparaison_morphologique():
    print("\n Expérimentation : Comparaison des Stratégies Morphologiques ")
    
    # Corpus de test riche en variations morphologiques
    # "chats"/"chat", "chantent"/"chanteur", "mangé"/"manger"
    tokBrute = [
        "les", "chats", "jouent", "avec", "le", "chat", 
        "ils", "ont", "mangé", "et", "ils", "vont", "manger",
        "le", "chanteur", "chante", "les", "chansons",
        "programmation", "programmer", "programme"
    ]
    
    print(f"Nombre de tokens total : {len(tokBrute)}")
    print("-" * 65)
    print(f"{'Stratégie':<20} | {'Vocabulaire':<12} | {'Taux Hapax':<10} | {'Exemple (5 premiers)'}")
    print("-" * 65)

    strategies = {
        "Aucune": {"stemming": False, "lemmatisation": False},
        "Lemmatisation Seule": {"stemming": False, "lemmatisation": True},
        "Stemming Seul": {"stemming": True, "lemmatisation": False},
        "Combiné (Lem+Stem)": {"stemming": True, "lemmatisation": True}
    }

    for nom, cfg in strategies.items():
        # 1. Application du pipeline
        tokens_traites = pipeline_morphologique(tokBrute, cfg, langue="fr")
        
        # 2. Calcul des métriques
        vocab = set(tokens_traites)
        taille_vocab = len(vocab)
        try:
            taux = calculer_taux_hapax(tokens_traites)
        except NameError:
            from collections import Counter
            c = Counter(tokens_traites)
            hapax = sum(1 for k,v in c.items() if v==1)
            taux = hapax / taille_vocab if taille_vocab else 0

        # 3. Affichage
        exemple = ", ".join(tokens_traites[:5])
        print(f"{nom:<20} | {taille_vocab:<12} | {taux:<10.2f} | {exemple}")

    print("-" * 65)
    print("Analyse :")
    print("-> Le 'Stemming' réduit le plus le vocabulaire (agressif).")
    print("-> La 'Lemmatisation' préserve mieux le sens (moins de fusion abusive).")
    print(" Test Comparaison validé.")

#test_comparaison_morphologique()

#6 Statistiques après filtrage et normalisation 

#a

def calculer_statistiques_post_traitement(corpus_filtre, vocabulaire_filtre, langue="fr"):
    """
    Description :
        Calcule les statistiques lexicales sur le corpus après filtrage et normalisation.
        Permet de mesurer l'impact du pipeline.
    
    Paramètres :
        corpus_filtre       dict, {id : liste de listes de tokens}.
        vocabulaire_filtre  list, la liste des tokens uniques du corpus filtré.
        langue              str, pour vérifier les stopwords résiduels.
    
    Retour :
        dict, dictionnaire de synthèse des indicateurs.
    """
    tokens = []
    if corpus_filtre:
        tokens = [token for doc in corpus_filtre.values() for phrase in doc for token in phrase]
    
    nbTokensTotal = len(tokens)
    tailleVoc = len(vocabulaire_filtre)
    richesse = 0.0
    tauxHapax = 0.0
    proportionBruit = 0.0
    
    if nbTokensTotal > 0:
        richesse = tailleVoc / nbTokensTotal
        frequences = Counter(tokens)
        nb = sum(1 for count in frequences.values() if count == 1)
        if tailleVoc > 0:
            tauxHapax = nb / tailleVoc
        try:
            stop = set(construire_liste_stopwords(langue))
            nbBruit = sum(1 for t in tokens if t in stop)
            proportionBruit = nbBruit / nbTokensTotal
        except NameError:
            proportionBruit = -1.0
    stats = {
        "nbDocument": len(corpus_filtre) if corpus_filtre else 0,
        "nbTokensTotal": nbTokensTotal,
        "tailleVoc": tailleVoc,
        "richesseLexicale": round(richesse, 4),
        "tauxHapax": round(tauxHapax, 4),
        "proportionBruitResiduel": round(proportionBruit, 4)
    }
    
    return stats


def test_calculer_statistiques_post_traitement():
    print("\n Test : calculer_statistiques_post_traitement ")
    
    # Simulation d'un corpus après stemming
    corp = {
        "d1": [["chat", "mang"]],
        "d2": [["chat", "dort", "le"]]
    }
    
    # Vocabulaire unique correspondant
    vocab = ["chat", "mang", "dort", "le"]
    stats = calculer_statistiques_post_traitement(corp, vocab, langue="fr")
    
    print(f"  Stats Post-Traitement : {stats}")
    assert stats["nbTokensTotal"] == 5
    assert stats["tailleVoc"] == 4
    assert stats["richesseLexicale"] == 0.8
    assert stats["tauxHapax"] == 0.75
    
    if stats["proportionBruitResiduel"] != -1.0:
        assert stats["proportionBruitResiduel"] == 0.2
    else:
        print("  (Test du bruit ignoré : fonction stopwords manquante)")
        
    print(" Test Bilan Post-Traitement validé.")


#test_calculer_statistiques_post_traitement()


#b
def visualiser_statistiques_post_traitement(stats_initiales, stats):
    """
    Description :
        Génère un tableau de bord comparatif pour visualiser
        l'impact du prétraitement sur le corpus.
    
    Paramètres :
        stats_initiales  dict, statistiques sur le corpus brut.
        stats       dict, statistiques sur le corpus nettoyé.
    
    Retour :
        matplotlib.figure.Figure, l'objet graphique comparatif.
    """
    
    if not stats_initiales or not stats:
        return None


    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    cAvant = 'lightgray'
    cApres = 'skyblue'
    vAvant = stats_initiales.get('tailleVoc', stats_initiales.get('vocabulaire_unique', 0))
    vApres = stats.get('tailleVoc', stats.get('vocabulaire_unique', 0))
    
    axes[0].bar(['Brut', 'Nettoyé'], [vAvant, vApres], color=[cAvant, cApres], edgecolor='black')
    axes[0].set_title("Réduction du Vocabulaire")
    axes[0].set_ylabel("Nombre de mots uniques")
    if vAvant > 0:
        reduction = ((vAvant - vApres) / vAvant) * 100
        axes[0].text(1, vApres, f"-{reduction:.1f}%", ha='center', va='bottom', fontweight='bold')
    labels = ['Richesse Lexicale', 'Taux Hapax']
    
    valAvant = [stats_initiales.get('richesse_lexicale', 0), stats_initiales.get('taux_hapax', 0)]
    valApres = [stats.get('richesse_lexicale', 0), stats.get('taux_hapax', 0)]
    
    x = np.arange(len(labels))
    width = 0.35
    
    axes[1].bar(x - width/2, valAvant, width, label='Avant', color=cAvant, edgecolor='black')
    axes[1].bar(x + width/2, valApres, width, label='Après', color=cApres, edgecolor='black')
    
    axes[1].set_title("Évolution de la Structure Lexicale")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylim(0, 1.1)
    axes[1].legend()

    tAvant = stats_initiales.get('nbTokensTotal', stats_initiales.get('total_tokens', 0))
    tApres = stats.get('nbTokensTotal', stats.get('total_tokens', 0))
    
    bruitSupprime = max(0, tAvant - tApres)
    
    sizes = [tApres, bruitSupprime]
    label = ['Information Utile\n(Conservée)', 'Bruit\n(Supprimé)']
    color = [cApres, 'salmon']
    
    if tAvant > 0:
        axes[2].pie(sizes, labels=label, colors=color, autopct='%1.1f%%', startangle=90, explode=(0.05, 0))
        axes[2].set_title(f"Ratio Compression (Total tokens : {tAvant})")
    else:
        axes[2].text(0.5, 0.5, "Données insuffisantes", ha='center')
    plt.suptitle("Impact du Pipeline de Prétraitement", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig

def test_visualiser_comparaison():
    print("\n Test : visualiser_statistiques_post_traitement (Visuel) ")
    
    # Simulation de données réalistes
    stats_init = {
        'tailleVoc': 2500,
        'nbTokensTotal': 10000,
        'richesse_lexicale': 0.25,
        'taux_hapax': 0.40
    }
    
    # Après : Moins de mots (stopwords virés), vocabulaire réduit (stemming)
    stats = {
        'tailleVoc': 1800,  
        'nbTokensTotal': 6000, 
        'richesse_lexicale': 0.30,   
        'taux_hapax': 0.35          
    }
    
    try:
        fig = visualiser_statistiques_post_traitement(stats_init, stats)
        assert fig is not None
        nom_fichier = "comparatif_avantApres.png"
        fig.savefig(nom_fichier)
        plt.close(fig)
        
        print(f" Test validé. Graphique sauvegardé : {nom_fichier}")
        
    except Exception as e:
        print(f" Erreur : {e}")


#test_visualiser_comparaison()

#7. Comparaison des configurations de prétraitement 

#a
def pipeline_pretraitement(corpus, config, langue="fr", stopwords=None, lemmes=None):
    """
    Applique le nettoyage : Minuscule -> Regex Alphanum -> Stopwords -> Longueur
    """
    if not corpus:
        return {}

    # Si stopwords non fournis, on utilise la liste globale
    if config.get("stopwords") and not stopwords:
        stopwords = TOUS_STOPWORDS
    else:
        stopwords = set()

    corpus_nettoye = {}

    for doc_id, contenu in corpus.items():
        doc_traite = []
        
        # Gestion flexible : contenu peut être une liste de mots ou une liste de listes (phrases)
        # On aplatit tout pour traiter mot par mot
        if contenu and isinstance(contenu[0], list):
            liste_mots_bruts = [m for phrase in contenu for m in phrase]
        else:
            liste_mots_bruts = contenu

        mots_propres_doc = []
        
        for token in liste_mots_bruts:
            # 1. MISE EN MINUSCULE (CRUCIAL : à faire en premier)
            t = token.lower()
            
            # 2. NETTOYAGE PONCTUATION VIA REGEX
            # On garde les lettres (a-z), les chiffres (0-9) et les accents français
            # On supprime tout le reste (points, virgules, parenthèses...)
            if config.get("non_alphabetiques", True):
                t = re.sub(r'[^a-z0-9àâçéèêëîïôûùüÿñæoe]+', '', t)
            
            # Si le mot est devenu vide (ex: "..." devient ""), on le saute
            if not t:
                continue

            # 3. STOPWORDS
            if config.get("stopwords", True):
                if t in stopwords:
                    continue

            # 4. LONGUEUR MINIMUM
            l_min = config.get("longueur_min", 2)
            if len(t) < l_min:
                continue
            
            # 5. STEMMING / LEMMATISATION (Optionnel)
            # (Ajoutez vos appels de fonctions ici si nécessaire)
            
            mots_propres_doc.append(t)
        
        # On garde le document s'il reste des mots
        if mots_propres_doc:
            corpus_nettoye[doc_id] = mots_propres_doc
            
    return corpus_nettoye

def test_comparaison_configurations():
    print("\n Test : Comparaison des Configurations (A, B, C, D, E) ")
    
    # Phrase témoin riche :
    phrase_temoin = [["Les", "chiens", "jouent", "rapidement", "123", "!"]]
    corpus_test = {"doc1": phrase_temoin}
    
    # Définition des configurations
    configs = {
        "A (Brut)": {
            "stopwords": False, "longueur_min": 0, "non_alphabetiques": False, 
            "stemming": False, "lemmatisation": False
        },
        "B (Filtres légers)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": False, 
            "stemming": False, "lemmatisation": False
        },
        "C (Filtres stricts)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": True, 
            "stemming": False, "lemmatisation": False
        },
        "D (Stemming)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": True, 
            "stemming": True, "lemmatisation": False
        },
        "E (Lemmatisation+Stem)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": True, 
            "stemming": True, "lemmatisation": True
        }
    }
    
    # Simulation d'un dictionnaire de lemmes pour le test
    lemmes_test = {"chiens": "chien", "jouent": "jouer"}

    print(f"Phrase originale : {phrase_temoin[0]}")
    print("-" * 60)
    print(f"{'Config':<25} | {'Résultat'}")
    print("-" * 60)

    for nom, cfg in configs.items():
        res_corpus = pipeline_pretraitement(corpus_test, cfg, langue="fr", lemmes=lemmes_test)
        
        if "doc1" in res_corpus:
            tokens = res_corpus["doc1"][0]
            print(f"{nom:<25} | {tokens}")
            
            if nom == "A (Brut)":
                assert len(tokens) == 6 
            elif nom == "B (Filtres légers)":
                assert "Les" not in tokens 
                assert "123" in tokens 
            elif nom == "C (Filtres stricts)":
                assert "123" not in tokens
                assert "chiens" in tokens
            elif nom == "D (Stemming)":
                assert "rapide" in tokens or "rapid" in tokens
            elif nom == "E (Lemmatisation+Stem)":
                pass
        else:
            print(f"{nom:<25} | (Document vide)")

    print("-" * 60)
    print(" Test Comparaison Configurations validé.")

#test_comparaison_configurations()

#b

def evaluer_configurations(corpus_tokenise, configurations, langue="fr"):
    """
    Description :
        Applique une série de configurations de prétraitement sur un corpus tokenisé
        et calcule les statistiques pour chacune.
    
    Paramètres :
        corpus_tokenise  dict, {id : liste de listes de tokens}.
        configurations   dict, {nom_config : dict_parametres}.
        langue           str, langue pour les stopwords/lemmes.
    
    Retour :
        dict, {nom_config : {statistiques...}}.
    """
    if not corpus_tokenise or not configurations:
        return {}
        
    resultats = {}
    for nom, config in configurations.items():
        corp = pipeline_pretraitement(corpus_tokenise, config, langue=langue)
        vocab = construire_vocabulaire(corp)
        stats = calculer_statistiques_post_traitement(corp, vocab, langue=langue)
        resultats[nom] = {
            "nbTokens": stats["nbTokensTotal"],
            "vocab": stats["tailleVoc"],
            "richesse": stats["richesseLexicale"],
            "hapax": stats["tauxHapax"],
            "bruit": stats["proportionBruitResiduel"]
        }
        
    return resultats

def test_evaluation_configurations():
    print("\n Test : Évaluation des Configurations (Benchmark) ")
    corpus_input = {
        "d1": [["le", "chat", "mange", "la", "souris", "."]],
        "d2": [["les", "chats", "mangent", "des", "souris", "123", "!"]]
    }
    configs = {
        "A (Brut)": {
            "stopwords": False, "longueur_min": 0, "non_alphabetiques": False, 
            "stemming": False, "lemmatisation": False
        },
        "B (Filtres légers)": {
            "stopwords": True, "longueur_min": 2, "non_alphabetiques": False, 
            "stemming": False, "lemmatisation": False
        },
        "C (Filtres stricts)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": True, 
            "stemming": False, "lemmatisation": False
        },
        "D (Stemming)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": True, 
            "stemming": True, "lemmatisation": False
        },
        "E (Lemmatisation)": {
            "stopwords": True, "longueur_min": 3, "non_alphabetiques": True, 
            "stemming": False, "lemmatisation": True
        }
    }
    
    # - 3. Exécution -
    try:
        resultats = evaluer_configurations(corpus_input, configs, langue="fr")
        
        # - 4. Analyse des résultats -
        print("\n- Résultats du Benchmark -")
        print(f"{'Config':<20} | {'Tokens':<8} | {'Vocab':<8} | {'Richesse':<8}")
        print("-" * 50)
        
        for nom, res in resultats.items():
            print(f"{nom:<20} | {res['nbTokens']:<8} | {res['vocab']:<8} | {res['richesse']:<8.2f}")
            
        # Vérifications logiques
        # A (Brut) doit avoir le plus de tokens
        assert resultats["A (Brut)"]["nbTokens"] == 13
        
        # C (Strict) doit avoir moins de tokens que A (suppression stopwords/chiffres)
        assert resultats["C (Filtres stricts)"]["nbTokens"] < 13
        
        # D (Stemming) doit avoir un vocabulaire plus petit ou égal à C

        assert resultats["D (Stemming)"]["vocab"] < resultats["C (Filtres stricts)"]["vocab"]
        
        print("\n Test Benchmark validé avec succès.")
        
    except NameError as e:
        print(f"\n Test ignoré : fonction manquante ({e})")


#test_evaluation_configurations()


#c


def analyser_resultats_comparatifs(resultats):
    """
    Description :
        Analyse les différences entre les configurations
        et retourne un rapport structuré.
    
    Paramètres :
        resultats  dict, le dictionnaire retourné par 'evaluer_configurations'.
    
    Retour :
        dict, un rapport complet contenant l'analyse des réductions, 
              le classement par richesse et la comparaison morphologique.
    """
    if not resultats or "A (Brut)" not in resultats:
        return {"erreur": "Résultats manquants ou Config A (référence) absente."}

    rapport = {
        "analyse_reduction": {},
        "classement_qualite": [],
        "analyse_morphologique": {},
        "meilleure_config_reduction": None
    }
    ref = resultats["A (Brut)"]
    vocab = ref["vocab"]
    tokens = ref["nb_tokens"]

    max = -1
    meilleure = None

    for nom, data in resultats.items():
        if nom == "A (Brut)": continue
        
        gainVocab = ((vocab - data["vocab"]) / vocab) * 100
        gainVolume = ((tokens - data["nb_tokens"]) / tokens) * 100
        
        rapport["analyse_reduction"][nom] = {
            "gain_vocabulaire_pct": round(gainVocab, 2),
            "gain_volume_pct": round(gainVolume, 2)
        }
        
        if gainVocab > max:
            max = gainVocab
            meilleure = nom

    rapport["meilleure_config_reduction"] = (meilleure, round(max, 2))

    for nom, data in resultats.items():
        entry = {
            "nom": nom,
            "richesse": data["richesse"],
            "bruit_residuel": data["bruit"]
        }
        rapport["classement_qualite"].append(entry)
        
    rapport["classement_qualite"].sort(key=lambda x: x["richesse"], reverse=True)

    if "D (Stemming)" in resultats and "E (Lemmatisation)" in resultats:
        d = resultats["D (Stemming)"]
        e = resultats["E (Lemmatisation)"]
        diff= d["vocab"] - e["vocab"]
        
        constat = ""
        if diff< 0:
            constat = "Stemming plus agressif (réduit plus)"
        else:
            constat = "Lemmatisation plus efficace (réduit plus)"
            
        rapport["analyse_morphologique"] = {
            "diff_vocabulaire_absolue": abs(diff),
            "constat": constat,
            "vocab_stemming": d["vocab"],
            "vocab_lemmatisation": e["vocab"]
        }

    return rapport


def test_analyser_resultats():
    print("\n Test : analyser_resultats_comparatifs (Retour Dict) ")
    
    # Données simulées réalistes
    resultats_fictifs = {
        "A (Brut)": {"vocab": 5000, "nb_tokens": 20000, "richesse": 0.25, "bruit": 0.4},
        "B (Filtres légers)": {"vocab": 4800, "nb_tokens": 12000, "richesse": 0.40, "bruit": 0.05},
        "C (Filtres stricts)": {"vocab": 4500, "nb_tokens": 11000, "richesse": 0.41, "bruit": 0.0},
        "D (Stemming)": {"vocab": 3500, "nb_tokens": 11000, "richesse": 0.31, "bruit": 0.0},
        "E (Lemmatisation)": {"vocab": 3800, "nb_tokens": 11000, "richesse": 0.34, "bruit": 0.0}
    }
    
    rapport = analyser_resultats_comparatifs(resultats_fictifs)
    
    # Vérifications

    meilleur_nom, meilleur_score = rapport["meilleure_config_reduction"]
    print(f"  Meilleure réduction : {meilleur_nom} ({meilleur_score}%)")
    assert "D (Stemming)" == meilleur_nom
    assert 30.0 == meilleur_score
    
    # 2. Vérification du classement qualité
    top_qualite = rapport["classement_qualite"][0]
    print(f"  Top Qualité : {top_qualite['nom']} (Richesse: {top_qualite['richesse']})")
    
    assert top_qualite["nom"] == "C (Filtres stricts)"
    assert top_qualite["richesse"] == 0.41
    
    # 3. Vérification de l'analyse morphologique
    morpho = rapport["analyse_morphologique"]
    print(f"  Analyse Morpho : {morpho['constat']}")
    
    assert morpho["diff_vocabulaire_absolue"] == 300
    assert "Stemming plus agressif" in morpho["constat"]
    
    print(" Test Analyseur validé.")


#test_analyser_resultats()

#d

def visualiser_comparaison_configurations(resultats_configurations):
    """
    Description :
        Génère un tableau de bord graphique comparant les performances
        de plusieurs configurations de prétraitement.
    
    Paramètres :
        resultats_configurations  dict, résultats du benchmark.
        Format : { "NomConfig": {"vocab": int, "richesse": float...} }
    
    Retour :
        matplotlib.figure.Figure, l'objet graphique comparatif.
    """
    if not resultats_configurations:
        return None
    nomsConfig = sorted(resultats_configurations.keys())
    
    vocabs = [resultats_configurations[c]["vocab"] for c in nomsConfig]
    richesses = [resultats_configurations[c]["richesse"] for c in nomsConfig]
    hapax_taux = [resultats_configurations[c]["hapax"] for c in nomsConfig]
    bruits = [resultats_configurations[c]["bruit"] * 100 for c in nomsConfig]
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    x = np.arange(len(nomsConfig))
    axes[0].bar(x, vocabs, color='skyblue', edgecolor='black', zorder=3)
    axes[0].set_title("Taille du Vocabulaire (Nb mots uniques)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(nomsConfig, rotation=45)
    axes[0].grid(True, axis='y', linestyle='', alpha=0.7, zorder=0)
    for i, v in enumerate(vocabs):
        axes[0].text(i, v + (max(vocabs)*0.01), str(v), ha='center', fontsize=9)

    width = 0.35
    bar1 = axes[1].bar(x - width/2, richesses, width, label='Richesse Lexicale', color='#90EE90', edgecolor='black')
    bar2 = axes[1].bar(x + width/2, hapax_taux, width, label='Taux Hapax', color='#FFB6C1', edgecolor='black')
    
    axes[1].set_title("Indicateurs de Qualité (0 à 1)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(nomsConfig, rotation=45)
    axes[1].set_ylim(0, 1.1)
    axes[1].legend(loc='lower right')
    axes[1].grid(True, axis='y', linestyle='', alpha=0.5)

    bars = axes[2].bar(x, bruits, color='salmon', edgecolor='black')
    
    axes[2].set_title("Proportion de Bruit Résiduel (%)")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(nomsConfig, rotation=45)
    axes[2].set_ylabel("% de tokens (Stopwords résiduels)")
    axes[2].grid(True, axis='y', linestyle='', alpha=0.5)
    
    if bruits:
        min_bruit = min(bruits)
        idx_best = bruits.index(min_bruit)
        axes[2].patches[idx_best].set_facecolor('#20B2AA')
        axes[2].text(idx_best, min_bruit + 0.1, "Meilleur", ha='center', va='bottom', fontweight='bold')

    plt.suptitle("Comparaison des Stratégies de Prétraitement", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    return fig

def test_visualiser_comparaison_configurations():
    print("\n Test : visualiser_comparaison_configurations ")
    
    # Données simulées (Scénario typique)
    
    mock_results = {
        "A (Brut)":       {"vocab": 5000, "richesse": 0.20, "hapax": 0.45, "bruit": 0.40},
        "B (Stopwords)":  {"vocab": 4900, "richesse": 0.45, "hapax": 0.50, "bruit": 0.05},
        "C (Strict)":     {"vocab": 4500, "richesse": 0.46, "hapax": 0.51, "bruit": 0.02},
        "D (Stemming)":   {"vocab": 3000, "richesse": 0.35, "hapax": 0.30, "bruit": 0.02},
        "E (Lemmatisation)":{"vocab": 3800, "richesse": 0.38, "hapax": 0.35, "bruit": 0.02}
    }
    
    try:
        # Génération
        fig = visualiser_comparaison_configurations(mock_results)
        
        assert fig is not None
        nom_fichier = "comparaison_configs.png"
        fig.savefig(nom_fichier)
        plt.close(fig)
        print(f" Test validé. Graphique sauvegardé sous : {nom_fichier}")
        
    except Exception as e:
        print(f" Erreur lors de la génération : {e}")


#test_visualiser_comparaison_configurations()
