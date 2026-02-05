-- 1) Procédure stockée pour attribuer des candidats aux missions
-- Cette procédure assigne automatiquement des candidats aux missions en fonction de leurs fonctions souhaitées et de leurs diplômes.

CREATE OR REPLACE PROCEDURE Attribuer_Candidats_Missions IS
  CURSOR cur_missions IS
    SELECT m.Id_Mission, m.Id_Fonction
    FROM Mission m
    WHERE NOT EXISTS (
      SELECT 1 FROM Contacte c WHERE c.Id_Mission = m.Id_Mission
    );

  CURSOR cur_candidats(p_Id_Fonction INT) IS
    SELECT c.Id_Candidat
    FROM Candidat c
    JOIN Se_Sent_Capable ssc ON c.Id_Candidat = ssc.Id_Candidat
    WHERE ssc.Id_Fonction = p_Id_Fonction;

  v_Id_Mission   INT;
  v_Id_Fonction  INT;
  v_Id_Candidat  INT;
BEGIN
  OPEN cur_missions;
  LOOP
    FETCH cur_missions INTO v_Id_Mission, v_Id_Fonction;
    EXIT WHEN cur_missions%NOTFOUND;

    OPEN cur_candidats(v_Id_Fonction);
    FETCH cur_candidats INTO v_Id_Candidat;

    IF cur_candidats%FOUND THEN
      INSERT INTO Contacte (Id_Candidat, Id_Mission, Date_Contacte)
      VALUES (v_Id_Candidat, v_Id_Mission, SYSDATE);
    END IF;

    CLOSE cur_candidats;
  END LOOP;
  CLOSE cur_missions;

EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE_APPLICATION_ERROR(-20001, 'Erreur lors de l''attribution des candidats aux missions : ' || SQLERRM);
END;
/

-- 2) Trigger pour mettre à jour le statut 'Cliente' d'une entreprise
-- Ce trigger met à jour le statut 'Cliente' d'une entreprise à '1' lorsqu'elle propose sa première mission.

CREATE OR REPLACE TRIGGER trg_Update_Cliente_Status
AFTER INSERT ON Mission
FOR EACH ROW
DECLARE
BEGIN
  MERGE INTO Entreprise e
  USING (SELECT :NEW.Id_Entreprise AS Id_Entreprise FROM dual) src
  ON (e.Id_Entreprise = src.Id_Entreprise)
  WHEN MATCHED THEN
    UPDATE SET e.Cliente = 1;
END;
/

-- 3) Package pour la gestion des candidats
-- Ce package contient des procédures pour ajouter, supprimer et lister des candidats.

CREATE OR REPLACE PACKAGE pkg_Gestion_Candidats IS
  TYPE t_IdList IS TABLE OF INT INDEX BY PLS_INTEGER;

  PROCEDURE Ajouter_Candidat(p_Id_Personne INT, p_Salarie NUMBER, p_Experience NUMBER, p_Situation VARCHAR2);
  PROCEDURE Supprimer_Candidat(p_Id_Candidat INT);
  PROCEDURE Lister_Candidats(p_Situation VARCHAR2);
END pkg_Gestion_Candidats;
/

CREATE OR REPLACE PACKAGE BODY pkg_Gestion_Candidats IS

  PROCEDURE Ajouter_Candidat(p_Id_Personne INT, p_Salarie NUMBER, p_Experience NUMBER, p_Situation VARCHAR2) IS
    v_Id_Candidat INT;
  BEGIN
    SELECT NVL(MAX(Id_Candidat), 0) + 1 INTO v_Id_Candidat FROM Candidat;
    INSERT INTO Candidat (Id_Candidat, Salarie, Experience, Situation_Professionnelle, Id_Personne)
    VALUES (v_Id_Candidat, p_Salarie, p_Experience, p_Situation, p_Id_Personne);
    COMMIT;
  EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
      RAISE_APPLICATION_ERROR(-20002, 'Le candidat existe déjà.');
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20003, 'Erreur lors de l''ajout du candidat : ' || SQLERRM);
  END;

  PROCEDURE Supprimer_Candidat(p_Id_Candidat INT) IS
    v_Count INT;
  BEGIN
    SELECT COUNT(*) INTO v_Count FROM Contacte WHERE Id_Candidat = p_Id_Candidat;
    IF v_Count > 0 THEN
      RAISE_APPLICATION_ERROR(-20004, 'Impossible de supprimer un candidat contacté pour une mission.');
    END IF;
    DELETE FROM Candidat WHERE Id_Candidat = p_Id_Candidat;
    COMMIT;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20005, 'Erreur lors de la suppression du candidat : ' || SQLERRM);
  END;

  PROCEDURE Lister_Candidats(p_Situation VARCHAR2) IS
    v_IdList t_IdList;
    idx PLS_INTEGER := 0;
  BEGIN
    FOR rec IN (SELECT Id_Candidat FROM Candidat WHERE Situation_Professionnelle = p_Situation) LOOP
      idx := idx + 1;
      v_IdList(idx) := rec.Id_Candidat;
    END LOOP;
    FOR i IN 1..v_IdList.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('Candidat ID: ' || v_IdList(i));
    END LOOP;
  END;

END pkg_Gestion_Candidats;
/

-- 4) Procédure pour mettre à jour les informations des candidats à partir des étudiants
-- Cette procédure convertit les étudiants diplômés en candidats en insérant ou mettant à jour leurs informations.

CREATE OR REPLACE PROCEDURE Maj_Candidats_Depuis_Etudiants IS
  CURSOR cur_etudiants IS
    SELECT e.Id_Etudiant, p.Id_Personne, e.Moyenne, e.Appreciation
    FROM Etudiant e
    JOIN Personne p ON e.Id_Personne = p.Id_Personne
    WHERE e.Moyenne >= 10; -- Supposons que 10 est la note minimale pour l'obtention du diplôme

BEGIN
  FOR rec IN cur_etudiants LOOP
    MERGE INTO Candidat c
    USING (SELECT rec.Id_Personne AS Id_Personne FROM dual) src
    ON (c.Id_Personne = src.Id_Personne)
    WHEN MATCHED THEN
      UPDATE SET c.Experience = 0, c.Situation_Professionnelle = 'Nouveau diplômé'
    WHEN NOT MATCHED THEN
      INSERT (Id_Candidat, Salarie, Experience, Situation_Professionnelle, Id_Personne)
      VALUES ((SELECT NVL(MAX(Id_Candidat), 0) + 1 FROM Candidat), 0, 0, 'Nouveau diplômé', rec.Id_Personne);
  END LOOP;
  COMMIT;
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE_APPLICATION_ERROR(-20006, 'Erreur lors de la mise à jour des candidats depuis les étudiants : ' || SQLERRM);
END;
/


-- 5) Trigger pour empêcher la suppression d'un candidat affecté à une mission
-- Ce trigger empêche la suppression d'un candidat s'il est actuellement contacté pour une mission.

CREATE OR REPLACE TRIGGER trg_Prevent_Candidat_Deletion
BEFORE DELETE ON Candidat
FOR EACH ROW
DECLARE
  v_Count INT;
BEGIN
  SELECT COUNT(*) INTO v_Count FROM Contacte WHERE Id_Candidat = :OLD.Id_Candidat;
  IF v_Count > 0 THEN
    RAISE_APPLICATION_ERROR(-20007, 'Impossible de supprimer un candidat assigné à une mission.');
  END IF;
END;
/

