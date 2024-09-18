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

from imecas.components.grating_couplers.simulation.simulate_lumerical import simulate_gc_by_lumerical_fdtd
import numpy as np
import os
import scipy.optimize as opt
from pyswarms.single.global_best import GlobalBestPSO
import multiprocessing
from functools import partial
import matplotlib.pyplot as plt
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.sampling.lhs import LatinHypercubeSampling
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.util.display.display import Display


def optimize_gc_scipy(
        gc_class,
        initial_period=0.4,
        initial_line_width=0.2,
        initial_first_curve_radius=2.5,
        initial_line_length=2.5,
        max_iter=100,
        wavelengths=(1.25, 1.35, 101),
        center_wavelength=1.31,
        verbose=False,
        plot=True,
):
    """Optimizes the length and waveguide spacing of a gc at fixed wavelength, .

    Parameters
    ----------
    gc_class :
        PCell class of the gc to optimize
    initial_period : float, optional, default=0.4
        Initial period of the GC at the first iteration [um]
    initial_line_width : float, optional, default=0.2
        Initial line width of the GC at the first iteration [um]
    initial_line_length : float, optional, default=2.5
        Initial line length of the GC at the first iteration [um]
    initial_first_curve_radius : float, optional, default=2.5
        Initial first curve radius of the GC at the first iteration [um]
    max_iter : int, optional, default=100
        Max number of iterations for the optimization
    wavelengths : float, optional, default=(1.25, 1.35, 101)
        Wavelengths of the optimization [um]
    center_wavelength : float, optional, default=1.31
        Center wavelength of the optimization [um]
    verbose : boolean, optional, default=False
        Print statements if True
    plot : boolean, optional, default=True
        Plot the optimized result

    Returns
    -------
    optimized_length, optimized_waveguide_spacing : float, float
        Optimized length and waveguide spacing for the MMI
    """

    def to_minimize(x):
        # Round the values to 3 decimal places
        x = np.round(x, 3)

        # Paths
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "data")
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        base_directory = os.path.join(data_dir, gc_class().data_tag)
        if not os.path.exists(base_directory):
            os.mkdir(base_directory)
        base_directory_lum = os.path.join(base_directory, f"lum_{x[0]}_{x[1]}_{x[2]}_{x[3]}")
        if not os.path.exists(base_directory_lum):
            os.mkdir(base_directory_lum)
        base_directory_model = os.path.join(base_directory, "model")
        if not os.path.exists(base_directory_model):
            os.mkdir(base_directory_model)

        smatrix_path = os.path.join(base_directory_lum, "smatrix.s2p")

        if x[1] < 0.18:  # If line width (x[1]) is out of bounds, return very small value of trans
            cost = 0.00001

        elif x[0] - x[1] < 0.18:  # If etch width (x[1] - x[2]) is out of bounds, return very small value of trans
            cost = 0.00001
        else:  # If wg_spacing (x[1]) is in bounds, run the simulation
            lv = gc_class(
                period=x[0],
                line_width=x[1],
                first_curve_radius=x[2],
                line_length=x[3],
            ).Layout()

            smatrix = simulate_gc_by_lumerical_fdtd(
                layout=lv,
                project_folder=base_directory_lum,
                wavelengths=wavelengths
            )
            smatrix.to_touchstone(smatrix_path)
            index = np.searchsorted(np.linspace(wavelengths[0], wavelengths[1], wavelengths[2]), center_wavelength)
            trans = np.abs(smatrix["out", "vertical_in"])[index]
            cost = -trans

        if verbose is True:
            print(
                "period: {} - line width: {} - first curve radius: {} - line length: {} - transmission: {} ".format(
                    x[0], x[1], x[2], x[3], np.abs(cost)
                )
            )

        if np.abs(cost) > 1.0:
            import warnings

            warnings.warn(
                "The transmission of value of {} is bigger than 1.0, something must be incorrect in the simulation."
            )

        return -np.abs(cost)

    res = opt.minimize(
        to_minimize,
        x0=np.array([initial_period, initial_line_width, initial_first_curve_radius, initial_line_length]),
        method="Nelder-Mead",
        options={"xtol": 1e-2, "disp": True, "maxiter": max_iter},
    )

    if plot:
        lv_opt = gc_class(
            period=res.x[0],
            line_width=res.x[1],
            first_curve_radius=res.x[2],
            line_length=res.x[3],
        ).Layout()
        lv_opt.visualize(annotate=True)

    return res.x


def optimize_gc_pso(
        gc_class,
        # initial_period=0.4,
        # initial_line_width=0.2,
        # initial_first_curve_radius=2.5,
        # initial_line_length=2.5,
        max_iter=50,
        wavelengths=(1.25, 1.35, 101),
        center_wavelength=1.31,
        verbose=False,
        plot=True,
):
    def objective_function(x):
        costs = []
        for params in x:
            # Round the values to 3 decimal places
            params = np.round(params, 3)

            # Paths
            data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "data")
            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
            base_directory = os.path.join(data_dir, gc_class().data_tag)
            if not os.path.exists(base_directory):
                os.mkdir(base_directory)
            base_directory_lum = os.path.join(base_directory, f"lum_{params[0]}_{params[1]}_{params[2]}_{params[3]}")
            if not os.path.exists(base_directory_lum):
                os.mkdir(base_directory_lum)
            base_directory_model = os.path.join(base_directory, "model")
            if not os.path.exists(base_directory_model):
                os.mkdir(base_directory_model)

            smatrix_path = os.path.join(base_directory_lum, "smatrix.s3p")

            if params[1] < 0.18 or params[0] - params[1] < 0.18:  # If out of bounds, return very small value of trans
                cost = 0.0001
                trans_up = 0
                trans_down = 0
                reflection = 0
            else:  # If in bounds, run the simulation
                lv = gc_class(
                    period=params[0],
                    line_width=params[1],
                    first_curve_radius=params[2],
                    line_length=params[3],
                ).Layout()

                smatrix = simulate_gc_by_lumerical_fdtd(
                    layout=lv,
                    project_folder=base_directory_lum,
                    wavelengths=wavelengths
                )
                smatrix.to_touchstone(smatrix_path)
                index = np.searchsorted(np.linspace(wavelengths[0], wavelengths[1], wavelengths[2]), center_wavelength)

                # Get both upward and downward coupling
                trans_up = np.abs(smatrix["out", "vertical_in"])[index]
                trans_down = np.abs(smatrix["out", "substrate"])[index]
                reflection = np.abs(smatrix["out", "out"])[index]

                # Calculate cost: maximize upward coupling and minimize downward coupling
                cost = -(trans_up - 0.3 * trans_down - 0.4 * reflection)

            if verbose:
                print(
                    f"period: {params[0]} - line width: {params[1]} - first curve radius: {params[2]} - "
                    f"line length: {params[3]} - upward trans: {trans_up:.4f} - downward trans: {trans_down:.4f}"
                    f"- reflection: {reflection} - cost: {cost:.4f}"
                )

            if np.abs(cost) > 1.0:
                import warnings
                warnings.warn(
                    "The transmission value of {} is bigger than 1.0, something must be incorrect in the simulation."
                )

            costs.append(-np.abs(cost))
        return np.array(costs)

    # Define bounds
    lower_bound = [0.36, 0.18, 1.0, 1.0]  # Adjust these values based on your requirements
    upper_bound = [0.7, 0.52, 5.0, 5.0]  # Adjust these values based on your requirements
    bounds = (lower_bound, upper_bound)

    # Initialize swarm
    options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
    optimizer = GlobalBestPSO(n_particles=10, dimensions=4, options=options, bounds=bounds)

    # Perform optimization
    cost, pos = optimizer.optimize(objective_function, iters=max_iter)

    # 计算最佳参数的 trans_up 和 trans_down
    _, best_trans_up, best_trans_down, best_reflection = objective_function_single(pos, gc_class, wavelengths,
                                                                                   center_wavelength, verbose)

    if plot:
        lv_opt = gc_class(
            period=pos[0],
            line_width=pos[1],
            first_curve_radius=pos[2],
            line_length=pos[3],
        ).Layout()
        lv_opt.visualize(annotate=True)

        # Plot the cost history
        plt.figure(figsize=(10, 6))
        plt.plot(optimizer.cost_history)
        plt.title('Optimization Progress')
        plt.xlabel('Iteration')
        plt.ylabel('Cost')
        plt.show()

    # Print the best parameters found
    print(f"Best parameters: period={pos[0]:.3f}, line_width={pos[1]:.3f}, "
          f"first_curve_radius={pos[2]:.3f}, line_length={pos[3]:.3f}")
    print(f"Best cost: {cost:.6f}")
    print(f"Best trans up: {best_trans_up:.6f}")
    print(f"Best trans down: {best_trans_down:.6f}")
    print(f"Best reflection: {best_reflection:.6f}")

    return pos, best_trans_up, best_trans_down, best_reflection


# NSGA2
class GratingCouplerProblem(Problem):
    def __init__(self, gc_class, wavelengths, center_wavelength):
        super().__init__(n_var=4, n_obj=3, n_constr=1,
                         xl=np.array([0.36, 0.18, 1.0, 1.0]),
                         xu=np.array([0.7, 0.52, 5.0, 5.0]))
        self.gc_class = gc_class
        self.wavelengths = wavelengths
        self.center_wavelength = center_wavelength

    def _evaluate(self, x, out, *args, **kwargs):
        f = np.full((x.shape[0], 3), 1e10)  # Initialize with worst possible values
        g = np.zeros((x.shape[0], 1))

        for i, params in enumerate(x):
            params = np.round(params, 3)
            print(f"Evaluating: {params}")

            # Check constraints
            if params[1] < 0.18 or params[0] - params[1] < 0.18:
                g[i] = -1  # Constraint violation
                continue  # Skip to the next iteration

            data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "data")
            os.makedirs(data_dir, exist_ok=True)
            base_directory = os.path.join(data_dir, self.gc_class().data_tag)
            os.makedirs(base_directory, exist_ok=True)
            base_directory_lum = os.path.join(base_directory, f"lum_me_se_{params[0]}_{params[1]}_{params[2]}_{params[3]}")
            os.makedirs(base_directory_lum, exist_ok=True)

            smatrix_path = os.path.join(base_directory_lum, "smatrix.s3p")

            gc = self.gc_class(
                period=params[0],
                line_width=params[1],
                first_curve_radius=params[2],
                line_length=params[3],
            )
            lv = gc.Layout()

            try:
                smatrix = simulate_gc_by_lumerical_fdtd(
                    layout=lv,
                    project_folder=base_directory_lum,
                    wavelengths=self.wavelengths
                )
                smatrix.to_touchstone(smatrix_path)
                index = np.searchsorted(np.linspace(self.wavelengths[0], self.wavelengths[1], self.wavelengths[2]),
                                        self.center_wavelength)

                trans_up = np.abs(smatrix["out", "vertical_in"])[index]
                trans_down = np.abs(smatrix["out", "substrate"])[index]
                reflection = np.abs(smatrix["out", "out"])[index]

                f[i] = [-trans_up, reflection, trans_down]  # Objectives to minimize
                g[i] = 0

                print(f"Transmission up: {trans_up}, reflection: {reflection}, down: {trans_down}")
            except Exception as e:
                print(f"Error in simulation: {e}")

        out["F"] = f
        out["G"] = g


class MyDisplay(Display):
    def _do(self, problem, evaluator, algorithm):
        super()._do(problem, evaluator, algorithm)
        self.output.append("Best trans_up", -algorithm.pop.get("F")[:, 0].min())
        self.output.append("Best reflection", algorithm.pop.get("F")[:, 1].min())
        self.output.append("Best trans_down", algorithm.pop.get("F")[:, 2].min())


def optimize_gc_nsga2(
        gc_class,
        max_gen=100,
        pop_size=50,
        wavelengths=(1.25, 1.35, 101),
        center_wavelength=1.31,
        verbose=True,
        plot=True,
        n_best_solutions=10
):
    problem = GratingCouplerProblem(gc_class, wavelengths, center_wavelength)

    ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

    algorithm = NSGA2(
        pop_size=pop_size,
        n_offsprings=pop_size,
        sampling=LatinHypercubeSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True,
        ref_dirs=ref_dirs
    )

    class MyCallback:
        def __init__(self) -> None:
            self.data = {
                "best_trans_up": [],
                "best_reflection": [],
                "best_trans_down": []
            }

        def __call__(self, algorithm):
            self.data["best_trans_up"].append(-algorithm.pop.get("F")[:, 0].min())
            self.data["best_reflection"].append(algorithm.pop.get("F")[:, 1].min())
            self.data["best_trans_down"].append(algorithm.pop.get("F")[:, 2].min())

    callback = MyCallback()

    display = MyDisplay() if verbose else None

    res = minimize(
        problem,
        algorithm,
        ('n_gen', max_gen),
        callback=callback,
        verbose=verbose,
        display=display,
        seed=1
    )

    if plot:
        # 绘制帕累托前沿
        Scatter().add(res.F, s=30, facecolors='none', edgecolors='b').show()
        plt.title("Pareto Front")
        plt.xlabel("Trans Up (negative)")
        plt.ylabel("Reflection")
        plt.savefig('pareto_front.png')
        plt.close()

        # 绘制目标函数随代数的变化
        plt.figure(figsize=(12, 4))
        plt.subplot(131)
        plt.plot(callback.data['best_trans_up'])
        plt.title("Best Trans Up")
        plt.xlabel("Generation")
        plt.subplot(132)
        plt.plot(callback.data['best_reflection'])
        plt.title("Best Reflection")
        plt.xlabel("Generation")
        plt.subplot(133)
        plt.plot(callback.data['best_trans_down'])
        plt.title("Best Trans Down")
        plt.xlabel("Generation")
        plt.tight_layout()
        plt.savefig('objective_history.png')
        plt.close()

    # 按优先级排序所有解
    sorted_indices = np.lexsort((res.F[:, 2], res.F[:, 1], -res.F[:, 0]))
    best_solutions = res.X[sorted_indices[:n_best_solutions]]
    best_objectives = res.F[sorted_indices[:n_best_solutions]]

    return best_solutions, -best_objectives[:, 0], best_objectives[:, 1], best_objectives[:, 2]


# PSO parallel version
def objective_function_single(params, gc_class, wavelengths, center_wavelength, verbose):
    # Round the values to 3 decimal places
    params = np.round(params, 3)

    # Paths
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "data")
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    base_directory = os.path.join(data_dir, gc_class().data_tag)
    if not os.path.exists(base_directory):
        os.mkdir(base_directory)
    base_directory_lum = os.path.join(base_directory, f"lum_{params[0]}_{params[1]}_{params[2]}_{params[3]}")
    if not os.path.exists(base_directory_lum):
        os.mkdir(base_directory_lum)
    base_directory_model = os.path.join(base_directory, "model")
    if not os.path.exists(base_directory_model):
        os.mkdir(base_directory_model)

    smatrix_path = os.path.join(base_directory_lum, "smatrix.s3p")

    if params[1] < 0.18 or params[0] - params[1] < 0.18:  # If out of bounds, return very small value of trans
        cost = 0.00001
        trans_up = 0
        trans_down = 0
        reflection = 0
    else:  # If in bounds, run the simulation
        lv = gc_class(
            period=params[0],
            line_width=params[1],
            first_curve_radius=params[2],
            line_length=params[3],
        ).Layout()

        smatrix = simulate_gc_by_lumerical_fdtd(
            layout=lv,
            project_folder=base_directory_lum,
            wavelengths=wavelengths,
        )
        smatrix.to_touchstone(smatrix_path)
        index = np.searchsorted(np.linspace(wavelengths[0], wavelengths[1], wavelengths[2]), center_wavelength)

        # Get both upward and downward coupling
        trans_up = np.abs(smatrix["out", "vertical_in"])[index]
        trans_down = np.abs(smatrix["out", "substrate"])[index]
        reflection = np.abs(smatrix["out", "out"])[index]

        # Calculate cost: maximize upward coupling and minimize downward coupling
        cost = -(trans_up - 0.5 * trans_down - 0.5 * reflection)

    if verbose:
        print(
            f"period: {params[0]} - line width: {params[1]} - first curve radius: {params[2]} - "
            f"line length: {params[3]} - upward trans: {trans_up:.4f} - downward trans: {trans_down:.4f}"
            f"reflection: {reflection} - cost: {cost:.4f}"
        )

    return cost, trans_up, trans_down, reflection


def optimize_gc_pso_in_and_sub(
        gc_class,
        max_iter=100,
        wavelengths=(1.25, 1.35, 101),
        center_wavelength=1.31,
        verbose=False,
        plot=True,
        n_particles=20,
        n_processes=None  # 新参数，用于控制进程数
):
    if n_processes is None:
        n_processes = 5  # 默认使用5个进程

    def objective_function(x):
        with multiprocessing.Pool(processes=n_processes) as pool:
            func = partial(objective_function_single, gc_class=gc_class, wavelengths=wavelengths,
                           center_wavelength=center_wavelength, verbose=verbose)
            results = pool.map(func, x)
        costs = np.array([r[0] for r in results])
        return costs

    # Define bounds
    lower_bound = [0.36, 0.18, 1.0, 1.0]
    upper_bound = [0.7, 0.52, 5.0, 5.0]
    bounds = (lower_bound, upper_bound)

    # Initialize swarm with optimized parameters
    options = {
        'c1': 1.5,  # 个体学习因子
        'c2': 1.5,  # 群体学习因子
        'w': 0.7,  # 惯性权重
        'k': 3,  # 使用K-近邻拓扑
        'p': 2  # p-norm to use for velocity scaling
    }
    optimizer = GlobalBestPSO(n_particles=n_particles, dimensions=4, options=options, bounds=bounds)

    # Perform optimization
    cost, pos = optimizer.optimize(objective_function, iters=max_iter)

    # 计算最佳参数的 trans_up 和 trans_down
    _, best_trans_up, best_trans_down, best_reflection = objective_function_single(
        pos, gc_class, wavelengths, center_wavelength, verbose
    )

    if plot:
        # Plot cost history
        plt.figure(figsize=(10, 6))
        plt.plot(optimizer.cost_history)
        plt.title("PSO Optimization Cost History")
        plt.xlabel("Iteration")
        plt.ylabel("Cost")
        plt.yscale('log')
        plt.grid(True)
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pso_cost_history.png"))
        plt.close()

    # Print the best parameters found
    print(f"Best parameters: period={pos[0]:.3f}, line_width={pos[1]:.3f}, "
          f"first_curve_radius={pos[2]:.3f}, line_length={pos[3]:.3f}")
    print(f"Best cost: {cost:.6f}")
    print(f"Best trans up: {best_trans_up:.6f}")
    print(f"Best trans down: {best_trans_down:.6f}")

    return pos, best_trans_up, best_trans_down
