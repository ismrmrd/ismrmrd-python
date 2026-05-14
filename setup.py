import os
from setuptools import setup, find_packages, Command

import shutil
import re

schema_file = os.path.join('schema','ismrmrd.xsd')
config_file = os.path.join('schema','.xsdata.xml')


# The xsdata-generated files are committed to the repository.
# The generate_schema command is kept here for maintainers to use when the
# schema or the xsdata version changes:
#
#   python setup.py generate_schema
#
# After running it, commit the updated files under ismrmrd/xsd/ismrmrdschema/.

class GenerateSchemaCommand(Command):
    description = "Regenerate Python code from ISMRMRD XML schema using xsdata (maintainers only)"
    user_options = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_lib = None
        self.editable_mode = False

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        outdir = 'ismrmrd/xsd/'
        self.announce(f'Generating schema to {outdir}', level=3)
        self.generate_schema(schema_file, config_file, 'ismrmrdschema', outdir)

    def get_source_files(self):
        return [schema_file, config_file]

    def get_outputs(self):
        return [
            "ismrmrd/xsd/ismrmrdschema/__init__.py",
            "ismrmrd/xsd/ismrmrdschema/ismrmrd.py"
        ]

    def fix_init_file(self, package_name, filepath):
        with open(filepath,'r+') as f:
            text = f.read()
            text = re.sub(f'from {package_name}.ismrmrd', 'from .ismrmrd', text)
            f.seek(0)
            f.write(text)
            f.truncate()

    def generate_schema(self, schema_filename, config_filename, subpackage_name, outdir):
        import sys
        import subprocess
        args = [sys.executable, '-m', 'xsdata', 'generate', str(schema_filename), '--config', str(config_filename), '--package', subpackage_name]
        subprocess.run(args, check=True)
        self.fix_init_file(subpackage_name, f"{subpackage_name}/__init__.py")
        destination = os.path.join(outdir, subpackage_name)
        shutil.rmtree(destination, ignore_errors=True)
        shutil.move(subpackage_name, destination)

setup(
    version='1.15.0',
    packages=find_packages(),
    cmdclass={
        'generate_schema': GenerateSchemaCommand
    }
)
