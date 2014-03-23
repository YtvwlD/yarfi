class target:
	def __init__():
		self.description = "execs /sbin/init"
		self.depends = ["exec_init"] #almost nothing
		self.conflicts = ["dbus"] #everything
