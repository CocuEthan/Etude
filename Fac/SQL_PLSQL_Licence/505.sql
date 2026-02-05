-- Insertions pour la table Diplome
INSERT INTO Diplome VALUES (1, 'Informatique', 'Bachelor');
INSERT INTO Diplome VALUES (2, 'Management', 'Master');
INSERT INTO Diplome VALUES (3, 'Droit', 'Licence');
INSERT INTO Diplome VALUES (4, 'Marketing', 'Bachelor');
INSERT INTO Diplome VALUES (5, 'Finance', 'Master');

-- Insertions pour la table Entreprise
INSERT INTO Entreprise VALUES (1, 'TechCorp', 'Développement logiciel', 1, 5);
INSERT INTO Entreprise VALUES (2, 'FinServe', 'Services financiers', 1, 3);
INSERT INTO Entreprise VALUES (3, 'EduWorld', 'Éducation', 0, 1);
INSERT INTO Entreprise VALUES (4, 'HealthPlus', 'Santé', 1, 4);
INSERT INTO Entreprise VALUES (5, 'GreenEnergy', 'Énergies renouvelables', 1, 2);

-- Insertions pour la table Institut
INSERT INTO Institut VALUES (1, 'Université Paris', 'Université');
INSERT INTO Institut VALUES (2, 'HEC', 'École de commerce');
INSERT INTO Institut VALUES (3, 'Polytechnique', 'École d'ingénieur');
INSERT INTO Institut VALUES (4, 'Sciences Po', 'École de sciences politiques');
INSERT INTO Institut VALUES (5, 'CentraleSupélec', 'École d'ingénieur');

INSERT INTO Localisation VALUES (1, 'France', 'Paris', '10 Rue de Rivoli', '75001');
INSERT INTO Localisation VALUES (2, 'France', 'Paris', '20 Avenue des Champs-Élysées', '75008');
INSERT INTO Localisation VALUES (3, 'France', 'Paris', '30 Rue Saint-Honoré', '75001');
INSERT INTO Localisation VALUES (4, 'France', 'Paris', '40 Boulevard Haussmann', '75009');
INSERT INTO Localisation VALUES (5, 'France', 'Paris', '50 Rue de la Paix', '75002');
INSERT INTO Localisation VALUES (6, 'France', 'Lyon', '10 Rue de la République', '69002');
INSERT INTO Localisation VALUES (7, 'France', 'Lyon', '20 Rue Garibaldi', '69003');
INSERT INTO Localisation VALUES (8, 'France', 'Lyon', '30 Quai Saint-Antoine', '69002');
INSERT INTO Localisation VALUES (9, 'France', 'Lyon', '40 Rue Victor Hugo', '69002');
INSERT INTO Localisation VALUES (10, 'France', 'Lyon', '50 Avenue Jean Jaurès', '69007');
INSERT INTO Localisation VALUES (11, 'France', 'Marseille', '10 Boulevard Longchamp', '13001');
INSERT INTO Localisation VALUES (12, 'France', 'Marseille', '20 Avenue de la Canebière', '13001');
INSERT INTO Localisation VALUES (13, 'France', 'Marseille', '30 Rue de Rome', '13006');
INSERT INTO Localisation VALUES (14, 'France', 'Marseille', '40 Rue Paradis', '13008');
INSERT INTO Localisation VALUES (15, 'France', 'Marseille', '50 Rue Saint-Ferréol', '13001');
INSERT INTO Localisation VALUES (16, 'France', 'Toulouse', '10 Rue d'Alsace Lorraine', '31000');
INSERT INTO Localisation VALUES (17, 'France', 'Toulouse', '20 Rue de Metz', '31000');
INSERT INTO Localisation VALUES (18, 'France', 'Toulouse', '30 Allée Jean Jaurès', '31000');
INSERT INTO Localisation VALUES (19, 'France', 'Toulouse', '40 Rue Bayard', '31000');
INSERT INTO Localisation VALUES (20, 'France', 'Toulouse', '50 Rue Saint-Rome', '31000');
INSERT INTO Localisation VALUES (21, 'France', 'Nice', '10 Promenade des Anglais', '06000');
INSERT INTO Localisation VALUES (22, 'France', 'Nice', '20 Avenue Jean Médecin', '06000');
INSERT INTO Localisation VALUES (23, 'France', 'Nice', '30 Rue Masséna', '06000');
INSERT INTO Localisation VALUES (24, 'France', 'Nice', '40 Rue de France', '06000');
INSERT INTO Localisation VALUES (25, 'France', 'Nice', '50 Rue de la Liberté', '06000');

-- Insertions pour la table Fonction
INSERT INTO Fonction VALUES (1, 'Ingénieur logiciel');
INSERT INTO Fonction VALUES (2, 'Chef de projet');
INSERT INTO Fonction VALUES (3, 'Analyste financier');
INSERT INTO Fonction VALUES (4, 'Responsable marketing');
INSERT INTO Fonction VALUES (5, 'Architecte');
INSERT INTO Fonction VALUES (6, 'Dévelopeur web');
INSERT INTO Fonction VALUES (7, 'Ingénieur des réseaux');

-- Insertions pour la table Mission
INSERT INTO Mission VALUES (1, 50000, 'CDD', TO_DATE('2023-01-10', 'YYYY-MM-DD'), 'Développement d'une application mobile', '12 mois', 1, 1);
INSERT INTO Mission VALUES (2, 60000, 'CDD', TO_DATE('2023-02-15', 'YYYY-MM-DD'), 'Gestion de projet pour une nouvelle plateforme', '6 mois', 2, 2);
INSERT INTO Mission VALUES (3, 70000, 'CDI', TO_DATE('2023-03-01', 'YYYY-MM-DD'), 'Analyse financière', 'Indéfinie', 3, 3);
INSERT INTO Mission VALUES (4, 45000, 'CDD', TO_DATE('2023-04-20', 'YYYY-MM-DD'), 'Campagne de marketing digital', '8 mois', 4, 4);
INSERT INTO Mission VALUES (5, 80000, 'CDI', TO_DATE('2023-05-30', 'YYYY-MM-DD'), 'Construction de bâtiments écologiques', '24 mois', 5, 5);

-- Insertions pour la table Personne
INSERT INTO Personne VALUES (1, 'Dupont', 'Jean', '0102030405', 1, 'jean.dupont@mail.com', 'Célibataire', 30);
INSERT INTO Personne VALUES (2, 'Martin', 'Sophie', '0105060708', 0, 'sophie.martin@mail.com', 'Mariée', 28);
INSERT INTO Personne VALUES (3, 'Durand', 'Pierre', '0607080910', 1, 'pierre.durand@mail.com', 'Divorcé', 40);
INSERT INTO Personne VALUES (4, 'Moreau', 'Claire', '0203040506', 0, 'claire.moreau@mail.com', 'Célibataire', 35);
INSERT INTO Personne VALUES (5, 'Petit', 'Luc', '0708091011', 1, 'luc.petit@mail.com', 'Marié', 32);
INSERT INTO Personne VALUES (6, 'Rousseau', 'Julie', '0304050607', 1, 'julie.rousseau@mail.com', 'Célibataire', 25);
INSERT INTO Personne VALUES (7, 'Fournier', 'Nicolas', '0809101112', 0, 'nicolas.fournier@mail.com', 'Pacsé', 29);
INSERT INTO Personne VALUES (8, 'Garnier', 'Laura', '0405060708', 1, 'laura.garnier@mail.com', 'Divorcée', 33);
INSERT INTO Personne VALUES (9, 'Lambert', 'Alex', '0910111213', 0, 'alex.lambert@mail.com', 'Célibataire', 27);
INSERT INTO Personne VALUES (10, 'Lemoine', 'Anna', '0506070809', 1, 'anna.lemoine@mail.com', 'Mariée', 31);
INSERT INTO Personne VALUES (11, 'Legrand', 'Marie', '0101020304', 1, 'marie.legrand@mail.com', 'Célibataire', 24);
INSERT INTO Personne VALUES (12, 'Bernard', 'Paul', '0707070707', 0, 'paul.bernard@mail.com', 'Pacsé', 45);
INSERT INTO Personne VALUES (13, 'Schneider', 'Erik', '0606060606', 1, 'erik.schneider@mail.com', 'Divorcé', 50);
INSERT INTO Personne VALUES (14, 'Leroy', 'Alice', '0808080808', 0, 'alice.leroy@mail.com', 'Mariée', 29);
INSERT INTO Personne VALUES (15, 'Muller', 'Carla', '0505050505', 1, 'carla.muller@mail.com', 'Célibataire', 22);
INSERT INTO Personne VALUES (16, 'Renaud', 'Michel', '0202020202', 1, 'michel.renaud@mail.com', 'Veuf', 60);
INSERT INTO Personne VALUES (17, 'Delcroix', 'Hélène', '0404040404', 1, 'helene.delcroix@mail.com', 'Mariée', 38);
INSERT INTO Personne VALUES (18, 'Joly', 'Fabien', '0909090909', 1, 'fabien.joly@mail.com', 'Célibataire', 33);
INSERT INTO Personne VALUES (19, 'Noel', 'Estelle', '0303030303', 0, 'estelle.noel@mail.com', 'Divorcée', 42);
INSERT INTO Personne VALUES (20, 'Perrot', 'Vincent', '0209090706', 1, 'vincent.perrot@mail.com', 'Pacsé', 36);

-- Insertions pour la table Etudiant
INSERT INTO Etudiant VALUES (1, 15.2, 'Très bien', 1, 19);
INSERT INTO Etudiant VALUES (2, 12.5, 'Bien', 2, 18);
INSERT INTO Etudiant VALUES (3, 16.8, 'Excellent', 3, 17);
INSERT INTO Etudiant VALUES (4, 10.0, 'Passable', 1, 16);
INSERT INTO Etudiant VALUES (5, 13.7, 'Bien', 2, 20);

-- Insertions pour la table Candidat
INSERT INTO Candidat VALUES (1, 1, 5, 'Freelance', 1);
INSERT INTO Candidat VALUES (2, 0, 3, 'Sans emploi', 2);
INSERT INTO Candidat VALUES (3, 1, 8, 'Interimaire', 3);
INSERT INTO Candidat VALUES (4, 0, 1, 'Sans emploi', 4);
INSERT INTO Candidat VALUES (5, 1, 4, 'Embauche', 5);
INSERT INTO Candidat VALUES (6, 0, 2, 'Sans emploi', 6);
INSERT INTO Candidat VALUES (7, 1, 6, 'En poste', 7);
INSERT INTO Candidat VALUES (8, 1, 7, 'En poste', 8);
INSERT INTO Candidat VALUES (9, 0, 1, 'Sans emploi', 9);
INSERT INTO Candidat VALUES (10, 1, 3, 'En poste', 10);
INSERT INTO Candidat VALUES (11, 1, 5, 'Sans emploi', 11);
INSERT INTO Candidat VALUES (12, 0, 0, 'Nouvel entrant', 12);
INSERT INTO Candidat VALUES (13, 1, 9, 'En poste', 13);
INSERT INTO Candidat VALUES (14, 1, 15, 'En recherche active', 14);
INSERT INTO Candidat VALUES (15, 0, 2, 'Étudiant', 15);
INSERT INTO Candidat VALUES (16, 1, 7, 'Etudiant', 16);

-- Insertions pour la table Habite
INSERT INTO Habite VALUES (1, 1);
INSERT INTO Habite VALUES (1, 2);
INSERT INTO Habite VALUES (1, 3);
INSERT INTO Habite VALUES (3, 4);
INSERT INTO Habite VALUES (4, 5);
INSERT INTO Habite VALUES (5, 16);
INSERT INTO Habite VALUES (6, 17);
INSERT INTO Habite VALUES (7, 18);
INSERT INTO Habite VALUES (8, 19);
INSERT INTO Habite VALUES (9, 20);
INSERT INTO Habite VALUES (10, 6);
INSERT INTO Habite VALUES (11, 7);
INSERT INTO Habite VALUES (12, 8);
INSERT INTO Habite VALUES (13, 9);
INSERT INTO Habite VALUES (14, 10);
INSERT INTO Habite VALUES (15, 11);
INSERT INTO Habite VALUES (8, 12);
INSERT INTO Habite VALUES (7, 13);
INSERT INTO Habite VALUES (9, 14);
INSERT INTO Habite VALUES (15, 15);

-- Insertions pour la table A_recu
INSERT INTO A_recu VALUES (1, 1);
INSERT INTO A_recu VALUES (2, 2);
INSERT INTO A_recu VALUES (3, 3);
INSERT INTO A_recu VALUES (4, 4);
INSERT INTO A_recu VALUES (5, 5);

-- Insertions pour la table Se_Situe
INSERT INTO Se_Situe VALUES (1, 1);
INSERT INTO Se_Situe VALUES (2, 2);
INSERT INTO Se_Situe VALUES (3, 3);
INSERT INTO Se_Situe VALUES (4, 4);
INSERT INTO Se_Situe VALUES (5, 5);

-- Insertions pour la table Depend
INSERT INTO Depend VALUES (1, 1);
INSERT INTO Depend VALUES (2, 2);
INSERT INTO Depend VALUES (3, 3);
INSERT INTO Depend VALUES (4, 4);
INSERT INTO Depend VALUES (5, 5);

-- Insertions pour la table Se_Sent_Capable
INSERT INTO Se_Sent_Capable VALUES (1, 1, 1);
INSERT INTO Se_Sent_Capable VALUES (1, 2, 0);
INSERT INTO Se_Sent_Capable VALUES (2, 3, 1);
INSERT INTO Se_Sent_Capable VALUES (3, 4, 0);
INSERT INTO Se_Sent_Capable VALUES (4, 5, 1);

-- Insertions pour la table Contacte
INSERT INTO Contacte VALUES (1, 1, TO_DATE('2023-01-15', 'YYYY-MM-DD'));
INSERT INTO Contacte VALUES (2, 2, TO_DATE('2023-02-20', 'YYYY-MM-DD'));
INSERT INTO Contacte VALUES (3, 3, TO_DATE('2023-03-25', 'YYYY-MM-DD'));
INSERT INTO Contacte VALUES (4, 4, TO_DATE('2023-04-30', 'YYYY-MM-DD'));
INSERT INTO Contacte VALUES (5, 5, TO_DATE('2023-05-05', 'YYYY-MM-DD'));

-- Insertions pour la table Localise
INSERT INTO Localise VALUES (1, 1);
INSERT INTO Localise VALUES (2, 2);
INSERT INTO Localise VALUES (3, 3);
INSERT INTO Localise VALUES (4, 4);
INSERT INTO Localise VALUES (5, 5);
