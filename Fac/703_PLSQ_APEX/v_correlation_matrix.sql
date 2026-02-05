CREATE OR REPLACE VIEW v_correlation_matrix AS
SELECT 
    'Poids vs Cal. Brûlées' as paire, 
    ROUND(CORR(WEIGHT__KG_, CALORIES_BURNED), 2) as coefficient, 
    CASE 
        WHEN ABS(CORR(WEIGHT__KG_, CALORIES_BURNED)) > 0.7 THEN 'Très Forte'
        WHEN ABS(CORR(WEIGHT__KG_, CALORIES_BURNED)) > 0.4 THEN 'Moyenne'
        ELSE 'Faible' 
    END as force,
    CASE 
        WHEN ABS(CORR(WEIGHT__KG_, CALORIES_BURNED)) > 0.7 THEN 'u-danger-text'
        ELSE 'u-normal-text' 
    END as css_class
FROM "FINAL_DATA"

UNION ALL

SELECT 
    'Sucre vs Cholestérol', 
    ROUND(CORR(SUGAR_G, CHOLESTEROL_MG), 2),
    CASE 
        WHEN ABS(CORR(SUGAR_G, CHOLESTEROL_MG)) > 0.5 THEN 'Forte' 
        ELSE 'Faible' 
    END,
    CASE 
        WHEN ABS(CORR(SUGAR_G, CHOLESTEROL_MG)) > 0.5 THEN 'u-warning-text' 
        ELSE 'u-normal-text' 
    END
FROM "FINAL_DATA"

UNION ALL

SELECT 
    'Sport vs BPM Repos', 
    ROUND(CORR(WORKOUT_FREQUENCY__DAYS_WEEK_, RESTING_BPM), 2),
    CASE 
        WHEN ABS(CORR(WORKOUT_FREQUENCY__DAYS_WEEK_, RESTING_BPM)) > 0.5 THEN 'Forte' 
        ELSE 'Faible' 
    END,
    CASE 
        WHEN ABS(CORR(WORKOUT_FREQUENCY__DAYS_WEEK_, RESTING_BPM)) > 0.5 THEN 'u-success-text' 
        ELSE 'u-normal-text' 
    END
FROM "FINAL_DATA";