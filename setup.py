from setuptools import setup

setup(
    name='susytest',
    version='0.0.1',
    py_modules=[
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'susytest=susytest:cli'
        ]
    }
)