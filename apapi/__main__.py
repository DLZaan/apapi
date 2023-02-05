import argparse
import sys

from apapi import __description__, __title__, __version__


def main():
    parser = argparse.ArgumentParser(
        prog=__title__,
        description=__description__,
        epilog="""Usage should be similar to official Anaplan Connect:
               https://anaplanenablement.s3.amazonaws.com/Community/Anapedia/Anaplan_Connect._User_Guide_v4.0.3.pdf""",
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
        help="Auth: Provide basic auth info (password can be also given later)",
        metavar="{username:password}",
    )
    parser.add_argument(
        "-v", "-via", help="Proxy: Use specified proxy settings", metavar="{proxy}"
    )
    parser.add_argument(
        "-vu",
        "-viauser",
        help="Proxy: Use proxy configuration {domain/workstation optional}",
        metavar="{domain/workstation/username:password}",
    )
    parser.add_argument(
        "-auth",
        "-authServiceUrl",
        help="Config: Use specified authentication service",
        metavar="{url}",
    )
    parser.add_argument(
        "-s", "-service", help="Config: Use specified API service", metavar="{url}"
    )
    parser.add_argument(
        "-ct",
        "-httptimeout",
        type=float,
        help="Config: Use connection timeout as specified",
        metavar="{seconds}",
    )
    parser.add_argument(
        "-mrc",
        "-maxretrycount",
        type=int,
        help="Config: Use retry count as specified",
        metavar="{count}",
    )
    parser.add_argument(
        "-rt",
        "-retrytimeout",
        type=float,
        help="Config: Use retry timeout as specified",
        metavar="{seconds}",
    )
    # Chaining IDs
    parser.add_argument(
        "-w", "-workspace", help="Info: Use specified workspace", metavar="{ID/name}"
    )
    parser.add_argument(
        "-m", "-model", help="Info: Use specified model", metavar="{ID/name}"
    )
    parser.add_argument(
        "-l", "-list", help="Info: Use specified list", metavar="{ID/name}"
    )
    parser.add_argument(
        "-mo", "-module", help="Info: Use specified module", metavar="{ID/name}"
    )
    parser.add_argument(
        "-vi", "-view", help="Info: Use specified view", metavar="{ID/name}"
    )
    # Additional arguments & output config
    parser.add_argument(
        "-chunksize",
        type=float,
        help="Info: Use given max chunk size for imports",
        metavar="{MBs}",
    )
    parser.add_argument(
        "-pages",
        help="Info: Use given pages selection for cells read",
        metavar="{pages}",
    )
    parser.add_argument(
        "-xm",
        "-mappingproperty",
        help="Info: Use given selection for import",
        metavar="{dimension:item}",
    )
    parser.add_argument(
        "-xl",
        "-locale",
        help="Info: Use specified ISO language and country code",
        metavar="{lang_country}",
    )
    parser.add_argument(
        "-o",
        "-output",
        help="Info: Save errors dump to specified path",
        metavar="{path}",
    )
    parser.add_argument(
        "-f", "-file", help="Info: Use specified file", metavar="{ID/name}"
    )
    parser.add_argument(
        "-im",
        "-itemmappingproperty",
        help="Info: Path to mapping between local and Anaplan columns",
        metavar="{path}",
    )
    # Actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "-i", "-import", help="Action: Run specified import", metavar="{ID/name}"
    )
    action_group.add_argument(
        "-e", "-export", help="Action: Run specified export", metavar="{ID/name}"
    )
    action_group.add_argument(
        "-a", "-action", help="Action: Run specified action", metavar="{ID/name}"
    )
    action_group.add_argument(
        "-pr", "-process", help="Action: Run specified process", metavar="{ID/name}"
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
        "-putItems:csv", help="Action: Add items to list from CSV", metavar="{path}"
    )
    action_group.add_argument(
        "-putItems:json", help="Action: Add items to list from JSON", metavar="{path}"
    )
    action_group.add_argument(
        "-updateItems:csv", help="Action: Update list items from CSV", metavar="{path}"
    )
    action_group.add_argument(
        "-updateItems:json",
        help="Action: Update list items from JSON",
        metavar="{path}",
    )
    action_group.add_argument(
        "-upsertItems:csv",
        help="Action: Upsert (add or update) list items from CSV",
        metavar="{path}",
    )
    action_group.add_argument(
        "-upsertItems:json",
        help="Action: Upsert (add or update) list items from JSON",
        metavar="{path}",
    )
    action_group.add_argument(
        "-deleteItems:csv",
        help="Action: Delete items from list from CSV",
        metavar="{path}",
    )
    action_group.add_argument(
        "-deleteItems:json",
        help="Action: Delete items from list from JSON",
        metavar="{path}",
    )
    # Input options
    put_group = parser.add_mutually_exclusive_group()
    put_group.add_argument(
        "-p",
        "-put",
        help="Input option: Get data from specified path",
        metavar="{path}",
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
    get_group.add_argument(
        "-t", "-get", help="Output option: write to specified path", metavar="{path}"
    )
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
        "-get:csv",
        help="Output option: write to specified path as CSV",
        metavar="{path}",
    )
    get_group.add_argument(
        "-get:csv_sc",
        help="Output option: write single-column view to specified path as CSV",
        metavar="{path}",
    )
    get_group.add_argument(
        "-get:csv_mc",
        help="Output option: write multi-column view to specified path as CSV",
        metavar="{path}",
    )
    get_group.add_argument(
        "-get:json",
        help="Output option: write to specified path as JSON",
        metavar="{path}",
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

    args_dict = vars(parser.parse_args(args=None if sys.argv[1:] else ["-h"]))

    raise NotImplementedError("Apapi module execution is not supported yet.")


if __name__ == "__main__":
    main()
