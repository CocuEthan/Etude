
#Calcul de l’image (ou antécédent) d’un mot par le DES
class FBij64BitsDES(object):
    def __init__(self ,cle,verbose=False):
        self.cle = cle
        self.verbose = verbose
        self.souscle = liste16Cles(intToListBits(cle, 64), verbose)

    def __repr__(self):
        return f"FBij64BitsDES(cle=0x{self.cle:x})"

    def __call__(self,mot64bits):
        """
        >>> hex(FBij64BitsDES(0x0e329232ea6d0d73)(0x8787878787878787))
        '0x0'
        >>> hex(FBij64BitsDES(0x123556789ABDDEF0)(0x0123456789ABCDEF))
        '0x85e813540f0ab405'
        """
        lbits = intToListBits(mot64bits, 64)
        lbits = lbImage(lbits, tPI)
        g, d = lbits[:32], lbits[32:]
        for i in range(1, 17):
            sousCle = self.souscle[i]
            id = lbImage(d, tEBox)
            kxorid = [e ^ k for e, k in zip(id, sousCle)]
            sorti = []
            for j in range(8):
                bloc6 = kxorid[j * 6:(j + 1) * 6]
                ligne = (bloc6[0] << 1) | bloc6[5]
                colonne = (bloc6[1] << 3) | (bloc6[2] << 2) | (bloc6[3] << 1) | bloc6[4]
                sorti += intToListBits(SBOX[j][ligne][colonne], 4)
            sortiImage = lbImage(sorti, tP)
            g, d = d, [g ^ p for g, p in zip(g, sortiImage)]
        lbits = d + g
        return listBitsToInt(lbImage(lbits, tPIm1))


    def valInv(self,mot64bitsChiffre):
        """
        >>> hex(FBij64BitsDES(0x0e329232ea6d0d73).valInv(0x0000000000000000))
        '0x8787878787878787'
        >>> hex(FBij64BitsDES(0x123556789ABDDEF0).valInv(0x85e813540f0ab405))
        '0x0123456789abcdef'
        """
        lbits = intToListBits(mot64bitsChiffre, 64)
        lbits = lbImage(lbits, tPIm1)
        g, d = lbits[:32], lbits[32:]
        for i in range(16, 0, -1):
            sousCle = self.souscle
            id = lbImage(d,tEBox)
            kxorid = [e ^ k for e, k in zip(id,sousCle)]
            sorti = []
            for j in range(8):
                bloc6 = kxorid[j * 6:(j+1)*6]
                ligne = bloc6[0]<< 1| bloc6[5]
                colonne = (bloc6[1] << 3) | (bloc6[2] << 2) | (bloc6[3] << 1) | bloc6[4]
                sorti += intToListBits(SBOX[j][ligne][colonne], 4)
            sortiImage = lbImage(sorti, tP)
            g, d = d,[g^ p for g, p in zip(g, sortiImage)]
        lbits = d+g
        return listBitsToInt(lbImage(lbits, tPI))
