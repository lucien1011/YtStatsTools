import ROOT as r

class Quiet:
   def __init__(self, level = r.kInfo + 1):
      self.level = level

   def __enter__(self):
      self.oldlevel = r.gErrorIgnoreLevel
      r.gErrorIgnoreLevel = self.level

   def __exit__(self, type, value, traceback):
      r.gErrorIgnoreLevel = self.oldlevel
