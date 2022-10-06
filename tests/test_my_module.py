"""
Module included to illustrate how a module outside the package can access modules within the package to test,
demostrate, etc. the operation of the package.
"""

from demo_package_sample_data_with_code.my_module import print_value_from_resource
import demo_package_sample_data_with_code.constants as source

def run_module():
    print_value_from_resource("π", source.PACKAGENAME_PI, source.FILENAME_PI)
    print_value_from_resource("e", source.PACKAGENAME_E, source.FILENAME_E)


if __name__ == "__main__":
    run_module()