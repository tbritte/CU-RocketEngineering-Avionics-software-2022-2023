using DevExpress.Xpf.Charts;
using System;
using System.Windows;
using System.Windows.Controls;

namespace ModernUIDesign.MVVM.View
{
    /// <summary>
    /// Interaction logic for HomeView.xaml
    /// </summary>
    public partial class HomeView : UserControl
    {
        public HomeView()
        {
            InitializeComponent();
        }


        private void CurrentAltitudeChart_BoundDataChanged(object sender, RoutedEventArgs e)
        {
            // Adjust the visual range.
            AxisX2D axisX = ((XYDiagram2D) CurrentAltitudeChart.Diagram).ActualAxisX;
            DateTime maxRangeValue = (DateTime) axisX.ActualWholeRange.ActualMaxValue;
            axisX.ActualVisualRange.SetMinMaxValues(maxRangeValue.AddSeconds(-20), maxRangeValue);
        }


    }
}
