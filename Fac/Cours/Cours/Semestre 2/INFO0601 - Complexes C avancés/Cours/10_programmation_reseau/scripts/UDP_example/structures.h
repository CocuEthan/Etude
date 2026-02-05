#ifndef _STRUCTURES_
#define _STRUCTURES_

// Request types
#define CODE_HOUR 1
#define CODE_DATE 2

// Maximum length for response
#define MAX_MSG 256

// Request
typedef struct {
  int id;
  int code;
} request_t;

// Response
typedef struct {
  int id;
  char result[MAX_MSG];
} response_t;

#endif