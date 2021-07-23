from ...imports import *


__all__ = ["from_eureka"]


def loadevent(filename, load=[], loadfilename=None):  # from Eureka source code
    """
    Loads an event stored in .dat and .h5 files.

    Parameters
    ----------
    filename : String
               The string contains the name of the event file.
    load     : String tuple
               The elements of this tuple contain the parameters to read.
               We usually use the values: 'data', 'uncd', 'head', 'bdmskd',
               'brmskd' or 'mask'.

    Notes
    -----
    The input filename should not have the .dat nor the .h5 extentions.

    Returns
    -------
    This function return an Event instance.

    Examples
    --------
    See package example.

    Revisions
    ---------
    2010-07-10  patricio  Added documentation.     pcubillos@fulbrightmail.org
    """

    from astropy.io import fits
    import h5py as h5

    handle = open(filename + ".dat", "rb")
    event = pickle.load(handle, encoding="latin1")
    handle.close()

    if loadfilename == None:
        loadfilename = filename

    if load != []:
        handle = h5.File(loadfilename + ".h5", "r")
        for param in load:
            exec("event." + param + ' = handle["' + param + '"][:]')

            # calibration data:
            if event.havecalaor:
                exec("event.pre" + param + ' = handle["pre' + param + '"][:]')
                exec("event.post" + param + ' = handle["post' + param + '"][:]')

        handle.close()

    return event


def eureadka(filename):
    """
    Read eureka's Stage 3 outputs (time-series spectra).
    """

    fileprefix = filename.strip(".dat")

    # load the event data
    event = loadevent(fileprefix, load=[])

    # guess the meta file from the data file, and load it
    metaname = fileprefix.replace("Data", "Meta")
    meta = loadevent(metaname, load=[])

    # pull out some variables
    t = event.int_times["int_mid_BJD_TDB"]  # UT time for the midpoint of exposure
    f = event.optspec[:, meta.xwindow[0] : meta.xwindow[1]]
    e = event.opterr[:, meta.xwindow[0] : meta.xwindow[1]]
    w = event.subwave[meta.src_ypos, meta.xwindow[0] : meta.xwindow[1]]
    # this assumes the wavelength axis is the same for all exposures

    timelike = {}
    timelike["time"] = t * u.day  # TODO: check time units

    wavelike = {}
    wavelike["wavelength"] = w * u.micron  # TODO: check wavelength units

    fluxlike = {}
    fluxlike["flux"] = f.transpose()
    fluxlike["error"] = e.transpose()

    return wavelike, timelike, fluxlike
    # TO-DO: add relevant metadata
    # TO-DO: add other useful time-series information


def from_eureka(rainbow, filename, **kwargs):
    """
    Populate a Rainbow from a eureka pipeline S3 output.

    Parameters
    ----------

    rainbow : Rainbow
        The object to be populated. (This is intended
        to be used as a class method of Rainbow or
        of a class derived from Rainbow, as a way of
        initializing an object from files.)
    filename : str
        The path to the file.
    """

    # load the Eureka event
    wavelike, timelike, fluxlike = eureadka(filename)

    # populate the rainbow
    rainbow._initialize_from_dictionaries(
        wavelike=wavelike, timelike=timelike, fluxlike=fluxlike
    )
