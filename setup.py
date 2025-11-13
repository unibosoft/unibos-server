"""
UNIBOS Setup Configuration
Installation script for the unibos CLI tool.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name='unibos',
    version='0.533.0',
    description='UNIBOS - Universal Integrated Backend and Operating System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Berk Hatirli',
    author_email='berk@hatirli.com',
    url='https://github.com/berkhatirli/unibos',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'unibos=core.cli.main:main',
        ],
    },
    install_requires=[
        'click>=8.0.0',
        'django>=4.2.0',
        'psycopg2-binary>=2.9.0',
        'redis>=4.0.0',
        'celery>=5.2.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='unibos backend framework platform',
    project_urls={
        'Documentation': 'https://github.com/berkhatirli/unibos/wiki',
        'Source': 'https://github.com/berkhatirli/unibos',
        'Tracker': 'https://github.com/berkhatirli/unibos/issues',
    },
)
