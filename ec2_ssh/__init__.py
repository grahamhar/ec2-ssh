import boto3
import cmd

ec2_client = None
instance_tag_keys = []
instance_key = 'Name'
instance_key_value = ''


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
        instances = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances']]
        return instances

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
            prompt = '(Tag:"{}" Vaule:"{}") '.format(instance_key, instance_key_value)
        else:
            print('Unknown value for tag key, it remains set to: {}'.format(instance_key))

    def complete_set_key(self, text, line, begidx, endidx):
        global instance_tag_keys
        if not instance_tag_keys:
            instance_tag_keys = self.get_unique_instance_tag_keys()
        return sorted([tag_key for tag_key in instance_tag_keys if tag_key.startswith(text)])


if __name__ == '__main__':
    EC2HostFinder().cmdloop()
