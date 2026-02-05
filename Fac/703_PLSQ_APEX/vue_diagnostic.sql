CREATE OR REPLACE VIEW vue_diagnostic AS
WITH user_data AS (
    SELECT 
        TO_NUMBER(v('P9_WEIGHT')) as p_weight,
        TO_NUMBER(v('P9_HEIGHT')) as p_height,
        TO_NUMBER(v('P9_SUGAR'))  as p_sugar,
        TO_NUMBER(v('P9_SODIUM')) as p_sodium,
        TO_NUMBER(v('P9_CHOLESTEROL')) as p_chol,
        TO_NUMBER(v('P9_PROTEINS')) as p_prot,
        TO_NUMBER(v('P9_RESTING_BPM')) as p_bpm,
        TO_NUMBER(v('P9_WORKOUT_FREQ')) as p_freq
    FROM DUAL
)
SELECT 
    -- 1. ANALYSE OBÉSITÉ
    'Analyse Obésité (IMC)' as titre,
    CASE 
        WHEN p_weight / NULLIF(p_height * p_height, 0) >= 30 THEN 'Obésité'
        WHEN p_weight / NULLIF(p_height * p_height, 0) >= 25 THEN 'Surpoids'
        WHEN p_weight / NULLIF(p_height * p_height, 0) < 18.5 THEN 'Maigreur'
        ELSE 'Poids Santé'
    END as valeur,
    'fa fa-user' as icon,
    CASE 
        WHEN p_weight / NULLIF(p_height * p_height, 0) >= 25 THEN 'u-warning-text'
        ELSE 'u-success-text'
    END as css_class,
    1 as ordre
FROM user_data

UNION ALL

SELECT 
    -- 2. PRÉDICTION RISQUE DIABÈTE
    'Prédiction Risque Diabète',
    CASE 
        WHEN p_sugar > 70 THEN 'Risque Élevé'
        WHEN p_sugar > 50 THEN 'Risque Modéré'
        ELSE 'Risque Faible'
    END,
    'fa fa-cube',
    CASE 
        WHEN p_sugar > 50 THEN 'u-danger-text'
        ELSE 'u-success-text'
    END,
    2
FROM user_data

UNION ALL

SELECT 
    -- 3. PRÉDICTION SANTÉ CARDIAQUE
    'Santé Cardiaque',
    CASE 
        WHEN p_chol > 240 OR p_bpm > 90 THEN 'Attention Requise'
        WHEN p_chol > 200 OR p_bpm > 80 THEN 'À surveiller'
        ELSE 'Coeur Optimal'
    END,
    'fa fa-heartbeat',
    CASE 
        WHEN p_chol > 240 OR p_bpm > 90 THEN 'u-danger-text'
        WHEN p_chol > 200 OR p_bpm > 80 THEN 'u-warning-text'
        ELSE 'u-success-text'
    END,
    3
FROM user_data

UNION ALL

SELECT 
    -- 4. ANALYSE MUSCULAIRE
    'Analyse Musculaire',
    CASE 
        WHEN p_prot < (p_weight * 0.8) THEN 'Manque de Protéines'
        WHEN p_prot > (p_weight * 2.2) THEN 'Excès de Protéines'
        ELSE 'Apport Optimal'
    END,
    'fa fa-cutlery',
    CASE 
        WHEN p_prot < (p_weight * 0.8) THEN 'u-warning-text'
        ELSE 'u-success-text'
    END,
    4
FROM user_data

UNION ALL

SELECT 
    -- 5. ANALYSE HYDRATATION
    'Analyse Hydratation',
    CASE 
        WHEN p_sodium > 2300 OR p_freq > 5 THEN 'Besoin Hydratation Élevé'
        ELSE 'Hydratation Standard'
    END,
    'fa fa-tint',
    CASE WHEN p_sodium > 2300 OR p_freq > 5 THEN 'u-info-text' ELSE 'u-success-text' END,
    5
FROM user_data

UNION ALL

SELECT 
    -- 6. SCORE DE SANTÉ GLOBAL
    'Score Santé Global',
    TO_CHAR(GREATEST(0, LEAST(100, 
        100 
        - (CASE WHEN p_weight / NULLIF(p_height * p_height, 0) >= 30 THEN 20 ELSE 0 END) 
        - (CASE WHEN p_sugar > 50 THEN 15 ELSE 0 END)       
        - (CASE WHEN p_bpm > 90 THEN 15 ELSE 0 END)         
        - (CASE WHEN p_freq = 0 THEN 20 
                WHEN p_freq > 6 THEN 10 
                ELSE 0 END)
    ))) || '/100',
    'fa fa-tachometer',
    'u-normal-text',
    6
FROM user_data;