from .rainbownpy import *


def guess_writer(filepath, format=None):
    """
    A wrapper to guess the appropriate writer from the filename
    (and possibily an explicitly-set file format string).

    Parameters
    ----------
    filepath : str
        The path to the file to be written.
    format : str, None
        The file format to use.
    """
    import fnmatch, glob

    # if format='abcdefgh', return the `to_abcdefgh` function
    if format is not None:
        return locals()[f"to_{format}"]
    # does it look like a .rainbow.npy chromatic file?
    elif fnmatch.fnmatch(filepath, "*.rainbow.npy"):
        return to_rainbownpy