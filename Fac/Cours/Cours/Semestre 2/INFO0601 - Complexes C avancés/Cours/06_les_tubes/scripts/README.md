# Scripts of course #6

## Compilation

To compile, type the following command:

```bash
make
```

## Programs/files

Here is the list of the generated programs or files used:
- `pipe1`: create of a pipe between a process and its child
- `pipe2`: two-way communication between a father and its child
- `pipe3`: using `fcntl` to change file descriptor attributes
- `mkfifo1_server` and `mkfifo1_client`: creation of a named pipe and communication between the two programs
- `mkfifo2_server` and `mkfifo2_client`: creation of a named pipe and two-way communication between the two programs
- `ring`: illustration of programs that communicate using a ring of named pipes
- `ring_exec`: program that automatically runs the `ring` program 5 times
- `dup1`: use `dup` to create a redirection between 2 programs.
- `dup2`: use `dup2` to create a redirection between 2 programs.