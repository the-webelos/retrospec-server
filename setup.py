from setuptools import setup, find_packages

install_requires = ['redis>=2.10.6', 'flask-socketio>=3.0.0', 'eventlet>=0.23.0']
testing_requires = ['boto3==1.7.19', 'docker>=3.1.0', 'redis>=2.10.6']

setup(
    name='retrospec-server',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=testing_requires,
    include_package_data=True,
    test_suite='test'
)
