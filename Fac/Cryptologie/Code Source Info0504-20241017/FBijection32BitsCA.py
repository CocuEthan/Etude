# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import random
from arithmetiqueDansZ import ElementDeZnZ

class FBijection32BitsCA(object):
    "Une classe abstraite de bijection sur des mots de 32bits"
    def __init__(self ):
        raise NotImplementedError
    def __repr__(self):
        raise NotImplementedError
    def __call__(self,octet):
        """Renvoie l'image du mot de 32bits par la bijection"""
        raise NotImplementedError
    def valInv(self,octetC):
        """Renvoie l'antécédent du mot de 32bits par la bijection"""
        raise NotImplementedError

class FAffine32bits(FBijection32BitsCA):
    "Une bijection beaucoup trop facilement inversible à la lecture de ses seules valeurs"
    ##2**32=4294967296 ~~ 4.3E9
    def __init__(self,a=1234567891,b=7 ):
        self.a,self.b=ElementDeZnZ(a,4294967296),ElementDeZnZ(b,4294967296)
        assert self.a.estInversible(),"{a} doit être inversible dans Z/4294967296Z"
        self.inverseDea=self.a.inverse()
    def __repr__(self):
        return f"FAffine32bits(a={self.a},b={self.b})"
    def __call__(self,x):
        return int(x*self.a+self.b)
    def valInv(self,y):
        """Renvoie l'antécédent de y"""
        assert self.a.estInversible(),"{self.a=} doit être inversible"
        return int((y-self.b)*self.inverseDea)

class FRotationDroite32bits(FBijection32BitsCA):
     "Une Bijection trop simple"
     def __init__(self,nbBitsR=1 ):
         self.nbBitsR=nbBitsR
     def __repr__(self):
         return f"FRotationDroite32bits({self.nbBitsR})"
     def __call__(self,mot32bits):
        """
        >> bin(FRotationDroite32bits(2)(0b1000000000000000000000000001110)
        '0b1010000000000000000000000000011'
        """
        xg= (mot32bits << (32-self.nbBitsR)) & 0xffffffff
        xd = (mot32bits >> self.nbBitsR)
        y=  xg |xd
        return y
     def valInv(self,mot32bits):
        """
        >>> hex(FRotationDroite32bits(4).valInv(0x12345678))
        '0x23456781'
        """
        n=2
        xg = (mot32bits << self.nbBitsR)& 0xffffffff
        xd= mot32bits >> (32-self.nbBitsR)
        y=  xg |xd

        return y

class FMasque32bits(FBijection32BitsCA):
     "Une Bijection trop simple"
     def __init__(self,masque32bits=0b10101010101010101010101010101010 ):
         self.masque32bits=masque32bits
     def __repr__(self):
         return f"FMasque(masque32bits={self.masque32bits})"
     def __call__(self,mot32bits):
         return mot32bits^self.masque32bits
     def valInv(self,mot32bits):
         return mot32bits^self.masque32bits

class FPermutation32Bits(FBijection32BitsCA):
    "Une Bijection triviale"
    def __init__(self,lp=[2,4,1,3,6,5,0,7,10,12,9,11,14,13,8,15,18,20,17,19,22,21,16,23,26,28,25,27,24,29,31,30]):
        "Fonction bijective sur [0..255] permutant les bits"
        "par exemple le bit 0 de l'image sera la valeur du bit 2 du résultat"
        assert len(lp)==32
        self.lp=lp
        self.lpinv=[-1]*32
        for k,val in enumerate(self.lp):
            self.lpinv[val]=k
        assert not((-1) in self.lpinv),"Toutes les valeurs ne sont pas prises. {lp}ne représente pas une permutation."
    def __repr__(self):
        return f"FPermutation32Bits(lp={repr(self.lp)})"
    def __call__(self,mot32bits):
        """
        renvoie l'image de octet
        >>> bin(FPermutation32Bits()(0b00000010000000000000000000000001))
        '0b10000000000000000000000000000010'
        """
        x,lbx = int(mot32bits) , [-1]*32
        sx=bin(x)[2:];sx="0"*(32-len(sx))+sx #'00000000000000000000000000000010'

        ly=["."]*32
        for k in range(32):
            ly[self.lp[k]]=sx[k]

        return int("0b"+"".join((ly)),2)

    def valInv(self,mot32bits):
        """
        renvoie l'image de octet
        >>> bin(FPermutation32Bits().valInv(0b10000000000000000000000000000010))
        '0b10000000000000000000000001'
        """
        x,lbx = int(mot32bits) , [-1]*32
        sx=bin(x)[2:];sx="0"*(32-len(sx))+sx #'00000000000000000000000000000010'
        ly=["."]*32
        for k in range(32):
            ly[self.lpinv[k]]=sx[k]
        return int("0b"+"".join((ly)),2)

def demo():
    x=0x12345678
    for f in [FAffine32bits(),
              FMasque32bits(),
              FPermutation32Bits(),
              ]:
        y=f(x)
        z=f.valInv(y)
        print(f"L'image de {x=:02x} est {y=:02x}")
        print(f"  et l'antécédent {z=:02x} est bien égal à {x=:02x} ? : {z==x}")
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    f=FRotationDroite32bits(2)
    x=0b10110111011110111110111111011111
    y=f(x)
    xx=f.valInv(y)
    print(f"  f({x:032b})={y:032b} avec {f=}")
    print(f"f-1({y:032b})={xx:032b} test ok ? {x==xx}")
    demo()