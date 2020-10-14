"""anmad module setup.py."""
from setuptools import setup, find_packages

setup(name='anmad',
    version='0.18.2',
    description='Creates a simple api and a browser interface for running ansible playbooks.',
    download_url='https://github.com/jefg60/anmad',
    author='Jeff Hibberd',
    author_email='jeff@jeffhibberd.com',
    license='GPLv3',
    install_requires=[
        'ansible',
        'ansible-vault >=1.2.1',
        'configargparse',
        'flask',
        'hotqueue',
        'psutil',
        'pyyaml',
        'redis',
        'requests',
        'ssh_agent_setup',
        ],
    packages=find_packages()
    )
