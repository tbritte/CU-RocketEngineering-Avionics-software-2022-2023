using DevExpress.Xpf.Charts;
using System;
using System.Windows;
using System.Windows.Controls;

namespace ModernUIDesign.MVVM.View
{
    /// <summary>
    /// Interaction logic for TelemetryView.xaml
    /// </summary>
    public partial class TelemetryView : UserControl
    {
        public TelemetryView()
        {
            InitializeComponent();
        }

        private void AltitudeChart_BoundDataChanged(object sender, RoutedEventArgs e)
        {
            // Adjust the visual range.
            AxisX2D axisX = ((XYDiagram2D) AltitudeChart.Diagram).ActualAxisX;
            DateTime maxRangeValue = (DateTime) axisX.ActualWholeRange.ActualMaxValue;
            axisX.ActualVisualRange.SetMinMaxValues(maxRangeValue.AddSeconds(-20), maxRangeValue);
        }

        private void AccelerationChart_BoundDataChanged(object sender, RoutedEventArgs e)
        {
            // Adjust the visual range.
            AxisX2D axisX = ((XYDiagram2D) AccelerationChart.Diagram).ActualAxisX;
            DateTime maxRangeValue = (DateTime) axisX.ActualWholeRange.ActualMaxValue;
            axisX.ActualVisualRange.SetMinMaxValues(maxRangeValue.AddSeconds(-20), maxRangeValue);
        }

        private void GyroscopeChart_BoundDataChanged(object sender, RoutedEventArgs e)
        {
            // Adjust the visual range.
            AxisX2D axisX = ((XYDiagram2D) GyroscopeChart.Diagram).ActualAxisX;
            DateTime maxRangeValue = (DateTime) axisX.ActualWholeRange.ActualMaxValue;
            axisX.ActualVisualRange.SetMinMaxValues(maxRangeValue.AddSeconds(-20), maxRangeValue);
        }

        private void MagnetometerChart_BoundDataChanged(object sender, RoutedEventArgs e)
        {
            // Adjust the visual range.
            AxisX2D axisX = ((XYDiagram2D) MagnetometerChart.Diagram).ActualAxisX;
            DateTime maxRangeValue = (DateTime) axisX.ActualWholeRange.ActualMaxValue;
            axisX.ActualVisualRange.SetMinMaxValues(maxRangeValue.AddSeconds(-20), maxRangeValue);
        }

    }
}
