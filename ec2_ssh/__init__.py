import boto3
import cmd
import subprocess

from collections import defaultdict

ec2_client = None
instance_tag_keys = []
instance_tag_values = {}
instance_key = 'Name'
instance_tag_value = ''
instance_ips = defaultdict(lambda: defaultdict(list))


class EC2HostFinder(cmd.Cmd):
    """Find the hosts you need in EC2 by tags"""
    prompt = '(Tag:"Name" Vaule:"") '

    def get_ec2_client(self):
        global ec2_client
        if ec2_client is None:
            ec2_client = boto3.client('ec2')
        return ec2_client

    def get_ec2_instances(self, tag_value, tag_filter='Name'):
        # TODO: handle paginated responses

        response = self.get_ec2_client().describe_instances(
            Filters=[
                {
                    'Name': 'tag:{}'.format(tag_filter),
                    'Values': [
                        tag_value,
                    ]
                },
            ],
            DryRun=False,
            MaxResults=1000
        )
        return [network_interface['PrivateIpAddress'] for reservation in response['Reservations'] for instance in
                reservation['Instances'] for network_interface in instance['NetworkInterfaces']]

    def get_unique_instance_tag_values(self, tag_filter='Name'):
        # TODO: handle paginated responses
        response = self.get_ec2_client().describe_tags(MaxResults=1000, DryRun=False,
                                                       Filters=[{'Name': 'key', 'Values': [tag_filter]},
                                                                {'Name': 'resource-type', 'Values': ['instance', 'reserved-instances']}])
        return set([tag['Value'] for tag in response['Tags']])

    def get_unique_instance_tag_keys(self):
        """
        Get a list of unique instance tag keys
        :return:
        """
        # TODO: handle paginated responses
        response = self.get_ec2_client().describe_tags(MaxResults=1000, DryRun=False,
                                                       Filters=[{'Name': 'resource-type',
                                                                 'Values': ['instance', 'reserved-instances']}])
        return set(tag['Key'] for tag in response['Tags'])

    def do_quit(self, line):
        """Exit back to your native shell"""
        return True

    def do_EOF(self, line):
        """Exit back to your native shell on ctrl-d"""
        return True

    def do_set_key(self, line):
        """Set the key name to filter on"""
        global instance_key, instance_tag_keys, prompt
        if not instance_tag_keys:
            instance_tag_keys = self.get_unique_instance_tag_keys()
        if line in instance_tag_keys:
            instance_key = line
            print('Tag key value set to: {}'.format(line))
            prompt = '(Tag:"{}" Vaule:"{}") '.format(instance_key, instance_tag_value)
        else:
            print('Unknown value for tag key, it remains set to: {}'.format(instance_key))

    def complete_set_key(self, text, line, begidx, endidx):
        global instance_tag_keys
        if not instance_tag_keys:
            instance_tag_keys = self.get_unique_instance_tag_keys()
        return sorted([tag_key for tag_key in instance_tag_keys if tag_key.startswith(text)])

    def do_set_value(self, line):
        """Set the key value to filter on"""
        global instance_tag_values, instance_tag_value, prompt
        if not instance_tag_values:
            instance_tag_values[instance_key] = self.get_unique_instance_tag_values(tag_filter=instance_key)
        if line in instance_tag_values[instance_key]:
            instance_tag_value = line
            print('Tag value set to: {}'.format(line))
            prompt = '(Tag:"{}" Vaule:"{}") '.format(instance_key, instance_tag_value)
        else:
            print('Unknown value for tag value, it remains set to: {}'.format(instance_tag_value))

    def complete_set_value(self, text, line, begidx, endidx):
        """Provide tab completion for key value"""
        global instance_tag_values
        if instance_key not in instance_tag_values.keys():
            instance_tag_values[instance_key] = self.get_unique_instance_tag_values(tag_filter=instance_key)
        return sorted(
            [tag_value for tag_value in instance_tag_values[instance_key] if tag_value.startswith(text)])

    def execute_ssh(self, ip_address):
        """ssh to the provided IP"""
        subprocess.call(['ssh {}'.format(ip_address)], shell=True)

    def do_ssh(self, line):
        """ssh to the selected ip[s]"""
        global instance_ips
        matched_ip = False
        if not instance_ips[instance_key][instance_tag_value]:
            print('Select either an IP address or a partial IP address using TAB complete\n')
            return
        if line in instance_ips[instance_key][instance_tag_value]:
            self.execute_ssh(line)
            matched_ip = True
        else:
            for ip_address in instance_ips[instance_key][instance_tag_value]:
                if ip_address.startswith(line):
                    self.execute_ssh(ip_address)
                    matched_ip = True
        if not matched_ip:
            print('The supplied IP didn\'t match any EC2 instances tagged with {}:{}'.format(instance_key,
                                                                                             instance_tag_value))
        else:
            print('SSH to all hosts complete')

    def complete_ssh(self, text, line, begidx, endidx):
        """Provide tab completion for ssh"""
        global instance_ips
        if not instance_ips[instance_key][instance_tag_value]:
            instance_ips[instance_key][instance_tag_value] = self.get_ec2_instances(tag_value=instance_tag_value,
                                                                                    tag_filter=instance_key)
        return sorted(
            ip_address for ip_address in instance_ips[instance_key][instance_tag_value] if ip_address.startswith(text))


if __name__ == '__main__':
    EC2HostFinder().cmdloop()
