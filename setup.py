from setuptools import setup

setup(
    name='flask-ipblock',
    version='0.3',
    url='http://github.com/closeio/flask-ipblock',
    license='MIT',
    description='Block certain IP addresses from accessing your Flask app',
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
    packages=[
        'flask_ipblock',
    ],
    install_requires=[
        'Flask',
        'mongoengine'
    ]
)
