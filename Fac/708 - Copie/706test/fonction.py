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

test_statistiques_corpus()

def afficher_rapport(corpus):
    stats = statistiques_corpus(corpus)
    print(f"RAPPORT")
    print(f"Moyenne globale : {stats['moyenne']}")


from unittest.mock import patch
import io

class TestInterfaceUtilisateur(unittest.TestCase):
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_affichage_rapport(self, mock_stdout):
        """Teste si la fonction d'interface affiche le bon texte."""
        corpus = {"d1": [["mot1", "mot2"]]} 
        afficher_rapport(corpus)
        
        sortie = mock_stdout.getvalue()
        
        self.assertIn(" RAPPORT", sortie)
        self.assertIn("Moyenne globale : 2.0", sortie)


from behave import given, when, then

@given('un corpus contenant 2 documents')
def step_impl(context):
    context.corpus = {}

@given('le premier document a {n} tokens')
def step_impl(context, n):
    context.corpus["doc1"] = [["x"] * int(n)]

@given('le second document a {n} tokens')
def step_impl(context, n):
    context.corpus["doc2"] = [["x"] * int(n)]

@when("je lance l'analyse statistique")
def step_impl(context):
    context.resultat = statistiques_corpus(context.corpus)

@then('la moyenne des longueurs doit être {valeur}')
def step_impl(context, valeur):
    assert context.resultat["moyenne"] == float(valeur)

    