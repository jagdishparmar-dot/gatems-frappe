// Copyright (c) 2026, GateMS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicles", {
	refresh(frm) {
		frm.trigger("make_dashboard");
		show_compliance_alerts(frm);

		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Fleet Tracker"), () => frappe.set_route("fleet-tracker"));
		frm.add_custom_button(__("Yard Board"), () => frappe.set_route("yard-status"));
		if (frappe.model.can_read("Vehicle Live Track")) {
			frm.add_custom_button(__("Live Track"), () => {
				frappe.set_route("Form", "Vehicle Live Track", frm.doc.name);
			});
		}
		if (frappe.model.can_read("Yard Visit")) {
			frappe.call({
				method: "gatems.gatems.doctype.yard_visit.yard_visit.get_open_visit",
				args: { vehicle: frm.doc.name },
				callback(r) {
					if (r.message && r.message.name) {
						frm.add_custom_button(__("Open Yard Visit"), () => {
							frappe.set_route("Form", "Yard Visit", r.message.name);
						});
					}
				},
			});
		}
	},

	make_dashboard(frm) {
		if (frm.is_new()) {
			return;
		}

		const status_color = {
			Active: "green",
			Inactive: "grey",
			Blacklisted: "red",
			Sold: "blue",
			Scrapped: "purple",
			"Under Maintenance": "orange",
		};

		if (!frm.dashboard) {
			return;
		}

		frm.dashboard.add_indicator(
			__("Status: {0}", [frm.doc.status || "-"]),
			status_color[frm.doc.status] || "blue"
		);

		if (frm.doc.make || frm.doc.model) {
			frm.dashboard.add_indicator(
				[frm.doc.make, frm.doc.model, frm.doc.variant].filter(Boolean).join(" "),
				"blue"
			);
		}

		if (frm.doc.vehicle_type || frm.doc.fuel_type) {
			frm.dashboard.add_indicator(
				[frm.doc.vehicle_type, frm.doc.fuel_type].filter(Boolean).join(" / "),
				"orange"
			);
		}

		if (frm.doc.state || frm.doc.rto_code) {
			frm.dashboard.add_indicator(
				[frm.doc.state, frm.doc.rto_code].filter(Boolean).join(" / "),
				"grey"
			);
		}

		if (frm.doc.owner_name) {
			frm.dashboard.add_indicator(__("Owner: {0}", [frm.doc.owner_name]), "grey");
		}
	},

	registration_number(frm) {
		if (!frm.doc.registration_number) {
			return;
		}
		const normalized = frm.doc.registration_number.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
		if (frm.doc.registration_number !== normalized) {
			frm.set_value("registration_number", normalized);
			return;
		}
		apply_registration_defaults(frm);
	},

	chassis_number(frm) {
		if (frm.doc.chassis_number) {
			frm.set_value("chassis_number", frm.doc.chassis_number.replace(/\s+/g, "").toUpperCase());
		}
	},

	status(frm) {
		frm.toggle_reqd("blacklist_reason", frm.doc.status === "Blacklisted");
	},

	hypothecated(frm) {
		frm.toggle_reqd("financier_name", frm.doc.hypothecated);
	},
});

const STATE_CODES = {
	AN: "Andaman and Nicobar Islands",
	AP: "Andhra Pradesh",
	AR: "Arunachal Pradesh",
	AS: "Assam",
	BR: "Bihar",
	CG: "Chhattisgarh",
	CH: "Chandigarh",
	DD: "Dadra and Nagar Haveli and Daman and Diu",
	DL: "Delhi",
	DN: "Dadra and Nagar Haveli and Daman and Diu",
	GA: "Goa",
	GJ: "Gujarat",
	HP: "Himachal Pradesh",
	HR: "Haryana",
	JH: "Jharkhand",
	JK: "Jammu and Kashmir",
	KA: "Karnataka",
	KL: "Kerala",
	LA: "Ladakh",
	LD: "Lakshadweep",
	MH: "Maharashtra",
	ML: "Meghalaya",
	MN: "Manipur",
	MP: "Madhya Pradesh",
	MZ: "Mizoram",
	NL: "Nagaland",
	OD: "Odisha",
	OR: "Odisha",
	PB: "Punjab",
	PY: "Puducherry",
	RJ: "Rajasthan",
	SK: "Sikkim",
	TN: "Tamil Nadu",
	TR: "Tripura",
	TS: "Telangana",
	TG: "Telangana",
	UA: "Uttarakhand",
	UK: "Uttarakhand",
	UP: "Uttar Pradesh",
	WB: "West Bengal",
};

function apply_registration_defaults(frm) {
	const reg = (frm.doc.registration_number || "").toUpperCase();
	if (!/^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$/.test(reg)) {
		return;
	}
	const state = STATE_CODES[reg.slice(0, 2)];
	if (state && !frm.doc.state) {
		frm.set_value("state", state);
	}
	const rto = reg.match(/^([A-Z]{2}[0-9]{1,2})/);
	if (rto && !frm.doc.rto_code) {
		frm.set_value("rto_code", rto[1]);
	}
}

function show_compliance_alerts(frm) {
	if (frm.is_new()) {
		return;
	}
	const today = frappe.datetime.get_today();
	const expired = [];
	const soon = [];
	const checks = [
		["insurance_valid_upto", __("Insurance")],
		["puc_valid_upto", __("PUC")],
		["tax_valid_upto", __("Road Tax")],
		["fitness_valid_upto", __("Fitness Certificate")],
		["permit_valid_upto", __("Permit")],
	];
	checks.forEach(([field, label]) => {
		const value = frm.doc[field];
		if (!value) {
			return;
		}
		if (value < today) {
			expired.push(__("{0} expired on {1}", [label, frappe.datetime.str_to_user(value)]));
		} else if (frappe.datetime.get_diff(value, today) <= 15) {
			soon.push(__("{0} expires on {1}", [label, frappe.datetime.str_to_user(value)]));
		}
	});
	if (expired.length) {
		frm.dashboard.set_headline_alert(expired.join(" · "), "red");
	} else if (soon.length) {
		frm.dashboard.set_headline_alert(soon.join(" · "), "yellow");
	}
}
