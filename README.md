# SuSy Test
Um script para automatizar o teste de programas
a serem submetidos à plataforma SuSy da Unicamp.

## Instalando
```
$ git clone https://github.com/a1varo-costa/susytest.git
$ cd susytest
$ pip install .
```

## Uso
```
$ susytest --help
Usage: susytest [OPTIONS] URL PROG

  A script to automate the testing of programs to be submitted to Unicamp's
  SuSy platform.

Options:
  -n, --nodiff   Disable output diff.
  -v, --verbose  Enable verbose output.
  --version      Show the version and exit.
  --help         Show this message and exit.
```