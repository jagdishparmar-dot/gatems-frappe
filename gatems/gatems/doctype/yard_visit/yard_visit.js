// Copyright (c) 2026, GateMS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Yard Visit", {
	refresh(frm) {
		frm.add_custom_button(__("Yard Board"), () => frappe.set_route("yard-status"));
		if (frm.is_new()) {
			return;
		}

		const actions = {
			assign_dock: __("Assign Dock"),
			start_operation: __("Start Loading / Unloading"),
			stop_operation: __("Stop Loading / Unloading"),
			dock_out: __("Dock Out"),
			check_out: __("Check Out"),
		};

		frappe.call({
			method: "gatems.gatems.doctype.yard_visit.yard_visit.get_yard_status",
			callback(r) {
				const next = ((r.message || {}).parked || [])
					.concat((r.message || {}).on_dock || [])
					.concat((r.message || {}).ready || [])
					.find((row) => row.name === frm.doc.name);
				const list = (next && next.next_actions) || [];
				list.forEach((action) => {
					frm.add_custom_button(actions[action] || action, () => run_visit_action(frm, action, r.message), __("Yard"));
				});
			},
		});
	},
});

function run_visit_action(frm, action, yard) {
	if (action === "assign_dock") {
		const docks = (yard && yard.available_docks) || [];
		if (!docks.length) {
			frappe.msgprint(__("No docks are available"));
			return;
		}
		const dialog = new frappe.ui.Dialog({
			title: __("Assign Dock"),
			fields: [
				{
					fieldname: "dock",
					fieldtype: "Select",
					label: __("Dock"),
					options: docks.map((d) => d.name).join("\n"),
					reqd: 1,
				},
			],
			primary_action_label: __("Assign"),
			primary_action(values) {
				call_advance(frm, action, values.dock);
				dialog.hide();
			},
		});
		dialog.show();
		return;
	}
	if (action === "start_operation" && frm.doc.visit_type === "Both") {
		frappe.prompt(
			{
				fieldname: "operation",
				fieldtype: "Select",
				label: __("Operation"),
				options: "Loading\nUnloading",
				reqd: 1,
			},
			(values) => call_advance(frm, action, null, values.operation),
			__("Start Operation")
		);
		return;
	}
	call_advance(frm, action);
}

function call_advance(frm, action, dock, operation) {
	frappe.call({
		method: "gatems.gatems.doctype.yard_visit.yard_visit.advance_visit",
		args: { visit: frm.doc.name, action, dock, operation },
		freeze: true,
		callback() {
			frm.reload_doc();
		},
	});
}
