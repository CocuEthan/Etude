#ifndef _COLORS_
#define _COLORS_

// Colors constants
typedef enum {
    WHITE = 1,
    GREEN = 2,
    BLUE = 3,
    RED = 4 ,
    YELLOW = 5,
    CYAN = 6,
    MAGENTA = 7,
    BK_WHITE = 8,
    BK_GREEN = 9,
    BK_BLUE = 10,
    BK_RED = 11,
    BK_YELLOW =12,
    BK_CYAN = 13,
    BK_MAGENTA = 14,
} color_t;

/**
 * Palette definition.
 */
void palette();

#endif