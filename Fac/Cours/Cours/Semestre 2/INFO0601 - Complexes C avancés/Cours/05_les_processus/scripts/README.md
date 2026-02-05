# Scripts of course #7

## Compilation

To compile, type the following command:

```bash
make
```

## Programs/files

Here is the list of the generated programs or files used:
- `background`: program to test CRTL+Z in terminal and `fg` or `bg` commands
- `sigaction`: positionning a handler with `sigaction`
- `kill_server` and `kill_client`: send a signal with `kill`
- `alarm`: use of `pause` and `alarm`
- `sleep`: use of `sleep` and `nanosleep`
- `sigprocmask`: blocking signals with `sigprocmask`
- `sigpending_server` and `sigpending_client`: checking blocked signals with `sigpending`
- `sigsuspend_server` and `sigsuspend_client`: wait for a signal with `sigsuspend`
- `sigqueue`: use of real-time signals and send a value with `sigqueue`
- `sigwaitinfo`: wait for a signal with `sigwaitinfo`