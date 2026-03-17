Feature: Analyse statistique du corpus
  En tant que linguiste
  Je veux connaître la longueur moyenne des documents
  Afin d'analyser la complexité du texte

  Scenario: Calcul standard d'un corpus simple
    Given un corpus contenant 2 documents
    And le premier document a 2 tokens
    And le second document a 4 tokens
    When je lance l'analyse statistique
    Then la moyenne des longueurs doit être 3.0