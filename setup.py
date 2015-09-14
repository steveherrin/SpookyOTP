from setuptools import setup
from version import get_version

def readme():
    with open('README.md') as f:
        return f.read()

version = get_version()

setup(name='SpookyOTP',
      version=version,
      description='A lightweight Python 2/3 package for handling HOTP/'
                  'TOTP (Google Authenticator) authentication.',
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Security'],
      keywords='totp hotp authenticator',
      url='https://github.com/steveherrin/SpookyOTP',
      download_url=
        'https://github.com/steveherrin/SpookyOTP/archive/{}.tar.gz'.format(version),
      author='Steve Herrin',
      author_email='steve.herrin@gmail.com',
      license='Apache2',
      packages=['spookyotp'],
      install_requires=['qrcode'],
      include_package_data=True,
      setup_requires=['wheel'],
      test_suite='nose.collector',
      tests_require=['nose', 'mock'],
      zip_safe=True)
