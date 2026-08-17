import json

import frappe
from frappe.utils import now_datetime

from gatems.gatems.doctype.vehicle_live_track.vehicle_live_track import DEMO_ROUTES, point_geojson

GATEMS_WORKSPACE_CONTENT = json.dumps(
	[
		{
			"id": "gatems-yard-header",
			"type": "header",
			"data": {"text": "<b>Yard Management</b>", "col": 12},
		},
		{
			"id": "gatems-yard-board",
			"type": "shortcut",
			"data": {"shortcut_name": "Yard Board", "col": 4},
		},
		{
			"id": "gatems-yard-visits",
			"type": "shortcut",
			"data": {"shortcut_name": "Yard Visits", "col": 4},
		},
		{"id": "gatems-header", "type": "header", "data": {"text": "<b>Masters</b>", "col": 12}},
		{"id": "gatems-vehicles", "type": "shortcut", "data": {"shortcut_name": "Vehicles", "col": 4}},
		{
			"id": "gatems-tracker",
			"type": "shortcut",
			"data": {"shortcut_name": "Fleet Tracker", "col": 4},
		},
		{"id": "gatems-card-yard", "type": "card", "data": {"card_name": "Yard", "col": 4}},
		{"id": "gatems-card-masters", "type": "card", "data": {"card_name": "Masters", "col": 4}},
		{"id": "gatems-card-track", "type": "card", "data": {"card_name": "Tracking", "col": 4}},
	]
)

DEMO_VEHICLES = [
	{
		"registration_number": "MH12AB1234",
		"make": "Maruti Suzuki",
		"model": "Swift",
		"variant": "ZXi",
		"vehicle_type": "Car",
		"body_type": "Hatchback",
		"vehicle_class": "Light Motor Vehicle (LMV)",
		"fuel_type": "Petrol",
		"emission_norm": "BS-VI",
		"color": "White",
		"vehicle_category": "Private",
		"usage_type": "Employee",
		"chassis_number": "MA3ERLF1S00123456",
		"engine_number": "K12MN1234567",
		"manufacturing_year": 2023,
		"cubic_capacity": 1197,
		"engine_power_bhp": 88.5,
		"seating_capacity": 5,
		"unladen_weight": 920,
		"gross_vehicle_weight": 1340,
		"number_of_cylinders": 4,
		"owner_type": "Company",
		"owner_name": "GateMS Demo Fleet",
		"owner_address": "Bandra Kurla Complex, Mumbai, Maharashtra 400051",
		"mobile_number": "9876543210",
		"last_odometer": 18450,
		"insurance_company": "ICICI Lombard",
		"insurance_policy_no": "IL-MH-2026-88912",
		"insurance_type": "Comprehensive",
		"insurance_start_date": "2026-01-15",
		"insurance_valid_upto": "2027-01-14",
		"puc_number": "MH12PUC8891",
		"puc_valid_upto": "2026-12-31",
		"tax_valid_upto": "2027-03-31",
		"fastag_id": "608268XXXX8891",
		"access_tag_id": "RFID-MH-1001",
		"status": "Active",
	},
	{
		"registration_number": "DL01CA4321",
		"make": "Hyundai",
		"model": "Creta",
		"variant": "SX",
		"vehicle_type": "SUV",
		"body_type": "SUV",
		"vehicle_class": "Light Motor Vehicle (LMV)",
		"fuel_type": "Diesel",
		"emission_norm": "BS-VI",
		"color": "Silver",
		"vehicle_category": "Private",
		"usage_type": "Company Owned",
		"chassis_number": "MALC381RLTM432100",
		"engine_number": "D4FADL432100",
		"manufacturing_year": 2024,
		"cubic_capacity": 1493,
		"engine_power_bhp": 113.4,
		"seating_capacity": 5,
		"unladen_weight": 1245,
		"gross_vehicle_weight": 1720,
		"number_of_cylinders": 4,
		"owner_type": "Company",
		"owner_name": "GateMS Demo Fleet",
		"owner_address": "Connaught Place, New Delhi 110001",
		"mobile_number": "9810012345",
		"last_odometer": 9620,
		"insurance_company": "Bajaj Allianz",
		"insurance_policy_no": "BA-DL-2026-4321",
		"insurance_type": "Comprehensive",
		"insurance_start_date": "2026-04-01",
		"insurance_valid_upto": "2027-03-31",
		"puc_number": "DL01PUC4321",
		"puc_valid_upto": "2026-11-30",
		"tax_valid_upto": "2027-03-31",
		"fastag_id": "608268XXXX4321",
		"access_tag_id": "RFID-DL-1002",
		"status": "Active",
	},
	{
		"registration_number": "KA03MG2468",
		"make": "Tata",
		"model": "Nexon EV",
		"variant": "Fearless+",
		"vehicle_type": "SUV",
		"body_type": "SUV",
		"vehicle_class": "Light Motor Vehicle (LMV)",
		"fuel_type": "Electric",
		"emission_norm": "EV (Zero Emission)",
		"color": "Blue",
		"vehicle_category": "Private",
		"usage_type": "Company Owned",
		"chassis_number": "MAT6222468NE00001",
		"engine_number": "EV-MOTOR-2468",
		"manufacturing_year": 2025,
		"cubic_capacity": 0,
		"engine_power_bhp": 127.0,
		"seating_capacity": 5,
		"unladen_weight": 1400,
		"gross_vehicle_weight": 1840,
		"number_of_cylinders": 0,
		"owner_type": "Company",
		"owner_name": "GateMS Demo Fleet",
		"owner_address": "MG Road, Bengaluru, Karnataka 560001",
		"mobile_number": "9845011122",
		"last_odometer": 4210,
		"insurance_company": "HDFC ERGO",
		"insurance_policy_no": "HE-KA-2026-2468",
		"insurance_type": "Comprehensive",
		"insurance_start_date": "2026-02-10",
		"insurance_valid_upto": "2027-02-09",
		"puc_number": "KA03PUC2468",
		"puc_valid_upto": "2027-02-09",
		"tax_valid_upto": "2028-03-31",
		"fastag_id": "608268XXXX2468",
		"access_tag_id": "RFID-KA-1003",
		"status": "Active",
	},
]


def after_install():
	create_roles()
	bind_doctypes_to_app()
	seed_demo_fleet()
	seed_demo_yard()
	fix_workspace()
	ensure_gatems_user()
	apply_branding()
	apply_realtime_config()


def after_migrate():
	create_roles()
	bind_doctypes_to_app()
	seed_demo_fleet()
	seed_demo_yard()
	fix_workspace()
	ensure_gatems_user()
	apply_branding()
	apply_realtime_config()


GATEMS_LOGO = "/assets/gatems/images/gatems-mark.svg"


def apply_branding():
	if frappe.db.exists("DocType", "Website Settings"):
		frappe.db.set_value(
			"Website Settings",
			"Website Settings",
			{
				"app_name": "GateMS",
				"app_logo": GATEMS_LOGO,
				"favicon": GATEMS_LOGO,
				"splash_image": GATEMS_LOGO,
				"disable_signup": 1,
			},
			update_modified=False,
		)
	if frappe.db.exists("DocType", "Navbar Settings"):
		frappe.db.set_value(
			"Navbar Settings",
			"Navbar Settings",
			{"app_logo": GATEMS_LOGO},
			update_modified=False,
		)
	if frappe.db.exists("DocType", "System Settings"):
		frappe.db.set_value(
			"System Settings",
			"System Settings",
			{"app_name": "GateMS"},
			update_modified=False,
		)
	frappe.db.commit()


def apply_realtime_config():
	from frappe.installer import update_site_config

	update_site_config("socketio_port", 9001)
	frappe.conf.socketio_port = 9001


def create_roles():
	for role_name in ("Gate Manager", "Gate User"):
		if frappe.db.exists("Role", role_name):
			continue
		role = frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 1,
			}
		)
		role.insert(ignore_permissions=True)


GATEMS_USER_EMAIL = "gateuser@gatems.local"
GATEMS_USER_PASSWORD = "Gatems@123"
GATEMS_ALLOWED_MODULES = {"GateMS"}
GATEMS_USER_ROLES = ("Gate Manager",)


def create_module_profile():
	blocked = [
		{"module": module_name}
		for module_name in frappe.get_all("Module Def", pluck="module_name")
		if module_name not in GATEMS_ALLOWED_MODULES
	]
	if frappe.db.exists("Module Profile", "GateMS"):
		profile = frappe.get_doc("Module Profile", "GateMS")
		profile.set("block_modules", blocked)
		profile.save(ignore_permissions=True)
		return
	frappe.get_doc(
		{
			"doctype": "Module Profile",
			"module_profile_name": "GateMS",
			"block_modules": blocked,
		}
	).insert(ignore_permissions=True)


def restrict_workspace_roles():
	if not frappe.db.exists("Workspace", "GateMS"):
		return
	workspace = frappe.get_doc("Workspace", "GateMS")
	wanted = ["System Manager", "Gate Manager", "Gate User"]
	existing = {row.role for row in workspace.roles}
	changed = False
	for role in wanted:
		if role not in existing:
			workspace.append("roles", {"role": role})
			changed = True
	if changed:
		workspace.save(ignore_permissions=True)


def ensure_gatems_user():
	create_roles()
	create_module_profile()
	restrict_workspace_roles()

	is_new = not frappe.db.exists("User", GATEMS_USER_EMAIL)
	if is_new:
		user = frappe.new_doc("User")
		user.email = GATEMS_USER_EMAIL
		user.first_name = "Gate"
		user.last_name = "User"
		user.send_welcome_email = 0
		user.user_type = "System User"
	else:
		user = frappe.get_doc("User", GATEMS_USER_EMAIL)

	user.enabled = 1
	user.module_profile = "GateMS"
	if frappe.db.exists("Workspace", "GateMS"):
		user.default_workspace = "GateMS"
	user.default_app = "gatems"
	user.set("roles", [])
	for role in GATEMS_USER_ROLES:
		user.append("roles", {"role": role})

	user.flags.no_welcome_mail = True
	user.flags.ignore_password_policy = True
	if is_new:
		user.insert(ignore_permissions=True)
		user.new_password = GATEMS_USER_PASSWORD
		user.save(ignore_permissions=True)
	else:
		user.save(ignore_permissions=True)
	frappe.db.commit()


def bind_doctypes_to_app():
	frappe.db.sql(
		"""
		UPDATE `tabDocType` dt
		INNER JOIN `tabModule Def` md ON dt.module = md.module_name
		SET dt.app = 'gatems'
		WHERE md.app_name = 'gatems'
		"""
	)


def seed_demo_fleet():
	if not frappe.db.exists("DocType", "Vehicles") or not frappe.db.exists(
		"DocType", "Vehicle Live Track"
	):
		return

	for idx, vehicle in enumerate(DEMO_VEHICLES):
		name = vehicle["registration_number"]
		if frappe.db.exists("Vehicles", name):
			frappe.db.set_value("Vehicles", name, {k: v for k, v in vehicle.items() if k != "registration_number"})
		else:
			doc = frappe.get_doc({"doctype": "Vehicles", **vehicle, "status": vehicle.get("status") or "Active"})
			doc.insert(ignore_permissions=True)

		route = DEMO_ROUTES[name]["route"]
		lat, lng = route[0]
		values = {
			"vehicle": name,
			"status": "Moving",
			"latitude": lat,
			"longitude": lng,
			"location_name": DEMO_ROUTES[name]["location_names"][0],
			"speed_kmph": 36 + idx * 4,
			"heading": 45,
			"ignition": 1,
			"is_demo": 1,
			"demo_progress": idx * 0.2,
			"last_ping": now_datetime(),
			"geolocation": point_geojson(lat, lng),
		}
		if frappe.db.exists("Vehicle Live Track", name):
			frappe.db.set_value("Vehicle Live Track", name, {"is_demo": 1, "vehicle": name})
			continue
		track = frappe.get_doc({"doctype": "Vehicle Live Track", **values})
		track.insert(ignore_permissions=True)

	frappe.db.commit()


DEMO_DOCKS = [
	{"dock_code": "D01", "dock_name": "Dock 1", "dock_type": "Unloading", "sort_order": 1},
	{"dock_code": "D02", "dock_name": "Dock 2", "dock_type": "Loading", "sort_order": 2},
	{"dock_code": "D03", "dock_name": "Dock 3", "dock_type": "Both", "sort_order": 3},
	{"dock_code": "D04", "dock_name": "Dock 4", "dock_type": "Unloading", "sort_order": 4},
	{"dock_code": "D05", "dock_name": "Dock 5", "dock_type": "Loading", "sort_order": 5},
	{"dock_code": "D06", "dock_name": "Dock 6", "dock_type": "Both", "sort_order": 6},
]


def seed_docks():
	if not frappe.db.exists("DocType", "Dock"):
		return
	for row in DEMO_DOCKS:
		if frappe.db.exists("Dock", row["dock_code"]):
			continue
		frappe.get_doc({"doctype": "Dock", "status": "Available", **row}).insert(ignore_permissions=True)


def seed_demo_yard():
	if not frappe.db.exists("DocType", "Yard Visit") or not frappe.db.exists("DocType", "Dock"):
		return
	seed_docks()
	if frappe.db.count("Yard Visit"):
		return

	from gatems.gatems.doctype.dock.dock import occupy_dock

	now = now_datetime()
	samples = [
		{
			"vehicle": "MH12AB1234",
			"status": "Parked",
			"visit_type": "Unloading",
			"parking_slot": "P01",
			"driver_name": "Ramesh Patil",
			"driver_mobile": "9876543210",
			"driver_license_no": "MH12 20190012345",
			"transporter": "Pune Freight Co",
			"material_type": "Raw Material",
			"material_description": "Corrugated packaging rolls",
			"party_name": "West Coast Supplies",
			"quantity": 24,
			"uom": "Pallet",
			"reference_no": "PO-88421",
			"check_in_time": now,
		},
		{
			"vehicle": "DL01CA4321",
			"status": "Loading",
			"visit_type": "Loading",
			"dock": "D02",
			"driver_name": "Amit Sharma",
			"driver_mobile": "9810012345",
			"driver_license_no": "DL01 20210055667",
			"transporter": "Delhi Logistics",
			"material_type": "Finished Goods",
			"material_description": "Outbound cartons for north region",
			"party_name": "North Distributors",
			"quantity": 18,
			"uom": "Ton",
			"reference_no": "INV-33012",
			"check_in_time": now,
			"dock_assigned_time": now,
			"operation_start": now,
		},
		{
			"vehicle": "KA03MG2468",
			"status": "Ready to Check Out",
			"visit_type": "Unloading",
			"dock": "D03",
			"driver_name": "Suresh Nair",
			"driver_mobile": "9845011122",
			"driver_license_no": "KA03 20180099881",
			"transporter": "Bengaluru Carriers",
			"material_type": "Spare Parts",
			"material_description": "Empty return after spare-parts delivery",
			"party_name": "Plant Stores",
			"quantity": 6,
			"uom": "Crate",
			"reference_no": "DN-22901",
			"check_in_time": now,
			"dock_assigned_time": now,
			"operation_start": now,
			"operation_end": now,
			"dock_out_time": now,
		},
	]
	for values in samples:
		vehicle = values["vehicle"]
		if not frappe.db.exists("Vehicles", vehicle):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Yard Visit",
				"vehicle_source": "Master",
				"make": frappe.db.get_value("Vehicles", vehicle, "make"),
				"model": frappe.db.get_value("Vehicles", vehicle, "model"),
				"vehicle_type": frappe.db.get_value("Vehicles", vehicle, "vehicle_type"),
				**values,
			}
		)
		doc.insert(ignore_permissions=True)
		if values["status"] in ("Dock Assigned", "On Dock", "Loading", "Unloading"):
			occupy_dock(values["dock"], doc.name)
	frappe.db.commit()


def fix_workspace():
	if not frappe.db.exists("Workspace", "GateMS"):
		return
	frappe.db.set_value("Workspace", "GateMS", "content", GATEMS_WORKSPACE_CONTENT, update_modified=False)
	frappe.db.commit()
