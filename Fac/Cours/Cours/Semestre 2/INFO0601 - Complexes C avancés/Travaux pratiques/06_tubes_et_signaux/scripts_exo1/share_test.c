#include <stdio.h>
#include <stdlib.h>

#include "share.h"

int main(int argc, char *argv[]) {
    share_t array;

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s name where name is the name of the shared variable.\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    
    // Test the array
    array = share_init(argv[1]);
    printf("Size of the array: %d\n", share_size(array));
    printf("Set 1 to the first cell of the array\n");
    share_set(array, 0, 1);
    printf("Get value of the first cell of the array: %d\n", share_get(array, 0));
    share_clean(array);

    return EXIT_SUCCESS;
}