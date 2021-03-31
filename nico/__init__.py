#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from . import command

@click.group()
def cli():
    pass

@cli.command()
@click.argument('input') 
@click.argument('output', default='out.mp4')
def download(input, output):
    command.download(input, output)

def main():
    cli()

