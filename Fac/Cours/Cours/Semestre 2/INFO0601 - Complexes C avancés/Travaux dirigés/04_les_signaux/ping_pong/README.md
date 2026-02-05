# Ping pong game

A ping pong game based on real-time signals.

## Compilation

To compile, type the following command:

```bash
make
```

## Programs/files

Here is the list of the generated programs or files used:
- `utils.h` and `utils.c`: utils functions (random)
- `client`: the client
- `server`: the server

## Execution

First, start the server. It shows its PID. Then, run the client by specifying
this PID as argument. The programs stop when the server or the client loses.