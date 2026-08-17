frappe.listview_settings["Dock"] = {
	add_fields: ["status", "dock_type", "current_visit"],
	get_indicator(doc) {
		if (doc.status === "Occupied") {
			return [__("Occupied"), "orange", "status,=,Occupied"];
		}
		if (doc.status === "Maintenance") {
			return [__("Maintenance"), "grey", "status,=,Maintenance"];
		}
		return [__("Available"), "green", "status,=,Available"];
	},
};
