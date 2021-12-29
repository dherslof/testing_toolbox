


class LogcatEntry:
   def __init__(self, date='', time='', process='', pid='', tid='', level='', tag='', msg=''):
      self.date = date
      self.time = time
      self.process = process
      self.pid = pid
      self.tid = tid
      self.level = level
      self.tag = tag
      self.msg = msg
      self.details_set = True
      self.non_formatted_entry

   # Class printing function
   def display(self):
      print('{} {} {} {} {} {} {}'.format(self.date, self.time, self.process, self.pid, self.tid, self.level, self.tag, self.msg))

   def set_non_formatted_entry(self, entry):
      self.set_non_formatted_entry = entry
      self.details_set = False
