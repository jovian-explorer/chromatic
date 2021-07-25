"""
Define a writer for chromatic .rainbow.npy files.
"""

# import the general list of packages
from ...imports import *
from ...version import version

# define list of the only things that will show up in imports
__all__ = ["to_rainbownpy"]


def to_rainbownpy(rainbow, filepath):
    """
    Write a Rainbow to a file in the .rainbow.npy format.

    Parameters
    ----------

    rainbow : Rainbow
        The object to be saved.

    filepath : str
        The path to the file to write.
    """

    assert ".rainbow.npy" in filepath

    # populate a dictionary containing the four core dictionaries
    dictionary_to_save = {k: vars(rainbow)[k] for k in rainbow._core_dictionaries}

    # save that to a file
    np.save(filepath, [dictionary_to_save, version()], allow_pickle=True)
