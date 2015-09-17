##
#         Project: gpTrace
# Description: Trace the activities of an external application
#            Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
#     Copyright: 2014 Fabio Castelli
#         License: GPL-2+
#    This program is free software; you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#    FITNESS FOR A PARTICULAR PURPOSE.    See the GNU General Public License for
#    more details.
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

from ptrace import PtraceError
from ptrace.func_call import FunctionCallOptions
from ptrace.debugger import (PtraceDebugger, Application, ProcessExit,
                             ProcessSignal, NewProcessEvent, ProcessExecution,
                             ChildError)


class SyscallTracer(Application):
    def __init__(self, options, program, ignore_syscall_callback,
                 syscall_callback, event_callback, quit_callback):
        Application.__init__(self)
        # Parse self.options
        self.options = options
        self.program = program
        self.processOptions()
        self.ignore_syscall_callback = ignore_syscall_callback
        self.syscall_callback = syscall_callback
        self.event_callback = event_callback
        self.quit_callback = quit_callback

    def runDebugger(self):
        # Create debugger and traced process
        self.setupDebugger()
        process = self.createProcess()
        if not process:
            return

        self.syscall_options = FunctionCallOptions(
            write_types=True,
            write_argname=True,
            replace_socketcall=False,
            string_max_length=300,
            write_address=False,
            max_array_count=20,
        )
        self.syscall_options.instr_pointer = self.options.show_ip
        self.syscallTrace(process)

    def displaySyscall(self, syscall):
        self.syscall_callback(syscall)

    def syscall(self, process):
        state = process.syscall_state
        syscall = state.event(self.syscall_options)
        if syscall and (syscall.result is not None or self.options.enter):
            self.displaySyscall(syscall)
        # Break at next syscall
        process.syscall()

    def syscallTrace(self, process):
        # First query to break at next syscall
        self.prepareProcess(process)

        while True:
            # No more process? Exit
            if not self.debugger:
                break
            # Wait until next syscall enter
            try:
                event = self.debugger.waitSyscall()
                process = event.process
            except ProcessExit as event:
                self.processExited(event)
                continue
            except ProcessSignal as event:
                self.event_callback(event)
                #event.display()
                process.syscall(event.signum)
                continue
            except NewProcessEvent as event:
                self.event_callback(event)
                process = event.process
                self.prepareProcess(process)
                process.parent.syscall()
                continue
            except ProcessExecution as event:
                self.event_callback(event)
                process = event.process
                process.syscall()
                continue

            # Process syscall enter or exit
            self.syscall(process)

    def prepareProcess(self, process):
        process.syscall()
        process.syscall_state.ignore_callback = self.ignore_syscall_callback

    def processExited(self, event):
        # Display syscall which has not exited
        state = event.process.syscall_state
        if (state.next_event == "exit") and (not self.options.enter) and state.syscall:
            self.displaySyscall(state.syscall)
        self.event_callback(event)

    def main(self):
        self.debugger = PtraceDebugger()
        try:
            self.runDebugger()
        except ChildError as event:
            self.event_callback(event)
        except ProcessExit as event:
            self.processExited(event)
        except (KeyError, PtraceError, OSError) as error:
            self._handle_exceptions_during_quit(error, 'main')
        if self.debugger:
            self.debugger.quit()
        self.quit_callback()

    def quit(self):
        try:
            self.debugger.quit()
        except (KeyError, PtraceError, OSError) as error:
            self._handle_exceptions_during_quit(error, 'quit')
        self.quit_callback()
        self.debugger = None

    def _handle_exceptions_during_quit(self, exception, context):
        if isinstance(exception, KeyError):
            # When the debugger is waiting for a syscall and the debugger
            # process is closed with quit() a KeyError Exception for missing
            # PID is fired
            pass
        elif isinstance(exception, PtraceError):
            print "PtraceError from %s" % context, exception
        elif isinstance(exception, OSError):
            print 'OSError from %s' % context, exception
        else:
            print 'Unexpected exception from %s' % context