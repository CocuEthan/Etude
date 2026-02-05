class ChiffreurECB:
    def __init__(self, bijection):
        """
        bijection : instance de FBijFeistel ou autre bijection
        """
        self.bijection = bijection

    def __repr__(self):
        return f"ChiffreurECB(bijection={self.bijection})"

    def chiffrer(self, message):
        """
        message : une liste d'octets (entiers entre 0 et 255)
        Retourne le message chiffré en appliquant la bijection à chaque octet.
        """
        return [self.bijection(octet) for octet in message]

    def dechiffrer(self, message_chiffre):
        """
        message_chiffre : une liste d'octets chiffrés
        Retourne le message déchiffré en appliquant l'inverse de la bijection à chaque octet.
        """
        return [self.bijection.valInv(octet) for octet in message_chiffre]
