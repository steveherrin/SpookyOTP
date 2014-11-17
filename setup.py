from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='SpookyOTP',
      version='0.1',
      description='A lightweight Python 2/3 package for handling HOTP/'
                  'TOTP (Google Authenticator) authentication.',
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Security'],
      keywords='totp hotp authenticator',
      url='https://github.com/steveherrin/SpookyOTP',
      download_url='https://github.com/steverherrin/SpookyOTP/tarball/0.1',
      author='Steve Herrin',
      author_email='steve.herrin@gmail.com',
      license='Apache2',
      packages=['spookyotp'],
      install_requires=['qrcode'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose', 'mock'],
      zip_safe=True)
