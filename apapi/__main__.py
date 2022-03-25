# -*- coding: utf-8 -*-
import argparse
import sys

from apapi import __title__, __description__, __version__
from apapi import Connection


def main():
    parser = argparse.ArgumentParser(
        prog=__title__,
        description=__description__,
        epilog="""Usage should be similar to official Anaplan Connect:
               https://anaplanenablement.s3.amazonaws.com/Community/Anapedia/Anaplan_Connect_User_Guide_v3.0.0.pdf""",
    )
    # General
    parser.add_argument(
        "-version", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-help", action="help", help=argparse.SUPPRESS)
    parser.add_argument(
        "-d", "-debug", action="store_true", help="Flag: Enable debugging"
    )
    parser.add_argument(
        "-q", "-quiet", action="store_true", help="Flag: Reduce verbosity"
    )
    # Connection config
    parser.add_argument(
        "-u",
        "-user",
        required=True,
        help="Auth: Use basic authentication specified as {username:password}",
    )
    parser.add_argument("-v", "-via", help="Proxy: Use specified proxy settings")
    parser.add_argument(
        "-vu",
        "-viauser",
        help="Proxy: Use proxy configuration specified as {domain/workstation/username:password}",
    )
    parser.add_argument(
        "-auth", "-authServiceUrl", help="Config: Use specified authentication service"
    )
    parser.add_argument("-s", "-service", help="Config: Use specified API service")
    parser.add_argument(
        "-ct", "-httptimeout", help="Config: Use connection timeout as specified"
    )
    parser.add_argument(
        "-mrc", "-maxretrycount", help="Config: Use retry count as specified"
    )
    parser.add_argument(
        "-rt", "-retrytimeout", help="Config: Use retry timeout as specified"
    )
    # Chaining IDs
    parser.add_argument(
        "-w", "-workspace", help="Info: Use workspace specified by ID/name"
    )
    parser.add_argument("-m", "-model", help="Info: Use model specified by ID/name")
    parser.add_argument("-l", "-list", help="Info: Use list specified by ID/name")
    parser.add_argument("-mo", "-module", help="Info: Use module specified by ID/name")
    parser.add_argument("-vi", "-view", help="Info: Use view specified by ID/name")
    # Additional arguments & output config
    parser.add_argument("-chunksize", help="Info: Use given max chunk size for imports")
    parser.add_argument("-pages", help="Info: Use given pages selection for cells read")
    parser.add_argument(
        "-xm",
        "-mappingproperty",
        help="Info: Use given {dimension:item} selection for import",
    )
    parser.add_argument(
        "-xl", "-locale", help="Info: Use specified ISO language and country code"
    )
    parser.add_argument(
        "-o", "-output", help="Info: Save errors dump to specified path"
    )
    parser.add_argument("-f", "-file", help="Info: Use file specified by ID/name")
    parser.add_argument(
        "-im",
        "-itemmappingproperty",
        help="Info: Path to mapping between local and Anaplan columns",
    )
    # Actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "-i", "-import", help="Action: Run import specified by ID/name"
    )
    action_group.add_argument(
        "-e", "-export", help="Action: Run export specified by ID/name"
    )
    action_group.add_argument(
        "-a", "-action", help="Action: Run action specified by ID/name"
    )
    action_group.add_argument(
        "-pr", "-process", help="Action: Run process specified by ID/name"
    )
    action_group.add_argument(
        "-I",
        "-imports",
        action="store_true",
        help="Action: Get available model imports definitions",
    )
    action_group.add_argument(
        "-E",
        "-exports",
        action="store_true",
        help="Action: Get available model exports definitions",
    )
    action_group.add_argument(
        "-A",
        "-actions",
        action="store_true",
        help="Action: Get available model actions definitions",
    )
    action_group.add_argument(
        "-P",
        "-processes",
        action="store_true",
        help="Action: Get available model processes definitions",
    )
    action_group.add_argument(
        "-F",
        "-files",
        action="store_true",
        help="Action: Get available model files definitions",
    )
    action_group.add_argument(
        "-W",
        "-workspaces",
        action="store_true",
        help="Action: Get available workspaces",
    )
    action_group.add_argument(
        "-M", "-models", action="store_true", help="Action: Get available models"
    )
    action_group.add_argument(
        "-L", "-lists", action="store_true", help="Action: Get available model lists"
    )
    action_group.add_argument(
        "-MO",
        "-modules",
        action="store_true",
        help="Action: Get available model modules",
    )
    action_group.add_argument(
        "-V", "-views", action="store_true", help="Action: Get available model views"
    )
    action_group.add_argument(
        "-putItems:csv", help="Action: Add items to list from CSV"
    )
    action_group.add_argument(
        "-putItems:json", help="Action: Add items to list from JSON"
    )
    action_group.add_argument(
        "-updateItems:csv", help="Action: Update list items from CSV"
    )
    action_group.add_argument(
        "-updateItems:json", help="Action: Update list items from JSON"
    )
    action_group.add_argument(
        "-upsertItems:csv", help="Action: Upsert (add or update) list items from CSV"
    )
    action_group.add_argument(
        "-upsertItems:json", help="Action: Upsert (add or update) list items from JSON"
    )
    action_group.add_argument(
        "-deleteItems:csv", help="Action: Delete items from list from CSV"
    )
    action_group.add_argument(
        "-deleteItems:json", help="Action: Delete items from list from JSON"
    )
    # Input options
    put_group = parser.add_mutually_exclusive_group()
    put_group.add_argument(
        "-p", "-put", help="Input option: Get data from specified path"
    )
    put_group.add_argument(
        "-putc",
        action="store_true",
        help="Input option: Get data as tab-separated from terminal",
    )
    put_group.add_argument(
        "-puts", action="store_true", help="Input option: Get data from terminal"
    )
    # Output options
    get_group = parser.add_mutually_exclusive_group()
    get_group.add_argument("-t", "-get", help="Output option: write to specified path")
    get_group.add_argument(
        "-getc",
        action="store_true",
        help="Output option: Display file content as tab-separated in terminal",
    )
    get_group.add_argument(
        "-gets",
        action="store_true",
        help="Output option: Display file content in terminal",
    )
    get_group.add_argument(
        "-get:csv", help="Output option: write to specified path as CSV"
    )
    get_group.add_argument(
        "-get:csv_sc",
        help="Output option: write single-column view to specified path as CSV",
    )
    get_group.add_argument(
        "-get:csv_mc",
        help="Output option: write multi-column view to specified path as CSV",
    )
    get_group.add_argument(
        "-get:json", help="Output option: write to specified path as JSON"
    )
    # Execute types
    execute_group = parser.add_mutually_exclusive_group()
    execute_group.add_argument(
        "-x", "-execute", action="store_true", help="Execute type: execute action"
    )
    execute_group.add_argument(
        "-x:all",
        "-execute:all",
        action="store_true",
        help="Execute type: get list items with properties",
    )
    execute_group.add_argument(
        "-emd", action="store_true", help="Execute type: get export's details"
    )

    args = parser.parse_args(args=None if sys.argv[1:] else ["-h"])


if __name__ == "__main__":
    main()
