from setuptools import setup

setup(
    name='susytest',
    version='0.0.1',
    description='Automate the testing of programs to be submitted to Unicamp\'s SuSy platform.',
    author='Álvaro A. Costa',
    py_modules=[
        'susytest'
    ],
    install_requires=[
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'susytest = susytest:cli'
        ]
    }
)