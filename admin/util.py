# -*- coding: utf-8 -*-
#
# Cherokee-admin
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2001-2010 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import os
import sys
import glob
import socket
import CTK

#
# Strings
#
def bool_to_active (b):
    return (_('Deactived'), _('Active'))[bool(b)]

def bool_to_onoff (b):
    return (_('Off'), _('On'))[bool(b)]

def bool_to_yesno (b):
    return (_('No'), _('Yes'))[bool(b)]


#
# Virtual Server
#

def cfg_vsrv_get_next():
    """ Get the prefix of the next vserver """
    tmp = [int(x) for x in CTK.cfg.keys("vserver")]
    tmp.sort()
    next = str(tmp[-1] + 10)
    return "vserver!%s" % (next)

def cfg_vsrv_rule_get_next (pre):
    """ Get the prefix of the next rule of a vserver """
    tmp = [int(x) for x in CTK.cfg.keys("%s!rule"%(pre))]
    tmp.sort()
    if tmp:
        next = tmp[-1] + 100
    else:
        next = 100
    return (next, "%s!rule!%d" % (pre, next))

def cfg_vsrv_rule_find_extension (pre, extension):
    """Find an extension rule in a virtual server """
    for r in CTK.cfg.keys("%s!rule"%(pre)):
        p = "%s!rule!%s" % (pre, r)
        if CTK.cfg.get_val ("%s!match"%(p)) == "extensions":
            if extension in CTK.cfg.get_val ("%s!match!extensions"%(p)):
                return p

def cfg_vsrv_rule_find_regexp (pre, regexp):
    """Find a regular expresion rule in a virtual server """
    for r in CTK.cfg.keys("%s!rule"%(pre)):
        p = "%s!rule!%s" % (pre, r)
        if CTK.cfg.get_val ("%s!match"%(p)) == "request":
            if regexp == CTK.cfg.get_val ("%s!match!request"%(p)):
                return p

#
# Information Sources
#

def cfg_source_get_next ():
    tmp = [int(x) for x in CTK.cfg.keys("source")]
    if not tmp:
        return (1, "source!1")
    tmp.sort()
    next = tmp[-1] + 10
    return (next, "source!%d" % (next))

def cfg_source_find_interpreter (in_interpreter = None,
                                 in_nick        = None):
    for i in CTK.cfg.keys("source"):
        if CTK.cfg.get_val("source!%s!type"%(i)) != 'interpreter':
            continue

        if (in_interpreter and
            in_interpreter in CTK.cfg.get_val("source!%s!interpreter"%(i))):
            return "source!%s" % (i)

        if (in_nick and
            in_nick in CTK.cfg.get_val("source!%s!nick"%(i))):
            return "source!%s" % (i)

def cfg_source_find_empty_port (n_ports=1):
    ports = []
    for i in CTK.cfg.keys("source"):
        host = CTK.cfg.get_val ("source!%s!host"%(i))
        if not host: continue

        colon = host.rfind(':')
        if colon < 0: continue

        port = int (host[colon+1:])
        if port < 1024: continue

        ports.append (port)

    pport = 1025
    for x in ports:
        if pport + n_ports < x:
            return pport

    assert (False)

def cfg_source_find_free_port (host_name='localhost'):
    """Return a port not currently running anything"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host_name, 0))
    addr, port = s.getsockname()
    s.close()
    return port

def cfg_source_get_localhost_addr ():
    x, x, addrs = socket.gethostbyname_ex('localhost')
    if addrs:
        return addrs[0]
    return None

def cfg_get_surrounding_repls (macro, value, n_minus=9, n_plus=9):
    replacements = {}

    tmp = value.split('!')
    pre = '!'.join(tmp[:-1])
    num = int(tmp[-1])

    for n in range(n_minus):
        replacements['%s_minus%d'%(macro,n+1)] = '%s!%d' %(pre, num-(n+1))

    for n in range(n_plus):
        replacements['%s_plus%d'%(macro,n+1)] = '%s!%d' %(pre, num+(n+1))

    return replacements


#
# Paths
#

def path_find_binary (executable, extra_dirs=[], custom_test=None):
    """Find an executable.
    It checks 'extra_dirs' and the PATH.
    The 'executable' parameter can be either a string or a list.
    """

    assert (type(executable) in [str, list])

    dirs = extra_dirs

    env_path = os.getenv("PATH")
    if env_path:
        dirs += filter (lambda x: x, env_path.split(":"))

    for dir in dirs:
        if type(executable) == str:
            tmp = os.path.join (dir, executable)
            if os.path.exists (tmp):
                if custom_test:
                    if not custom_test(tmp):
                        continue
                return tmp
        elif type(executable) == list:
            for n in executable:
                tmp = os.path.join (dir, n)
                if os.path.exists (tmp):
                    if custom_test:
                        if not custom_test(tmp):
                            continue
                    return tmp

def path_find_w_default (path_list, default=''):
    """Find a path.
    It checks a list of paths (that can contain wildcards),
    if none exists default is returned.
    """
    for path in path_list:
        if '*' in path or '?' in path:
            to_check = glob.glob (path)
        else:
            to_check = [path]
        for p in to_check:
            if os.path.exists (p):
                return p
    return default


#
# OS
#
def os_get_document_root():
    if sys.platform == 'darwin':
        return "/Library/WebServer/Documents"
    elif sys.platform == 'linux2':
        if os.path.exists ("/etc/redhat-release"):
            return '/var/www'
        elif os.path.exists ("/etc/fedora-release"):
            return '/var/www'
        elif os.path.exists ("/etc/SuSE-release"):
            return '/srv/www/htdocs'
        elif os.path.exists ("/etc/debian_version"):
            return '/var/www'
        elif os.path.exists ("/etc/gentoo-release"):
            return '/var/www'
        elif os.path.exists ("/etc/slackware-version"):
            return '/var/www'
        return '/var/www'

    return ''


#
# Misc
#
def split_list (value):
    ids = []
    for t1 in value.split(','):
        for t2 in t1.split(' '):
            id = t2.strip()
            if not id:
                continue
            ids.append(id)
    return ids


def lists_differ (a, b):
    """Compare lists disregarding order"""
    if len(a) != len(b):
        return True
    if bool (set(a)-set(b)):
        return True
    if bool (set(b)-set(a)):
        return True
    return False