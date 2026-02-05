#include "utils.h"

#include <stdlib.h>

/**
 * Generate a random integer in an given interval [a,b].
 * @param a the lower bound of the interval
 * @param b the upper bound of the interval
 * @return a random integer in [a,b]
 */
int _random(int a, int b) {
    return rand() % (b - a + 1) + a;
}