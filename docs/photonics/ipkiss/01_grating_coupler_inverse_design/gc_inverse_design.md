# 光栅耦合器逆向设计

## 目标
在这个例子我希望设计一个应用在二维激光雷达中的光栅耦合器，参考：[2D OPA](nature11727.pdf)。注意，在二维激光雷达中，
使用的光栅耦合器的尺寸不能太大。因此，使用3D FDTD仿真的方法来设计光栅耦合器是可行的。

## 原有代码修改
版图部分在IPKISS中实现，仿真部分通过[IPKISS Link for Ansys FDTD](https://academy.lucedaphotonics.com/tutorials/device_sim/lumerical_fdtd_solutions#lumerical-fdtd-tutorial)
在Ansys FDTD中实现。但是目前IPKISS Link for Ansys FDTD并不支持垂直方向端口的设置。因此，我们需要修改原有的代码。

```python
# file: luceda_{version}\python\envs\ipkiss3\Lib\site-packages\ipkiss3\simulation\engines\lumerical\fdtd\exporter.py
class PortExporter(LumericalFDTDExporter):
    """Exports Lumerical statements for IPKISS ports"""

    primitive_type: Type[Port] = Port

    def export(self, port: Port) -> Iterator[Tuple[StatementGroups, str]]:
        context = self.context
        x, y, z = port.position

        # print("position", port.position)
        # print("box_size", port.box_size)
        # print("normal", port.normal)
        if port.normal[2] != 0:
            port_length, port_width = port.box_size
            # by default, the projection of the port normal on the xy plane is the x axis
            port_angle = math.atan2(port.normal[2], port.normal[0]) * RAD2DEG

            if z > 0:
                injection_axis = "z-axis"
                direction = "Backward"
                width_axis = "y"
                length_axis = "x"
                phi = 0.0
                angle = 90 - port_angle

            else:
                injection_axis = "z-axis"
                direction = "forward"
                width_axis = "y"
                length_axis = "x"
                phi = 0.0
                angle = 90 - port_angle

            port_name = context.normalize_variable_name(port.name)

            stmts = [
                "addport;",
                f"port_{port_name}_x = {format_val(x * 1e-6)};",
                f"port_{port_name}_y = {format_val(y * 1e-6)};",
                f"port_{port_name}_z = {format_val(z * 1e-6)};",
                f'set("name", "{port.name}");',
                f'set("injection axis", "{injection_axis}");',
                f'set("phi", {phi});',
                f'set("direction","{direction}");',
                f'set("x", port_{port_name}_x);',
                f'set("y", port_{port_name}_y);',
                f'set("z", port_{port_name}_z);',
                f'set("{width_axis} span", {format_val(abs(port_width * 1.e-6 / math.cos(angle * DEG2RAD)))});',
                f'set("{length_axis} span", {format_val(port_length * 1.e-6)});',
                f'set("theta", {angle});',
                f'set("number of field profile samples", {3});',
            ]


        else:
            ...
            # the following is the original code in the software.
```

在上面的代码中我们添加了一个新的`if`语句，通过端口的法向量来判断端口的方向。
如果端口的法向量的z分量不为0，那么我们就认为这是一个垂直方向的端口。在这里，为了简化问题，
我只考虑了以光栅器件的波导方向作为x轴的情况（即垂直输入端口的法向量y分量为0）。
此时我们可以通过端口的法向量的z分量来判断端口的方向。如果z分量大于0，那么我们认为光从端口的上方进入，端口为"backward"；
反之则为"forward"。这与Ansys FDTD官网的光栅示例是一致的。

## 版图设计与仿真
在版图设计中，我套用了`Luceda Academy`中的[光栅耦合器](https://academy.lucedaphotonics.com/pdks_sources/si_fab/si_fab/ipkiss/si_fab/components/grating_coupler/doc/)。在Luceda Academy中,
`Grating Coupler`的设计被分拆为了`Grating`和`Socket`两个部分。这里的光栅使用了两种不同的刻蚀方式，通过破坏周期性的方式将更多光耦合到空间上方。一共设置了四个优化参数：

- `grating_period`: 光栅周期
- `grating_width`: 光栅宽度
- `line_width`: 刻蚀线宽
- `first_curve_radius`: 第一个曲线的半径

优化目标有三个，我们希望尽量尽量增大向上的耦合效率，同时减小反射率和向下的耦合效率。

在仿真部分，我们使用了IPKISS Link for Ansys FDTD将版图传输给Ansys FDTD来进行仿真。考虑到我们的优化目标，我们需要在仿真中设置三个监视器/端口，
其中两个是垂直方向的端口，一个是水平方向的端口。因此我们需要一个额外的函数来把垂直端口添加到仿真中：

```python
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
```

返回的`Port`对象可以直接由IPKISS Link传入到仿真中。

优化算法使用了[pymoo](https://pymoo.org/)中的 `NSGA-II`，并且设置了`pop_size=20`，`max_gen=30`。

最终的优化结果如下：

```python
# Evaluating: [0.494 0.245 2.575 4.957]
# Transmission up: 0.3897203009661673, reflection: 0.09949659213882654, down: 0.1342305583145064
```

得到的光栅耦合器的周期为2.575um，宽度为0.494um，刻蚀线宽为0.245um，第一个曲线的半径为4.957um。向上的耦合效率为0.3897%，略低于论文中的情况；考虑到我们的设计工作在损耗略大的O波段，这是一个可以接受的结果。

## 补充
如果需要设计的完整代码，请联系我：[Email](mailto:xuhao.wu@kaust.edu.sa) 并说明您的用途。任何商业用途都是不被允许的。
