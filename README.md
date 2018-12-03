# PJL Honeypot

This is a very basic PJL or Jetdirect honeypot created as a byproduct of TUM's honeypot and malware analysis course.

When connecting to it via [PRET](https://github.com/RUB-NDS/PRET), you probably won't notice a difference to other printers, and dropping PCL files will store them in a configurable directory (see usage).

The honeypot is a standalone Python 3 script and is contained in a single file, allowing you to drop it on your existing honeypots easily. Furthermore, you can use the [Dockerfile](Dockerfile) to include it in your honeypot setup conveniently. Please refer to the [docker-compose.yml](docker-compose.yml) for using the image within a compose environment.

## Usage

```bash
# no args => shows usage
$ python3 jetdirect.py
usage: jetdirect.py PORT PCL_DIRECTORY [LOGFILE]

# use it e.g like this to
# - listen on port 9100
# - store printed pages in ./prints/
# - log to ./jetdirect.log
$ python3 jetdirect.py 9100 ./prints ./jetdirect.log
```

Additionally, there's a [Makefile](Makefile), which can be used to build and run the honeypot's Docker image:

```bash
# build the docker image
$ make build

# run the honeypot
$ make run

# remove the docker image
$ make clean

# connect to localhost via telnet
$ make jetdirect
```

## Hacking

This honeypot is built around a `commands` dictionary, containing most commands specified in HP's PJL handbook. You can modify that dictionary to match your needs. Commands are traversed via the dictionary, thus `INFO CONFIG` will first go to the `INFO` dictionary, and then search the `CONFIG` key.

Once the honeypot finds a value, it'll interpret it. If it's a plain string, that's what will be sent back to the attacker. If it's a function or lambda, the first argument will be the command string passed in, so you can do your own processing.

The filesystem is stored in `fs`, a read-only dictionary-like structure, allowing traversal and file information. If you want to store actual files in there, simply add their contents via `fs.add_file()`, the "directories" will then be created automatically.

## License

This honeypot is licensed under the [MIT license](LICENSE), so feel free to modify it.
