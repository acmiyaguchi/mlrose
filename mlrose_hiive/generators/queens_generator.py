import numpy as np

from mlrose_hiive import QueensOpt


class QueensGenerator:
    @staticmethod
    def generate(seed, size=20, **kwargs):
        np.random.seed(seed)
        problem = QueensOpt(length=size, **kwargs)
        return problem
