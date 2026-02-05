#include <stdio.h>
#include <locale.h>
#include <stdlib.h>
#include <wchar.h>
#include <string.h>

#include "level.h"

//    000000000011111111112222222222333333333344444444445555555555
//    012345678901234567890123456789012345678901234567890123456789
// 00 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 00
// 01 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 01
// 02 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 02
// 03 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 03
// 04 ▓                                                          ▓ 04
// 05 ▓                    ┌┴┐                         001       ▓ 05
// 06 ▓                    └┬┘                         ███       ▓ 06
// 07 ▓                    ─┼─                         ███       ▓ 07
// 08 ▓                    ┌┴┐               O         ███       ▓ 08
// 09 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓├─┤▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 09
// 10 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓├─┤▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 10
// 11 ▓               ├─┤                                        ▓ 11
// 12 ▓  ███          ├─┤                                        ▓ 12
// 13 ▓  █E█          ├─┤                                        ▓ 13
// 14 ▓  ███          ├─┤                          1             ▓ 14
// 15 ▓  ███          ├─┤                          ┘             ▓ 15
// 16 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 16
// 17 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 17
// 18 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 18
// 19 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 19
//    000000000011111111112222222222333333333344444444445555555555
//    012345678901234567890123456789012345678901234567890123456789
void sample_1() {
    int i;
    level_t level;
    
    level_init(&level);
    
    for(i = 0; i < WIDTH; i++) {
        level_add_block(&level, i, 0);
        level_add_block(&level, i, 1);
        level_add_block(&level, i, 2);
        level_add_block(&level, i, 3);
        level_add_block(&level, i, 9);
        level_add_block(&level, i, 10);
        level_add_block(&level, i, 16);
        level_add_block(&level, i, 17);
        level_add_block(&level, i, 18);
        level_add_block(&level, i, 19);
    }
    for(i = 0; i < HEIGHT; i++) {
        level_add_block(&level, 0, i);
        level_add_block(&level, WIDTH - 1, i);
    }
    
    level_add_robot(&level, 21, 5);
    
    for(i = 9; i <= 15; i++)
        level_add_ladder(&level, 16, i);
    
    level_add_start(&level, 3, 12);
    level_add_bomb(&level, 39, 8);
    level_add_door(&level, 49, 5, 1);
    level_add_key(&level, 45, 14, 1);
    
    level_display(&level);
}

//    000000000011111111112222222222333333333344444444445555555555
//    012345678901234567890123456789012345678901234567890123456789
// 00 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 00
// 01 ▓003                         1                          004▓ 01
// 02 ▓███                         ┼                          ███▓ 02
// 03 ▓███                         ┼                          ███▓ 03
// 04 ▓███                         ┼                          ███▓ 04
// 05 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 05
// 06 ▓                                                       003▓ 06
// 07 ▓                 ├─┤                                   ███▓ 07
// 08 ▓                 └─┘                                   ███▓ 08
// 09 ▓                                                       ███▓ 09
// 10 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓├─┤▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 10
// 11 ▓001                        ├─┤      ┌┴┐                002▓ 11
// 12 ▓███                        ├─┤      └┬┘                ███▓ 12
// 13 ▓███                        ├─┤      ─┼─                ███▓ 13
// 14 ▓███                        ├─┤      ┌┴┐                ███▓ 14
// 15 ▓▓▓▓├─┤     ├─┤▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓├─┤     ├─┤▓▓▓▓ 15
// 16 ▓   ├─┤     ├─┤                              ├─┤     ├─┤   ▓ 16
// 17 ▓   ├─┤     ├─┤                              ├─┤     ├─┤   ▓ 17
// 18 ▓   ├─┤     ├─┤                              ├─┤     ├─┤   ▓ 18
// 19 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 19
//    000000000011111111112222222222333333333344444444445555555555
//    012345678901234567890123456789012345678901234567890123456789
void sample_2() {
    level_t level;
    int i;
    
    level_init(&level);
    
    for(i = 0; i < WIDTH; i++) {
        level_add_block(&level, i, 0);
        level_add_block(&level, i, 5);
        level_add_block(&level, i, 10);
        level_add_block(&level, i, 15);
        level_add_block(&level, i, 19);
    }
    for(i = 0; i < HEIGHT; i++) {
        level_add_block(&level, 0, i);
        level_add_block(&level, WIDTH - 1, i);
    }
    for(i = 7; i <= 11; i++)
        level_add_empty(&level, i, 15);
    for(i = 48; i <= 52; i++)
        level_add_empty(&level, i, 15);
    
    for(i = 15; i <= 18; i++) {
        level_add_ladder(&level, 4, i);
        level_add_ladder(&level, 12, i);
        level_add_ladder(&level, 45, i);
        level_add_ladder(&level, 53, i);
    }
    for(i = 10; i <= 14; i++)
        level_add_ladder(&level, 28, i);
    level_add_door(&level, 1, 11, 1);
    level_add_door(&level, 56, 11, 2);
    level_add_door(&level, 56, 6, 3);
    level_add_door(&level, 1, 1, 3);
    level_add_door(&level, 56, 1, 4);
    
    for(i = 1; i <= 4; i++)
        level_add_gate(&level, 29, i, 1);
    
    level_add_robot(&level, 37, 11);
    level_add_probe(&level, 18, 7);
    
    level_display(&level);
}

//    000000000011111111112222222222333333333344444444445555555555
//    012345678901234567890123456789012345678901234567890123456789
// 00 ▓▓▓▓▓▓▓▓▓▓▓▓                                    ▓▓▓▓▓▓▓▓▓▓▓▓ 00
// 01 ▓002       ▓                                    ▓       004▓ 01
// 02 ▓███       ▓                                    ▓       ███▓ 02
// 03 ▓███      2▓                                    ▓       ███▓ 03
// 04 ▓███      ┘▓                                    ▓       ███▓ 04
// 05 ▓├─┤#######▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓#######├─┤▓ 05
// 06 ▓├─┤                         2                          ├─┤▓ 06
// 07 ▓├─┤              ├─┤        ┼                          ├─┤▓ 07
// 08 ▓├─┤              └─┘        ┼                          ├─┤▓ 08
// 09 ▓├─┤                         ┼                          ├─┤▓ 09
// 10 ▓▓▓▓#######▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓#######▓▓▓▓ 10
// 11 ▓          ▓                                    ▓          ▓ 11
// 12 ▓          ▓                                    ▓          ▓ 12
// 13 ▓          ▓                                    ▓          ▓ 13
// 14 ▓          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓          ▓ 14
// 15 ▓    ┌┴┐                                                   ▓ 15
// 16 ▓    └┬┘                                                   ▓ 16
// 17 ▓    ─┼─                                                   ▓ 17
// 18 ▓    ┌┴┐                                                   ▓ 18
// 19 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 19
//    000000000011111111112222222222333333333344444444445555555555
//    012345678901234567890123456789012345678901234567890123456789
void sample_3() {
    level_t level;
    int i;
    
    level_init(&level);
    
    for(i = 0; i < WIDTH; i++)
        level_add_block(&level, i, 19);
    for(i = 11; i <= 48; i++) {
        level_add_block(&level, i, 5);
        level_add_block(&level, i, 10);
        level_add_block(&level, i, 14);
    }
    for(i = 0; i <= 11; i++)
        level_add_block(&level, i, 0);
    for(i = 48; i <= 59; i++)
        level_add_block(&level, i, 0);
    
    for(i = 0; i < HEIGHT; i++) {
        level_add_block(&level, 0, i);
        level_add_block(&level, WIDTH - 1, i);
    }
    for(i = 10; i <= 14; i++) {
        level_add_block(&level, 11, i);
        level_add_block(&level, 48, i);
    }
    for(i = 0; i <= 5; i++) {
        level_add_block(&level, 11, i);
        level_add_block(&level, 48, i);
    }
    
    for(i = 5; i <= 9; i++) {
        level_add_ladder(&level, 1, i);
        level_add_ladder(&level, 56, i);
    }
    for(i = 1; i <= 3; i++) {
        level_add_block(&level, i, 10);
        level_add_block(&level, 55 + i, 10);
    }
    for(i = 4; i <= 10; i++) {
        level_add_trap(&level, i, 5);
        level_add_trap(&level, i, 10);
        level_add_trap(&level, 45 + i, 5);
        level_add_trap(&level, 45 + i, 10);
    }
    
    level_add_door(&level, 1, 1, 2);
    level_add_door(&level, 56, 1, 4);
    
    level_add_robot(&level, 5, 15);
    level_add_probe(&level, 18, 7);
    
    for(i = 6; i <= 9; i++)
        level_add_gate(&level, 29, i, 2);
    
    level_add_key(&level, 10, 3, 2);
    
    level_display(&level);
}

int main() {
    if(setlocale(LC_ALL, "") == NULL)
        printf("setlocale failed.\n");
    
    sample_1();
    sample_2();
    sample_3();
    
    return EXIT_SUCCESS;
}