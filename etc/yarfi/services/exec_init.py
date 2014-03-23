class service:
	def __init__(self):
		self.description = "execs /sbin/init"
		self.depends = []
		self.conflicts = ["dbus"]
		
	def start(self, args):
		os = args["os"]
		os.execv("/sbin/init")
	
	def stop(self, args):
		pass