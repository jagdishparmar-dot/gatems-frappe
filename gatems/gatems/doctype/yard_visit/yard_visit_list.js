frappe.listview_settings["Yard Visit"] = {
	add_fields: ["status", "visit_type", "dock", "parking_slot"],
	get_indicator(doc) {
		const map = {
			Parked: ["Parked", "orange", "status,=,Parked"],
			"Dock Assigned": ["Dock Assigned", "blue", "status,=,Dock Assigned"],
			"On Dock": ["On Dock", "cyan", "status,=,On Dock"],
			Loading: ["Loading", "yellow", "status,=,Loading"],
			Unloading: ["Unloading", "purple", "status,=,Unloading"],
			"Ready to Check Out": ["Ready to Check Out", "green", "status,=,Ready to Check Out"],
			"Checked Out": ["Checked Out", "darkgrey", "status,=,Checked Out"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},
};
