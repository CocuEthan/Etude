import matplotlib.pyplot as plt
def lFrequences(m):
    """Renvoie la liste des fréquences de chaque valeur du message m
    Une fréquence est un nombre entre 0 et 1 et correspond à un pourcentage : 0.25=25%
    >>> lFrequences(Message([1,2,3,3,3,3,4,8,8,128]))[3]
    0.4"""
    total = len(m)
    freq_dict = {}

    for value in m:
        freq_dict[value] = freq_dict.get(value, 0) + 1
        frequences = {k: value / total for k, value in freq_dict.items()}

    return frequences


def afficheTableauDesFrequences(m):
    frequencies = Frequence.lFrequences(m)

    print("Valeur \t Pourcentage Fréquence \t Histogramme")
    for k, value in frequencies.items():
        histogram = int(value * 10)
        print(f"{k} {value:.2%} {value:.1f} {'*' * histogram}")


def afficheTableauDesFrequencesDecroissantes(m):
    frequencies = Frequence.lFrequences(m)

    sorted_frequencies = sorted(frequencies.items(), k=lambda x: x[1], reverse=True)

    print("Valeur Pourcentage Fréquence Histogramme")
    for k, value in sorted_frequencies:
        histogram = int(value * 10)
        print(f"{k} {value:.2%} {value:.1f} {'*' * histogram}")

def afficheHistogrammeDesFrequences(m, titre="Histogramme des fréquences", nbValMax=20):
    lf = lFrequences(m)
    mTries = sorted(range(256), key=lambda b: lf.get(b, 0), reverse=True)
    mTriesNonNuls = [b for b in mTries if lf.get(b, 0) > 0]
    lEtiquettes = [f"{b:02x}:{chr(b)}" for b in mTriesNonNuls]
    lVal = [lf.get(b, 0) for b in mTriesNonNuls]
    plt.bar(lEtiquettes[:nbValMax], lVal[:nbValMax])
    plt.title(titre)
    plt.show()
