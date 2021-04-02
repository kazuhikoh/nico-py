#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import click

from . import command

@click.group()
def cli():
    pass

@cli.command()
@click.argument('channel')
def list(channel):
    ok = command.list(channel)
    sys.exit( 0 if ok else 1 )

@cli.command()
@click.argument('input') 
@click.argument('output', default='out.mp4')
def download(input, output):
    command.download(input, output)

def main():
    cli()

