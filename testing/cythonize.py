from distutils.core import Extension, setup
from Cython.Build import cythonize

ext = Extension(name='hello', sources=['example_cython.pyx'])
setup(ext_modules = cythonize(ext))

# define an extension that will be cythonized and compiled
#ext = Extension(name="hello", sources=["cython.pyx"])
#setup(ext_modules=cythonize(ext))