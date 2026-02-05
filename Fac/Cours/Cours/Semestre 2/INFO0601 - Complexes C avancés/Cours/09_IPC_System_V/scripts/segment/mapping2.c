/**
 * This program shows how to map a shared memory segment.
 * mapping1: create and initialize the segment
 * mapping2: get the segment and display the content
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>

#include "mapping.h"

/**
 * Map a structure on a segment.
 * @param address the segment address
 * @return structure mapping the segment
 **/
segment_t *segment_mapping(void *address) {  
    segment_t *segment;

    // Allocate the structure
    if((segment = (segment_t*)malloc(sizeof(segment_t))) == NULL) {
        perror("Error allocating structure");
        exit(EXIT_FAILURE);
    }
  
    // Mapping
    segment->size = (size_t*)address;
    segment->array = (int*)&segment->size[1];
    segment->string = (char*)&segment->array[*segment->size];
    segment->value = (double*)&segment->string[strlen(segment->string) + 1];
  
    return segment;
}

int main() {
    int shmid, i;
    void *address;
    segment_t *segment;

    // Get the segment
    if((shmid = shmget(KEY, 0, 0)) == -1) {
        perror("Error getting segment identifier");
        exit(EXIT_FAILURE);
    }
    printf("Segment identifier obtained\n");
    
    // Attach the segment
    if((address = shmat(shmid, NULL, 0)) == (void*)-1) {
        perror("Error attaching segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment attached\n");
    
    // Mapping of the segment
    segment = segment_mapping(address);
    
    // Display content of the segment
    printf("Array : [ ");
    for(i = 0; i < *segment->size; i++)
        printf("%d ", segment->array[i]);
    printf("]\n");
    printf("String: '%s'\n", segment->string);
    printf("Value: %lf\n", *segment->value);
    
    // Detach segment
    if(shmdt(address) == -1) {
        perror("Error detaching segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment detached\n");
    
    free(segment);

    return EXIT_SUCCESS;
}