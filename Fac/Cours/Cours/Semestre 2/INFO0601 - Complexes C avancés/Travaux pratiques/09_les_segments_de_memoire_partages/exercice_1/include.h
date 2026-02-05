#ifndef _INCLUDE_
#define _INCLUDE_

#define KEY               1978     // Key for the shared memory segment
#define HEIGHT              20     // Height of the map
#define WIDTH               20     // Width of the map

#define SPEED          1000000     // Refresh period

// To create a virus, a random value is generated in the interval [0; MAX].
// If it is lower than CREATE, a new virus is created.
#define MAX                 100
#define CREATE                2

// Number of viruses to lose a life
#define LIMIT                15

#endif