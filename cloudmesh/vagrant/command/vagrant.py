from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command

from docopt import docopt
import cloudmesh.vagrant as vagrant
from cloudmesh_client.common.dotdict import dotdict
from pprint import pprint
from cloudmesh_client.common.Printer import Printer
from cloudmesh_client.common.Shell import Shell
import sys
import os


# from cloudmesh_vagrant.version import __version__


def defaults():
    """
    default values
    :return: a number of default values for memory, image, and script
    :rtype: dotdict
    """
    d = dotdict()
    d.memory = 1024
    # d.image = "ubuntu/xenial64"
    d.image = "ubuntu/trusty64"
    d.port = 8080
    d.script = None
    return d


def _convert(lst, id="name"):
    d = {}
    for entry in lst:
        d[entry[id]] = entry
    return d


def _list_print(l, output, order=None):
    if output in ["yaml", "dict", "json"]:
        l = _convert(l)

    result = Printer.write(l,
                           order=order,
                           output=output)

    if output in ["table", "yaml", "json", "csv"]:
        print(result)
    else:
        pprint(result)


class VagrantCommand(PluginCommand):
    @command
    def do_vagrant(self, args, arguments):
        """
        ::
    
          Usage:
            vagrant version [--format=FORMAT]
            vagrant image list [--format=FORMAT]
            vagrant image find NAME
            vagrant image add NAME
            vagrant vm list [--format=FORMAT] [-v]
            vagrant vm delete NAME
            vagrant vm config NAME
            vagrant vm ip NAME [--all]
            vagrant create NAME ([--memory=MEMORY]
                              [--image=IMAGE]
                              [--script=SCRIPT] | list)
            vagrant vm boot NAME ([--memory=MEMORY]
                               [--image=IMAGE]
                               [--port=PORT]
                               [--script=SCRIPT] | list)
            vagrant vm ssh NAME [-e COMMAND]
        """
        arguments.format = arguments["--format"] or "table"
        arguments.verbose = arguments["-v"]
        arguments.all = arguments["--all"]

        """
        if arg.version:
            versions = {
                "vagrant": {
                   "attribute": "Vagrant Version",
                    "version": vagrant.version(),
                },
                "cloudmesh-vagrant ": {
                    "attribute":"cloudmesh vagrant  Version",
                    "version": __version__
                }
            }
            _LIST_PRINT(versions, arg.format)
        """
        if arguments.image and arguments.list:
            l = vagrant.image.list(verbose=arguments.verbose)
            _list_print(l, arguments.format, order=["name", "provider", "date"])

        elif arguments.image and arguments.add:
            l = vagrant.image.add(arguments.NAME)
            print(l)

        elif arguments.image and arguments.find:
            l = vagrant.image.find(arguments.NAME)
            print(l)

        elif arguments.vm and arguments.list:
            l = vagrant.vm.list()
            _list_print(l,
                        arguments.format,
                        order=["name", "state", "id", "provider", "directory"])

        elif arguments.create and arguments.list:

            result = Shell.cat("{NAME}/Vagrantfile".format(**arguments))
            print(result)

        elif arguments.create:

            d = defaults()

            arguments.memory = arguments["--memory"] or d.memory
            arguments.image = arguments["--image"] or d.image
            arguments.script = arguments["--script"] or d.script

            vagrant.vm.create(
                name=arguments.NAME,
                memory=arguments.memory,
                image=arguments.image,
                script=arguments.script)

        elif arguments.config:

            # arguments.NAME
            d = vagrant.vm.info(name=arguments.NAME)

            result = Printer.attribute(d, output=arguments.format)

            print(result)

        elif arguments.ip:

            data = []
            result = vagrant.vm.execute(arguments.NAME, "ifconfig")
            if result is not None:
                lines = result.splitlines()[:-1]
                for line in lines:
                    if "inet addr" in line:
                        line = line.replace("inet addr", "ip")
                        line = ' '.join(line.split())
                        _adresses = line.split(" ")
                        address = {}
                        for element in _adresses:
                            attribute, value = element.split(":")
                            address[attribute] = value
                        data.append(address)
            if arguments.all:
                d = {}
                i = 0
                for e in data:
                    d[str(i)] = e
                    i = i + 1
                result = Printer.attribute(d, output=arguments.format)
                print(result)
            else:
                for element in data:
                    ip = element['ip']
                    if ip == "127.0.0.1" or ip.startswith("10."):
                        pass
                    else:
                        print(element['ip'])

        elif arguments.boot:

            d = defaults()

            arguments.memory = arguments["--memory"] or d.memory
            arguments.image = arguments["--image"] or d.image
            arguments.script = arguments["--script"] or d.script
            arguments.port = arguments["--port"] or d.port

            vagrant.vm.boot(
                name=arguments.NAME,
                memory=arguments.memory,
                image=arguments.image,
                script=arguments.script,
                port=arguments.port)

        elif arguments.delete:

            result = vagrant.vm.delete(name=arguments.NAME)
            print(result)

        elif arguments.ssh:

            if arguments.COMMAND is None:
                os.system("cd {NAME}; vagrant ssh {NAME}".format(**arguments))
            else:
                result = vagrant.vm.execute(arguments.NAME, arguments.COMMAND)
                if result is not None:
                    lines = result.splitlines()[:-1]
                    for line in lines:
                        print(line)

        else:

            print("use help")
