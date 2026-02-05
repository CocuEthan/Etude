/**
 * Use of generic pointers with `read` and `write`.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main() {
  int fd, integer = 5;
  float real = 2.4;
  void *ptr1 = &real, *ptr2 = &integer;

  if((fd = open("toto.bin", O_RDWR | O_CREAT, S_IRUSR | S_IWUSR)) == -1) {
      perror("Error opening file 'toto.bin'");
      exit(EXIT_FAILURE);
  }
  
  if(write(fd, &integer, sizeof(int)) == -1) {
      perror("Error writing integer");
      exit(EXIT_FAILURE);
  }
  if(write(fd, &real, sizeof(float)) == -1) {
      perror("Error writing real");
      exit(EXIT_FAILURE);
  }
  
  if(lseek(fd, 0L, SEEK_SET) == -1) {
      perror("Error moving in file");
      exit(EXIT_FAILURE);
  }
  
  if(read(fd, ptr2, sizeof(float)) == -1) {
      perror("Error reading integer");
      exit(EXIT_FAILURE);
  }
  if(read(fd, ptr1, sizeof(int)) == -1) {
      perror("Error reading real");
      exit(EXIT_FAILURE);
  }
  
  printf("integer = %d, real = %f\n", *(int*)ptr2, *(float*)ptr1);
  
  if(close(fd) == -1) {
      perror("Error closing file");
      exit(EXIT_FAILURE);
  }
  
  return EXIT_SUCCESS;
}