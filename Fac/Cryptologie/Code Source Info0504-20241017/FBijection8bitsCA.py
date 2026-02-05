# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import random
import arithmetiqueDansZ

class FBijection8bitsCA(object):
    "Une classe abstraite de bijection de [0..255]"
    def __init__(self ):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __call__(self,octet):
        """Renvoie l'image (int) de octet (int ou ElementZnZ) par la bijection"""
        raise NotImplementedError

    def valInv(self,octetC):
        "Renvoie l'antécédent de octetC"
        raise NotImplementedError

    def construitGraphique(self):
        "f est une fonction bijective de [0..255]"
        lm=[m for m in range(256)]
        lc=[self(m) for m in lm]
        plt.plot(lm,lc,".")
        plt.title(f"{self}")

    def construitGraphiqueDifferentielle(self,df=lambda x:(x+1)%256):
        "df est une fonction bijective appliquant une légère différence de [0..255]"
        lm=[m for m in range(256)]
        lc=[self(m)^self(df(m)) for m in lm]
        plt.plot(lm,lc,".")
        plt.title(f"Différences")


    def afficheGraphiquesDeDiffusionConfusion(self):
        x=random.randint(0,255)
        f=self
        print(f"Tests de valeurs et Affichage des graphiques de la bijection {f=} : ")
        print(f"    Test Inverse de {f=} : f({x})=={f(x)}, f.valInv({f(x)})=={f.valInv(f(x))} : {f.valInv(f(x))==x}")

        lx=[x for x in range(256)]
        ly=[self(x) for x in lx]
        ldfy=[self(x)^self((x+1)%256) for x in lx] #  Xor avec la valeur suivante
        # Sous-graphiques
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

        # Premier sous-graphique
        axes[0].plot(lx, ly,".b")
        axes[0].set_title("Valeurs")
        axes[0].set_xlabel("X")
        axes[0].set_ylabel("f(X)")

        # Second sous-graphique
        axes[1].plot(lx, ldfy,".g")
        axes[1].set_title(f"Différences avec la valeur suivante")
        axes[1].set_xlabel("X")
        axes[1].set_ylabel("f'(X)")

        # Titre global
        plt.suptitle(f"Graphique de la bijection{self}")

        # Affichage du graphique
        plt.show()


#Pas de main pour cette classe abstraite
#insérer un appel à afficheGraphiquesDeDiffusionConfusion dans le main des classes dérivées