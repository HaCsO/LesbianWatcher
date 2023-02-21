import json
import datetime

class ConfigHolder():
	def __init__(self, config_path):
		self.config = {}
		self.lastupdate = None
		self.path = config_path
		self.validate_config()
		self.update_from_file()

	def validate_config(self):
		try:
			open(self.path, "r")
		except:
			self.reset_config()			

	def update_from_file(self):
		with open(self.path, "r") as f:
			try:
				self.config = json.load(f)
			except Exception as e:
				print("Error was occured while updating from file, now we reset config and make copy of error config")
				print(e)
				with open("errorconfig.json", "w") as ef:
					ef.write(f.read())

				self.reset_config()


		print("Config was updated")
		self.lastupdate = datetime.datetime.now()

	def upload_to_file(self):
		with open(self.path, "w") as f:
			json.dump(self.config, f)

		print("Config was updated")
		self.lastupdate = datetime.datetime.now()

	def reset_config(self):
		self.config = {
			"log_channel": None,
			"owner": None,
			"headmod": None,
			"moders": []
		}
		self.upload_to_file()
	