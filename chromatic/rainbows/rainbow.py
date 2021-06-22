from ..imports import *
from ..talker import Talker
from ..resampling import *


class Rainbow(Talker):
    """
    Rainbow objects represent the flux of an object
    as a function of both wavelength and time.
    """

    def __init__(self, wavelength=None, time=None, flux=None, uncertainty=None, **kw):
        """
        Initialize a generic Rainbow object.

        Parameters
        ----------
        wave : astropy.unit.Quantity
            A 1D array of wavelengths, in any unit.
        time : astropy.unit.Quantity or astropy.unit.Time
            A 1D array of times, in any unit.
        flux : np.array
            A 2D array of flux values.
        uncertainty : np.array
            A 2D array of uncertainties, associated with the flux.

        """

        # wavelike quanities are 1D arrays with nwave elements
        self.wavelike = {}
        self.wavelike["wavelength"] = wavelength

        # timelike quantities are 1D arrays with ntime elements
        self.timelike = {}
        self.timelike["time"] = time

        # fluxlike quantities are 2D arrays with nwave x time elements
        self.fluxlike = {}
        self.fluxlike["flux"] = flux
        self.fluxlike["uncertainty"] = uncertainty

    @property
    def wavelength(self):
        return self.wavelike["wavelength"]

    # @wavelength.setter
    # def wavelength(self, value):
    #    self.wavelike['wavelength'] = value

    @property
    def time(self):
        return self.timelike["time"]

    @property
    def flux(self):
        return self.fluxlike["flux"]

    @property
    def uncertainty(self):
        return self.fluxlike["uncertainty"]

    @property
    def shape(self):
        return (self.nwave, self.ntime)

    @property
    def nwave(self):
        if self.wavelength is None:
            return 0
        else:
            return len(self.wavelength)

    @property
    def ntime(self):
        if self.time is None:
            return 0
        else:
            return len(self.time)

    @property
    def nflux(self):
        return np.prod(self.shape)

    def __repr__(self):
        n = self.__class__.__name__
        return f"<{n} ({self.nwave}w, {self.ntime}t)>"

    def bin(self, dt=None, time=None, R=None, dw=None, wavelength=None):
        """
        Bin the rainbow in wavelength and/or time.

        Parameters
        ----------
        dt : astropy.units.Quantity
            The d(time) bin size for creating a grid
            that is uniform in linear space.
        time : array of astropy.units.Quantity
            An array of times, if you just want to give
            it an entirely custom array.

        The time-setting order of precendence is:
            1) time
            2) dt

        R : float
            The spectral resolution for creating a grid
            that is uniform in logarithmic space.
        dw : astropy.units.Quantity
            The d(wavelength) bin size for creating a grid
            that is uniform in linear space.
        wavelength : array of astropy.units.Quantity
            An array of wavelengths, if you just want to give
            it an entirely custom array.

        The wavelength-setting order of precendence is:
            1) wavelength
            2) dw
            3) R
        """
        if np.any([dt, time, R, dw, wavelength]) == False:
            return self

        if np.any([dt, time]):
            binned_in_time = self.bin_in_time(dt=dt, time=time)
        else:
            binned_in_time = self

        if np.any([dw, R, wavelength]):
            binned = binned_in_time.bin_in_wavelength(R=R, dw=dw, wavelength=wavelength)
        else:
            binned = binned_in_time

        return binned

    def bin_in_time(self, dt=None, time=None):
        """
        Bin the rainbow in time.

        Parameters
        ----------
        dt : astropy.units.Quantity
            The d(time) bin size for creating a grid
            that is uniform in linear space.
        time : array of astropy.units.Quantity
            An array of times, if you just want to give
            it an entirely custom array.

        The time-setting order of precendence is:
            1) time
            2) dt
        """

        if (time is None) and (dt is None):
            return self

        binkw = dict(weighting="inversevariance", drop_nans=False)
        if time is not None:
            binkw["newx"] = time
        elif dt is not None:
            binkw["dx"] = dt

        new = Rainbow()
        new.wavelike = {**self.wavelike}
        new.wscale = self.wscale

        # bin the timelike variables
        # TODO (add more careful treatment of uncertainty + DQ)
        new.timelike = {}
        for k in self.timelike:
            bt, bv = bintogrid(
                x=self.timelike["time"], y=self.timelike[k], unc=None, **binkw
            )
            new.timelike[k] = bv
        new.timelike[k] = bt

        # bin the flux like variables
        # TODO (add more careful treatment of uncertainty + DQ)
        # TODO (think about cleverer bintogrid for 2D arrays)
        new.fluxlike = {}
        for k in self.fluxlike:
            self.speak(f" binning {k} in time")
            for w in tqdm(range(new.nwave)):
                if self.uncertainty is None:
                    bt, bv = bintogrid(
                        x=self.time, y=self.fluxlike[k][w, :], unc=None, **binkw
                    )
                    bu = None
                else:
                    bt, bv, bu = bintogrid(
                        x=self.time, y=self.fluxlike[k][w, :], unc=self.uncertainty[w, :], **binkw
                    )


                if k not in new.fluxlike:
                    new_shape = (new.nwave, new.ntime)
                    new.fluxlike[k] = np.zeros(new_shape)
                    # TODO make this more robust to units

                if k == 'uncertainty':
                    new.fluxlike[k][w, :] = bu
                else:
                    new.fluxlike[k][w, :] = bv

        return new

    def imshow(
        self,
        ax=None,
        w_unit="micron",
        t_unit="hour",
        aspect="auto",
        colorbar=True,
        origin="upper",
        **kw,
    ):

        if ax is None:
            ax = plt.gca()

        w_unit, t_unit = u.Unit(w_unit), u.Unit(t_unit)

        if self.wscale == "linear":
            extent = [
                (min(self.time) / t_unit).decompose(),
                (max(self.time) / t_unit).decompose(),
                (min(self.wavelength) / w_unit).decompose(),
                (max(self.wavelength) / w_unit).decompose(),
            ]
        elif self.wscale == "log":
            extent = [
                (min(self.time) / t_unit).decompose(),
                (max(self.time) / t_unit).decompose(),
                np.log10(min(self.wavelength) / w_unit),
                np.log10(max(self.wavelength) / w_unit),
            ]
        else:
            raise RuntimeError("Can't imshow without knowing wscale.")

        with quantity_support():
            plt.sca(ax)
            plt.imshow(self.flux, extent=extent, aspect=aspect, origin=origin, **kw)
            if self.wscale == "linear":
                plt.ylabel(f"Wavelength ({w_unit.to_string('latex_inline')})")
            elif self.wscale == "log":
                plt.ylabel(
                    r"log$_{10}$" + f"[Wavelength/({w_unit.to_string('latex_inline')})]"
                )
            plt.xlabel(f"Time ({t_unit.to_string('latex_inline')})")
            if colorbar:
                plt.colorbar(ax=ax)
        return ax
