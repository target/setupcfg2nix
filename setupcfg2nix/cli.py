from __future__ import print_function
from setuptools.config import read_configuration
import argparse

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
    print('{ pname            = "', cfg['metadata']['name'], '";', sep='')
    print('  version          = "', cfg['metadata']['version'], '";', sep='')

    print_dependencies(cfg, 'install_requires')
    print_dependencies(cfg, 'setup_requires')
    print_dependencies(cfg, 'tests_require')

    print('}')

def print_dependencies(cfg, name):
    deps = cfg['options'].get(name, [])
    if deps:
        print('  ' + name + ' = ')
        print('    [ "', deps[0], '"', sep='')
        for req in deps[1:]:
            print('     "', req, '"', sep='')
        print('    ];')

if __name__ == '__main__':
    main()
