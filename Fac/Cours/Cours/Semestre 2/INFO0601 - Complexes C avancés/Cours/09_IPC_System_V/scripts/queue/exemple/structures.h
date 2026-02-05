#ifndef _STRUCTURES_
#define _STRUCTURES_

// Key for the message queue
#define KEY 1056

// Type for request message
#define TYPE_REQUEST 1

// Request message
typedef struct {
    long type;
    int value1;
    int value2;
} request_t;

// Type for response message
#define TYPE_RESPONSE 2

// Response message
typedef struct {
    long type;
    int result;
} response_t;

#endif