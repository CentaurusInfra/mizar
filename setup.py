from setuptools import setup, find_packages

setup(
    name='mizar',
    version='0.1.0',
    packages=find_packages(include=['mizar', 'mizar.*']),
    entry_points={
        'console_scripts': [
            'mizard=mizar.daemon.app:main'
        ]
    },
    install_requires=[]
)
