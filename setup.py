"""anmad module setup.py."""
from setuptools import setup, find_packages

setup(name='anmad',
    version='0.20.0',
    description='Creates a simple api and a browser interface for running ansible playbooks.',
    url='https://github.com/jefg60/anmad',
    author='Jeff Hibberd',
    author_email='jeff@jeffhibberd.com',
    license='GPLv3',
    include_package_data=True,
    install_requires=[
        'ansible',
        'ansible-vault >=2.0.1',
        'configargparse',
        'cryptography >=3.1.1',
        'flask',
        'hotqueue',
        'psutil',
        'pyyaml',
        'redis',
        'requests',
        'ssh_agent_setup',
        'gitpython',
        ],
    packages=find_packages()
    )
