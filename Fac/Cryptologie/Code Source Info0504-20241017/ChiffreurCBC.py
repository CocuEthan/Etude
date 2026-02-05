class ChiffreurCBC:
    def __init__(self, bijection, iv):
        """
        bijection : instance de FBijFeistel ou autre bijection
        iv : vecteur d'initialisation (entier entre 0 et 255)
        """
        self.bijection = bijection
        self.iv = iv % 256

    def __repr__(self):
        return f"ChiffreurCBC(bijection={self.bijection}, iv={self.iv})"

    def chiffrer(self, message):
        """
        message : une liste d'octets (entiers entre 0 et 255)
        Retourne le message chiffré en appliquant la bijection avec mode CBC.
        """
        message_chiffre = []
        bloc_precedent = self.iv
        for octet in message:
            bloc = octet ^ bloc_precedent
            bloc_chiffre = self.bijection(bloc)
            message_chiffre.append(bloc_chiffre)
            bloc_precedent = bloc_chiffre
        return message_chiffre

    def dechiffrer(self, message_chiffre):
        """
        message_chiffre : une liste d'octets chiffrés
        Retourne le message déchiffré en appliquant la bijection inverse avec mode CBC.
        """
        message = []
        bloc_precedent = self.iv
        for bloc_chiffre in message_chiffre:
            bloc = self.bijection.valInv(bloc_chiffre)  # Appliquer l'inverse de la bijection
            octet = bloc ^ bloc_precedent  # XOR avec le bloc précédent
            message.append(octet)
            bloc_precedent = bloc_chiffre
        return message
