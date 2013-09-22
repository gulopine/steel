#!/usr/bin/env python

from distutils.core import setup, Command


class TestDiscovery(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess
        errno = subprocess.call([
            sys.executable,
            '-m', 'unittest',
            'discover',
            '-p', '*.py',
            'tests',
        ])
        raise SystemExit(errno)


setup(name='Steel',
      version='0.1',
      description='A Python framework for describing binary file formats',
      author='Marty Alchin',
      author_email='marty@martyalchin.com',
      url='https://github.com/gulopine/steel',
      packages=['steel'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Topic :: System :: Filesystems',
          ],
      cmdclass={'test': TestDiscovery},
     )
