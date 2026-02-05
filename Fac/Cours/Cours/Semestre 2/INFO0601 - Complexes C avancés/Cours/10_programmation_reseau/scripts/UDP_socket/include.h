#ifndef _INCLUDE_
#define _INCLUDE_

// Server port
#define PORT 1234

// Maximum message size
#define MAX 256

// Request
typedef struct {
    char msg[MAX];
} request_t;

// Response
typedef struct {
    char msg[MAX];
} response_t;

#endif