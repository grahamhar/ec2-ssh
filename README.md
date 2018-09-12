# ec2-ssh
Make ssh to EC2 instances easier

Pre-requisites:

python (>2.7.12 or >3.7.0)

pipenv (installed via pip)

Usage:

```
git clone https://github.com/grahamhar/ec2-ssh

cd ec2-ssh

export AWS_PROFILE=<profile from ~/.aws/credentials to use>

pipenv install

pipenv shell

python ec2_ssh/__init__.py
```
