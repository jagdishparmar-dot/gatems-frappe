# Copyright (c) 2026, GateMS and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from gatems.gatems.doctype.vehicles.vehicles import normalize_registration_number


class IntegrationTestVehicles(IntegrationTestCase):
	def test_normalize_registration_number(self):
		self.assertEqual(normalize_registration_number("mh 12-ab 1234"), "MH12AB1234")
		self.assertEqual(normalize_registration_number("22 BH 1234 AA"), "22BH1234AA")

	def test_create_india_vehicle_master(self):
		doc = frappe.get_doc(
			{
				"doctype": "Vehicles",
				"registration_number": "mh 12 ab 1234",
				"make": "Maruti Suzuki",
				"model": "Swift",
				"vehicle_type": "Car",
				"fuel_type": "Petrol",
				"vehicle_category": "Private",
			}
		).insert()
		self.assertEqual(doc.registration_number, "MH12AB1234")
		self.assertEqual(doc.name, "MH12AB1234")
		self.assertEqual(doc.state, "Maharashtra")
		self.assertEqual(doc.rto_code, "MH12")
		doc.delete()
