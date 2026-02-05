class FBijAvecMasque(FBijection8bitsCA):
    def __init__(self, masque):
        self.masque = masque

    def __repr__(self):
        return f"FBijAvecMasque(masque={hex(self.masque)})"

    def __call__(self, octet):
        return octet ^ self.masque

    def valInv(self, octetC):
        return octetC ^ self.masque
