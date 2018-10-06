from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ec2-ssh',

    version='0.0.0',

    description='A simple AWS ec2 host discovery and ssh script',

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/grahamhar/aws-rotate',

    author='grahamhar',


    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],

    keywords='aws ec2 ssh',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['awscli', 'boto3', 'click', 'click-completion'],

    extras_require={
        'dev': ['pytest', 'pytest-cov', 'coveralls'],
    },
    scripts=['ec2_ssh/cli/bin/ssh_ec2'],
    project_urls={
        'Bug Reports': 'https://github.com/grahamhar/ec2-ssh/issues',
        'Source': 'https://github.com/grahamhar/ec2-ssh/',
    },
)
