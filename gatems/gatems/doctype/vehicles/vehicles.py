# Copyright (c) 2026, GateMS and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, getdate


STANDARD_REGISTRATION = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$")
BHARAT_SERIES = re.compile(r"^[0-9]{2}BH[0-9]{4}[A-Z]{1,2}$")
RTO_CODE = re.compile(r"^[A-Z]{2}[0-9]{1,2}$")

STATE_CODES = {
	"AN": "Andaman and Nicobar Islands",
	"AP": "Andhra Pradesh",
	"AR": "Arunachal Pradesh",
	"AS": "Assam",
	"BR": "Bihar",
	"CG": "Chhattisgarh",
	"CH": "Chandigarh",
	"DD": "Dadra and Nagar Haveli and Daman and Diu",
	"DL": "Delhi",
	"DN": "Dadra and Nagar Haveli and Daman and Diu",
	"GA": "Goa",
	"GJ": "Gujarat",
	"HP": "Himachal Pradesh",
	"HR": "Haryana",
	"JH": "Jharkhand",
	"JK": "Jammu and Kashmir",
	"KA": "Karnataka",
	"KL": "Kerala",
	"LA": "Ladakh",
	"LD": "Lakshadweep",
	"MH": "Maharashtra",
	"ML": "Meghalaya",
	"MN": "Manipur",
	"MP": "Madhya Pradesh",
	"MZ": "Mizoram",
	"NL": "Nagaland",
	"OD": "Odisha",
	"OR": "Odisha",
	"PB": "Punjab",
	"PY": "Puducherry",
	"RJ": "Rajasthan",
	"SK": "Sikkim",
	"TN": "Tamil Nadu",
	"TR": "Tripura",
	"TS": "Telangana",
	"TG": "Telangana",
	"UA": "Uttarakhand",
	"UK": "Uttarakhand",
	"UP": "Uttar Pradesh",
	"WB": "West Bengal",
}


def normalize_registration_number(value: str | None) -> str:
	if not value:
		return ""
	return re.sub(r"[^A-Za-z0-9]", "", value).upper()


class Vehicles(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		access_tag_id: DF.Data | None
		amended_from: DF.Link | None
		assigned_employee: DF.Data | None
		blacklist_reason: DF.SmallText | None
		body_type: DF.Literal["", "Saloon / Sedan", "Hatchback", "SUV", "MUV / MPV", "Coupe", "Convertible", "Pickup", "Hard Top", "Soft Top", "Goods Carrier", "Tanker", "Tipper", "Bus Body", "Ambulance", "Other"]
		chassis_number: DF.Data | None
		color: DF.Data | None
		company: DF.Data | None
		cubic_capacity: DF.Int
		emission_norm: DF.Literal["", "BS-III", "BS-IV", "BS-VI", "BS-VI Stage 2", "EV (Zero Emission)"]
		engine_number: DF.Data | None
		engine_power_bhp: DF.Float
		fastag_id: DF.Data | None
		financier_name: DF.Data | None
		fitness_valid_upto: DF.Date | None
		fuel_type: DF.Literal["Petrol", "Diesel", "CNG", "LPG", "Electric", "Hybrid (Petrol + Electric)", "Hybrid (Diesel + Electric)", "Ethanol / Flex Fuel", "Hydrogen"]
		gross_vehicle_weight: DF.Int
		hypothecated: DF.Check
		insurance_company: DF.Data | None
		insurance_copy: DF.Attach | None
		insurance_policy_no: DF.Data | None
		insurance_start_date: DF.Date | None
		insurance_type: DF.Literal["", "Comprehensive", "Third Party", "Own Damage"]
		insurance_valid_upto: DF.Date | None
		last_odometer: DF.Int
		make: DF.Data
		manufacturing_year: DF.Int
		mobile_number: DF.Data | None
		model: DF.Data
		number_of_cylinders: DF.Int
		owner_address: DF.SmallText | None
		owner_name: DF.Data | None
		owner_type: DF.Literal["", "Individual", "Company", "Government", "Partnership", "Trust / Society"]
		permit_copy: DF.Attach | None
		permit_number: DF.Data | None
		permit_type: DF.Literal["", "National Permit", "State Permit", "Contract Carriage", "Stage Carriage", "Goods Permit", "Temporary Permit"]
		permit_valid_upto: DF.Date | None
		puc_copy: DF.Attach | None
		puc_number: DF.Data | None
		puc_valid_upto: DF.Date | None
		rc_copy: DF.Attach | None
		registering_authority: DF.Data | None
		registration_date: DF.Date | None
		registration_number: DF.Data
		remarks: DF.SmallText | None
		rto_code: DF.Data | None
		seating_capacity: DF.Int
		state: DF.Literal["", "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]
		status: DF.Literal["Active", "Inactive", "Blacklisted", "Sold", "Scrapped", "Under Maintenance"]
		tax_valid_upto: DF.Date | None
		unladen_weight: DF.Int
		usage_type: DF.Literal["", "Company Owned", "Employee", "Visitor", "Contractor", "Vendor", "Government", "Other"]
		variant: DF.Data | None
		vehicle_category: DF.Literal["Private", "Commercial", "Government"]
		vehicle_class: DF.Literal["", "Two Wheeler", "Three Wheeler", "Light Motor Vehicle (LMV)", "Medium Goods Vehicle (MGV)", "Medium Passenger Vehicle (MPV)", "Heavy Goods Vehicle (HGV)", "Heavy Passenger Vehicle (HPV)", "Trailer", "Construction Equipment Vehicle", "Agricultural Tractor", "Others"]
		vehicle_photo: DF.AttachImage | None
		vehicle_type: DF.Literal["", "Car", "SUV", "Van", "Bus", "Mini Bus", "Truck", "Pickup / Tempo", "Motorcycle", "Scooter", "Auto Rickshaw", "Tractor", "Tanker", "Ambulance", "Fire Tender", "Other"]
	# end: auto-generated types

	def autoname(self):
		self.registration_number = normalize_registration_number(self.registration_number)
		self._apply_registration_defaults()
		self.name = self.registration_number

	def before_validate(self):
		self.registration_number = normalize_registration_number(self.registration_number)
		if self.chassis_number:
			self.chassis_number = re.sub(r"\s+", "", self.chassis_number).upper()
		if self.engine_number:
			self.engine_number = re.sub(r"\s+", "", self.engine_number).upper()
		if self.fastag_id:
			self.fastag_id = re.sub(r"\s+", "", self.fastag_id).upper()
		if self.rto_code:
			self.rto_code = normalize_registration_number(self.rto_code)
		self._apply_registration_defaults()

	def validate(self):
		self._validate_registration_number()
		self._validate_rto_code()
		self._validate_manufacturing_year()
		self._validate_weights()
		self._validate_date_order(
			self.insurance_start_date,
			self.insurance_valid_upto,
			_("Insurance Valid Upto"),
			_("Insurance Start Date"),
		)
		if self.status == "Blacklisted" and not self.blacklist_reason:
			frappe.throw(_("Please enter a Blacklist Reason"))
		if self.hypothecated and not self.financier_name:
			frappe.throw(_("Financier Name is required when the vehicle is hypothecated"))
		self._validate_unique_chassis()

	def _apply_registration_defaults(self):
		reg = self.registration_number or ""
		if not STANDARD_REGISTRATION.match(reg):
			return

		state_code = reg[:2]
		state_name = STATE_CODES.get(state_code)
		if state_name and not self.state:
			self.state = state_name

		match = re.match(r"^([A-Z]{2}[0-9]{1,2})", reg)
		if match and not self.rto_code:
			self.rto_code = match.group(1)

	def _validate_registration_number(self):
		reg = self.registration_number
		if not reg:
			frappe.throw(_("Registration Number is required"))
		if not (STANDARD_REGISTRATION.match(reg) or BHARAT_SERIES.match(reg)):
			frappe.throw(
				_(
					"Enter a valid Indian registration number, e.g. MH12AB1234 or Bharat series 22BH1234AA"
				)
			)

	def _validate_rto_code(self):
		if self.rto_code and not RTO_CODE.match(self.rto_code):
			frappe.throw(_("RTO Code should look like MH12 or DL1"))

	def _validate_manufacturing_year(self):
		year = cint(self.manufacturing_year)
		if not year:
			return
		current_year = getdate().year
		if year < 1950 or year > current_year + 1:
			frappe.throw(_("Year of Manufacture must be between 1950 and {0}").format(current_year + 1))
		if self.registration_date and year > getdate(self.registration_date).year:
			frappe.throw(_("Year of Manufacture cannot be after Registration Date"))

	def _validate_weights(self):
		if (
			cint(self.unladen_weight)
			and cint(self.gross_vehicle_weight)
			and cint(self.gross_vehicle_weight) < cint(self.unladen_weight)
		):
			frappe.throw(_("Gross Vehicle Weight cannot be less than Unladen Weight"))

	def _validate_unique_chassis(self):
		if not self.chassis_number:
			return
		exists = frappe.db.exists(
			"Vehicles",
			{"chassis_number": self.chassis_number, "name": ["!=", self.name or ""]},
		)
		if exists:
			frappe.throw(_("Chassis Number {0} already exists on {1}").format(self.chassis_number, exists))

	def _validate_date_order(self, start, end, end_label, start_label):
		if start and end and getdate(end) < getdate(start):
			frappe.throw(_("{0} cannot be before {1}").format(end_label, start_label))
