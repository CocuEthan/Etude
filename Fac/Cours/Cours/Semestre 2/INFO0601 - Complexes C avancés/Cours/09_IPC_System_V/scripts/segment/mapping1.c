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
 * Create the segment, initialize and map it.
 * @param[in,out] address the segment's address
 * @param size the size of the array
 * @param array the array
 * @param string the string
 * @param value the value
 * @return the structure corresponding to the segment
 */
segment_t *segment_create(void **address, size_t size, int *array, char *string, double value) {
    int shmid, i;
    size_t segment_size;
    segment_t *segment;

    // Compute segment size
    segment_size = sizeof(size_t) + size * sizeof(int) + (strlen(string) + 1) * sizeof(char) + sizeof(double);

    // Create segment
    if((shmid = shmget(KEY, segment_size, IPC_CREAT | IPC_EXCL | S_IRUSR | S_IWUSR)) == -1) {
        perror("Error creating the segment");
        exit(EXIT_FAILURE);
    }

    // Attach segment
    if((*address = shmat(shmid, NULL, 0)) == (void*)-1) {
        perror("Error attaching the segment");
        exit(EXIT_FAILURE);
    }

    // Create mapping structure
    if((segment = (segment_t*)malloc(sizeof(segment_t))) == NULL) {
        perror("Error allocating structure");
        exit(EXIT_FAILURE);
    }

    // Mapping and initialization
    segment->size = (size_t*)*address;
    *segment->size = size;

    segment->array = (int*)&segment->size[1];
    for(i = 0; i < size; i++)
        segment->array[i] = array[i];

    segment->string = (char*)&segment->array[*segment->size];
    strcpy(segment->string, string);

    segment->value = (double*)&segment->string[strlen(segment->string) + 1];
    *segment->value = value;

    return segment;
}

int main() {
    void *address;
    segment_t *segment;
    int t[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    char *string = "Hello everybody!";
    double value = 2022.2023;
    
    segment = segment_create(&address, 10, t, string, value);
    printf("Segment created and initialized\n");
    
    // Detach segment
    if(shmdt(address) == -1) {
        perror("Error detaching the segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment detached\n");
    
    free(segment);

    return EXIT_SUCCESS;
}