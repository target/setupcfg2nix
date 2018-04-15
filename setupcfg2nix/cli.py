from setuptools.config import read_configuration
from pkg_resources import Requirement
import argparse
import setuptools

requires_sets = [ "install_requires", "setup_requires", "tests_require" ]

def main():
    """Parses a setup.cfg file and prints a nix representation to stdout.

    The path to the setup.cfg is parsed from sys.argv.

    Args:
        cfg (str): The path to the setup.cfg file, defaults to 'setup.cfg' in the current directory

    Returns:
        None: Prints to stdout

    """
    parser = argparse.ArgumentParser(description='Parse a setuptools setup.cfg into nix expressions')
    parser.add_argument('cfg', metavar='CFG', nargs='?', default='setup.cfg', help='The path to the configuration file (defaults to setup.cfg)')
    args = parser.parse_args()
    cfg = read_configuration(args.cfg)
    print('{')
    print(f"  pname = ''{cfg['metadata']['name']}'';")
    print(f"  version = ''{cfg['metadata']['version']}'';")

    for r in requires_sets:
        print_dependencies(cfg, r)

    print('}')

def print_dependencies(cfg, name):
    deps = cfg['options'].get(name, [])
    if deps:
        print(f"  {name} = [")
        for req in deps:
            # TODO should we care about 'extras'?
            print(f"    ''{Requirement.parse(req).project_name}''")
        print('  ];')

if __name__ == '__main__':
    main()
