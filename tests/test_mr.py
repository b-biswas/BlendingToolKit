from unittest.mock import patch

from conftest import data_dir

from btk.catalog import CatsimCatalog
from btk.draw_blends import CatsimGenerator
from btk.measure import MeasureGenerator
from btk.measure import sep_measure
from btk.metrics import meas_ksb_ellipticity
from btk.metrics import MetricsGenerator
from btk.plot_utils import plot_metrics_summary
from btk.sampling_functions import DefaultSampling
from btk.survey import get_surveys


@patch("btk.plot_utils.plt.show")
def test_multiresolution(mock_show):
    catalog_name = data_dir / "sample_input_catalog.fits"

    stamp_size = 24.0
    batch_size = 8
    cpus = 1
    add_noise = True
    surveys = get_surveys(["Rubin", "HSC"])

    catalog = CatsimCatalog.from_file(catalog_name)
    sampling_function = DefaultSampling(stamp_size=stamp_size)
    draw_blend_generator = CatsimGenerator(
        catalog,
        sampling_function,
        surveys,
        stamp_size=stamp_size,
        batch_size=batch_size,
        cpus=cpus,
        add_noise=add_noise,
    )

    meas_generator = MeasureGenerator(sep_measure, draw_blend_generator, cpus=cpus)
    metrics_generator = MetricsGenerator(
        meas_generator, target_meas={"ellipticity": meas_ksb_ellipticity}, meas_band_num=(2, 1)
    )
    blend_results, measure_results, metrics_results = next(metrics_generator)

    assert "Rubin" in blend_results["blend_list"].keys(), "Both surveys get well defined outputs"
    assert "HSC" in blend_results["blend_list"].keys(), "Both surveys get well defined outputs"
    assert blend_results["blend_images"]["Rubin"][0].shape[-1] == int(
        24.0 / 0.2
    ), "Rubin survey should have a pixel scale of 0.2"
    assert blend_results["blend_images"]["HSC"][0].shape[-1] == int(
        24.0 / 0.167
    ), "HSC survey should have a pixel scale of 0.167"
    assert (
        "Rubin" in measure_results["catalog"]["sep_measure"].keys()
    ), "Both surveys get well defined outputs"
    assert (
        "HSC" in measure_results["catalog"]["sep_measure"].keys()
    ), "Both surveys get well defined outputs"
    assert "Rubin" in metrics_results["sep_measure"].keys(), "Both surveys get well defined outputs"
    assert "HSC" in metrics_results["sep_measure"].keys(), "Both surveys get well defined outputs"

    plot_metrics_summary(
        metrics_results,
        target_meas_keys=["ellipticity0"],
        target_meas_limits=[[-1, 1]],
        interactive=False,
    )
    plot_metrics_summary(
        metrics_results,
        target_meas_keys=["ellipticity0"],
        target_meas_limits=[[-1, 1]],
        interactive=True,
    )
