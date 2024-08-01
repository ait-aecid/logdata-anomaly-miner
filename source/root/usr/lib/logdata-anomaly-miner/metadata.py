__authors__ = ["Markus Wurzenberger", "Max Landauer", "Wolfgang Hotwagner", "Ernst Leierzopf", "Roman Fiedler", "Georg Hoeld",
               "Florian Skopik"]
__contact__ = "aecid@ait.ac.at"
__copyright__ = "Copyright 2023, AIT Austrian Institute of Technology GmbH"
__date__ = "2023/01/20"
__deprecated__ = False
__email__ = "aecid@ait.ac.at"
__website__ = "https://aecid.ait.ac.at"
__license__ = "GPLv3"
__maintainer__ = "Markus Wurzenberger"
__status__ = "Production"
__version__ = "2.7.0-126-g7618331c"
_indentation = int(max(0,  max(0, (29 - len(__version__)))) / 2)
# skipcq: PYL-C0209
__version_string__ = """   (Austrian Institute of Technology)\n       (%s)\n%sVersion: %s""" % (
    __website__, " " * _indentation, __version__ + " " * _indentation)
__all__ = ['__authors__', '__contact__', '__copyright__', '__date__', '__deprecated__', '__email__', '__website__', '__license__',
           '__maintainer__', '__status__', '__version__', '__version_string__']
del _indentation
