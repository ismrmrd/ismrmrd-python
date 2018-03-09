import os
from setuptools import setup
from distutils.command.build import build
from distutils.command.build_py import build_py

import pyxb.binding.generate
import logging
logging.basicConfig()
log_ = logging.getLogger(__name__)

schema_file = os.path.join('schema','ismrmrd.xsd')

class my_build(build):
    def run(self):
        self.run_command("build_py")
        build.run(self)

class my_build_py(build_py):
    def run(self):
        # honor the --dry-run flag
        if not self.dry_run:
            outloc = self.get_package_dir('ismrmrd')
            modname = 'xsd'
            modfile = os.path.join(outloc, '%s.py' % modname)
            generate_schema(schema_file, modname, outloc)
            with open(modfile, 'a') as f:
                f.write('\nimport pyxb.utils.domutils\n' +
                        'pyxb.utils.domutils.BindingDOMSupport.SetDefaultNamespace(Namespace)\n')

        # distutils uses old-style classes, so no super()
        build_py.run(self)

def generate_schema(schema_filename, module_name, output_directory):
    """ Extracted from the `pyxbgen` tool provided by
    PyXB (http://pyxb.sourceforge.net/) """
    generator = pyxb.binding.generate.Generator()
    parser = generator.optionParser()
    (options, args) = parser.parse_args(args=[
        '-u', '%s' % schema_filename,
        '-m', module_name,
        '--binding-root=%s' % output_directory
        ])

    generator.applyOptionValues(options, args)
    generator.resolveExternalSchema()

    if 0 == len(generator.namespaces()):
        raise RuntimeError("error creating PyXB generator")

    # Save binding source first, so name-in-binding is stored in the
    # parsed schema file
    try:
        tns = generator.namespaces().pop()
        modules = generator.bindingModules()
        top_module = None
        path_dirs = set()
        for m in modules:
            m.writeToModuleFile()
        generator.writeNamespaceArchive()
    except Exception as e:
        raise RuntimeError("error generating bindings (%s)" % e)


setup(
    name='ismrmrd',
    version='1.4.0',
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
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    install_requires=['PyXB', 'numpy', 'h5py>=2.3'],
    setup_requires=['nose>=1.0', 'pyxb'],
    test_suite='nose.collector',
    cmdclass={'build_py':my_build_py,'build':my_build}
)
