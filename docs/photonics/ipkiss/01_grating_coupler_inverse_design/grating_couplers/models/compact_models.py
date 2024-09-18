from ipkiss3.pcell.photonics.term import OpticalTerm
from ipkiss3.pcell.model.model import CompactModel
import numpy as np
from scipy.constants import c

c_mu = c * 1.0e6


class GratingCoupler1DCompactModel(CompactModel):
    parameters = ["gc_data", "polarisation"]
    terms = [
        OpticalTerm(name="vertical_in", n_modes=2),
        OpticalTerm(name="out1", n_modes=2),
    ]

    def calculate_smatrix(parameters, env, S):
        peak_wavelength = parameters.gc_data[0]
        peak_il = parameters.gc_data[1]
        bw_1db = parameters.gc_data[2]
        peak_transmission = 10.0 ** (-0.1 * peak_il)
        gc_factor = (2.0 / bw_1db) * np.sqrt(0.1)
        delta_wavelength = peak_wavelength - env.wavelength
        loss = np.sqrt(peak_transmission * (10.0 ** (-((gc_factor * delta_wavelength) ** 2.0))))
        if parameters.polarisation == 0:
            S["vertical_in:0", "out1:0"] = S["out1:0", "vertical_in:0"] = loss
            S["out1:0", "out1:0"] = S["vertical_in:0", "vertical_in:0"] = 0.0001
        else:
            S["vertical_in:1", "out1:1"] = S["out1:1", "vertical_in:1"] = loss
            S["out1:1", "out1:1"] = S["vertical_in:1", "vertical_in:1"] = 0.0001

    def calculate_signals(parameters, env, output_signals, y, t, input_signals):
        peak_wavelength = parameters.gc_data[0]
        peak_il = parameters.gc_data[1]
        bw_1db = parameters.gc_data[2]
        peak_transmission = 10.0 ** (-0.1 * peak_il)
        gc_factor = (2.0 / bw_1db) * np.sqrt(0.1)
        delta_wavelength = peak_wavelength - env.wavelength
        loss = np.sqrt(peak_transmission * (10.0 ** (-((gc_factor * delta_wavelength) ** 2.0))))
        if parameters.polarisation == 0:
            output_signals["vertical_in:0"] = loss * input_signals["out1:0"]
            output_signals["out1:0"] = loss * input_signals["vertical_in:0"]
        else:
            output_signals["vertical_in:1"] = loss * input_signals["out1:1"]
            output_signals["out1:1"] = loss * input_signals["vertical_in:1"]


class GratingCoupler2DCompactModel(CompactModel):
    parameters = ["gc_data"]
    terms = [
        OpticalTerm(name="vertical_in", n_modes=2),
        OpticalTerm(name="out1_1", n_modes=2),
        OpticalTerm(name="out1_2", n_modes=2),
    ]

    def calculate_smatrix(parameters, env, S):
        peak_wavelength = parameters.gc_data[0]
        peak_il = parameters.gc_data[1]
        bw_1db = parameters.gc_data[2]
        peak_transmission = 10.0 ** (-0.1 * peak_il)
        gc_factor = (2.0 / bw_1db) * np.sqrt(0.1)
        delta_wavelength = peak_wavelength - env.wavelength
        loss = peak_transmission * (10.0 ** (-((gc_factor * delta_wavelength) ** 2.0)))
        S["vertical_in:0", "out1_1:0"] = S["out1_1:0", "vertical_in:0"] = loss
        S["vertical_in:0", "out1_2:0"] = S["out1_2:0", "vertical_in:0"] = loss
        S["vertical_in:1", "out1_1:1"] = S["out1_1:1", "vertical_in:1"] = loss
        S["vertical_in:1", "out1_2:1"] = S["out1_2:1", "vertical_in:1"] = loss

    def calculate_signals(parameters, env, output_signals, y, t, input_signals):
        peak_wavelength = parameters.gc_data[0]
        peak_il = parameters.gc_data[1]
        bw_1db = parameters.gc_data[2]
        peak_transmission = 10.0 ** (-0.1 * peak_il)
        gc_factor = (2.0 / bw_1db) * np.sqrt(0.1)
        delta_wavelength = peak_wavelength - env.wavelength
        loss = peak_transmission * (10.0 ** (-((gc_factor * delta_wavelength) ** 2.0)))
        output_signals["vertical_in:0"] = loss * (input_signals["out1_1:0"] + input_signals["out1_2:0"])
        output_signals["vertical_in:1"] = loss * (input_signals["out1_1:1"] + input_signals["out1_2:1"])
        output_signals["out1_1:0"] = loss * input_signals["vertical_in:0"]
        output_signals["out1_1:1"] = loss * input_signals["vertical_in:1"]
        output_signals["out1_2:0"] = loss * input_signals["vertical_in:0"]
        output_signals["out1_2:1"] = loss * input_signals["vertical_in:1"]
