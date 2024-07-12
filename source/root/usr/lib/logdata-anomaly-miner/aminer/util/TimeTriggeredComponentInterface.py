"""
This is the interface-class for the TimeTriggeredComponent.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

"""

import abc


class TimeTriggeredComponentInterface(metaclass=abc.ABCMeta):
    """
    This is the common interface of all components that can be registered to receive timer interrupts.
    There might be different timelines for triggering, real time and normalized log data time scale for forensic analysis. For forensic
    analyis different timers might be available to register a component. Therefore the component should state, which type of triggering it
    would require.
    """

    @property
    @abc.abstractmethod
    def time_trigger_class(self):
        raise NotImplementedError

    def get_time_trigger_class(self):
        """
        Get the trigger class this component can be registered for.
        See AnalysisContext class for different trigger classes available.
        """
        if self.time_trigger_class not in (1, 2):
            raise NotImplementedError("The self.time_trigger_class property must be set to AnalysisContext.TIME_TRIGGER_CLASS_REALTIME or "
                                      "AnalysisContext.TIME_TRIGGER_CLASS_ANALYSISTIME.")
        return self.time_trigger_class

    @abc.abstractmethod
    def do_timer(self, trigger_time):
        """
        Perform trigger actions and to determine the time for next invocation.
        The caller may decide to invoke this method earlier than requested during the previous call. Classes implementing this method have
        to handle such cases. Each class should try to limit the time spent in this method as it might delay trigger signals to other
        components. For extensive computational work or IO, a separate thread should be used.
        @param trigger_time the time this trigger is invoked. This might be the current real time when invoked from real time
        timers or the forensic log timescale time value.
        @return the number of seconds when next invocation of this trigger is required.
        """
