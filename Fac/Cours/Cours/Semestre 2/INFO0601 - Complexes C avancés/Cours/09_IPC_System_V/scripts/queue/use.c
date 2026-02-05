/**
 * Program that illustrates the use of a message queue. It creates or retrieves
 * the queue. Then he sends a message and reads it again immediately.
 * @author Cyril Rabat
 */
#define KEY 2023 // Key for message queue

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <sys/msg.h>
#include <sys/stat.h>

typedef struct {
    long type;
    char msg[256];
} message_t;

int main(int argc, char *argv[]) {
    int msqid;
    message_t msg1 = { 1, "Hello" }, msg2;

    // Get/create the message queue
    if((msqid = msgget(KEY, S_IRUSR | S_IWUSR | IPC_CREAT)) == -1) {
        perror("Erreur creating/getting the message queue");
        exit(EXIT_FAILURE);
    }
    printf("Message queue (key=%d, id=%d)...\n", KEY, msqid);
    
    // Send a message
    if(msgsnd(msqid, &msg1, sizeof(msg1) - sizeof(long), 0) == -1) {
        perror("Error writing to the message queue");
        exit(EXIT_FAILURE);
    }
    printf("Message sent successfully.\n");
    
    // Get a message
    if(msgrcv(msqid, &msg2, sizeof(msg2) - sizeof(long), 0, 0) == -1) {
        perror("Error reading from the message queue");
        exit(EXIT_FAILURE);
    }
    printf("Message received: '%s'.\n", msg2.msg);

    return EXIT_SUCCESS;
}