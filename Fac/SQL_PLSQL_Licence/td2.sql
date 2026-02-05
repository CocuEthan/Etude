// 1 faire une fonction factorielle en PL/SQL

//a itérative
Create or replace fonction factorielle_ite( num in integer):return integer IS
result integer := 1;
BEGIN
    IF n = 0 then
        return 0;
    END IF;

    IF n < 0 then
        return NULL;
    END IF;

    FOR i IN 1..num loop
        result := result * i;
        END loop;
    return result;
END factorielle_ite

//b récursive

Create or replace fonction factorielle_rec( num in integer):return integer IS
BEGIN
if num = 0 then
 return 0;
 end if;
if num < 0 then
return NULL;
end if;
 return num * factorielle_rec( num -1);

 end factorielle_rec

CREATE OR REPLACE FUNCTION get_emp(emp Employé)
return HR.employé Row Type is
result HR employe  Row Type; 
ma_chaine VARCHAR(200);
Begin
    return (SELECT * FROM Employé e
                WHERE e.empid=emp.empid  );
end;
/
execute immediate ma_chaine into result  using e.empid;
return result;





CREATE OR REPLACE FUNCTION Salary (id number)
return number is
    plsql VARCHAR(200)
    declare
        empec employé % Row Type
        Begin 
            empec : get_emp(:id)
            :res==empec.Salary + 12
        end
    result number;
Begin
    execute immediate plsql
        using in id , out result
    return result;
end;
/

create ... place package typos is
TYPE type_garantie IS RECORD ( number, number ) ;
SUBTYPE garantie IS type_garantie ;
end typos;

Exo 4 TD2 Cormier

CREATE OR REPLACE PACKAGE toto AS
    --TYPE rt_order IS REF CURSOR RETURN order%ROWTYPE;
    TYPE type_cust_rec IS customers%ROWTYPE;
    TYPE rt_cust IS REF CURSOR RETURN customers%ROWTYPE;
    PROCEDURE get_order(p_order IN NUMBER, pc_cv_order IN OUT rt_order);
    PROCEDURE get_cust(p_cust IN NUMBER, pc_cust IN OUT rt_cust):
END toto;

CREATE OR REPLACE PACKAGE BODY toto AS
    PROCEDURE get_order(p_order IN NUMBER,pc_cv_order IN OUT rt_order)
    IS BEGIN
    OPEN pc_cv_order FOR SELECT * FROM orders WHERE order_id=p_order_id;
    --CLOSE pc_cv_order
    END get_order;

    PROCEDURE get_cust(p_cust_id IN NUMBER,pc_cv_cust IN OUT rt_cust)
    IS BEGIN
    OPEN pc_cv_cust FOR SELECT * FROM customers WHERE customer_id=p_cust_id;
    --CLOSE pc_cv_cust
    END get_cust;
END;--fin du body


TD3
CREATE TYPE NomPrenom AS Object (
    Nom Varchar2(50),
    Prenom Varchar2(50)
);


Ex1
CREATE TYPE t_personne AS OBJECT(
    Nom VARCHAR2(50), 
    Prenom VARCHAR2(50)
);

CREATE TYPE t_personne_nst AS TABLE OF t_personne

CREATE TABLE Equipe(
    Numero NUMBER,
    DateCrea DATE,
    Liste_p t_personne_nst) NESTED TABLE Liste_p STORE AS Liste_p_Tab

CREATE TYPE t_Carte_credit AS OBJECT(
    Type VARCHAR2(200),
    NumeroCarte NUMBER
);

CREATE TYPE t_carte_nst TABLE OF t_Carte_credit

ALTER TABLE customers ADD (mes_cartes t_carte_nst) NESTED TABLE mes_cartes STORE AS mes_cartes_Tab

CREATE OR REPLACE PACKAGE Card_pkg AS
    PROCEDURE Mettre_a_jour_carte(p_cust_id NUMBER, p_carte_type VARCHAR2, p_carte_numero NUMBER);
    PROCEDURE Info_carte(p_cust_id NUMBER);
END Card_pkg


CREATE OR REPLACE PACKAGE BODY Card_pkg IS
    PROCEDURE Mettre_a_jour_carte(p_cust_id NUMBER, p_carte_type VARCHAR2, p_carte_numero NUMBER)IS
    result t_carte_nst
    i INTEGER;
        BEGIN
            SELECT mes_cartes INTO result FROM customers WHERE customer_id=p_cust_id
        IF result.EXISTS(1) THEN -- ajout des infos
            i=result.LAST;
            result.EXTEND(1);
            result(i+1)=t_Carte_credit(p_carte_type,p_carte_numero);
    UPDATE customers SET mes_cartes=result WHER customer_id=p_cust_id;
        ELSE --on la construit
    UPDATE customers SET mes_cartes = t_carte_nst(t_Carte_credit(p_carte_type,p_carte_numero)) WHERE customer_id=p_cust_id
        END IF
END Card_pkg

    PROCEDURE Info_carte(p_cust_id NUMBER)