# -*- coding: utf-8 -*-
from FBijection8bitsCA import FBijection8bitsCA
class FBijection8bitsExemple(FBijection8bitsCA):
    "Un exemple de bijection de [0..255]"
    def __init__(self,n=1 ):
        self.n=n

    def __repr__(self):
        return f"FBijection8bitsExemple({self.n})"
    def __str__(self):
        return f"FBijection8bitsExemple{self.n}"

    def __call__(self,octet):
        """Renvoie l'image (int) de octet (int ou ElementZnZ) par la bijection"""
        return octet >> self.n | ((octet<<(8-self.n))&0xff)

    def valInv(self,octetC):
        "Renvoie l'antécédent de octetC"
        return octetC>>(8-self.n) | ((octetC<<self.n)&0xff)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    f=FBijection8bitsExemple()
    for b in [0,1,15,16,17,127,128,255]:
        print(f"{f}({b:08b})={f(b):08b} et Inverse({f(b):08b})={f.valInv(f(b)):08b}")
        print(f"{f}({b})={f(b)} et Inverse({f(b)})={f.valInv(f(b))}")

    f.afficheGraphiquesDeDiffusionConfusion()