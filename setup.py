from setuptools import setup, find_packages


requirements_file = 'requirements.txt'
requirements =  [x.strip() for x in open(requirements_file).readlines() if not x.startswith('#')]

setup(
    name='mono-diff',
    version='0.1',
    license='MIT',
    author="Ran Sasportas",
    author_email='ran729@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ran729/mono',
    keywords='mono',
    install_requires=requirements_file
)