using System;
using System.Windows.Input;

namespace ModernUIDesign.Core
{
    public class ViewCommand : ICommand
    {
        private ViewCommand resetDisplayFields;
        private Func<object, bool> canResetDisplayFields;

        public Action<object> ExecuteViewCommand { get; set; }
        public Func<object, bool> CanExecuteViewCommand { get; set; }

        public ViewCommand(Action<object> executeMethod, Func<object, bool> canExecuteMethod)
        {
            ExecuteViewCommand = executeMethod;
            CanExecuteViewCommand = canExecuteMethod;
        }

        public ViewCommand(ViewCommand resetDisplayFields, Func<object, bool> canResetDisplayFields)
        {
            this.resetDisplayFields = resetDisplayFields;
            this.canResetDisplayFields = canResetDisplayFields;
        }

        public bool CanExecute(object parameter)
        {
            return CanExecuteViewCommand(parameter);
        }

        public void RaiseCanExecuteChanged()
        {
            CanExecuteChanged?.Invoke(this, new EventArgs());
        }

        public event EventHandler CanExecuteChanged;

        public void Execute(object parameter)
        {
            ExecuteViewCommand(parameter);
        }
    }
}
