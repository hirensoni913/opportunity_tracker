import numpy as np
from enum import Enum
from dataclasses import dataclass
import base64
from io import BytesIO

from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import numpy as np


class ChartType(str, Enum):
    BAR = "bar"
    PIE = "pie"
    LINE = "line"


@dataclass
class ChartSeries:
    label: str
    values: list[float | int]


class ChartProcessor:

    @staticmethod
    def create(
        chart_type: ChartType,
        title: str | None = None,
        categories=None,
        series=None,
        width: float = 10,
        height: float = 5
    ):

        if chart_type == ChartType.BAR:
            return ChartProcessor._create_bar_chart(
                title=title,
                categories=categories,
                series=series,
                width=width,
                height=height
            )

        raise ValueError(f"Unsupported chart type: {chart_type}")

    @staticmethod
    def _create_bar_chart(
        title=None,
        categories=None,
        series=None,
        width=10,
        height=5
    ):

        if not categories:
            raise ValueError("Categories are required for a bar chart.")

        if not series:
            raise ValueError(
                "At least one series is required for a bar chart.")

        for chart_series in series:
            if len(chart_series.values) != len(categories):
                raise ValueError(
                    f"Series '{chart_series.label}' must have the same number "
                    "of values as categories."
                )
        figure = Figure(figsize=(width, height))
        axis = figure.add_subplot(111)

        x_positions = np.arange(len(categories))
        number_of_series = len(series)
        bar_width = 0.8 / number_of_series

        for index, chart_series in enumerate(series):
            offset = (
                index - (number_of_series - 1) / 2
            ) * bar_width

            axis.bar(
                x_positions + offset,
                chart_series.values,
                width=bar_width,
                label=chart_series.label,
            )

        if title:
            axis.set_title(title)

        axis.set_xticks(x_positions)
        axis.set_xticklabels(categories)
        axis.legend()

        figure.tight_layout()

        return ChartProcessor._figure_to_base64_svg(figure)

    @staticmethod
    def _figure_to_base64_svg(figure) -> str:
        buffer = BytesIO()

        canvas = FigureCanvasSVG(figure)
        canvas.print_svg(buffer)

        buffer.seek(0)
        svg = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()

        return svg
