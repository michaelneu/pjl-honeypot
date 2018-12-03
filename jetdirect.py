#!/usr/bin/env python3

import os
import sys
import socket
import logging
import re
import hashlib
from collections import defaultdict

class JPLServer:
    def __init__(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self, port=9100, backlog=100):
        self._server.bind(("0.0.0.0", port))
        self._server.listen(backlog)

        logging.info("listening on port %d" % port)

    def close(self):
        self._server.close()

    def accept(self):
        client, addr = self._server.accept()
        ip = addr[0]
        logging.info("%s connected" % ip)

        return JPLClient(client, ip)

class JPLClient:
    def __init__(self, client, address):
        self._client = client
        self._address = address

    def get_command(self, junk_size=1024):
        command = b""

        while True:
            packet = self._client.recv(junk_size)

            if not packet:
                break

            command += packet

            if b"\r\n" in command:
                break

        logging.info("received command '%s' from %s" % (command, self._address))

        return command

    def reply(self, message):
        logging.info("sending '%s' to %s" % (message, self._address))
        self._client.send(message)

    def close(self):
        self._client.close()

class Filesystem:
    def __init__(self):
        self._fs = defaultdict(defaultdict)

    def split_path(self, path):
        return [part for part in re.split(r"(\\|/)", path) if part.strip() not in ["", "/", "\\"]]

    def add_file(self, name, content):
        parts = self.split_path(name)
        cwd = self._fs

        for part in parts[:-1]:
            cwd[part] = defaultdict(defaultdict)
            cwd = cwd[part]

        cwd[parts[-1]] = content

    def listdir(self, name=""):
        parts = self.split_path(name)
        cwd = self._fs

        for part in parts:
            if part not in cwd:
                return "FILEERROR=1"

            cwd = cwd[part]

        if isinstance(cwd, str):
            return "%s TYPE=FILE SIZE=%d" % (parts[-1], len(cwd))

        directory = [
            ". TYPE=DIR",
        ]

        if cwd != self._fs:
            directory.append(".. TYPE=DIR")

        for element in cwd:
            if isinstance(cwd[element], str):
                directory.append("%s TYPE=FILE SIZE=%d" % (element, len(cwd[element])))
            else:
                directory.append("%s TYPE=DIR" % element)

        return "\n".join(directory)

fs = Filesystem()
fs.add_file("0:\\pcl\\macros\\jobs", "")

commands = {
    "@PJL": {
        "COMMENT": "",
        "ENTER": {
            "LANGUAGE": {
                "PCL": "E . . . . PCL Job . . . . E",
                "POSTSCRIPT": "%!PS-ADOBE ... PostScript print job ...",
            }
        },
        "JOB": "",
        "EOJ": "",
        "DEFAULT": "",
        "SET": "",
        "INITIALIZE": "",
        "RESET": "",
        "INQUIRE": {
            "RET": "MEDIUM",
            "PAGEPROTECT": "OFF",
            "RESOLUTION": "600",
            "PERSONALITY": "AUTO",
            "TIMEOUT": "15",
            "LPARM:PCL": {
                "PITCH": "10.00",
                "PTSIZE": "12.00",
                "SYMSET": "ROMAN8",
            },
        },
        "DINQUIRE": {
            "RET": "MEDIUM",
            "PAGEPROTECT": "OFF",
            "RESOLUTION": "600",
            "PERSONALITY": "AUTO",
            "TIMEOUT": "15",
            "LPARM:PCL": {
                "PITCH": "10.00",
                "PTSIZE": "12.00",
                "SYMSET": "ROMAN8",
            },
        },
        "ECHO": lambda command: command,
        "INFO": {
            "ID": "HP LASERJET 4ML",
            "CONFIG": "IN TRAYS [3 ENUMERATED]\n\tINTRAY1 MP\n\tINTRAY2 PC\n\tINTRAY3 LC\nENVELOPE TRAY\nOUT TRAYS [1 ENUMERATED]\n\tNORMAL FACEDOWN\nPAPERS [9 ENUMERATED]\n\tLETTER\n\tLEGAL\n\tA4\n\tEXECUTIVE\n\tMONARCH\n\tCOM10\n\tDL\n\tC5\n\tB5\nLANGUAGES [2 ENUMERATED]\n\tPCL\n\tPOSTSCRIPT\nUSTATUS [4 ENUMERATED]\n\tDEVICE\n\tJOB\n\tPAGE\n\tTIMED\nFONT CARTRIDGE SLOTS [1 ENUMERATED]\n\tCARTRIDGE\nMEMORY=2097152\nDISPLAY LINES=1\nDISPLAY CHARACTER SIZE=16",
            "FILESYS": "VOLUME TOTAL SIZE FREE SPACE LOCATION LABEL STATUS\n0:     1755136    1718272    <HT>     <HT>  READ-WRITE",
            "MEMORY": "TOTAL=1494416\nLARGEST=1494176",
            "PAGECOUNT": "PAGECOUNT=183933",
            "STATUS": "CODE=10001\nDISPLAY=\"Non HP supply in use\"\nONLINE=TRUE",
            "VARIABLES": "COPIES=1 [2 RANGE]\n\t1\n\t999\nPAPER=LETTER [3 ENUMERATED]\n\tLETTER\n\tLEGAL\n\tA4\nORIENTATION=PORTRAIT [2 ENUMERATED]\n\tPORTRAIT\n\tLANDSCAPE\nFORMLINES=60 [2 RANGE]\n\t5\n\t128\nMANUALFEED=OFF [2 ENUMERATED]\n\tOFF\n\tON\nRET=MEDIUM [4 ENUMERATED]\n\tOFF\n\tLIGHT\n\tMEDIUM\n\tDARK\nPAGEPROTECT=OFF [4 ENUMERATED]\n\tOFF\n\tLETTER\n\tLEGAL\n\tA4\nRESOLUTION=600 [2 ENUMERATED]\n\t300\n\t600\nPERSONALITY=AUTO [3 ENUMERATED]\n\tAUTO\n\tPCL\n\tPOSTSCRIPT\nTIMEOUT=15 [2 RANGE]\n\t5\n\t300\nMPTRAY=CASSETTE [3 ENUMERATED]\n\tMANUAL\n\tCASSETTE\n\tFIRST\nINTRAY1=UNLOCKED [2 ENUMERATED]\n\tUNLOCKED\n\tLOCKED\nINTRAY2=UNLOCKED [2 ENUMERATED]\n\tUNLOCKED\n\tLOCKED\nINTRAY3=UNLOCKED [2 ENUMERATED]\n\tUNLOCKED\n\tLOCKED\nCLEARABLEWARNINGS=ON [2 ENUMERATED READONLY]\n\tJOB\n\tON\nAUTOCONT=OFF [2 ENUMERATED READONLY]\n\tOFF\n\tON\n\nDENSITY=3 [2 RANGE READONLY]\n\t1\n\t5\nLOWTONER=ON [2 ENUMERATED READONLY]\n\tOFF\n\tON\nINTRAY1SIZE=LETTER [9 ENUMERATED READONLY]\n\tLETTER\n\tLEGAL\n\tA4\n\tEXECUTIVE\n\tCOM10\n\tMONARCH\n\tC5\n\tDL\n\tB5\nINTRAY2SIZE=LETTER [4 ENUMERATED READONLY]\n\tLETTER\n\tLEGAL\n\tA4\n\tEXECUTIVE\nINTRAY3SIZE=LETTER [4 ENUMERATED READONLY]\n\tLETTER\n\tLEGAL\n\tA4\n\tEXECUTIVE\nINTRAY4SIZE=COM10 [5 ENUMERATED READONLY]\n\tCOM10\n\tMONARCH\n\tC5\n\tDL\n\tB5\nLPARM:PCL FONTSOURCE=I [1 ENUMERATED]\n\tI\nLPARM:PCL FONTNUMBER=0 [2 RANGE]\n\t0\n\t50\nLPARM:PCL PITCH=10.00 [2 RANGE]\n\t0.44\n\t99.99\nLPARM:PCL PTSIZE=12.00 [2 RANGE]\n\t4.00\n\t999.75\nLPARM:PCL SYMSET=ROMAN8 [4 ENUMERATED]\n\tROMAN8\n\tISOL1\n\tISOL2\n\tWIN30\nLPARM:POSTSCRIPT PRTPSERRS=OFF [2 ENUMERATED]\n\tOFF\n\tON",
            "USTATUS": "DEVICE=OFF [3 ENUMERATED]\n\tOFF\n\tON\n\tVERBOSE\nJOB=OFF [2 ENUMERATED]\n\tOFF\n\tON\nPAGE=OFF [2 ENUMERATED]\n\tOFF\n\tON\nTIMED=0 [2 RANGE]\n\t5\n\t300",
        },
        "USTATUSOFF": "",
        "USTATUS": {
            "DEVICE": "CODE=10001\nDISPLAY=\"Non HP supply in use\"\nONLINE=TRUE",
            "JOB": "",
            "PAGE": "",
            "TIMED": "CODE=10001\nDISPLAY=\"Non HP supply in use\"\nONLINE=TRUE",
        },
        "RDYMSG": "",
        "OPMSG": "",
        "STMSG": "",
        "FSAPPEND": "",
        "FSDELETE": "",
        "FSDIRLIST": lambda command: fs.listdir(re.findall(r"\"([^\"]+)\"", command)[0]),
        "FSDOWNLOAD": "",
        "FSINIT": "",
        "FSMKDIR": "",
        "FSQUERY": lambda command: fs.listdir(re.findall(r"\"([^\"]+)\"", command)[0]),
        "FSUPLOAD": "",
    },
}

def log_command(command):
    logging.info("couldn't parse command '%s'" % command)

    return "?"

def find_action(command):
    search_area = commands
    parsed_command = command.strip()

    if not parsed_command:
        return None

    while len(parsed_command) > 0:
        could_parse = False

        if not isinstance(search_area, dict):
            break

        for (subcommand, area) in search_area.items():
            if subcommand == "":
                continue

            if parsed_command.lower().startswith(subcommand.lower()):
                parsed_command = parsed_command[len(subcommand):].strip()
                search_area = area
                could_parse = True
                break

        if not could_parse:
            logging.debug("unknown argument '%s'" % parsed_command)
            return None

    while isinstance(search_area, dict):
        if "" not in search_area.keys():
            return None

        search_area = search_area[""]

    return search_area


def run_command(command):
    command = command.strip()
    logging.debug("parsing '%s'" % command)
    action = find_action(command)

    if action == None:
        return log_command(command)

    if isinstance(action, str):
        logging.debug("found '%s' for '%s'" % (action, command))
        return action

    logging.debug("executing found action for '%s'" % command)
    try:
        result = action(command)
    except Exception as error:
        logging.warning("error in action: %s" % str(error))
        return log_command(command)

    logging.debug("execution result '%s' for '%s'" % (result, command))

    return result

if __name__ == "__main__":
    if not (3 <= len(sys.argv) <= 4):
        print("usage: %s PORT PCL_DIRECTORY [LOGFILE]" % sys.argv[0])
        exit(1)

    port = int(sys.argv[1])
    pcl_directory = sys.argv[2]
    log_handlers = [logging.StreamHandler()]

    if len(sys.argv) == 4:
        logfile = sys.argv[3]
        log_handlers.append(logging.FileHandler(logfile))

    logging.basicConfig(
        level = logging.DEBUG,
        format="%(asctime)s [%(levelname)s]  %(message)s",
        handlers=log_handlers
    )

    if not os.path.exists(pcl_directory):
        logging.warning("pcl directory '%s' not found" % pcl_directory)
        exit(2)

    server = JPLServer()
    server.listen(port)

    while True:
        try:
            client = server.accept()
        except KeyboardInterrupt:
            break

        while True:
            try:
                program = client.get_command()

                if program.startswith(b"\x1bE\x1b&l"):
                    md5 = hashlib.md5()
                    md5.update(program)
                    file_hash = md5.hexdigest()
                    filename = os.path.join(pcl_directory, file_hash)
                    logging.info("received document %s" % filename)

                    with open(filename, "wb") as file_handle:
                        file_handle.write(program)
                    continue

                if len(program) > 0 and program[0] == ord(b"\x1b"):
                    program_start = program.index(b"@")
                    program_delimiter = program[:program_start]
                    program = program[len(program_delimiter):-len(program_delimiter)]

                program = program.decode("utf-8").strip()
            except KeyboardInterrupt:
                break

            if not program:
                break

            replies = []

            for command in program.split("\r\n"):
                command_result = run_command(command)
                result = (command_result + "\n").replace("\n", "\r\n")
                replies.append(result)

            reply = bytes("\r\n".join(replies), "utf-8")
            client.reply(reply)

        client.close()

    server.close()
