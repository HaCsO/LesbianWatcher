import sqlite3
import contextlib

class LesCursor(sqlite3.Cursor):
	def get_structured_db_info_for_warn(self, user):
		self.execute(f"SELECT * FROM warn WHERE id = '{user.id}'")
		res = self.fetchall()
		if not res:
			return None
		return res[0]

class DBHolder:
	path = None
	connect = None

	def __init__(self, path) -> None:
		self.path = path
		assert self.__validate_database()

	def __validate_database(self):
		if not self.path:
			return False
		try:
			self.connect = sqlite3.connect(self.path) 
		except:
			return False
		return True
	
	@contextlib.contextmanager
	def interact(self):
		assert self.connect is not None
		cur = LesCursor(self.connect.cursor().connection) 
		try:
			yield cur
		finally:
			self.connect.commit()
			cur.close()