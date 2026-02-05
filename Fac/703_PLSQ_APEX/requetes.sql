-- requête n°1
SELECT first_name, salary, REGEXP_COUNT(first_name, '[aeiouyAEIOUY]') AS nbvoyelles
FROM employees;


-- requête n°2
SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS nb_employes
FROM departments d
JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
ORDER BY d.department_id;


-- requête n°3
SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS nb_employes
FROM departments d
LEFT OUTER JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
ORDER BY d.department_id;


-- requête n°4
SELECT e.employee_id, e.first_name, e.last_name, e.salary, e.job_id
FROM employees e
WHERE e.salary > (
  SELECT AVG(salary)
  FROM employees e2
  WHERE e2.job_id = e.job_id
);


-- requête n°5
SELECT e.employee_id, e.first_name, e.last_name
FROM EMPLOYEES e
WHERE e.SALARY BETWEEN (SELECT AVG(salary) -500 FROM EMPLOYEES) AND (SELECT AVG(salary) +500 FROM EMPLOYEES) 


-- requête n°6
SELECT e.employee_id, e.first_name, e.last_name, d.department_name, d.department_id
FROM EMPLOYEES e 
JOIN departments d 
ON e.department_id=d.department_id
WHERE e.SALARY BETWEEN (SELECT AVG(salary) -500 FROM EMPLOYEES) AND (SELECT AVG(salary) +500 FROM EMPLOYEES); 



-- requête n°7
SELECT * FROM (SELECT e.employee_id, e.first_name_, e.last_name, e.hire_date,e.salary,e.department_id, ROUND(MONTHS_BETWEEN(sysdate, e.hire_date)/12,2) as Nb_année_services,
OVER (PARTITION by e.department_id ORDER BY e.salary DESC) as salary_30PP  




-- requête n°8
SELECT d.department_id, d.department_name, 
COUNT(e.employee_id) AS nb_employes, 
ROUND(AVG(e.salary), 2) AS salaire_moyen, 
SUM(e.salary) AS salaire_total 
FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_id, d.department_name 
HAVING AVG(e.salary) > ( SELECT MEDIAN(salary) FROM employees ) AND COUNT(e.employee_id) > 5 AND SUM(e.salary) > 100000;


-- requête n°9
MERGE INTO employees e
USING (
  SELECT 
    employee_id,
    salary,
    CASE 
      WHEN REGEXP_LIKE(first_name, '^[AEIOUYaeiouy]') THEN ROUND(salary * 1.05, 0)
      ELSE salary
    END AS new_salary
  FROM employees
) src
ON (e.employee_id = src.employee_id)
WHEN MATCHED THEN
  UPDATE SET e.salary = src.new_salary
WHERE e.salary < src.new_salary;


-- requête n°10
MERGE INTO employees e
USING (
  SELECT 
    emp.employee_id,    emp.salary,  loc.city,
    CASE 
      WHEN loc.city = 'South San Francisco' AND emp.salary < 6000 THEN ROUND(emp.salary * 1.10, 0)
      WHEN loc.city = 'Oxford' AND emp.salary < 8000 THEN ROUND(emp.salary * 1.10, 0)
      ELSE emp.salary
    END AS new_salary
  FROM employees emp
  JOIN departments dep ON emp.department_id = dep.department_id
  JOIN locations loc ON dep.location_id = loc.location_id
) src
ON (e.employee_id = src.employee_id)
WHEN MATCHED THEN
  UPDATE SET e.salary = src.new_salary
WHERE e.salary < src.new_salary;


-- requête n°11
SELECT e.employee_id, e.first_name, e.last_name, j.job_title, h.start_date, h.end_date
FROM employees e
JOIN job_history h ON e.employee_id = h.employee_id
JOIN jobs j ON h.job_id = j.job_id
WHERE h.end_date - h.start_date > 365;


-- requête n°12
SELECT
  employee_id,
  first_name || ' ' || last_name AS full_name,
  manager_id,
  LEVEL AS niveau_hierarchique
FROM employees
START WITH employee_id = 111
CONNECT BY PRIOR manager_id = employee_id
ORDER BY LEVEL;


-- requête n°13
SELECT e.last_name, d.department_name, j.grade_level, 
RANK() OVER (PARTITION BY d.department_name ORDER BY e.salary DESC) AS rang FROM employees e 
JOIN departments d ON e.department_id = d.department_id 
JOIN job_grades j ON e.salary BETWEEN j.lowest_sal AND j.highest_sal;


-- requête n°14
SELECT LPAD(last_name, LENGTH(last_name)+(LEVEL*2)-2, '_') AS organigramme FROM employees 
START WITH last_name = 'King' 
CONNECT BY PRIOR employee_id = manager_id;


-- requête n°15
SELECT *
FROM (
    SELECT e.employee_id, e.first_name, e.last_name, e.salary,                 
           e.department_id, e.manager_id, d.department_name,
    RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS 
rang_salaire
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE REGEXP_LIKE(e.first_name), '^[aeiouyAEIOUY]')
      AND e.hire_date <= ADD_MONTHS(SYSDATE, -60)
      AND e.manager_id IN (    	SELECT manager_id
          					FROM employees
          					GROUP BY manager_id
          					HAVING COUNT(*) > 5 	)
)
WHERE rang_salaire <= 3;


-- requête n°16
 SELECT   department_id, job_id,
    COUNT(employee_id) AS nb_employes,
    ROUND(AVG(salary), 2) AS salaire_moyen,
    SUM(salary) AS total_salaire
FROM employees
GROUP BY GROUPING SETS (
    ROLLUP(department_id, job_id),
    CUBE(job_id)
)
HAVING SUM(salary) > 10000
ORDER BY department_id, job_id;



