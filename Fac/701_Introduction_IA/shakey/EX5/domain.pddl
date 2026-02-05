;Header and description

(define (domain Shakey)

  (:types
    robot
    box
    location
    room
    switch
  )
  (:predicates
    (At ?r - robot ?l - location)
    (Box ?b - box)
    (AtBox ?b - box ?l - location)
    (InRoom ?l - location ?rm - room)
    (Connected ?x - location ?y - location)
    (On ?r - robot ?b - box)
    
    (Clear ?l - location)
  )
  (:action Go
    :parameters (?x ?y - location ?r - robot)
    :precondition (At ?r ?x)
    :effect (and (Not (At ?r ?x))
                 (At ?r ?y))
  )
  (:action Push
    :parameters (?b - box ?x ?y - location ?r - robot)
    :precondition (and (At ?r ?x) (AtBox ?b ?x) (Connected ?x ?y))
    :effect (and (not (AtBox ?b ?x)) (AtBox ?b ?y))
  )
  (:action ClimbUp
    :parameters (?r - robot ?b - box ?l - location)
    :precondition (and (At ?r ?l) (AtBox ?b ?l))
    :effect (and (On ?r ?b) (not (At ?r ?l)))
  )  
  (:action ClimbDown
    :parameters (?r - robot ?b - box ?l - location)
    :precondition (On ?r ?b)
    :effect (and (At ?r ?l) (not (On ?r ?b)))
  )
)
    






