# Copyright (c) 2021 CNES
#
# All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.
import os
import pickle
import pytest
import netCDF4
try:
    import matplotlib.pyplot
    HAVE_PLT = True
except ImportError:
    HAVE_PLT = False
import numpy as np
import pyinterp.core as core
from .. import grid2d_path

def plot(x, y, z, filename):
    figure = matplotlib.pyplot.figure(figsize=(15, 15), dpi=150)
    value = z.mean()
    std = z.std()
    normalize = matplotlib.colors.Normalize(vmin=value - 3 * std,
                                            vmax=value + 3 * std)
    axe = figure.add_subplot(2, 1, 1)
    axe.pcolormesh(x, y, z, cmap='jet', norm=normalize, shading='auto')
    figure.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                filename),
                   bbox_inches='tight',
                   pad_inches=0.4)


def load_data(is_circle=True):
    with netCDF4.Dataset(grid2d_path()) as ds:
        z = ds.variables['mss'][:].T
        z[z.mask] = float("nan")
        return core.Grid2DFloat64(
            core.Axis(ds.variables['lon'][:], is_circle=is_circle),
            core.Axis(ds.variables['lat'][:]), z.data)


def test_grid2d_init():
    """Test construction and accessors of the object"""
    grid = load_data()
    assert isinstance(grid.x, core.Axis)
    assert isinstance(grid.y, core.Axis)
    assert isinstance(grid.array, np.ndarray)


def test_grid2d_pickle():
    """Serialization test"""
    grid = load_data()
    other = pickle.loads(pickle.dumps(grid))
    assert grid.x == other.x
    assert grid.y == other.y
    assert np.all(
        np.ma.fix_invalid(grid.array) == np.ma.fix_invalid(other.array))


def run_bivariate(interpolator, filename):
    """Testing an interpolation method."""
    grid = load_data()
    lon = np.arange(-180, 180, 1 / 3.0) + 1 / 3.0
    lat = np.arange(-90, 90, 1 / 3.0) + 1 / 3.0
    x, y = np.meshgrid(lon, lat, indexing="ij")

    z0 = core.bivariate_float64(grid,
                                x.flatten(),
                                y.flatten(),
                                interpolator,
                                num_threads=0)

    z1 = core.bivariate_float64(grid,
                                x.flatten(),
                                y.flatten(),
                                interpolator,
                                num_threads=1)

    # The data from the mono-threads and multi-threads execution must be
    # identical.
    z0 = np.ma.fix_invalid(z0)
    z1 = np.ma.fix_invalid(z1)
    assert np.all(z1 == z0)

    if HAVE_PLT:
        plot(x, y, z0.reshape((len(lon), len(lat))), filename)

    # Out of bounds interpolation
    with pytest.raises(ValueError):
        core.bivariate_float64(grid,
                               x.flatten(),
                               y.flatten(),
                               interpolator,
                               bounds_error=True,
                               num_threads=0)

    return z0


def test_bivariate_interpolator():
    """Testing of different interpolation methods"""
    a = run_bivariate(core.Nearest2D(), "mss_bivariate_nearest")
    b = run_bivariate(core.Bilinear2D(), "mss_bivariate_bilinear")
    c = run_bivariate(core.InverseDistanceWeighting2D(), "mss_bivariate_idw")
    assert (a - b).std() != 0
    assert (a - c).std() != 0
    assert (b - c).std() != 0


def test_bivariate_pickle():
    """Serialization of interpolator properties"""
    for item in [
            'InverseDistanceWeighting2D', 'InverseDistanceWeighting3D',
            'Bilinear2D', 'Bilinear3D', 'Nearest2D', 'Nearest3D'
    ]:
        obj = getattr(core, item)()
        assert isinstance(obj, getattr(core, item))
        assert isinstance(pickle.loads(pickle.dumps(obj)), getattr(core, item))


def test_spline_interpolator():
    """Testing of different spline interpolation methods"""
    grid = load_data()
    lon = np.arange(-180, 180, 1 / 3.0) + 1 / 3.0
    lat = np.arange(-90, 90, 1 / 3.0) + 1 / 3.0
    x, y = np.meshgrid(lon, lat, indexing="ij")
    z0 = core.spline_float64(grid,
                             x.flatten(),
                             y.flatten(),
                             fitting_model="akima",
                             num_threads=0)
    z1 = core.spline_float64(grid,
                             x.flatten(),
                             y.flatten(),
                             fitting_model="akima",
                             num_threads=1)
    z0 = np.ma.fix_invalid(z0)
    z1 = np.ma.fix_invalid(z1)
    assert np.all(z1 == z0)
    if HAVE_PLT:
        plot(x, y, z0.reshape((len(lon), len(lat))), "mss_akima.png")

    z0 = core.spline_float64(grid, x.flatten(), y.flatten())
    z0 = np.ma.fix_invalid(z0)
    assert not np.all(z1 == z0)
    if HAVE_PLT:
        plot(x, y, z0.reshape((len(lon), len(lat))), "mss_cspline.png")

    # Out of bounds interpolation
    with pytest.raises(ValueError):
        core.spline_float64(grid,
                            x.flatten(),
                            y.flatten(),
                            fitting_model="akima",
                            bounds_error=True,
                            num_threads=0)


def test_spline_degraded():
    """Testing of different spline interpolation methods"""
    grid = load_data(is_circle=False)
    lon = np.arange(-190, -170, 1 / 3.0)
    lat = np.arange(-40, 40, 1 / 3.0) + 1 / 3.0
    x, y = np.meshgrid(lon, lat, indexing="ij")

    with pytest.raises(ValueError):
        core.spline_float64(grid,
                            x.flatten(),
                            y.flatten(),
                            bounds_error=True,
                            num_threads=0)
