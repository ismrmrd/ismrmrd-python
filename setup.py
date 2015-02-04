import os
from distutils.core import setup
from distutils.command.build import build
from distutils.command.build_py import build_py

schema_file = os.path.join('schema','ismrmrd.xsd')

class my_build(build):
    def run(self):
        self.run_command("build_py")
        build.run(self)

class my_build_py(build_py):
    def run(self):
        # honor the --dry-run flag
        if not self.dry_run:
            outloc = os.path.join(self.build_lib,'ismrmrd')
            os.system('pyxbgen -u '+schema_file+' -m xsd --binding-root="'+outloc+'"')

        # distutils uses old-style classes, so no super()
        build_py.run(self)

setup(
    name='ismrmrd',
    version='1.2.2',
    author='ISMRMRD Developers',
    author_email='ismrmrd@googlegroups.com',
    description='Python implementation of the ISMRMRD',
    license='Public Domain',
    keywords='ismrmrd',
    url='https://ismrmrd.github.io',
    packages=['ismrmrd'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    requires=['Cython', 'numpy', 'PyXB', 'h5py'],

    cmdclass={'build_py':my_build_py,'build':my_build}
)
