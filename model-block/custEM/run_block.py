# -*- coding: utf-8 -*-
"""
@author:  Rochlitz.R
"""

# ########################################################################### #
# # # # #                         block model                         # # # # #
# ########################################################################### #
# # # # #                     computation script                      # # # # #
# ########################################################################### #

from custEM.core import MOD
import numpy as np

# ###################      define physical parameters       ################# #

res_ground = [0.3, 1., 2., 1000.]
res_blocks = [10., 100., 500.]

sigma_ground = np.repeat(1./np.array(res_ground), 3).reshape(-1, 3)
sigma_ground[2, 2] *= (1./2.)  # Apply VTI anisotropy for third layer
sigma_blocks = 1./np.array(res_blocks)

frequency = 1.
source_current = 800.

# ####################### run p1 and p2 computations ######################## #

for p in [2, 1]:

    mod = 'p' + str(p)
    mesh = 'block_model_p' + str(p)

    # Initialize model instance
    M = MOD(mod, mesh, 'E_t', p=p, overwrite=True,
            m_dir='./meshes', r_dir='./results')

    # update physical parameters
    M.MP.update_model_parameters(f=frequency,
                                 sigma_anom=sigma_blocks,
                                 sigma_ground=sigma_ground,
                                 J=source_current)

    # update fem parameters and define transmitter
    M.FE.build_var_form()
    # old non-automatized syntax
    #    M.FE.build_var_form(s_type='line',
    #                        start=[-100., 0., -550.],
    #                        stop=[100., 0., -550.])

    # Call solver, skip conversion to H-fields, and export results
    M.solve_main_problem(convert_to_H=False)

    # create regular inteprolation lines in x-direction at sea floor
    M.IB.create_line_meshes('x',  x0=-1e4, x1=1e4, y=-3e3, z=-600.1,
                            n_segs=100, line_name='l1m')
    M.IB.create_line_meshes('x',  x0=-1e4, x1=1e4, y=0., z=-600.1,
                            n_segs=100, line_name='l2m')
    M.IB.create_line_meshes('x',  x0=-1e4, x1=1e4, y=3e3, z=-600.1,
                            n_segs=100, line_name='l3m')

    for line in ['l1m_line_x', 'l2m_line_x', 'l3m_line_x']:
        M.IB.interpolate(line, 'E_t')
    M.IB.synchronize()  # synchronize all processes after interpolation
