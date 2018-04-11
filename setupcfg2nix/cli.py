from setuptools.config import read_configuration
import argparse
import unittest.mock
import errno
import os
import os.path
import tempfile
import setuptools
import sys
from distutils.errors import DistutilsFileError

requires_sets = [ "install_requires", "setup_requires", "tests_require" ]

def make_declarative(package_dir, out_file):
    cur_dir = os.getcwd()
    cur_path = sys.path[:]
    try:
        os.chdir(package_dir)
        sys.path.insert(0, '.')
        with unittest.mock.patch.object(setuptools, 'setup') as mock_setup:
            import setup

            args, kwargs = mock_setup.call_args
    finally:
        os.chdir(cur_dir)
        sys.path = cur_path

    out_file.write("[metadata]\n")
    out_file.write(f"name = {kwargs['name']}\n")
    out_file.write(f"version = {kwargs['version']}\n\n")
    out_file.write("[options]\n")
    for r in requires_sets:
        deps = kwargs.get(r, [])
        if deps:
            out_file.write(f"{r} =\n")
            for dep in deps:
                out_file.write(f"  {dep}\n")

class IncompleteConfig(Exception):
    pass

def read_configuration_with_fallback(cfg_path):
    try:
        cfg = read_configuration(cfg_path)
        if 'metadata' not in cfg or 'name' not in cfg['metadata']:
            raise IncompleteConfig
        return cfg
    except (IncompleteConfig, DistutilsFileError) as e:
        with tempfile.NamedTemporaryFile(mode='w+', prefix='setup.cfg') as tmp:
            make_declarative(os.path.dirname(cfg_path), tmp)
            tmp.flush()
            return read_configuration_with_fallback(tmp.name)

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
    parser.add_argument('--allow-autogeneration', action='store_true', help='Allow autogeneration of setup.cfg from setup.py when declarative setup.cfg is not available (runs python code in setup.py!)')
    args = parser.parse_args()
    if args.allow_autogeneration:
        cfg = read_configuration_with_fallback(args.cfg)
    else:
        cfg = read_configuration(args.cfg)
    print('{ pname            = "', cfg['metadata']['name'], '";', sep='')
    print('  version          = "', cfg['metadata']['version'], '";', sep='')

    for r in requires_sets:
        print_dependencies(cfg, r)

    print('}')

def print_dependencies(cfg, name):
    deps = cfg['options'].get(name, [])
    if deps:
        print('  ' + name + ' = ')
        print('    [ "', deps[0], '"', sep='')
        for req in deps[1:]:
            print('      "', req, '"', sep='')
        print('    ];')

if __name__ == '__main__':
    main()
