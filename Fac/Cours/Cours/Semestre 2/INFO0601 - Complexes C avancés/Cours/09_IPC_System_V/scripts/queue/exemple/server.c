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
#include <sys/stat.h>
#include <unistd.h>

#include "structures.h"

int main() {
    int msqid;
    request_t request;
    response_t response;

    // Create the message queue
    if((msqid = msgget(KEY, S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        if(errno == EEXIST)
            fprintf(stderr, "Message queue (key=%d) already exists\n", KEY);
        else
            perror("Error creating the message queue");
        exit(EXIT_FAILURE);
    }
    printf("Server ready (message queue=%d)...\n", msqid);

    // Wait for a request
    printf("Server: wait for a request...\n");
    if(msgrcv(msqid, &request, sizeof(request_t) - sizeof(long), TYPE_REQUEST, 0) == -1) {
        perror("Error receiving a request");
        exit(EXIT_FAILURE);
    }
    printf("Server: request received (%d, %d)\n", request.value1, request.value2);

    // Send response
    response.type = TYPE_RESPONSE;
    response.result = request.value1 + request.value2;

    if(msgsnd(msqid, &response, sizeof(response_t) - sizeof(long), 0) == -1) {
        perror("Error sending response");
        exit(EXIT_FAILURE);
    }
    printf("Server: response sent.\n");

    return EXIT_SUCCESS;
}