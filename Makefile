# $Id$

prefix ?= /usr/local
exec_prefix ?= $(prefix)
bindir ?= $(exec_prefix)/bin

all:

install:
	install -T backup-data-cd.py $(prefix)/bin/backup-data-cd
