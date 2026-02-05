#ifndef _MAPPING_
#define _MAPPING_

// Key of the segment
#define KEY 1056

typedef struct {
    size_t *size;
    int *array;
    char *string;
    double *value;
} segment_t;

#endif