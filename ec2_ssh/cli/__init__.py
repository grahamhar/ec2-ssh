#!/usr/bin/env python
import random
import subprocess

from collections import defaultdict

import click
import click_completion
import click_completion.core

from ec2_ssh.ec2_helpers import get_ec2_instance_ips, get_instance_tags

cmd_help = "Get hosts to ssh to by AWS Tag Name and Tag Value"
selected_tag_name = None
selected_tag_value = None
tag_instance_ips = defaultdict(lambda: defaultdict(list))


click_completion.init(complete_options=True)


class TagName(click.ParamType):
    name = "Tag Name"

    def __init__(self, choices):
        click.ParamType.__init__(self)
        self.choices = choices

    def convert(self, value, param, ctx):
        global selected_tag_name
        if value in self.choices:
            selected_tag_name = value
            return value
        self.fail('invalid choice')

    def complete(self, ctx, incomplete):
        match = click_completion.completion_configuration.match_incomplete
        return [c for c in self.choices if match(c, incomplete)]


class TagValue(click.ParamType):
    name = "Tag Value"

    def __init__(self, choices):
        click.ParamType.__init__(self)
        self.choices = choices

    def convert(self, value, param, ctx):
        global selected_tag_name, selected_tag_value
        if value in self.choices.get(selected_tag_name, []):
            selected_tag_value = value
            return value
        self.fail('invalid choice')

    def complete(self, ctx, incomplete):
        match = click_completion.completion_configuration.match_incomplete
        return [c for c in self.choices[selected_tag_name] if match(c, incomplete)]


class SSHHosts(click.ParamType):
    name = "SSH Hosts"

    def __init__(self):
        click.ParamType.__init__(self)

    def validate_tag_instance_ips(self):
        global tag_instance_ips
        if not tag_instance_ips[selected_tag_name][selected_tag_value]:
            tag_instance_ips[selected_tag_name][selected_tag_value] = get_ec2_instance_ips(selected_tag_name, selected_tag_value)

    def convert(self, value, param, ctx):
        global tag_instance_ips
        self.validate_tag_instance_ips()
        if value in tag_instance_ips[selected_tag_name][selected_tag_value]:
            return value
        self.fail('invalid choice')

    def complete(self, ctx, incomplete):
        global tag_instance_ips
        self.validate_tag_instance_ips()
        match = click_completion.completion_configuration.match_incomplete
        return [ip_address for ip_address in tag_instance_ips[selected_tag_name][selected_tag_value] if
                match(ip_address, incomplete)]


def execute_ssh(ip_address):
    """ssh to the IP Address"""
    subprocess.call(['ssh {}'.format(ip_address)], shell=True)


@click.group()
def cli(help=cmd_help):
    pass


@cli.command()
@click.argument('tag_key', required=True, type=TagName(get_instance_tags()))
@click.argument('tag_value', required=True, type=TagValue(get_instance_tags()))
@click.argument('ssh_host', required=True, type=SSHHosts())
def ssh(tag_key, tag_value, ssh_host):
    if ssh_host[0].isdigit():
        execute_ssh(ssh_host)
    elif ssh_host == 'all':
        for ip_address in tag_instance_ips[tag_key][tag_value]:
            if ip_address[0].isdigit():
                execute_ssh(ip_address)
    elif ssh_host == 'random':
        ip_addresses = [ip_address for ip_address in tag_instance_ips[tag_key][tag_value] if ip_address[0].isdigit()]
        execute_ssh(random.choice(ip_addresses))


if __name__ == '__main__':
    cli()
