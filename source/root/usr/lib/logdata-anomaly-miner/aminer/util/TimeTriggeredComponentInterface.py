interface_method_called = 'Interface method called'


class TimeTriggeredComponentInterface:
    """This is the common interface of all components that can be registered to receive timer interrupts. There might be different
    timelines for triggering, real time and normalized log data time scale for forensic analysis. For forensic analyis different
    timers might be available to register a component. Therefore the component should state, which type of triggering it would
    require."""

    # skipcq: PYL-R0201
    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. See AnalysisContext class for different trigger classes
        available."""
        raise Exception(interface_method_called)

    # skipcq: PYL-R0201
    def do_timer(self, trigger_time):
        """This method is called to perform trigger actions and to determine the time for next invocation. The caller may decide
        to invoke this method earlier than requested during the previous call. Classes implementing this method have to handle such
        cases. Each class should try to limit the time spent in this method as it might delay trigger signals to other components.
        For extensive compuational work or IO, a separate thread should be used.
        @param trigger_time the time this trigger is invoked. This might be the current real time when invoked from real time
        timers or the forensic log timescale time value.
        @return the number of seconds when next invocation of this trigger is required."""
        raise Exception(interface_method_called)
