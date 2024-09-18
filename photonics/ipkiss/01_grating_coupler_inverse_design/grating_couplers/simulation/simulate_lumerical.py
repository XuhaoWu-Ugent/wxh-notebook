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

from ipkiss3 import all as i3
import numpy as np
from ipkiss.constants import DEG2RAD, RAD2DEG


def convert_vertical_port_to_port(port, box_size=(2.0, 1.0), n_modes=1):

    if isinstance(port, i3.VerticalOpticalPort):
        name = port.name
        position = port.position
        angle = port.angle
        inclination = port.inclination
        Port = i3.device_sim.Port(
                name=name,
                position=(position[0], position[1], 1.5),
                # 1.5 is the esstimated height of the vertical port in si_fab pdk
                normal=(
                    np.cos(angle * DEG2RAD) * np.cos(inclination * DEG2RAD),
                    np.sin(angle * DEG2RAD) * np.cos(inclination * DEG2RAD),
                    np.sin(inclination * DEG2RAD)
                ),
                box_size=box_size,
                n_modes=n_modes
            )
    else:
        raise ValueError("The ports must be of type VerticalOpticalPort")

    return Port


def convert_substrate_port_to_port(port, box_size=(2.0, 1.0), n_modes=1):

    if isinstance(port, i3.VerticalOpticalPort):
        name = port.name
        position = port.position
        angle = port.angle
        inclination = port.inclination
        Port = i3.device_sim.Port(
                name=name,
                position=(position[0], position[1], -1.0),
                # 1.5 is the esstimated height of the vertical port in si_fab pdk
                normal=(
                    np.cos(angle * DEG2RAD) * np.cos(inclination * DEG2RAD),
                    np.sin(angle * DEG2RAD) * np.cos(inclination * DEG2RAD),
                    np.sin(inclination * DEG2RAD)
                ),
                box_size=box_size,
                n_modes=n_modes
            )
    else:
        raise ValueError("The ports must be of type VerticalOpticalPort")

    return Port


def simulate_gc_by_lumerical_fdtd(
        layout, project_folder, mesh_accuracy=1, wavelengths=(1.25, 1.35, 101), inspect=False
):
    """It simulates a gc using the link to ANSYS Lumerical FDTD and returns the transmission and
    reflection.

    Parameters
    ----------
    layout : LayoutView
        layout view of the gc
    project_folder : str
        Folder in which the simulation is performed
    mesh_accuracy : int, optional, default=1
        Accuracy of the mesh used for FDTD simulation
    wavelengths: tuple, optional, default=(1.5, 1.6, 101)
        Wavelength range of the simulation in um, format is (minumum wavelength, maximum wavelength, number of
        points)
    inspect: boolean, optional, default=False
        Whether or not to start a Lumerical GUI of the FDTD model before it runs.

    Returns
    -------
    transmission, reflection : list of floats, list of floats

    """

    geometry = i3.device_sim.SimulationGeometry(layout=layout)

    my_setup = i3.device_sim.Macro(commands=[
        # 'addgaussian;',
        # 'set("injection axis", "z");',
        # 'set("direction", "backward");',
        # 'set("x", -15e-6);',
        # 'set("y", 0);',
        # 'set("x span", 5e-6);',
        # 'set("y span", 5e-6);',
        # 'set("z", 5e-6);',
        # 'set("waist radius w0",0.5e-6);',
        # 'set("distance from waist",-5e-6);',
        'addpower;',
        'set("name", "in_power");',
        'set("monitor type", "2D Z-normal");',
        'set("z", 0.75e-6);',
        'set("x min", -3e-6);',
        'set("x max", 3e-6);',
        'set("y min", -2.81e-6);',
        'set("y max", 2.81e-6);',
        'addpower;',
        'set("name", "sub_power");',
        'set("monitor type", "2D Z-normal");',
        'set("z", 0.4e-6);',
        'set("x min", -3e-6);',
        'set("x max", 3e-6);',
        'set("y min", -2.81e-6);',
        'set("y max", 2.81e-6);',
    ])

    outputs = [
        i3.device_sim.SMatrixOutput(
            name="smatrix",
            symmetries=[],
            wavelength_range=wavelengths,
        )
    ]

    monitors = [i3.device_sim.Port(name=p.name, box_size=(2.0, 1.0)) for p in layout.ports
                if not (isinstance(p, i3.VerticalOpticalPort) or getattr(p, "domain", None) == i3.ElectricalDomain)
                ]

    for p in layout.ports:
        if isinstance(p, i3.VerticalOpticalPort):
            if "vertical_in" in p.name:
                monitors.append(convert_vertical_port_to_port(p))
            elif "substrate" in p.name:
                monitors.append(convert_substrate_port_to_port(p))
            else:
                print(f"Warning: Vertical port {p.name} does not match any known type")


    setup_macros = [
        i3.device_sim.lumerical_macros.fdtd_mesh_accuracy(mesh_accuracy=mesh_accuracy),
        i3.device_sim.lumerical_macros.fdtd_profile_xy(alignment_port="out"),
        my_setup
    ]

    material_map = {
        i3.TECH.MATERIALS.SILICON: "Si (Silicon) - Palik",
        i3.TECH.MATERIALS.SILICON_OXIDE: "SiO2 (Glass) - Palik",
    }

    # Simulation job
    simjob = i3.device_sim.LumericalFDTDSimulation(
        geometry=geometry,
        outputs=outputs,
        monitors=monitors,
        setup_macros=setup_macros,
        project_folder=project_folder,
        solver_material_map=material_map,
        verbose=True,
        headless=True,
    )

    # Execute and save_results.
    if inspect:
        simjob.inspect()

    smatrix = simjob.get_result(outputs[0].name)

    return smatrix
