import os

import csp_solver

sugarjar_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sugar-v1-15-0.jar'))
csp_solver_config = csp_solver.get_valid_csp_solver_config(
    sugarjar_path=sugarjar_path
)
