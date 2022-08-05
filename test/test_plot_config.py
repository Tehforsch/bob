import unittest

from bob.plotConfig import PlotConfig


class Test(unittest.TestCase):
    def test_verification(self) -> None:
        config = PlotConfig({"1": 1, "2": 2})
        config.setDefault("1", 2)
        config.setDefault("2", 1)
        assert config["1"] == 1
        assert config["2"] == 2
        config.verify()

    def test_unknown_parameter(self) -> None:
        config = PlotConfig({"1": 1, "2": 2})
        config.setDefault("1", 2)
        try:
            config.verify()
        except ValueError:
            pass
        else:
            assert False

    def test_missing_required_parameter(self) -> None:
        config = PlotConfig({"1": 1, "2": 2})
        config.setRequired("3")
        try:
            config.verify()
        except ValueError:
            pass
        else:
            assert False

    def test_wrong_choice(self) -> None:
        config = PlotConfig({"1": 4})
        config.setRequired("1", choices=[1, 2, 3])
        try:
            config.verify()
        except ValueError:
            pass
        else:
            assert False
