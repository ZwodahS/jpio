#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Check out https://github.com/ZwodahS/jpio for the latest version of the software.

import sys
import getopt
import json
from . import jstql

def print_help():
    print("jpio [options] <query>")
    print("    options:")
    print()
    print("    -f --infile          : read data from file instead of stdin")
    print("    -o --outfile         : output to file instead of stdout")
    print("    -s --splitlist       : split the list content each to their own line")
    print("    -p --pretty          : pretty print the json")
    print("    -h --help            : print this help")
    print("    -i --interactive     : interactive mode")
    print("    --list-functions     : list the available functions")


def print_functions():
    import extensions
    for fname, func in extensions.registered_functions.items():
        print("    {0} : {1}".format(fname, func.description))
        for use in func.usages:
            print("          {0}".format(use))


def print_result(result, out, split=False, pretty=False):
    if split and isinstance(result, list):
        for item in result:
            print_result(item, out, split=False, pretty=pretty)
    else:
        if type(result) in [dict, list]:
            if not pretty:
                print(json.dumps(result), file=out)
            else:
                print(json.dumps(result, indent=4, separators=(",", ": ")))
        else:
            print(result, file=out)


def start_interactive(data, splitfile, pretty):
    while True:
        try:
            command = input("Enter query:")
        except EOFError:
            break

        if command == "exit":
            break

        try:
            print("Parsing")
            commands = jstql.parse(command)
        except JSTQLParserException as e:
            print("Error parsing command")
            continue

        try:
            print("Running")
            result = jstql.run_query(data, commands)
        except Exception as e:
            import traceback; traceback.print_exc()
            import pdb; pdb.set_trace()
            continue

        print_result(result, sys.stdout, split=splitfile, pretty=pretty)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:o:hspi", ["infile=", "outfile", "help", "splitlist", "list-functions", "pretty", "interactive"])
        opts = { opt : arg for opt, arg in opts }
    except getopt.GetoptError as e:
        import traceback; traceback.print_exc()
        print_help()
        sys.exit(1)

    if "-h" in opts or "--help" in opts:
        print_help()
        sys.exit(0)

    if "--list-functions" in opts:
        print_functions()
        sys.exit(0)

    infile = opts.get("-f") or opts.get("--infile") or None
    outfile = opts.get("-o") or opts.get("--outfile") or None
    pretty = ("-p" in opts) or ("--pretty" in opts) or None
    is_interactive = (("-i" in opts) or ("--interactive" in opts) or False) and (infile is not None)
    splitfile = False

    if "-s" in opts or "--splitlist" in opts:
        splitfile = True

    try:
        if not infile:
            lines = sys.stdin.readlines()
        else:
            f = open(infile)
            lines = f.readlines()
            f.close()

        try:
            if is_interactive:
                print("Loading file ... ")
            d = json.loads("".join(lines))
        except Exception:
            raise jstql.JSTQLException(message="Error loading json file")

        if not is_interactive or not infile:
            result = jstql.run_query(d, jstql.parse(args[0] if len(args) == 1 else ""))

            if outfile:
                with open(outfile, 'w') as f:
                    print_result(result, f, split=splitfile, pretty=pretty)
            else:
                print_result(result, sys.stdout, split=splitfile, pretty=pretty)

        else:
            start_interactive(d, splitfile, pretty)

        sys.exit(0)
    except jstql.JSTQLException as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    except FileNotFoundError as e:
        print("File not found : {0}".format(e.filename), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        import traceback; traceback.print_exc()
        print("Unexpected error has occurs, please report this on github to make this software better", file=sys.stderr)


if __name__ == "__main__":
    main()
