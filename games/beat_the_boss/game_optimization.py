"""Beat the Boss - Optimization configuration for three boss modes."""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """
    Optimization setup for Beat the Boss.
    Configures RTP targets and distribution conditions for each boss mode.
    """

    def __init__(self, game_config: object):
        self.game_config = game_config
        self.game_config.opt_params = {
            # Macron Mode - Base (70% hit rate, 5000x max)
            "macron": {
                "conditions": {
                    # All spins distribution - natural RTP from paytable
                    "all_spins": ConstructConditions(
                        rtp=0.98,
                        hr=1.43  # ~70% hit rate (1/0.70 = 1.43 spins per win)
                    ).return_dict(),
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "all_spins",
                        "scale_factor": 1,
                        "win_range": (0, 5000),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=0.98,  # 98% RTP target
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },

            # Putin Mode - Medium (50% hit rate, 7500x max)
            "putin": {
                "conditions": {
                    # All spins distribution - natural RTP from paytable
                    "all_spins": ConstructConditions(
                        rtp=0.98,
                        hr=2.0  # ~50% hit rate (1/0.50 = 2.0 spins per win)
                    ).return_dict(),
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "all_spins",
                        "scale_factor": 1,
                        "win_range": (0, 7500),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=5,
                    max_m2m=10,
                    pmb_rtp=0.98,  # 98% RTP target
                    sim_trials=5000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },

            # Trump Mode - High (35% hit rate, 10000x max)
            "trump": {
                "conditions": {
                    # All spins distribution - natural RTP from paytable
                    "all_spins": ConstructConditions(
                        rtp=0.98,
                        hr=2.86  # ~35% hit rate (1/0.35 = 2.86 spins per win)
                    ).return_dict(),
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "all_spins",
                        "scale_factor": 1,
                        "win_range": (0, 10000),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=15000,
                    min_m2m=6,
                    max_m2m=12,
                    pmb_rtp=0.98,  # 98% RTP target
                    sim_trials=5000,
                    test_spins=[200, 500, 1000],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)