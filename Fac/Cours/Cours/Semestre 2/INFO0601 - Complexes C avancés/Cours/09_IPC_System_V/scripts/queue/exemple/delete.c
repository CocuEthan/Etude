/**
 * This program deletes the file created by the server.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/msg.h>

#include "structures.h"

int main() {
    int msqid;

    // Get the message queue
    if((msqid = msgget(KEY, 0)) == -1) {
        perror("Error getting the message queue");
        exit(EXIT_FAILURE);
    }

    // Delete the message queue
    if(msgctl(msqid, IPC_RMID, 0) == -1) {
        perror("Error deleting the message queue");
        exit(EXIT_FAILURE);
    }
    printf("Message queue deleted.\n");

    return EXIT_SUCCESS;
}