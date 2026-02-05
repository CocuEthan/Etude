-- 1. Vue pour la liste des Régimes
CREATE OR REPLACE VIEW v_lov_diet_type AS
SELECT DISTINCT DIET_TYPE as d, DIET_TYPE as r 
FROM "FINAL_DATA" 
ORDER BY 1;

-- 2. Vue pour la liste des Intensités
CREATE OR REPLACE VIEW v_lov_intensity AS
SELECT DISTINCT DIFFICULTY_LEVEL as d, DIFFICULTY_LEVEL as r 
FROM "FINAL_DATA" 
ORDER BY 1;

-- 3. Vue Principale pour le Tableau de Bord
CREATE OR REPLACE VIEW v_dashboard_nutrition AS
SELECT
    ROUND(AVG(PROTEINS), 1)  as proteines,
    ROUND(AVG(CARBS), 1)     as glucides,
    ROUND(AVG(FATS), 1)      as lipides,
    ROUND(AVG(SUGAR_G), 1)   as sucre,
    ROUND(AVG(SODIUM_MG), 0) as sodium,
    COUNT(*)                 as nombre_profils
FROM FINAL_DATA
WHERE 
    -- Filtre Régime
    (v('P8_DIET_TYPE') IS NULL OR DIET_TYPE = v('P8_DIET_TYPE'))
    
    -- Filtre Intensité
    AND (v('P8_INTENSITY') IS NULL OR DIFFICULTY_LEVEL = v('P8_INTENSITY'))

    -- Filtre Poids
    AND (v('P8_WEIGHT') IS NULL OR WEIGHT__KG_ BETWEEN TO_NUMBER(v('P8_WEIGHT')) - 2.5 
                                                 AND TO_NUMBER(v('P8_WEIGHT')) + 2.5)

    -- Filtre Taille 
    AND (v('P8_HEIGHT') IS NULL OR HEIGHT__M_ BETWEEN TO_NUMBER(v('P8_HEIGHT')) - 0.05 
                                                AND TO_NUMBER(v('P8_HEIGHT')) + 0.05)
                                                
    -- Filtre Fréquence Sport
    AND (v('P8_SPORT_FREQ') IS NULL OR WORKOUT_FREQUENCY__DAYS_WEEK_ BETWEEN TO_NUMBER(v('P8_SPORT_FREQ')) - 1 
                                                                       AND TO_NUMBER(v('P8_SPORT_FREQ')) + 1);