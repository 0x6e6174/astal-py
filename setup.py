from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import subprocess
import os

class BuildCUtils(build_py):
    def run(self):
        print('compiling add_child.c')
        build_c_utils()
        super().run()


def build_c_utils():
    pkg_config_flags = subprocess.check_output(
        ["pkg-config", "--cflags", "--libs", "gtk4"],
        text=True
    ).strip()

    pkg_config_args = pkg_config_flags.split()

    cmd = [
        "gcc",
        "-shared",
        "-o", "add_child.so",
        "-fPIC",
        "add_child.c"
    ] + pkg_config_args

    subprocess.run(cmd, cwd=os.path.join(os.path.dirname(__file__), "astal", "gtk4"), check=True)

setup(
    name="astal",
    version="0.1.0",
    description="",
    author="Natalie Roentgen Connolly",
    author_email="natalie@natalieee.net",
    packages=find_packages(),
    cmdclass={"build_py": BuildCUtils},
    include_package_data=True,
    package_data={
        "astal.gtk4": ["add_child.so"]
    },
)
