from setuptools import setup, find_packages

setup(
    name='overseer-cli',
    version='0.1.0',
    description='Overseer System Assistant CLI',
    author='Overseer Team',
    packages=find_packages(),
    install_requires=[
        'transformers>=4.40.0',
        'rich>=13.0.0',
        'fuzzywuzzy>=0.18.0',
        'python-Levenshtein>=0.12.2',
        'google-generativeai>=0.3.0',
    ],
    entry_points={
        'console_scripts': [
            'overseer=cli.overseer_cli:main',
        ],
    },
    python_requires='>=3.8',
) 