/**
 * This program aims to illustrate the use of a message queue. The server
 * creates a message queue and waits for a request (two integers). When it
 * receives one, it sends a response (the sum of the two integers).
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/msg.h>
#include <errno.h>
#include <unistd.h>

#include "structures.h"

int main() {
    int msqid;
    request_t request;
    response_t response;

    // Get the message queue
    if((msqid = msgget(KEY, 0)) == -1) {
        perror("Error getting the message queue");
        exit(EXIT_FAILURE);
    }

    // Send a request
    request.type = TYPE_REQUEST;
    request.value1 = 3;
    request.value2 = 6;

    if(msgsnd(msqid, &request, sizeof(request_t) - sizeof(long), 0) == -1) {
        perror("Error sending request");
        exit(EXIT_FAILURE);
    }
    printf("Client: request sent.\n");

    // Wait for a response
    printf("Client: wait for response...\n");
    if(msgrcv(msqid, &response, sizeof(response_t) - sizeof(long), TYPE_RESPONSE, 0) == -1) {
        perror("Error receiving the response");
        exit(EXIT_FAILURE);
    }

    printf("Client: the result is %d\n", response.result);

    return EXIT_SUCCESS;
}