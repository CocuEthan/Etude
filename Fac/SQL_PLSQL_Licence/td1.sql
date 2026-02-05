1)
select * from employees where salary > (select
max(salary) from employees where departement_id like '60')

2)
create table emp_2{
emp_2id int property by autoincrement
firstname Varchar[30]
lastname varchar[30]
email varchar[100]
}create table as select(first_name, last_name,email)
from employees 
merge into emp2
using employees on emp_2id = employeesid
when matched then update set
    emp2.firstname = employees.first_name
    emp2.lastname = employes.last_name
    emp2.email = employees.email
    when not matched then
    insert(emp2.firstname, emp2.lastname, emp_2.email)
    values(employees.first_name,employees.lastname,employees.email);

3)
select lastname,hire.date,sys_date,case
when sys_date - to_intervale('15-0')> hire_date then '+ 15 ans'
sys_date - to_intervale('10-0')> hire_date then '+ 10 ans'
sys_date - to_intervale('5-0')> hire_date then '+ 5 ans'
else 
    '-5ans'
end
from employees

4) select regexp (colonne, 'sous chaine', 1 , 'i')as
    ocurrences from table
    where colonne line %sous chaine%