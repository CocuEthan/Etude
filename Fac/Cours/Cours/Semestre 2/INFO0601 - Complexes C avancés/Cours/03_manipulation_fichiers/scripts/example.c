/**
 * This program illustrates how `strace` works.
 * Type the following command:
 *   strace ./example
 *    => Create the file toto.txt
 * The following commands illustrate the `strace` options:
 *   strace -o output.txt ./example
 *    => Create an output file `output.txt`
 *   strace -c -o output.txt ./example
 *    => Create a report
 *   strace -e write,close ./example
 *    => Display only output for `write` and `close` calls
 *   strace -p XXX
 *    => Trace on a running process (XXX is its PID)
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
  FILE *f;
  
  if((f = fopen("toto.txt", "w")) == NULL) {
    perror("An error occurs while opening 'toto.txt'");
    exit(EXIT_FAILURE);
  }
  fprintf(f, "Hello everybody!!!");
  if(fclose(f) != 0) {
      perror("An error occurs while closing 'toto.txt'");
      exit(EXIT_FAILURE);
  }

  return EXIT_SUCCESS;
}