import imecas.all as pdk
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c

c_mu = c * 1.0e6
wls_oband = np.linspace(1.26, 1.36, 10001)
wls_cband = np.linspace(1.5, 1.6, 10001)
gcs = [
    pdk.FGC_C_TE_WG450(),
    pdk.FGC_C_TM_WG450(),
    pdk.FGC_O_TE_WG380(),
    pdk.FGC_O_TM_WG380(),
]
wls_bands = [wls_cband, wls_cband, wls_oband, wls_oband]


########################################################################################################################
# Layout test bench grating couplers
########################################################################################################################

print(" ")
print("Test grating couplers layout...")

for gc in gcs:
    gc.Layout().visualize(annotate=True)


########################################################################################################################
# Steady state test bench grating couplers
########################################################################################################################

print(" ")
print("Test grating couplers steady state behavior...")

for gc, wls_band in zip(gcs, wls_bands):
    gc_S = gc.CircuitModel().get_smatrix(wavelengths=wls_band)
    tr_str = " transmission to "
    plt.plot(
        wls_band,
        np.abs(gc_S["vertical_in:0", "out1:0"]) ** 2,
        "bo-",
        linewidth=2.2,
        label="TE transmission",
    )
    plt.plot(
        wls_band,
        np.abs(gc_S["vertical_in:1", "out1:1"]) ** 2,
        "ro-",
        linewidth=2.2,
        label="TM transmission",
    )
    plt.xlabel("Wavelength [um]", fontsize=16)
    plt.ylabel("Transmission [a.u.]", fontsize=16)
    plt.title(gc.fixed_name, fontsize=16)
    plt.legend(fontsize=14, loc=6)
    plt.show()
