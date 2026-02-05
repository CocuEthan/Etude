CREATE OR REPLACE PACKAGE BODY pkg_analyse_correlation IS

    FUNCTION valider_colonne(p_col VARCHAR2) RETURN VARCHAR2 IS
    BEGIN
        IF p_col IN ('SUGAR_G', 'SODIUM_MG', 'CHOLESTEROL_MG', 'PROTEINS', 
                     'WEIGHT__KG_', 'BMI', 'RESTING_BPM', 'HEIGHT__M_', 
                     'CALORIES_BURNED') THEN
            RETURN p_col;
        ELSE
            RETURN 'WEIGHT__KG_'; 
        END IF;
    END;

    -- Fonction 1 : Le SQL pour le KPI 
    FUNCTION get_kpi_query(p_col_x VARCHAR2, p_col_y VARCHAR2) RETURN VARCHAR2 IS
        l_safe_x VARCHAR2(50) := valider_colonne(p_col_x);
        l_safe_y VARCHAR2(50) := valider_colonne(p_col_y);
    BEGIN
        RETURN 'SELECT 
                    ''Coefficient de Corrélation'' as label, 
                    ROUND(CORR(' || l_safe_x || ', ' || l_safe_y || '), 3) as valeur, 
                    CASE 
                        WHEN ABS(CORR(' || l_safe_x || ', ' || l_safe_y || ')) > 0.7 THEN ''Lien Très Fort'' 
                        WHEN ABS(CORR(' || l_safe_x || ', ' || l_safe_y || ')) > 0.4 THEN ''Lien Modéré'' 
                        ELSE ''Aucun lien significatif'' 
                    END as interpretation, 
                    ''fa fa-link'' as icon 
                FROM "FINAL_DATA"';
    END;

    FUNCTION get_chart_query(p_col_x VARCHAR2, p_col_y VARCHAR2) RETURN VARCHAR2 IS
        l_safe_x VARCHAR2(50) := valider_colonne(p_col_x);
        l_safe_y VARCHAR2(50) := valider_colonne(p_col_y);
    BEGIN
        RETURN 'SELECT ' || l_safe_x || ' as x_val, ' ||
               '       ' || l_safe_y || ' as y_val, ' ||
               '       GENDER as groupe ' ||
               'FROM (SELECT * FROM "FINAL_DATA" ORDER BY dbms_random.value) ' ||
               'WHERE ROWNUM <= 500';
    END;

END pkg_analyse_correlation;