# Copyright (c) 2026, GateMS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Dock(Document):
	def validate(self):
		if self.status == "Maintenance":
			self.current_visit = None
			return
		if self.current_visit:
			self.status = "Occupied"
		elif self.status == "Occupied" and not self.current_visit:
			self.status = "Available"


def occupy_dock(dock: str, visit: str) -> None:
	doc = frappe.get_doc("Dock", dock)
	if doc.status == "Maintenance":
		frappe.throw(_("Dock {0} is under maintenance").format(dock))
	if doc.current_visit and doc.current_visit != visit:
		frappe.throw(_("Dock {0} is already occupied by {1}").format(dock, doc.current_visit))
	doc.current_visit = visit
	doc.status = "Occupied"
	doc.save(ignore_permissions=True)


def release_dock(dock: str | None, visit: str | None = None) -> None:
	if not dock or not frappe.db.exists("Dock", dock):
		return
	doc = frappe.get_doc("Dock", dock)
	if visit and doc.current_visit and doc.current_visit != visit:
		return
	doc.current_visit = None
	if doc.status == "Occupied":
		doc.status = "Available"
	doc.save(ignore_permissions=True)
