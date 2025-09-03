import os
from setuptools import setup, find_packages, Command

import shutil
from pathlib import Path
import re

schema_file = os.path.join('schema','ismrmrd.xsd')
config_file = os.path.join('schema','.xsdata.xml')


import setuptools.command.build
setuptools.command.build.build.sub_commands.append(("generate_schema", None))

class GenerateSchemaCommand(Command):
    description = "Generate Python code from ISMRMRD XML schema using xsdata"
    user_options = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_lib = None
        self.editable_mode = False

    def initialize_options(self):
        pass

    def finalize_options(self):
        # # Set build_lib for non-editable installs
        self.set_undefined_options("build_py", ("build_lib", "build_lib"))

    def run(self):
        # Use editable_mode if present (PEP 660)
        if self.editable_mode:
            outdir = 'ismrmrd/xsd/'
        else:
            outdir = os.path.join(self.build_lib, 'ismrmrd/xsd/')
        self.announce(f'Generating schema to {outdir} (editable_mode={self.editable_mode})', level=3)
        self.generate_schema(schema_file, config_file, 'ismrmrdschema', outdir)

    def get_source_files(self):
        return [schema_file, config_file]

    def get_outputs(self):
        return [
            "{build_lib}/ismrmrd/xsd/ismrmrdschema/__init__.py",
            "{build_lib}/ismrmrd/xsd/ismrmrdschema/ismrmrd.py"
        ]

    def fix_init_file(self, package_name,filepath):
        with open(filepath,'r+') as f:
            text = f.read()
            text = re.sub(f'from {package_name}.ismrmrd', 'from .ismrmrd',text)
            f.seek(0)
            f.write(text)
            f.truncate()

    def generate_schema(self, schema_filename, config_filename, subpackage_name, outdir):
        import sys
        import subprocess
        # subpackage_name = 'ismrmrdschema'
        args = [sys.executable, '-m', 'xsdata', str(schema_filename), '--config', str(config_filename), '--package', subpackage_name]
        subprocess.run(args)
        self.fix_init_file(subpackage_name, f"{subpackage_name}/__init__.py")
        destination = os.path.join(outdir, subpackage_name)
        shutil.rmtree(destination, ignore_errors=True)
        shutil.move(subpackage_name, destination)

this_directory = Path(__file__).parent
long_description = (this_directory / "README").read_text()

setup(
    name='ismrmrd',
    version='1.14.1',
    author='ISMRMRD Developers',
    description='Python implementation of the ISMRMRD',
    license='Public Domain',
    keywords='ismrmrd',
    url='https://ismrmrd.github.io',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    install_requires=[
        'xsdata>=22.12',
        'numpy>=1.22.0',
        'h5py>=2.3'
    ],
    extras_require={
        'dev': ['pytest']
    },
    cmdclass={
        'generate_schema': GenerateSchemaCommand
    }
)
