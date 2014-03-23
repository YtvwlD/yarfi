class service:
	def __init__():
		self.description = "message bus"
		self.depends = ["filesystem"]
		self.conflicts = []
		self.respawn = True

	def start(self, args):
		os = args["os"]
		subprocess = args["subprocess"]
		try:
			os.mkdir("/var/run/dbus")
		except OSError as e:
			if e.errno == 17:
				pass
			else:
				raise
		passwd = open("/etc/passwd")
		for line in passwd:
			if line.startswith("messagebus"):
				uid = line.split(":")[2]
		passwd.close()
		group = open("/etc/group")
		for line in group:
			if line.startswith("messagebus"):
				gid = line.split(":")[2]
		group.close()
		os.chown("/var/run/dbus", uid, gid)
		
		subprocess.Popen(["dbus-uuidgen", "--ensure"]).wait()
		
		return (subprocess.Popen(["dbus-daemon", "--system"]))

	def stop(self, args):
		os = args["os"]
		subprocess = args["subprocess"]
		
		os.remove("/var/run/dbus/pid")