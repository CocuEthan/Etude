/**
 * Program illustrating how msgget works to create a message queue.
 * @author Cyril Rabat
 */
#define KEY 2023 // Key for message queue

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <sys/msg.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
    int msqid;

    // Create the message queue
    if((msqid = msgget(KEY, S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        if(errno == EEXIST)
            fprintf(stderr, "Message queue (key=%d) already exists\n", KEY);
        else
            perror("Error creating the message queue");
        exit(EXIT_FAILURE);
    }
    printf("Message queue (key=%d, id=%d) created successfully...\n", KEY, msqid);

    return EXIT_SUCCESS;
}