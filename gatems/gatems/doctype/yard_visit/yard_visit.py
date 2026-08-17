# Copyright (c) 2026, GateMS and contributors
# For license information, please see license.txt

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, now_datetime

from gatems.gatems.doctype.dock.dock import occupy_dock, release_dock
from gatems.gatems.doctype.vehicles.vehicles import normalize_registration_number

OPEN_STATUSES = (
	"Parked",
	"Dock Assigned",
	"On Dock",
	"Loading",
	"Unloading",
	"Ready to Check Out",
)
PARKED_STATUSES = ("Parked",)
ON_DOCK_STATUSES = ("Dock Assigned", "On Dock", "Loading", "Unloading")
READY_STATUSES = ("Ready to Check Out",)
PARKING_SLOTS = [f"P{i:02d}" for i in range(1, 13)]
VISIT_FIELDS = [
	"name",
	"vehicle",
	"make",
	"model",
	"vehicle_type",
	"status",
	"visit_type",
	"parking_slot",
	"dock",
	"driver_name",
	"driver_mobile",
	"driver_license_no",
	"transporter",
	"material_type",
	"material_description",
	"party_name",
	"quantity",
	"uom",
	"reference_no",
	"check_in_time",
	"dock_assigned_time",
	"operation_start",
	"operation_end",
	"dock_out_time",
	"check_out_time",
	"is_new_vehicle",
	"remarks",
]


class YardVisit(Document):
	def validate(self):
		self.vehicle = normalize_registration_number(self.vehicle)
		self._ensure_single_open_visit()
		if self.status != "Checked Out" and not self.check_in_time:
			self.check_in_time = now_datetime()
		if self.status == "Parked" and not self.parking_slot:
			self.parking_slot = next_parking_slot(self.name)

	def on_update(self):
		publish_yard_update(self)

	def on_trash(self):
		if self.dock and self.status in ON_DOCK_STATUSES:
			release_dock(self.dock, self.name)
		publish_yard_update(self)

	def _ensure_single_open_visit(self):
		if self.status == "Checked Out" or not self.vehicle:
			return
		existing = frappe.db.exists(
			"Yard Visit",
			{
				"vehicle": self.vehicle,
				"status": ["in", OPEN_STATUSES],
				"name": ["!=", self.name or ""],
			},
		)
		if existing:
			frappe.throw(_("Vehicle {0} is already in the yard on {1}").format(self.vehicle, existing))

	def next_actions(self) -> list[str]:
		return actions_for_status(self.status, self.visit_type)

	def apply_action(self, action: str, dock: str | None = None, operation: str | None = None) -> None:
		action = (action or "").strip()
		if action == "assign_dock":
			self._assign_dock(dock)
		elif action == "start_operation":
			self._start_operation(operation)
		elif action == "stop_operation":
			self._stop_operation()
		elif action == "dock_out":
			self._dock_out()
		elif action == "check_out":
			self._check_out()
		else:
			frappe.throw(_("Unknown yard action: {0}").format(action))

	def _assign_dock(self, dock: str | None):
		if self.status != "Parked":
			frappe.throw(_("Assign a dock only while the vehicle is parked"))
		if not dock:
			frappe.throw(_("Please select a dock"))
		occupy_dock(dock, self.name)
		self.dock = dock
		self.status = "Dock Assigned"
		self.dock_assigned_time = now_datetime()
		self.parking_slot = None

	def _start_operation(self, operation: str | None):
		if self.status not in ("Dock Assigned", "On Dock"):
			frappe.throw(_("Start loading or unloading after a dock is assigned"))
		if not self.dock:
			frappe.throw(_("Assign a dock before starting loading or unloading"))
		kind = resolve_operation(self.visit_type, operation)
		self.status = kind
		self.operation_start = now_datetime()
		self.operation_end = None

	def _stop_operation(self):
		if self.status not in ("Loading", "Unloading"):
			frappe.throw(_("No loading or unloading is in progress"))
		self.status = "On Dock"
		self.operation_end = now_datetime()

	def _dock_out(self):
		if self.status not in ON_DOCK_STATUSES:
			frappe.throw(_("Dock out is only allowed from a docked vehicle"))
		if self.status in ("Loading", "Unloading"):
			self.operation_end = now_datetime()
		release_dock(self.dock, self.name)
		self.status = "Ready to Check Out"
		self.dock_out_time = now_datetime()

	def _check_out(self):
		if self.status in ON_DOCK_STATUSES:
			frappe.throw(_("Dock out the vehicle before check-out"))
		if self.status not in ("Parked", "Ready to Check Out"):
			frappe.throw(_("Vehicle is not ready to check out"))
		if self.dock and self.status in ON_DOCK_STATUSES:
			release_dock(self.dock, self.name)
		self.status = "Checked Out"
		self.check_out_time = now_datetime()
		self.parking_slot = None


def actions_for_status(status: str, visit_type: str | None = None) -> list[str]:
	if status == "Parked":
		return ["assign_dock", "check_out"]
	if status == "Dock Assigned":
		return ["start_operation", "dock_out"]
	if status in ("Loading", "Unloading"):
		return ["stop_operation"]
	if status == "On Dock":
		actions = ["dock_out"]
		if visit_type == "Both":
			actions.insert(0, "start_operation")
		return actions
	if status == "Ready to Check Out":
		return ["check_out"]
	return []


def resolve_operation(visit_type: str, operation: str | None) -> str:
	if visit_type in ("Loading", "Unloading"):
		return visit_type
	kind = (operation or "").title()
	if kind not in ("Loading", "Unloading"):
		frappe.throw(_("Choose Loading or Unloading"))
	return kind


def next_parking_slot(ignore_visit: str | None = None) -> str:
	filters: dict[str, Any] = {"status": "Parked"}
	used = set(
		frappe.get_all(
			"Yard Visit",
			filters=filters,
			pluck="parking_slot",
		)
	)
	if ignore_visit:
		current = frappe.db.get_value("Yard Visit", ignore_visit, "parking_slot")
		if current:
			used.discard(current)
	for slot in PARKING_SLOTS:
		if slot not in used:
			return slot
	frappe.throw(_("All parking slots are occupied"))
	return PARKING_SLOTS[0]


def get_open_visit_name(vehicle: str) -> str | None:
	return frappe.db.exists(
		"Yard Visit",
		{"vehicle": normalize_registration_number(vehicle), "status": ["in", OPEN_STATUSES]},
	)


def ensure_vehicle(
	vehicle: str | None,
	is_new_vehicle: int,
	registration_number: str | None,
	make: str | None,
	model: str | None,
	vehicle_type: str | None,
	transporter: str | None,
) -> tuple[str, int]:
	created = 0
	if cint(is_new_vehicle):
		reg = normalize_registration_number(registration_number)
		if not reg:
			frappe.throw(_("Enter a registration number for the new vehicle"))
		if frappe.db.exists("Vehicles", reg):
			frappe.throw(
				_("Vehicle {0} already exists in the master. Select it from master instead.").format(reg)
			)
		doc = frappe.get_doc(
			{
				"doctype": "Vehicles",
				"registration_number": reg,
				"make": make or "Unknown",
				"model": model or "Unknown",
				"vehicle_type": vehicle_type or "Truck",
				"vehicle_category": "Commercial",
				"usage_type": "Vendor",
				"fuel_type": "Diesel",
				"status": "Active",
				"owner_type": "Company",
				"owner_name": transporter or "Gate check-in",
			}
		)
		doc.insert(ignore_permissions=True)
		return doc.name, 1

	name = normalize_registration_number(vehicle)
	if not name:
		frappe.throw(_("Select a vehicle from the master"))
	if not frappe.db.exists("Vehicles", name):
		frappe.throw(_("Vehicle {0} is not in the master").format(name))
	status = frappe.db.get_value("Vehicles", name, "status")
	if status == "Blacklisted":
		frappe.throw(_("Vehicle {0} is blacklisted").format(name))
	return name, created


def visit_as_dict(doc: Document) -> dict[str, Any]:
	data = {field: doc.get(field) for field in VISIT_FIELDS}
	data["next_actions"] = actions_for_status(doc.status, doc.visit_type)
	return data


YARD_REALTIME_EVENT = "gatems:yard_update"


def publish_yard_update(doc: Document | None = None) -> None:
	payload: dict[str, Any] = {}
	if doc:
		payload = {
			"name": doc.name,
			"vehicle": doc.vehicle,
			"status": doc.status,
			"dock": doc.dock,
			"parking_slot": doc.parking_slot,
		}
	frappe.publish_realtime(YARD_REALTIME_EVENT, payload, after_commit=True)


@frappe.whitelist()
def check_in(
	vehicle: str | None = None,
	is_new_vehicle: int | str = 0,
	registration_number: str | None = None,
	make: str | None = None,
	model: str | None = None,
	vehicle_type: str | None = None,
	driver_name: str | None = None,
	driver_mobile: str | None = None,
	driver_license_no: str | None = None,
	transporter: str | None = None,
	visit_type: str = "Unloading",
	material_type: str | None = None,
	material_description: str | None = None,
	quantity: float | str | None = None,
	uom: str | None = None,
	party_name: str | None = None,
	reference_no: str | None = None,
	remarks: str | None = None,
) -> dict[str, Any]:
	if not driver_name:
		frappe.throw(_("Driver name is required at check-in"))
	if visit_type not in ("Loading", "Unloading", "Both"):
		frappe.throw(_("Invalid visit type"))

	vehicle_name, created = ensure_vehicle(
		vehicle,
		cint(is_new_vehicle),
		registration_number,
		make,
		model,
		vehicle_type,
		transporter,
	)
	if get_open_visit_name(vehicle_name):
		frappe.throw(_("Vehicle {0} is already inside the yard").format(vehicle_name))

	doc = frappe.get_doc(
		{
			"doctype": "Yard Visit",
			"vehicle_source": "New Vehicle" if created else "Master",
			"vehicle": vehicle_name,
			"is_new_vehicle": created,
			"vehicle_type": vehicle_type or frappe.db.get_value("Vehicles", vehicle_name, "vehicle_type"),
			"make": make or frappe.db.get_value("Vehicles", vehicle_name, "make"),
			"model": model or frappe.db.get_value("Vehicles", vehicle_name, "model"),
			"status": "Parked",
			"visit_type": visit_type,
			"parking_slot": next_parking_slot(),
			"driver_name": driver_name,
			"driver_mobile": driver_mobile,
			"driver_license_no": driver_license_no,
			"transporter": transporter,
			"material_type": material_type,
			"material_description": material_description,
			"quantity": flt(quantity),
			"uom": uom,
			"party_name": party_name,
			"reference_no": reference_no,
			"remarks": remarks,
			"check_in_time": now_datetime(),
		}
	)
	doc.insert()
	frappe.db.commit()
	return visit_as_dict(doc)


@frappe.whitelist()
def advance_visit(
	visit: str,
	action: str,
	dock: str | None = None,
	operation: str | None = None,
) -> dict[str, Any]:
	doc = frappe.get_doc("Yard Visit", visit)
	doc.apply_action(action, dock=dock, operation=operation)
	doc.save()
	frappe.db.commit()
	return visit_as_dict(doc)


@frappe.whitelist()
def get_open_visit(vehicle: str) -> dict[str, Any] | None:
	name = get_open_visit_name(vehicle)
	if not name:
		return None
	return visit_as_dict(frappe.get_doc("Yard Visit", name))


@frappe.whitelist()
def get_yard_status() -> dict[str, Any]:
	visits = frappe.get_all(
		"Yard Visit",
		filters={"status": ["in", OPEN_STATUSES]},
		fields=VISIT_FIELDS,
		order_by="check_in_time asc",
	)
	by_name = {}
	for row in visits:
		row["next_actions"] = actions_for_status(row.status, row.visit_type)
		by_name[row.name] = row

	parked_by_slot = {
		row.parking_slot: row for row in visits if row.status in PARKED_STATUSES and row.parking_slot
	}
	parking_slots = [
		{"slot": slot, "visit": parked_by_slot.get(slot)}
		for slot in PARKING_SLOTS
	]

	docks = frappe.get_all(
		"Dock",
		fields=["name", "dock_code", "dock_name", "dock_type", "status", "current_visit", "sort_order"],
		order_by="sort_order asc, name asc",
	)
	for dock in docks:
		visit = by_name.get(dock.current_visit) if dock.current_visit else None
		if not visit:
			visit = next((row for row in visits if row.dock == dock.name and row.status in ON_DOCK_STATUSES), None)
		dock["visit"] = visit

	ready = [row for row in visits if row.status in READY_STATUSES]
	on_dock = [row for row in visits if row.status in ON_DOCK_STATUSES]
	parked = [row for row in visits if row.status in PARKED_STATUSES]
	available_docks = [
		{"name": dock.name, "dock_name": dock.dock_name, "dock_type": dock.dock_type}
		for dock in docks
		if dock.status == "Available" and not dock.get("visit")
	]

	return {
		"parking_slots": parking_slots,
		"docks": docks,
		"ready": ready,
		"parked": parked,
		"on_dock": on_dock,
		"available_docks": available_docks,
		"counts": {
			"in_yard": len(visits),
			"parked": len(parked),
			"on_dock": len(on_dock),
			"ready": len(ready),
		},
	}
