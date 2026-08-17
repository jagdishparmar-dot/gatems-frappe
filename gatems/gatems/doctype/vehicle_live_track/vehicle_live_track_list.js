frappe.listview_settings["Vehicle Live Track"] = {
	add_fields: ["status", "speed_kmph", "location_name"],
	hide_name_column: true,
	get_indicator(doc) {
		const colors = {
			Moving: "green",
			Idle: "orange",
			Stopped: "darkgrey",
			Offline: "red",
		};
		return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
	},
	onload(listview) {
		listview.page.add_inner_button(__("Fleet Tracker"), () => {
			frappe.set_route("fleet-tracker");
		});
	},
};
