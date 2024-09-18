from ipkiss3 import all as i3
from ...utils import ImecasCell
from ipcore.properties.predefined import StringProperty
from imecas.components.waveguides.fetch import StripWaveguideTemplate
from .models.circuit_models import GratingCoupler1DCircuitModel

__all__ = [
    "FGC_C_TE_WG450",
    "FGC_C_TM_WG450",
    "FGC_O_TE_WG380",
    "FGC_O_TM_WG380"
]


class FGC_C_TE_WG450(ImecasCell):
    """ FGC_C_TE_WG450 """

    model_name = StringProperty(
        doc="Name used for the model data txt files", locked=True
    )

    def _default_name(self):
        return "FGC_C_TE_WG450"

    def _default_foldername(self):
        return "grating_couplers"

    def _default_fixed_name(self):
        return "FGC_C_TE_WG450"

    def _default_model_name(self):
        return "FGC_C_TE_WG450"

    class Layout(ImecasCell.Layout):
        trace_template = StripWaveguideTemplate()
        trace_template.Layout(core_width=0.45)

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="out1",
                                    position=(43.911, 15.000),
                                    angle=0.0,
                                    trace_template=self.trace_template())
            ports += i3.VerticalOpticalPort(name="vertical_in",
                                            position=(15, 15),
                                            angle_deg=0,
                                            inclination_deg=180
                                            )

            return ports

    class CircuitModel(GratingCoupler1DCircuitModel):
        polarisation = 0


class FGC_C_TM_WG450(ImecasCell):
    """ FGC_C_TM_WG450 """

    model_name = StringProperty(
        doc="Name used for the model data txt files", locked=True
    )

    def _default_name(self):
        return "FGC_C_TM_WG450"

    def _default_foldername(self):
        return "grating_couplers"

    def _default_fixed_name(self):
        return "FGC_C_TM_WG450"

    def _default_model_name(self):
        return "FGC_C_TM_WG450"

    class Layout(ImecasCell.Layout):
        trace_template = StripWaveguideTemplate()
        trace_template.Layout(core_width=0.45)

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="out1",
                                    position=(44.401, 15.000),
                                    angle=0.0,
                                    trace_template=self.trace_template)
            ports += i3.VerticalOpticalPort(name="vertical_in",
                                            position=(15, 15),
                                            angle_deg=0,
                                            inclination_deg=180
                                            )

            return ports

    class CircuitModel(GratingCoupler1DCircuitModel):
        polarisation = 1


class FGC_O_TE_WG380(ImecasCell):
    """ FGC_O_TE_WG380 """

    model_name = StringProperty(
        doc="Name used for the model data txt files", locked=True
    )

    def _default_name(self):
        return "FGC_O_TE_WG380"

    def _default_foldername(self):
        return "grating_couplers"

    def _default_fixed_name(self):
        return "FGC_O_TE_WG380"

    def _default_model_name(self):
        return "FGC_O_TE_WG380"

    class Layout(ImecasCell.Layout):
        trace_template = StripWaveguideTemplate()
        trace_template.Layout(core_width=0.38)

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="out1",
                                    position=(46.000, 15.000),
                                    angle=0.0,
                                    trace_template=self.trace_template)
            ports += i3.VerticalOpticalPort(name="vertical_in",
                                            position=(14.887, 15),
                                            angle_deg=0,
                                            inclination_deg=180
                                            )

            return ports

    class CircuitModel(GratingCoupler1DCircuitModel):
        polarisation = 0


class FGC_O_TM_WG380(ImecasCell):
    """ FGC_O_TM_WG380 """

    model_name = StringProperty(
        doc="Name used for the model data txt files", locked=True
    )

    def _default_name(self):
        return "FGC_O_TM_WG380"

    def _default_foldername(self):
        return "grating_couplers"

    def _default_fixed_name(self):
        return "FGC_O_TM_WG380"

    def _default_model_name(self):
        return "FGC_O_TM_WG380"

    class Layout(ImecasCell.Layout):
        trace_template = StripWaveguideTemplate()
        trace_template.Layout(core_width=0.38)

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="out1",
                                    position=(45.355, 15.000),
                                    angle=0.0,
                                    trace_template=self.trace_template)
            ports += i3.VerticalOpticalPort(name="vertical_in",
                                            position=(15, 15),
                                            angle_deg=0,
                                            inclination_deg=180
                                            )

            return ports

    class CircuitModel(GratingCoupler1DCircuitModel):
        polarisation = 1


class Socket(i3.PCell):
    """Grating coupler socket with a parabolic taper between two waveguide templates."""

    _name_prefix = "Socket"
    start_wg_template = i3.WaveguideTemplateProperty(doc="Waveguide template for the socket at the output port")
    end_wg_template = i3.WaveguideTemplateProperty(doc="Waveguide template at the end of the socket")

    transition = i3.ChildCellProperty(doc="the transition (automatically evaluated)", locked=True)
    socket_length = i3.PositiveNumberProperty(default=40.0, doc="length of the socket")
    end_width = i3.PositiveNumberProperty(default=10.0, doc="end width of the socket")

    def _default_start_wg_template(self):
        return StripWaveguideTemplate()

    def _default_end_wg_template(self):
        # calculates the end trace template based on the start trace template
        return self.start_wg_template.modified_copy(name=self.name + "endwg")

    def _default_transition(self):
        # calculates the transition between the start and end waveguide template
        return i3.ParabolicWindowWaveguideTransition(
            name=self.name + "transition",
            start_trace_template=self.start_wg_template,
            end_trace_template=self.end_wg_template,
        )

    class Layout(i3.LayoutView):
        def _default_end_wg_template(self):
            # sets the widths of the end trace template
            lov = self.cell.end_wg_template.get_default_view(i3.LayoutView)
            lov.set(core_width=self.end_width, cladding_width=lov.cladding_width + self.end_width - lov.core_width)
            return lov

        def _default_transition(self):
            # sets the layout parameters of the transition
            lov = self.cell.transition.get_default_view(i3.LayoutView)
            lov.set(start_position=(0.5 * self.socket_length, 0.0), end_position=(-0.5 * self.socket_length, 0.0))
            return lov

        def _generate_instances(self, insts):
            # place the transition
            insts += i3.SRef(name="transition", reference=self.transition, flatten=True)
            return insts

        def _generate_ports(self, ports):
            # Only copy the 'in' port, but rename it to 'out', as it is the output port
            # of our socket
            ports += self.instances["transition"].ports["in"].modified_copy(name="out")
            return ports

    class Netlist(i3.NetlistFromLayout):
        pass


class Grating(i3.PCell):
    """Simple periodic grating whose grating lines follow a circular arc."""

    _name_prefix = "Grating"
    period = i3.PositiveNumberProperty(default=0.63, doc="period of the grating")
    line_width = i3.PositiveNumberProperty(default=0.32, doc="line width of the grating lines")
    line_length = i3.PositiveNumberProperty(default=12.0, doc="length of the grating lines")
    n_o_periods = i3.NonNegativeIntProperty(default=25, doc="number of periods in the grating")
    grating_layer_1 = i3.LayerProperty(default=i3.TECH.PPLAYER.METCH, doc="layer for the first grating line")
    grating_layer_2 = i3.LayerProperty(default=i3.TECH.PPLAYER.SETCH, doc="layer for the other grating lines")
    first_curve_radius = i3.PositiveNumberProperty(default=10.0, doc="Radius of curvature of first grating line.")

    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            # vertical ports, move the port more to the left
            mid_point = self.period * self.n_o_periods * 0.1
            ports += i3.VerticalOpticalPort(
                name="vertical_in",
                position=(-mid_point, 0.0),
                angle=180.0,
                inclination=80.0,
            )
            ports += i3.VerticalOpticalPort(
                name="substrate",
                position=(-mid_point, 0.0),
                angle=180.0,
                inclination=80.0,
            )
            return ports

        def _generate_elements(self, elems):
            # grating lines
            for i in range(self.n_o_periods):
                x = -i * self.period
                r = -x + self.first_curve_radius
                a = (self.line_length / r) * i3.RAD2DEG  # angular spread
                layer = self.grating_layer_1 if i == 0 else self.grating_layer_2
                elems += i3.ArcPath(
                    layer=layer,
                    center=(self.first_curve_radius, 0.0),
                    radius=r,
                    start_angle=180.0 - 0.5 * a,
                    end_angle=180.0 + 0.5 * a,
                    line_width=self.line_width,
                )
            return elems

    class Netlist(i3.NetlistFromLayout):
        pass


class GratingCoupler(i3.PCell):
    """Generic grating coupler PCell that has a grating and a socket child cell."""

    _name_prefix = "GratingCoupler"

    period = i3.PositiveNumberProperty(default=0.63, doc="period of the grating")
    line_width = i3.PositiveNumberProperty(default=0.32, doc="line width of the grating lines")
    line_length = i3.PositiveNumberProperty(default=12.0, doc="length of the grating lines")
    n_o_periods = i3.NonNegativeIntProperty(default=25, doc="number of periods in the grating")
    grating_layer_1 = i3.LayerProperty(default=i3.TECH.PPLAYER.METCH, doc="layer for the first grating line")
    grating_layer_2 = i3.LayerProperty(default=i3.TECH.PPLAYER.SETCH, doc="layer for the other grating lines")
    first_curve_radius = i3.PositiveNumberProperty(default=10.0, doc="Radius of curvature of first grating line.")

    start_wg_template = i3.WaveguideTemplateProperty(doc="Waveguide template for the socket at the output port")
    end_wg_template = i3.WaveguideTemplateProperty(doc="Waveguide template at the end of the socket")
    socket_length = i3.PositiveNumberProperty(default=40.0, doc="length of the socket")
    end_width = i3.PositiveNumberProperty(default=10.0, doc="end width of the socket")

    def _default_start_wg_template(self):
        tt = StripWaveguideTemplate()
        tt.Layout(core_width=0.38)
        return tt

    def _default_end_wg_template(self):
        # calculates the end trace template based on the start trace template
        end_width = self.end_width
        start_tt = self.start_wg_template
        lov = start_tt.get_default_view(i3.LayoutView)
        end_tt = start_tt.modified_copy(name=self.name + "endwg")
        end_tt.Layout(core_width=end_width, cladding_width=lov.cladding_width + end_width - lov.core_width)
        return end_tt

    grating = i3.ChildCellProperty(doc="the grating child cell")
    socket = i3.ChildCellProperty(doc="the socket child cell")

    def _default_grating(self):
        return Grating(
            name=self.name + "_grating",
            period=self.period,
            line_width=self.line_width,
            line_length=self.line_length,
            n_o_periods=self.n_o_periods,
            grating_layer_1=self.grating_layer_1,
            grating_layer_2=self.grating_layer_2,
            first_curve_radius=self.first_curve_radius,
        )

    def _default_socket(self):
        return Socket(
            name=self.name + "_socket",
            start_wg_template=self.start_wg_template,
            end_wg_template=self.end_wg_template,
            socket_length=self.socket_length,
            end_width=self.end_width,
        )

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            # add the child cells to the layout
            insts += i3.SRef(name="grating", reference=self.grating)
            insts += i3.SRef(name="socket", reference=self.socket)
            return insts

        def _generate_ports(self, ports):
            ports += [p.modified_copy() for p in self.instances["grating"].ports]
            ports += [p.modified_copy() for p in self.instances["socket"].ports]
            return ports

    class Netlist(i3.NetlistFromLayout):
        pass


class OPA_Grating_Oband(GratingCoupler):
    data_tag = i3.LockedProperty()

    def _default_data_tag(self):
        return "opa_grating_oband"

    def _default_name(self):
        return self.data_tag.upper()

    def _default_n_o_periods(self):
        return 5

    def _default_period(self):
        return 0.629

    def _default_line_width(self):
        return 0.281

    def _default_first_curve_radius(self):
        return 2.568

    def _default_line_length(self):
        return 4.043

    def _default_socket_length(self):
        return 6.0

    def _default_end_width(self):
        return 4.0
