from ipcore.properties.predefined import NumpyArrayProperty, IntProperty
from ipkiss3.simulation.engines.caphe_circuit_sim.pcell_views.caphemodel import (
    CircuitModelView,
)
import numpy as np
import os
from .compact_models import GratingCoupler1DCompactModel, GratingCoupler2DCompactModel

model_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_data")


class GratingCoupler1DCircuitModel(CircuitModelView):
    """
    Simple model describing the grating coupler transmission as a quadratic curve.
    """

    gc_data = NumpyArrayProperty(
        doc="Grating coupler data containing the peak wavelength, " "peak transmission and 1 dB bandwidth."
    )
    polarisation = IntProperty(doc="TE polarization: 0, TM polarization: 1", default=0)

    def _default_gc_data(self):
        return np.loadtxt(os.path.join(model_data_dir, "{}_data.txt".format(self.fixed_name)))

    def _generate_model(self):
        return GratingCoupler1DCompactModel(gc_data=self.gc_data, polarisation=self.polarisation)


class GratingCoupler2DCircuitModel(CircuitModelView):
    """
    Simple model describing the grating coupler transmission as a quadratic curve.
    """

    gc_data = NumpyArrayProperty(
        doc="Grating coupler data containing the peak wavelength, " "peak transmission and 1 dB bandwidth."
    )

    def _default_gc_data(self):
        return np.loadtxt(os.path.join(model_data_dir, "{}_data.txt".format(self.fixed_name)))

    def _generate_model(self):
        return GratingCoupler2DCompactModel(gc_data=self.gc_data)
