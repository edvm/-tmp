#!/usr/bin/env python

# -------------------------------------------------------------------------
# Author: Emiliano Dalla Verde Marcozzi <edvm@fedoraproject.org>
#
# Pipeme lets you receive data from a previous process that used | , for:
# example:
#  $: echo "hello world" | pipeme.py
# You will receive "hello world" as pipeme.py
#

import sys


def main():
    if len(sys.argv) == 1:
        infile = sys.stdin
        outfile = sys.stdout
    elif len(sys.argv) == 2:
        infile = open(sys.argv[1], 'rb')
        outfile = sys.stdout
    else:
        raise SystemExit(sys.argv[0])
    with infile:
        try:
            msg = infile.readline()
        except ValueError as e:
            raise SystemExit(e)
    with outfile:
        # Here add the statements you want to execute with data you received
        # as params
        print(msg)


if __name__ == '__main__':
    main()
