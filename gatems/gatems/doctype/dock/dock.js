// Copyright (c) 2026, GateMS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dock", {
	refresh(frm) {
		if (frm.doc.current_visit) {
			frm.add_custom_button(__("Open Yard Visit"), () => {
				frappe.set_route("Form", "Yard Visit", frm.doc.current_visit);
			});
		}
		frm.add_custom_button(__("Yard Board"), () => frappe.set_route("yard-status"));
	},
});
