# Copyright (C) 2020 Luceda Photonics
# This version of Luceda Academy and related packages
# (hereafter referred to as Luceda Academy) is distributed under a proprietary License by Luceda
# It does allow you to develop and distribute add-ons or plug-ins, but does
# not allow redistribution of Luceda Academy  itself (in original or modified form).
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# For the details of the licensing contract and the conditions under which
# you may use this software, we refer to the
# EULA which was distributed along with this program.
# It is located in the root of the distribution folder.

from imecas import all as pdk
import ipkiss3.all as i3
import multiprocessing
from imecas.components.grating_couplers.optimization.opt_utils import (
    # optimize_gc_pso,
    optimize_gc_nsga2
    # optimize_gc_pso_in_and_sub
)

wavelength = 1.31


class GC_Circuit(i3.Circuit):
    data_tag = i3.LockedProperty()
    period = i3.PositiveNumberProperty(doc="period of the grating")
    line_width = i3.PositiveNumberProperty(doc="line width of the grating lines")
    first_curve_radius = i3.PositiveNumberProperty(doc="radius of the first curve")
    line_length = i3.PositiveNumberProperty(doc="length of the grating lines")

    def _default_data_tag(self):
        return "opa_grating_oband"

    def _default_name(self):
        return self.data_tag

    def _default_period(self):
        return 0.629

    def _default_line_width(self):
        return 0.281

    def _default_first_curve_radius(self):
        return 2.568

    def _default_line_length(self):
        return 4.043

    def _default_insts(self):
        wg = pdk.SWG_O_WG380().Layout(shape=[(0, 0), (1.0, 0)])
        gc = pdk.OPA_Grating_Oband(
            period=self.period,
            line_width=self.line_width,
            first_curve_radius=self.first_curve_radius,
            line_length=self.line_length,
        )
        return {"wg": wg, "gc": gc}

    def _default_specs(self):
        return [
            i3.Place("gc:out", (0, 0)),
            i3.Place("wg:in", (0, 0), relative_to="gc:out"),
        ]

    def _default_exposed_ports(self):
        return {
            "wg:out": "out",
            "gc:vertical_in": "vertical_in",
            "gc:substrate": "substrate",
        }


def main():
    best_solutions, best_trans_up, best_reflection, best_trans_down = optimize_gc_nsga2(
        gc_class=GC_Circuit,
        max_gen=30,
        pop_size=20,
        wavelengths=(1.25, 1.35, 101),
        center_wavelength=1.31,
        verbose=True,
        plot=True,
        n_best_solutions=10
    )

    print("OPTIMIZATION RESULTS")
    print("Top 10 solutions:")
    for i, (solution, trans_up, reflection, trans_down) in enumerate(zip(best_solutions, best_trans_up, best_reflection, best_trans_down), 1):
        print(f"\nSolution {i}:")
        print(f"Period = {solution[0]:.6f} um")
        print(f"Line width = {solution[1]:.6f} um")
        print(f"First curve radius = {solution[2]:.6f} um")
        print(f"Line length = {solution[3]:.6f} um")
        print(f"Trans up: {trans_up:.6f}")
        print(f"Reflection: {reflection:.6f}")
        print(f"Trans down: {trans_down:.6f}")

    print("\nVisualization:")
    print("1. Pareto front has been saved as 'pareto_front.png'")
    print("2. Objective function history has been saved as 'objective_history.png'")


if __name__ == "__main__":
    main()

# scipy: period: 0.47 - line width: 0.289 - first curve radius: 1.803 - line length: 2.738 -
# transmission: 0.3589423372632435; one of the highest values - around 0.36

# pso: period: 0.629 - line width: 0.281 - first curve radius: 2.568 - line length: 4.043 -
# transmission: 0.53020035176997
# OPTIMIZATION RESULTS
# Optimal period = 0.628557661033572 um
# Optimal line width = 0.28119172279126503 um
# Optimal line length = 2.5679106122880833 um
# Optimal first curve radius = 4.043274934336219 um
# period: 0.598 - line width: 0.214 - first curve radius: 1.999 - line length: 3.328
# - upward trans: 0.3668 - downward trans: 0.0533 - cost: -0.3401
# period: 0.6 - line width: 0.212 - first curve radius: 2.074 - line length: 4.818
# - upward trans: 0.3471 - downward trans: 0.0573 - cost: -0.3184
# best cost: -0.2777424922609053, best pos: [0.42301378 0.23264959 3.41333121 3.04283981]

# NSGA2: Evaluating: [0.696 0.436 2.122 4.527]
# Transmission up: 0.3359488235431105, down: 0.15028771773409028, reflection: 0.09489401487517535
# Evaluating: [0.632 0.322 1.448 2.838]
# Transmission up: 0.32732792273192945, reflection: 0.12998861050045887, down: 0.07432472020135696
# Evaluating: [0.621 0.322 1.578 2.45 ]
# Transmission up: 0.34776945698263956, reflection: 0.059933680828008554, down: 0.10665485329908808
# Evaluating: [0.562 0.216 1.335 4.179]
# Transmission up: 0.36063217521458063, reflection: 0.07606690499244727, down: 0.06189943626043778
# Evaluating: [0.625 0.323 1.498 2.319]

# layer 1: FETCH, Layer 2: METCH
# Period = 0.595409 um
# Line width = 0.225507 um
# First curve radius = 1.280626 um
# Line length = 2.586288 um
# Trans up: 0.340900
# Reflection: 0.071891
# Trans down: 0.036983

# METCH, SETCH
# Evaluating: [0.493 0.249 2.579 4.957]
# Transmission up: 0.38895890507995823, reflection: 0.1009235833294181, down: 0.13652636481757835
# Evaluating: [0.494 0.245 2.575 4.957]
# Transmission up: 0.3897203009661673, reflection: 0.09949659213882654, down: 0.1342305583145064
# Evaluating: [0.492 0.249 2.579 4.978]
# Transmission up: 0.38952999607091876, reflection: 0.10176919776749742, down: 0.13767005625100762
