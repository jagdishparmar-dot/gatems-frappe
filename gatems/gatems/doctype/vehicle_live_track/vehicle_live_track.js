// Copyright (c) 2026, GateMS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Live Track", {
	refresh(frm) {
		frm.add_custom_button(__("Fleet Tracker"), () => {
			frappe.set_route("fleet-tracker");
		});
		if (frm.doc.latitude && frm.doc.longitude) {
			frm.dashboard.add_indicator(
				__("{0}, {1}", [frm.doc.latitude, frm.doc.longitude]),
				frm.doc.status === "Moving" ? "green" : "orange"
			);
		}
	},

	latitude(frm) {
		sync_map(frm);
	},

	longitude(frm) {
		sync_map(frm);
	},
});

function sync_map(frm) {
	if (!(frm.doc.latitude && frm.doc.longitude)) {
		return;
	}
	frm.set_value(
		"geolocation",
		JSON.stringify({
			type: "FeatureCollection",
			features: [
				{
					type: "Feature",
					properties: {},
					geometry: {
						type: "Point",
						coordinates: [frm.doc.longitude, frm.doc.latitude],
					},
				},
			],
		})
	);
}
