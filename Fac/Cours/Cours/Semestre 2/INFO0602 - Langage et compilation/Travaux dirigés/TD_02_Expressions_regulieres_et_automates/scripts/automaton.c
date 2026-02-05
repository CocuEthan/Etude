/**
 * This program simulates a deterministic finite automaton.
 * M = (Q, Σ, δ, s, F)
 *  Q = { q0, q1, q2 }
 *  Σ = { 'a', 'b' }
 *  s = q0
 *  F = { q1 }
 *  δ = (q0, 'a') -> q1
 *      (q0, 'b') -> q0
 *      (q1, 'a') -> q2
 *      (q1, 'b') -> q0
 *      (q2, 'a') -> q2
 *      (q2, 'b') -> q2
 * Try: abbabbab (accepted) a (accepted) abaab (rejected)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BOOL int
#define FALSE 0
#define TRUE  1

/**
 * Simulate the automaton.
 * @param str the word to parse
 * @return TRUE if the word is accepted
 */
BOOL automaton(char str[]) {
    int cpt = 0, state = 0, result = TRUE;
    
    while((result == TRUE) && (cpt < strlen(str))) {
        printf("state = q%i, symbol = %c => ", state, str[cpt]);
        switch(state) {
            case 0 : /* state 0 */
                if(str[cpt] == 'a')
                    state = 1;
                else if(str[cpt] == 'b')
                    state = 0;
                else
                    result= FALSE; /* error */
                break;
            case 1 : /* state 1 */
                if(str[cpt] == 'a')
                    state = 2;
                else if(str[cpt] == 'b')
                    state = 0;
                else
                    result = FALSE; /* error */
                break;
            case 2 : /* state 2 */
                if(str[cpt] == 'a')
                    state = 2;
                else if(str[cpt] == 'b')
                    state = 2;
                else
                    result = FALSE; /* error */
                break;
        }
        if(!result)
            printf("error\n");
        else
            printf("state q%d\n", state);
        cpt++;
    }

    return (result == TRUE) && (state == 1);
}

int main(int argc, char *argv[]) {
    char *msg;
    
    if(argc != 2) {
        fprintf(stderr, "Use: %s w\n\tWhere 'w' is the word to analyse.\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    msg = argv[1];

    if(automaton(msg))
        printf("'%s' is accepted by the automaton\n", msg);
    else
        printf("'%s' isn't accepted by the automaton\n", msg);

    return EXIT_SUCCESS;
}