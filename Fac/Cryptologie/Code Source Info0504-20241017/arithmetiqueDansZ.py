#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
from random import *
from math import sqrt,log
from sympy import isprime,nextprime

def secondDiviseur(a):
    """Renvoie le premier diviseur de a supérieur à 1
    >>> secondDiviseur(15845465)
    5
    >>> secondDiviseur(1)==1 and secondDiviseur(2)==2 and secondDiviseur(6)==2
    True
    >>> secondDiviseur(153)==3 and secondDiviseur(157)==157 and secondDiviseur(13)==13
    True
    """
    if a==1: return 1
    if a%2==0: return 2
    ra=int(sqrt(a))+1
    d=3
    while d<=ra and a%d!=0:
        d+=2
    if d>ra:
        return a
    else :
        return d

def eDiviseurs(a):
    """renvoie l'ensemble des diviseurs positifs de A
    >>> eDiviseurs(60)=={1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 60, 30}
    True
    >>> eDiviseurs(1)==set({1}) and eDiviseurs(13)==set({1, 13})
    True
    """
    ed=set({1,a})
    d=secondDiviseur(a)
    if d!=a:
        ed.add(d)
        ed.add(a//d)
        for d2 in range(2,a//d):
            if a%d2==0:
                ed.add(d2)
    return ed


def lPGCD(a,b):
    """ Renvoie le couple : (liste des dividendes,le PGCD)

    >>> lPGCD(360,304)
    ([1, 5, 2], 8)
    >>> lPGCD(517,513)
    ([1, 128], 1)
    >>> lPGCD(513,517)
    ([0, 1, 128], 1)
    """
    lq=[]
    on_n_a_pas_fini=True
    while (on_n_a_pas_fini):
        q,r = a//b , a%b
        if r==0:
            on_n_a_pas_fini=False
        else:
            lq+=[q]
            a,b=b,r
    return lq,b
def PGCD(a,b):
    """
    >>> PGCD(360,304)
    8
    >>> PGCD(517,513)
    1
    >>> PGCD(513,517)
    1
    """
    l,d=lPGCD(a,b)
    return d
def sontPremiersEntreEux(a,b):
    """
    >>> sontPremiersEntreEux(10,21) and sontPremiersEntreEux(100,37) and not(sontPremiersEntreEux(4,2))
    True
    """
    return PGCD(a,b)==1
def solDiophant(a,b,c):
    """
    Renvoie x et y de Z tels que a.x+b.y=c
    sous la forme x=x0+k.a' et y=y0+k.b'

    >>> solDiophant(2,5,16) #x0,y0,a',b' et les sols sont x=-32+5.k et y=16-2.k
    (-32, 16, 5, -2)
    >>> x0,y0,cx,cy=solDiophant(13,4,12)
    >>> 13*(x0+1234*cx)+4*(y0+1234*cy)==12
    True
    """
    d=PGCD(PGCD(a,b),c)
    aa,bb,cc=a//d,b//d,c//d
    x0,y0,dd=bezout(aa,bb)# donc a(x-x0)=-b(y-y0)
    assert cc%dd==0," Pas de solutions à l'équation"
    ccc=cc//dd
    return  x0*ccc,y0*ccc,bb,-aa

def bezout(a,b):
    """Renvoie (u,v,d) tel que a.u+b.v=d avec d=PGCD(a,b)
    >>> bezout(360,304)
    (11, -13, 8)
    >>> bezout(1254,493)
    (-149, 379, 1)
    >>> bezout(513,517)
    (129, -128, 1)
    """
    lq,d=lPGCD(a,b)
    u,v=1,-lq[-1]
    for k in range(len(lq)-1):
        u,v=v,u-v*lq[-k-2]
    return u,v,d

def estPremier(n):
    """
    >>> estPremier(13) and estPremier(2) and not(estPremier(6))and not(estPremier(35))
    True
    """
    if n==1 : return False
    if n==2 or n==3: return True
    if n%2==0: return False
    if n<640000:
        d=3
        rn=int(sqrt(n)+1)
        while n%d!=0 and d<rn:
            d+=2
        return n%d!=0
    else:
        return isprime(n)

def nbPremierSuivant(n):
    """Renvoie le plus petit nombre premier strictement supérieur à n
    >>> nbPremierSuivant(1)==2 and nbPremierSuivant(3)==5 and nbPremierSuivant(20)==23
    True
    """
    p=n+1
    while not(estPremier(p)):
        p+=1
    return p
def nbPremierAleaParNbBits(nbBits=32):
    """
    >>> estPremier(nbPremierAleaParNbBits(10)) and nbPremierAleaParNbBits(10)>1024 and nbPremierAleaParNbBits(10)<2048
    True
    """
    n=2**nbBits+randint(2**(nbBits-1),2**nbBits)
    return nbPremierSuivant(n)
def nbPremierEtMoitieSuivant(n):
    """renvoie le couple q,p de nombres premiers avec q=(p-1)/2
    >>> nbPremierEtMoitieSuivant(100)
    (107, 53)
    """
    p=nbPremierSuivant(n)
    while not(estPremier((p-1)//2)):
        p=nbPremierSuivant(p+2)
    return p,(p-1)//2
def grandEntier(n):
    """Renvoie le produit de deux nombres premiers choisis au hasard dans [n..2N]"""
    return nbPremierSuivant(randint(n,2*n))*nbPremierSuivant(randint(n,2*n))


def strExp(p):
    """renvoie l'exposant tout beau
    >>> strExp(9)
    '⁹'
    >>> strExp(-19)
    '-¹⁹'
    >>> strExp(0)
    '⁰'
    >>> strExp(1)
    ''
    """
    SE="⁰¹²³⁴⁵⁶⁷⁸⁹" #Cela serait malin de créer plutôt un dictionnaire
    SP,SM="⁺","⁻"
    pt=p
    if pt==0:return "⁰"
    if pt==1:return ""
    if pt<0:
        return "-"+strExp(-p)
    else:
        ch=""
    while pt>0:
##        p10p=int(log(pt,10))
##        v10=10**p10p
##        ch+=SE[pt//v10]
##        pt=pt%v10
          ch,pt =SE[pt%10]+ch ,pt//10
    return ch

def chFacteursPremiers(n):
    """renvoie une chaine de caractère donnant la décomposition en facteurs premiers de n
    >>> chFacteursPremiers(120)
    '2³×3×5'
    >>> chFacteursPremiers(3600)
    '2⁴×3²×5²'
    >>> chFacteursPremiers(1)+chFacteursPremiers(2)
    '12'
    >>> chFacteursPremiers(21)
    '3×7'
    """
    l=lFacteursPremiers(n)
    ch=""
    for d,p in l:
        ch+=f"{d}{strExp(p)}×"
    return ch[:-1]

def lFacteursPremiers(n):
    """renvoie une liste donnant la décomposition en facteurs premiers de n
    >>> lFacteursPremiers(18)
    [(2, 1), (3, 2)]
    >>> lFacteursPremiers(13)
    [(13, 1)]
    """
    assert isinstance(n,int) and n>0
    if n==1 : return [(1,1)]

    n1=n
    l,d=[],0

    while n1>1:
        dp=secondDiviseur(n1)
        if dp!=d:
            l+=[(dp,1)]
            d=dp
        else:
            l=l[:-1]+[( dp , l[-1][1] +1) ] #On incrémente la puissance
        n1=n1//dp
    return l
def indicatriceEuler(n):
    """
    >>> indicatriceEuler(5)==4 and indicatriceEuler(15)==8 and indicatriceEuler(125)==100
    True
    """
    lfp=lFacteursPremiers(n)
    res=1
    for p,k in lfp:
        res*=(p-1)*p**(k-1)
    return res
def lDecompoPGCDetPPCM(a,b):
    """Renvoie ce couple de décomposition en facteurs premiers
    en utilisant la décomposition en facteurs premier de a et b
    >> lDecompoPGCDetPPCM(60,700)
    [(2, 2),(5, 1)], [(2, 2), (5, 2), (7, 1)]
    """
    pass

def est_inversible_modulo(a,modulo):
        """
        >>> est_inversible_modulo(3,5)
        True
        >>> est_inversible_modulo(10,12)
        False
        """
        return  sontPremiersEntreEux(a,modulo)
def inverse_modulo(a,modulo):
        """
        >>> inverse_modulo(3,5)
        2

        # inverse_modulo(2,10).inverse() doit renvoyer une erreur
        """
        u,v,d=bezout(a,modulo)
        assert d==1,f"{a} n'est pas inversible modulo {modulo}!"
        #a et n premiers entre eux
        return u % modulo    #a.u=1(n)

def puissance_modulo(a,p,modulo):
        """
        >>> puissance_modulo(3,3,10)
        7
        >>> puissance_modulo(3,1,10)
        3
        >>> puissance_modulo(3,0,10)
        1
        >>> puissance_modulo(3,-1,10)
        7
        >>> puissance_modulo(3,4,10)
        1
        """
        if p<0:
            assert est_inversible_modulo(a,modulo),f" {a} n'est pas inversible modulo {modulo} et donc ne peut avoir de puissance négative"
            return puissance_modulo( inverse_modulo(a,modulo) ,-p,modulo)
        elif p==1: return a
        elif  p==0: return 1
        else:
            pd2,pr2 = p//2,p%2 # p= 2* pd2 +pr2
            return (puissance_modulo( (a*a) % modulo, pd2 ,modulo) * puissance_modulo(a, pr2,modulo))%modulo

def estUnCarre(a,p):
    """
    cours 3 http://math.univ-lyon1.fr/~roblot/ens.html
    Pour p premier, Le groupe multiplicatif Fp est cyclique d’ordre p − 1 et donc a
    exactement (p − 1)/2 carres (p impair) : si g est un générateur alors g**i
    est un carrée si et seulement si i est pair.
    Pour tout a ∈ Fp×, on a a**(p−1) = 1 et donc a est un carré si et seulement si
    a**(p−1)/2 = 1 (sinon c’est −1).
    """
    if a==0 or a==1: return True
    assert estPremier(p)
    return LegendreJacobi(a,p)==1
def LegendreJacobi(a,p):
    """
    cours 3 http://math.univ-lyon1.fr/~roblot/ens.html
    >>> LegendreJacobi(9,17)
    1
    >>> LegendreJacobi(3,17)
    -1
    """
    v=puissance_modulo(a, (p-1)//2 , p)
    if v==1: return 1
    elif v==-1:return -1
    else: return 0

def ordre(k,p):
        """
        Voir http://www.repcrypta.com/telechargements/fichecrypto_107.pdf
        >>> ordre(2,7)
        3
        >>> ordre(-2,7)
        6
        """
        assert est_inversible_modulo(k,p)
        ld=sorted(eDiviseurs(k-1))
        for d in ld[1:-1]:
            if puissance_modulo(k,d,p)==1:
                return d
        return k-1

def elementPrimitif(k,p):
    """Renvoie le premier élément primitif (d'ordre n-1) de Z/nZ suivant self
    >>> elementPrimitif(2,17)
    3
    >>> elementPrimitif(2,17)
    3
    >>> elementPrimitif(15,17)
    3
    >>> elementPrimitif(1,65537)
    3
    """
    res=(k+1)%p
    while not(est_inversible_modulo(res,p)) or ordre(res,p)!= p-1:
        res=(res+1)%p
    return res

def racineCarree(x,p):
    """Renvoie le r tell que r²==x [p] avec  r <= p/2
    >>> racineCarree(65535,65537)
    (4112,65537)
    >>> racineCarree(9,17)
    3
    >>> racineCarree(13,17)
    8
    >>> racineCarree(0,17)
    0
    >>> racineCarree(5,19)
    9
    >>> racineCarree(10,13)
    6
    """
    assert estUnCarre(x,p)
    if x==0 or x==1: return x

    if p%4==3: r= (x**((p+1)//4))%p
    elif p%8== 5:
        s=(x**((p-1)//4))%p
        if s==1:
            r= (x**((p+3)//8))%p
        else:
            r=  puissance_modulo( (2*x)*(4*x), (p-5)//8, p)#car 2**((p−1)/2= ≡ −1 (mod p)
    else:
        a,g = x , elementPrimitif(x,p)
        e1,e2=(p-1)//2,0  #a**e1.g**e2=1
        while e1%2==0:
            if (puissance_modulo(a, e1//2, p)  *   puissance_modulo(g,e2//2,p))%p==1:
                e1,e2=e1//2,e2//2
            else:
                e1,e2=e1//2, (e2+p-1)//2
        #e1=2e1p+1 est impair et e2=2e2p pair donc
        e1p,e2p=(e1-1)//2,e2//2
        r= (puissance_modulo(a,e1p+1,p)*puissance_modulo(g,e2p,p) )%p
    if r>p//2: r=(-r)%p
    return r


if __name__ == "__main__":
    x=racineCarree(16,17)
    x=racineCarree(13,17)
    import doctest
    doctest.testmod()

    a,b,n=7,255,256
    print(f"{a}*{b}=={a*b} [{n}]")
    print("calcul de puissance en modulo")
    print(f"{a}**{b}=={puissance_modulo(a,b,n)} [{n}]")
    print("calcul d'inverse en modulo")
    inva=inverse_modulo(a,n)
    print(f"{a}*{inva}=={ (a*inva)%n } [{n}]")

    a,b,n=7,255,2**256
    print(f"{a}*{b}=={a*b} [{n}]")
    print("calcul de puissance en modulo")
    print(f"{a}**{b}=={puissance_modulo(a,b,n)} [{n}]")
    print("calcul d'inverse en modulo")
    inva=inverse_modulo(a,n)
    print(f"{a}*{inva}=={ (a*inva)%n } [{n}]")

    n,p=4,11
    print(f"{n=} est un carré modulo {p} : {estUnCarre(n,p)}")
    print(f" et sa racine carré modulo {p} est {racineCarree(n,p)=}")