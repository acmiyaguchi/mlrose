import mlrose_hiive
from mlrose_hiive.decorators import short_name
from mlrose_hiive.runners._runner_base import _RunnerBase
import numpy as np
from functools import partial

"""
Example usage:

    experiment_name = 'example_experiment'
    problem = TSPGenerator.generate(seed=SEED, number_of_cities=22)
    
    # note that you can also initialize a temperature_list this way
    # temperature_list = [mlrose_hiive.GeomDecay(init_temp=t, decay=d) for (t, d) in [(1, 0.99), (1e2, 0.999)]]
    # if you use this form, the decay_list parameter is ignored.

    sa = SARunner(problem=problem,
                  experiment_name=experiment_name,
                  output_directory=OUTPUT_DIRECTORY,
                  seed=SEED,
                  iteration_list=2 ** np.arange(14),
                  max_attempts=5000,
                  temperature_list=[1, 10, 50, 100, 250, 500, 1000, 2500, 5000, 10000],
                  decay_list=[mlrose_hiive.GeomDecay])

    # the two data frames will contain the results
    df_run_stats, df_run_curves = sa.run()                  
"""


@short_name('sa')
class SARunner(_RunnerBase):

    def __init__(self, problem, experiment_name, seed, iteration_list, temperature_list, decay_list=None,
                 max_attempts=500, generate_curves=True, random_search=False, random_search_iterations=100, **kwargs):
        super().__init__(problem=problem, experiment_name=experiment_name, seed=seed, iteration_list=iteration_list,
                         max_attempts=max_attempts, generate_curves=generate_curves,
                         **kwargs)
        self.use_raw_temp = True
        self.temperature_list = temperature_list
        if isinstance(temperature_list, list) and all([np.isscalar(x) for x in temperature_list]):
            if decay_list is None:
                decay_list = [mlrose_hiive.GeomDecay]
            if all([np.isscalar(x) for x in decay_list]):
                decay_list = [partial(mlrose_hiive.GeomDecay, decay=d) for d in decay_list]
            self.decay_list = decay_list
            self.use_raw_temp = False
        elif hasattr(temperature_list, "rvs") and hasattr(decay_list, "rvs"):
            # let's randomly sample from the distribution and build up the list ahead of time
            # we make sure that we're using grid search downstream because SA is otherwise super hacky
            rows = []
            for _ in range(random_search_iterations):
                temp = temperature_list.rvs()
                decay = decay_list.rvs()
                rows.append(mlrose_hiive.GeomDecay(init_temp=temp, decay=decay))
            self.temperature_list = rows
            self.use_raw_temp = True

    def run(self):
        temperatures = self.temperature_list if self.use_raw_temp else [d(init_temp=t) for t in self.temperature_list
                                                                        for d in self.decay_list]
        return super().run_experiment_(algorithm=mlrose_hiive.simulated_annealing,
                                       schedule=('Temperature', temperatures))
