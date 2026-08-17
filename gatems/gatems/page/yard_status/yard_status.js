frappe.pages["yard-status"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Yard Board"),
		single_column: true,
	});
	if (frappe.gatems_yard) {
		frappe.gatems_yard.destroy();
	}
	frappe.gatems_yard = new GateMSYardBoard(page);
};

frappe.pages["yard-status"].on_page_show = function () {
	if (frappe.gatems_yard) {
		frappe.gatems_yard.refresh();
	}
};

class GateMSYardBoard {
	constructor(page) {
		this.page = page;
		this.timer = null;
		this.refreshing = false;
		this.make();
		this.bind_realtime();
		this.refresh();
	}

	make() {
		this.page.set_primary_action(__("Check In Vehicle"), () => this.open_checkin());
		this.page.add_inner_button(__("Yard Visits"), () => frappe.set_route("List", "Yard Visit"));
		this.page.add_inner_button(__("Docks"), () => frappe.set_route("List", "Dock"));
		this.page.add_inner_button(__("Refresh"), () => this.refresh(true));

		this.page.main.append(`
			<div class="gatems-yard flex flex-col gap-4 pb-4">
				<div class="flex items-center gap-2">
					<span class="gatems-live-dot shrink-0"></span>
					${__("Live yard")}
					<span id="gatems-yard-meta" class="ms-auto text-ink-gray-5"></span>
				</div>
				<div id="gatems-yard-kpis" class="gatems-yard-kpis"></div>
				<div class="gatems-yard-layout">
					<section class="gatems-yard-zone flex flex-col p-4 rounded-xl border">
						<div class="flex justify-between items-baseline gap-2 mb-3">
							<strong class="text-ink-base">${__("Parking")}</strong>
							<small class="text-ink-gray-5">${__("Checked in · waiting for dock")}</small>
						</div>
						<div id="gatems-yard-parking" class="gatems-yard-grid flex-1"></div>
					</section>
					<section class="gatems-yard-zone flex flex-col p-4 rounded-xl border">
						<div class="flex justify-between items-baseline gap-2 mb-3">
							<strong class="text-ink-base">${__("Docks")}</strong>
							<small class="text-ink-gray-5">${__("Assigned · loading / unloading")}</small>
						</div>
						<div id="gatems-yard-docks" class="gatems-yard-grid flex-1"></div>
					</section>
					<section class="gatems-yard-zone flex flex-col p-4 rounded-xl border">
						<div class="flex justify-between items-baseline gap-2 mb-3">
							<strong class="text-ink-base">${__("Exit Gate")}</strong>
							<small class="text-ink-gray-5">${__("Ready to check out")}</small>
						</div>
						<div id="gatems-yard-ready" class="flex flex-col gap-2 flex-1"></div>
					</section>
				</div>
			</div>
		`);
		this.$kpis = this.page.main.find("#gatems-yard-kpis");
		this.$parking = this.page.main.find("#gatems-yard-parking");
		this.$docks = this.page.main.find("#gatems-yard-docks");
		this.$ready = this.page.main.find("#gatems-yard-ready");
		this.$meta = this.page.main.find("#gatems-yard-meta");
	}

	bind_realtime() {
		this._on_yard = () => {
			if (this.is_current()) {
				this.refresh();
			}
		};
		this._on_list = (data) => {
			if (data && ["Yard Visit", "Dock"].includes(data.doctype) && this.is_current()) {
				this.refresh();
			}
		};
		if (frappe.realtime) {
			frappe.realtime.on("gatems:yard_update", this._on_yard);
			frappe.realtime.on("list_update", this._on_list);
		}
		this._on_visible = () => {
			if (!document.hidden && this.is_current()) {
				this.refresh();
			}
		};
		document.addEventListener("visibilitychange", this._on_visible);
	}

	destroy() {
		this.stop_timer();
		if (frappe.realtime && this._on_yard) {
			frappe.realtime.off("gatems:yard_update", this._on_yard);
			frappe.realtime.off("list_update", this._on_list);
		}
		if (this._on_visible) {
			document.removeEventListener("visibilitychange", this._on_visible);
		}
	}

	is_current() {
		return (frappe.get_route_str() || "") === "yard-status";
	}

	async refresh(manual = false) {
		if (this.refreshing) {
			this.schedule();
			return;
		}
		this.refreshing = true;
		try {
			const r = await frappe.call({
				method: "gatems.gatems.doctype.yard_visit.yard_visit.get_yard_status",
				freeze: manual,
				freeze_message: __("Updating yard"),
			});
			this.data = r.message || {};
			this.render();
			if (this.$meta && this.$meta.length) {
				this.$meta.text(__("updated {0}", [frappe.datetime.now_time()]));
			}
		} catch (e) {
			console.error("Yard Board refresh failed", e);
		} finally {
			this.refreshing = false;
			this.schedule();
		}
	}

	stop_timer() {
		if (this.timer) {
			clearTimeout(this.timer);
			this.timer = null;
		}
	}

	schedule() {
		this.stop_timer();
		this.timer = setTimeout(() => this.refresh(), 5000);
	}

	render() {
		const counts = this.data.counts || {};
		this.$kpis.html(
			[
				kpi(__("In Yard"), counts.in_yard, "ink"),
				kpi(__("Parked"), counts.parked, "amber"),
				kpi(__("On Dock"), counts.on_dock, "cyan"),
				kpi(__("Ready to Exit"), counts.ready, "green"),
			].join("")
		);
		this.$parking.html((this.data.parking_slots || []).map((row) => this.slot_html(row)).join(""));
		this.$docks.html((this.data.docks || []).map((row) => this.dock_html(row)).join(""));
		const ready = this.data.ready || [];
		this.$ready.html(
			ready.length
				? ready.map((visit) => this.card_html(visit)).join("")
				: `<div class="text-center text-ink-gray-5 p-4">${__("No vehicles waiting at the exit gate")}</div>`
		);
		this.bind_actions();
	}

	slot_html(row) {
		if (!row.visit) {
			return `<div class="gatems-yard-slot is-empty flex items-center justify-center rounded-lg text-ink-gray-4"><span>${frappe.utils.escape_html(
				row.slot
			)}</span></div>`;
		}
		return `<div class="gatems-yard-slot is-filled rounded-lg p-2">${this.card_html(row.visit)}</div>`;
	}

	dock_html(dock) {
		const visit = dock.visit;
		const state = visit ? "is-filled" : dock.status === "Maintenance" ? "is-maint" : "is-empty";
		return `
			<div class="gatems-yard-slot gatems-yard-dock rounded-lg p-2 ${state}">
				<div class="flex justify-between items-center gap-2 mb-1.5 text-ink-gray-5">
					<strong>${frappe.utils.escape_html(dock.dock_code || dock.name)}</strong>
					<span>${frappe.utils.escape_html(dock.dock_type)} · ${frappe.utils.escape_html(dock.status)}</span>
				</div>
				${
					visit
						? this.card_html(visit)
						: `<div class="text-center text-ink-gray-5 p-4">${__("Open bay")}</div>`
				}
			</div>
		`;
	}

	card_html(visit) {
		const actions = (visit.next_actions || [])
			.map(
				(action) =>
					`<button type="button" class="btn btn-sm btn-primary gatems-yard-action" data-visit="${frappe.utils.escape_html(
						visit.name
					)}" data-action="${action}">${action_label(action)}</button>`
			)
			.join("");
		return `
			<article class="gatems-yard-card rounded-lg border p-2.5 bg-surface-base cursor-pointer" data-visit="${frappe.utils.escape_html(
				visit.name
			)}">
				<div class="flex justify-between items-center gap-2">
					<strong class="text-ink-base">${frappe.utils.escape_html(visit.vehicle)}</strong>
					<span class="rounded-full px-2 py-0.5 ${pill_class(visit.status)}">${frappe.utils.escape_html(
						visit.status
					)}</span>
				</div>
				<div class="mt-1 text-ink-gray-5">
					${frappe.utils.escape_html(visit.driver_name || "—")}
					· ${frappe.utils.escape_html(visit.visit_type)}
				</div>
				<div class="mt-1 text-ink-gray-5 truncate">
					${frappe.utils.escape_html(visit.material_type || visit.material_description || visit.party_name || "No material")}
				</div>
				<div class="flex flex-wrap gap-1.5 mt-2">${actions}</div>
			</article>
		`;
	}

	bind_actions() {
		this.page.main.find(".gatems-yard-action").on("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			const $btn = $(e.currentTarget);
			this.run_action($btn.data("visit"), $btn.data("action"));
		});
		this.page.main.find(".gatems-yard-card").on("click", (e) => {
			if ($(e.target).closest(".gatems-yard-action").length) {
				return;
			}
			frappe.set_route("Form", "Yard Visit", $(e.currentTarget).data("visit"));
		});
	}

	async run_action(visit, action) {
		let dock = null;
		let operation = null;
		if (action === "assign_dock") {
			dock = await this.pick_dock();
			if (!dock) {
				return;
			}
		}
		if (action === "start_operation") {
			const row = this.find_visit(visit);
			if (row && row.visit_type === "Both") {
				operation = await this.pick_operation();
				if (!operation) {
					return;
				}
			}
		}
		await frappe.call({
			method: "gatems.gatems.doctype.yard_visit.yard_visit.advance_visit",
			args: { visit, action, dock, operation },
			freeze: true,
		});
		frappe.show_alert({ message: __("Yard updated"), indicator: "green" });
		this.refresh();
	}

	find_visit(name) {
		const lists = [this.data.parked, this.data.on_dock, this.data.ready];
		for (const list of lists) {
			const row = (list || []).find((item) => item.name === name);
			if (row) {
				return row;
			}
		}
		return null;
	}

	pick_dock() {
		const docks = this.data.available_docks || [];
		if (!docks.length) {
			frappe.msgprint(__("No docks are available"));
			return Promise.resolve(null);
		}
		return new Promise((resolve) => {
			let done = false;
			const finish = (value) => {
				if (done) {
					return;
				}
				done = true;
				resolve(value);
			};
			const dialog = new frappe.ui.Dialog({
				title: __("Assign Dock"),
				fields: [
					{
						fieldname: "dock",
						label: __("Dock"),
						fieldtype: "Select",
						options: docks.map((d) => d.name).join("\n"),
						reqd: 1,
						default: docks[0].name,
					},
				],
				primary_action_label: __("Assign"),
				primary_action(values) {
					dialog.hide();
					finish(values.dock);
				},
			});
			dialog.onhide = () => finish(null);
			dialog.show();
		});
	}

	pick_operation() {
		return new Promise((resolve) => {
			let done = false;
			const finish = (value) => {
				if (done) {
					return;
				}
				done = true;
				resolve(value);
			};
			const dialog = new frappe.ui.Dialog({
				title: __("Start Operation"),
				fields: [
					{
						fieldname: "operation",
						label: __("Operation"),
						fieldtype: "Select",
						options: "Loading\nUnloading",
						reqd: 1,
					},
				],
				primary_action_label: __("Start"),
				primary_action(values) {
					dialog.hide();
					finish(values.operation);
				},
			});
			dialog.onhide = () => finish(null);
			dialog.show();
		});
	}

	open_checkin() {
		const dialog = new frappe.ui.Dialog({
			title: __("Vehicle Check In"),
			size: "large",
			fields: [
				{
					fieldname: "vehicle_source",
					label: __("Vehicle"),
					fieldtype: "Select",
					options: "Select from master\nNew vehicle",
					default: "Select from master",
					reqd: 1,
				},
				{
					fieldname: "vehicle",
					label: __("Registration"),
					fieldtype: "Link",
					options: "Vehicles",
					depends_on: 'eval:doc.vehicle_source=="Select from master"',
					mandatory_depends_on: 'eval:doc.vehicle_source=="Select from master"',
					get_query: () => ({ filters: { status: ["!=", "Blacklisted"] } }),
				},
				{
					fieldname: "registration_number",
					label: __("New Registration No"),
					fieldtype: "Data",
					depends_on: 'eval:doc.vehicle_source=="New vehicle"',
					mandatory_depends_on: 'eval:doc.vehicle_source=="New vehicle"',
				},
				{
					fieldname: "make",
					label: __("Make"),
					fieldtype: "Data",
					depends_on: 'eval:doc.vehicle_source=="New vehicle"',
					mandatory_depends_on: 'eval:doc.vehicle_source=="New vehicle"',
				},
				{
					fieldname: "model",
					label: __("Model"),
					fieldtype: "Data",
					depends_on: 'eval:doc.vehicle_source=="New vehicle"',
					mandatory_depends_on: 'eval:doc.vehicle_source=="New vehicle"',
				},
				{
					fieldname: "vehicle_type",
					label: __("Vehicle Type"),
					fieldtype: "Select",
					options: "\nTruck\nPickup / Tempo\nTanker\nVan\nOther",
					default: "Truck",
					depends_on: 'eval:doc.vehicle_source=="New vehicle"',
				},
				{ fieldtype: "Section Break", label: __("Driver") },
				{ fieldname: "driver_name", label: __("Driver Name"), fieldtype: "Data", reqd: 1 },
				{ fieldname: "driver_mobile", label: __("Driver Mobile"), fieldtype: "Data" },
				{ fieldtype: "Column Break" },
				{ fieldname: "driver_license_no", label: __("License No"), fieldtype: "Data" },
				{ fieldname: "transporter", label: __("Transporter"), fieldtype: "Data" },
				{ fieldtype: "Section Break", label: __("Material") },
				{
					fieldname: "visit_type",
					label: __("Visit Type"),
					fieldtype: "Select",
					options: "Loading\nUnloading\nBoth",
					default: "Unloading",
					reqd: 1,
				},
				{
					fieldname: "material_type",
					label: __("Material Type"),
					fieldtype: "Select",
					options:
						"\nFinished Goods\nRaw Material\nPackaging\nSpare Parts\nWaste / Return\nEmpty Vehicle\nOther",
				},
				{ fieldname: "party_name", label: __("Customer / Vendor"), fieldtype: "Data" },
				{ fieldtype: "Column Break" },
				{ fieldname: "quantity", label: __("Quantity"), fieldtype: "Float" },
				{ fieldname: "uom", label: __("UOM"), fieldtype: "Data" },
				{ fieldname: "reference_no", label: __("Invoice / PO / DN"), fieldtype: "Data" },
				{
					fieldname: "material_description",
					label: __("Material Description"),
					fieldtype: "Small Text",
				},
			],
			primary_action_label: __("Check In"),
			primary_action: async (values) => {
				const is_new = values.vehicle_source === "New vehicle" ? 1 : 0;
				await frappe.call({
					method: "gatems.gatems.doctype.yard_visit.yard_visit.check_in",
					args: { ...values, is_new_vehicle: is_new },
					freeze: true,
					freeze_message: __("Checking in"),
				});
				dialog.hide();
				frappe.show_alert({ message: __("Vehicle checked in and parked"), indicator: "green" });
				this.refresh();
			},
		});
		dialog.show();
	}
}

function kpi(label, value, tone) {
	const tones = {
		ink: "text-ink-base",
		amber: "text-ink-amber-7",
		cyan: "text-ink-cyan-7",
		green: "text-ink-green-7",
	};
	return `<div class="flex flex-col gap-0.5 rounded-xl border p-4 bg-surface-base">
		<em class="gatems-kpi-value ${tones[tone] || "text-ink-base"}">${value || 0}</em>
		<span class="text-ink-gray-5">${label}</span>
	</div>`;
}

function pill_class(status) {
	return (
		{
			parked: "bg-surface-amber-2 text-ink-amber-8",
			dock_assigned: "bg-surface-amber-2 text-ink-amber-8",
			on_dock: "bg-surface-cyan-2 text-ink-cyan-8",
			loading: "bg-surface-yellow-2 text-ink-yellow-8",
			unloading: "bg-surface-purple-2 text-ink-purple-8",
			ready_to_check_out: "bg-surface-green-2 text-ink-green-8",
		}[frappe.scrub(status || "")] || "bg-surface-gray-2 text-ink-gray-7"
	);
}

function action_label(action) {
	return (
		{
			assign_dock: __("Assign Dock"),
			start_operation: __("Start Load/Unload"),
			stop_operation: __("Stop"),
			dock_out: __("Dock Out"),
			check_out: __("Check Out"),
		}[action] || action
	);
}
