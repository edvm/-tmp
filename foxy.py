#!/usr/bin/env python

# -------------------------------------------------------------------------
# Author: Emiliano Dalla Verde Marcozzi <edvm@fedoraproject.org>
#
# Foxy helps you launch process and check if the process you want to run
# is already running. I used this tool in cronjobs for example, to not let
# cronjobs overlap
#

from contextlib import contextmanager
from hashlib import sha256
import subprocess
import logging
import shlex
import sys
import os


FOXY_LOGFILE = '/tmp/foxy.log'
FOXY_PIDS = '/tmp/foxy'
if not os.path.isdir(FOXY_PIDS):
    os.makedirs(FOXY_PIDS)


def logthis(msg, as_='info'):
    FORMAT = '%(levelname)s %(asctime)-15s %(message)s'
    logging.basicConfig(filename=FOXY_LOGFILE,
                        level=logging.INFO,
                        format=FORMAT)
    logger = logging.getLogger('foxy')
    getattr(logger, as_)(msg)


def get_pid(cmd):
    if sys.version_info >= (3, 0):
        cmd = cmd.encode('utf-8')
    pid = sha256(cmd).hexdigest()
    return os.path.join(FOXY_PIDS, pid)


def process_is_running(pidfile):
    with open(pidfile, 'r') as fp:
        pid = fp.readline().strip()
        return os.path.isdir('/proc/%s' % pid)


@contextmanager
def execthis(cmd):
    pid = get_pid(cmd)
    is_running = False
    if os.path.isfile(pid) and process_is_running(pid):
        logthis('process running: %s' % pid)
        is_running = True
    yield is_running
    if is_running is False and os.path.isfile(pid):
        os.unlink(pid)


def exec_process(cmd):

    with open(get_pid(cmd), 'w') as fp:
        command = shlex.split(cmd)
        try:
            process = subprocess.Popen(command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            fp.write("%s" % process.pid)
            fp.close()
            stdout, stderr = process.communicate()
            if stderr != '':
                msg = '%s failed\n%s' % (cmd, stderr)
                logthis(msg, as_='error')
        except Exception as exc:
            msg = '%s raised %s' % (cmd, repr(exc))
            logthis(msg, as_='critical')


if __name__ == '__main__':
    cmd = ' '.join((x for x in sys.argv[1:]))
    with execthis(cmd) as is_running:
        if is_running is False:
            exec_process(cmd)
