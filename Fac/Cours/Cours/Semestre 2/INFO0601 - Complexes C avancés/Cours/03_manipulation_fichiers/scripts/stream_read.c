/**
 * Reads an integer and a string from the file 'toto.bin'.
 * It uses 'fopen', 'fread' and 'fclose'.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
 
int main(int argc, char* argv[]) {
  FILE *f;              // Stream
  int value;            // Integer read
  char character;       // Character read

  // Open file
  if((f = fopen("toto.bin", "r")) == NULL) {
    perror("Error opening file");
    exit(EXIT_FAILURE);
  }
  
  // Read integer
  if(fread(&value, sizeof(int), 1, f) != 1) {
      fprintf(stderr, "Error reading integer.\n");
      exit(EXIT_FAILURE);
  }  
  printf("Integer: %d\n", value);
  
  // Read string
  printf("String: '");
  while(!feof(f)) {
    if(fread(&character, sizeof(char), 1, f) == 0) {
      if(ferror(f)) {
        perror("Error reading character.\n");
        exit(EXIT_FAILURE);
      }
    }
    else
      printf("%c", character);
  }
  printf("'\n");
  
  // Close file
  if(fclose(f) == EOF) {
    perror("Error closing file");
    exit(EXIT_FAILURE);
  }
  
  return EXIT_SUCCESS;
}