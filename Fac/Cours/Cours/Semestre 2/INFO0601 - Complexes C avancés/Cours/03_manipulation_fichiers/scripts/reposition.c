/**
 * Reposition the offset of a file with lseek.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
 
int main(int argc, char* argv[]) {
  int fd, i;
  
  // Create file
  if((fd = open("toto.bin", O_RDWR|O_CREAT, S_IRUSR|S_IWUSR)) == -1) {
    perror("Error creating file 'toto.bin'");
    exit(EXIT_FAILURE);
  }    
  
  // Reposition the offset at the beginning of the file
  if(lseek(fd, 0, SEEK_SET) == -1) {
    perror("Error with lseek (1)");
    exit(EXIT_FAILURE);
  }
  
  // Write 5 integers
  for(i = 0; i < 5; i++) {
    if(write(fd, &i, sizeof(int)) == -1) {
      perror("Error writing integers");
      exit(EXIT_FAILURE);
    }
  }
  printf("5 integers written.\n");
  
  // Step back 2 integers
  if(lseek(fd, -sizeof(int) * 2, SEEK_CUR) == -1) {
    perror("Error with lseek (2)");
    exit(EXIT_FAILURE);
  }
  printf("Step back 2 integers.\n");
  
  // Read current integer
  if(read(fd, &i, sizeof(int)) == -1) {
    perror("Error reading integer");
    exit(EXIT_FAILURE);
  }
  printf("Integer read: %d\n", i);
  
  // Close file
  if(close(fd) == -1) {
    perror("Error closing file");
    exit(EXIT_FAILURE);
  }
  
  return EXIT_SUCCESS;
}