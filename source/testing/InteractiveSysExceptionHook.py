import sys

def overrideExceptHook():
  def overrideExceptHookFunction(type, value, tb):
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
# we are in interactive mode or we don't have a tty-like
# device, so we call the default hook
      sys.__excepthook__(type, value, tb)
    else:
      import traceback, pdb
# we are NOT in interactive mode, print the exception...
      traceback.print_exception(type, value, tb)
      print
# ...then start the debugger in post-mortem mode.
      pdb.pm()
#   pdb.set_trace()
  sys.excepthook=overrideExceptHookFunction
