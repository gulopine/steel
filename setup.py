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


setup(name='steel',
      version='0.2',
      description='A Python framework for describing binary file formats',
      author='Marty Alchin',
      author_email='marty@martyalchin.com',
      url='https://github.com/gulopine/steel',
      packages=['steel', 'steel.bits', 'steel.chunks', 'steel.common', 'steel.fields'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Topic :: System :: Filesystems',
          ],
      cmdclass={'test': TestDiscovery},
     )
