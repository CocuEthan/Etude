CREATE OR REPLACE PROCEDURE prc_estimer_donnees_manquantes (
    p_age          IN NUMBER,
    p_gender       IN VARCHAR2,
    p_weight       IN NUMBER,
    p_height       IN NUMBER,
    -- Ces paramètres sont en IN OUT car on veut pouvoir les modifier s'ils sont vides
    p_sugar        IN OUT NUMBER,
    p_sodium       IN OUT NUMBER,
    p_cholesterol  IN OUT NUMBER,
    p_proteins     IN OUT NUMBER,
    p_resting_bpm  IN OUT NUMBER,
    p_workout_freq IN OUT NUMBER
)
IS
    l_bmi NUMBER;
BEGIN
    -- 1. Calcul IMC 
    IF p_weight IS NOT NULL AND p_height IS NOT NULL AND p_height > 0 THEN
        l_bmi := p_weight / (p_height * p_height);
    END IF;

    -- 2. Recherche des profils similaires
    FOR r IN (
        SELECT 
            AVG(SUGAR_G) as avg_sugar,
            AVG(SODIUM_MG) as avg_sodium,
            AVG(CHOLESTEROL_MG) as avg_chol,
            AVG(PROTEINS) as avg_prot,
            AVG(RESTING_BPM) as avg_bpm,
            AVG(WORKOUT_FREQUENCY__DAYS_WEEK_) as avg_freq
        FROM "FINAL_DATA"
        WHERE (p_gender IS NULL OR GENDER = p_gender)
          AND (p_age IS NULL OR AGE BETWEEN p_age - 5 AND p_age + 5)
          AND (l_bmi IS NULL OR BMI BETWEEN l_bmi - 2 AND l_bmi + 2)
    ) LOOP
        -- 3. Remplissage des vides 
        IF p_sugar IS NULL THEN p_sugar := ROUND(r.avg_sugar, 1); END IF;
        IF p_sodium IS NULL THEN p_sodium := ROUND(r.avg_sodium, 0); END IF;
        IF p_cholesterol IS NULL THEN p_cholesterol := ROUND(r.avg_chol, 0); END IF;
        IF p_proteins IS NULL THEN p_proteins := ROUND(r.avg_prot, 1); END IF;
        IF p_resting_bpm IS NULL THEN p_resting_bpm := ROUND(r.avg_bpm, 0); END IF;
        IF p_workout_freq IS NULL THEN p_workout_freq := ROUND(r.avg_freq, 0); END IF;
    END LOOP;
    
    -- 4. Sécurité
    IF p_resting_bpm IS NULL THEN 
       SELECT ROUND(AVG(RESTING_BPM),0) INTO p_resting_bpm FROM "FINAL_DATA"; 
    END IF;

END;
/