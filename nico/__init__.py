#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

@click.group()
def cli():
    pass

@cli.command()
def piyo():
    click.echo('🐥')

def main():
    cli()

