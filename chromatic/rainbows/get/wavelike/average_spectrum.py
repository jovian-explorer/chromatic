from ....imports import *

__all__ = ["get_average_spectrum"]


def get_average_spectrum(self):
    """
    Return a average_spectrum of the star, averaged over all times.

    Parameters
    ----------

    Returns
    -------
    average_spectrum : array
        Wavelike array of average spectrum.
    """
    return self.get_average_spectrum_as_rainbow().flux[:, 0]
