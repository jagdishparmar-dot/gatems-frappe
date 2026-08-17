frappe.listview_settings["Vehicles"] = {
	add_fields: ["status", "insurance_valid_upto", "puc_valid_upto", "vehicle_type"],
	get_indicator(doc) {
		const today = frappe.datetime.get_today();
		if (doc.status === "Blacklisted") {
			return [__("Blacklisted"), "red", "status,=,Blacklisted"];
		}
		if (doc.status === "Inactive") {
			return [__("Inactive"), "darkgrey", "status,=,Inactive"];
		}
		if (doc.status === "Sold") {
			return [__("Sold"), "blue", "status,=,Sold"];
		}
		if (doc.status === "Scrapped") {
			return [__("Scrapped"), "purple", "status,=,Scrapped"];
		}
		if (doc.status === "Under Maintenance") {
			return [__("Under Maintenance"), "orange", "status,=,Under Maintenance"];
		}
		if (doc.insurance_valid_upto && doc.insurance_valid_upto < today) {
			return [__("Insurance Expired"), "red", "insurance_valid_upto,<,Today"];
		}
		if (doc.puc_valid_upto && doc.puc_valid_upto < today) {
			return [__("PUC Expired"), "orange", "puc_valid_upto,<,Today"];
		}
		return [__("Active"), "green", "status,=,Active"];
	},
};
