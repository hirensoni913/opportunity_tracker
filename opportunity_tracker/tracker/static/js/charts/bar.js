function createSimpleVerticalBarChart(
  ctx,
  labels,
  data,
  titleText,
  datasetLabel,
  xLabel,
  yLabel,
  backgroundColors,
  borderColors
) {
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: datasetLabel,
          data: data,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
        },
      ],
    },
    options: {
      responsive: true,
      indexAxis: "y", // Makes chart horizontal
      plugins: {
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: titleText,
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: xLabel ?? "",
            font: {
              weight: "bold",
            },
          },
        },
        y: {
          title: {
            display: true,
            text: yLabel ?? "",
            font: {
              weight: "bold",
            },
          },
        },
      },
    },
  });
}

function createBarChart(ctx, labels, datasets, titleText) {
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: datasets,
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: titleText,
        },
      },
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true,
          ticks: {
            callback: function (value) {
              if (Number.isInteger(value)) {
                return value; // Show only integers
              }
              return null; // Skip float values
            },
          },
        },
      },
    },
  });
}
