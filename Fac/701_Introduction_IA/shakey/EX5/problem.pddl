(define (problem shakey-problem) (:domain Shakey)
(:objects 
    Shakey - robot
    Box2 - box
    LocA LocB LocC LocD LocCouloir - location
    Room1 Room2 Room3 Room4 Room5 - room
   
)
(:init
;; Shakey et la boîte commence tout les deux dans Room1 (LocA)
    (At Shakey LocA)
    (AtBox Box2 LocA)
;; Pièces 
    (InRoom LocA Room1)
    (InRoom LocB Room2)
    (InRoom LocC Room3)
    (InRoom LocD Room4)
    (InRoom LocCouloir Room5)
;; Connexions
    (Connected LocA LocCouloir)
    (Connected LocCouloir LocA)
    (Connected LocB LocCouloir)
    (Connected LocCouloir LocB)
    (Connected LocC LocCouloir)
    (Connected LocCouloir LocC)
    (Connected LocD LocCouloir)
    (Connected LocCouloir LocD)
)
(:goal 
    (AtBox Box2 LocB)  ;; Box2 doit être dans Room2 (LocB)
)
)
