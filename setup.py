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
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Security',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   ],
      keywords='totp hotp authenticator',
      url='https://github.com/steveherrin/SpookyOTP',
      download_url=
        'https://github.com/steveherrin/SpookyOTP/archive/{}.tar.gz'.format(version),
      author='Steve Herrin',
      author_email='steve.herrin@gmail.com',
      license='Apache2',
      packages=['spookyotp'],
      install_requires=['qrcode', 'six'],
      include_package_data=True,
      setup_requires=['wheel'],
      test_suite='nose.collector',
      tests_require=['nose', 'mock', 'six'],
      zip_safe=True)
