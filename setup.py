from distutils.core import setup
import io

setup(name='commanded-api',
  version='0.0.1',
  description='Collection of utils I use to build scripts that pilots APIs',
  long_description=(io.open('README.md', 'r', encoding='utf-8').read()),
  author='Pierre Bellon',
  author_email='bellon.pierre@gmail.com',
  url='https://github.com/pbellon/commanded-api',
  packages=['commanded-api',],
 )
