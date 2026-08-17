frappe.pages["fleet-tracker"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Fleet Tracker"),
		single_column: true,
	});
	if (frappe.gatems_fleet) {
		frappe.gatems_fleet.destroy();
	}
	frappe.gatems_fleet = new GateMSFleetTracker(page);
};

frappe.pages["fleet-tracker"].on_page_show = function () {
	if (frappe.gatems_fleet) {
		frappe.gatems_fleet.refresh();
	}
};

class GateMSFleetTracker {
	constructor(page) {
		this.page = page;
		this.markers = {};
		this.selected = null;
		this.timer = null;
		this.refreshing = false;
		this.make();
		this.bind_realtime();
		this.refresh();
	}

	make() {
		this.page.set_primary_action(__("Refresh"), () => this.refresh(true));
		this.page.add_inner_button(__("Vehicle Live Track"), () => {
			frappe.set_route("List", "Vehicle Live Track");
		});
		this.page.add_inner_button(__("Vehicles"), () => {
			frappe.set_route("List", "Vehicles");
		});

		this.page.main.append(`
			<div class="gatems-fleet flex overflow-hidden rounded-xl border bg-surface-base shadow-sm">
				<div class="gatems-fleet-sidebar flex flex-col shrink-0 border-e">
					<div class="flex items-center gap-2 px-4 py-3 border-b">
						<span class="gatems-live-dot shrink-0"></span>
						${__("Live")}
						<span id="gatems-fleet-meta" class="ms-auto text-ink-gray-5"></span>
					</div>
					<div id="gatems-fleet-list" class="gatems-fleet-list flex flex-col gap-2 p-2.5"></div>
				</div>
				<div id="gatems-fleet-map" class="gatems-fleet-map flex-1 min-w-0"></div>
			</div>
		`);
		this.$map = this.page.main.find("#gatems-fleet-map");
		this.$list = this.page.main.find("#gatems-fleet-list");
		this.$meta = this.page.main.find("#gatems-fleet-meta");
	}

	async refresh(manual = false) {
		if (this.refreshing) {
			this.schedule();
			return;
		}
		this.refreshing = true;
		try {
			await frappe.require(["leaflet.bundle.js", "leaflet.bundle.css"]);
			if (!this.map) {
				this.init_map();
			}
			const r = await frappe.call({
				method: "gatems.gatems.doctype.vehicle_live_track.vehicle_live_track.get_fleet_positions",
				freeze: manual,
				freeze_message: __("Updating live positions"),
			});
			this.vehicles = r.message || [];
			this.render_list();
			this.render_markers();
			this.$meta.text(
				__("{0} vehicles · last update {1}", [this.vehicles.length, frappe.datetime.now_time()])
			);
		} catch (e) {
			console.error("Fleet Tracker refresh failed", e);
		} finally {
			this.refreshing = false;
			this.schedule();
		}
	}

	bind_realtime() {
		this._on_fleet = () => {
			if (this.is_current()) {
				this.refresh();
			}
		};
		if (frappe.realtime) {
			frappe.realtime.on("gatems:fleet_update", this._on_fleet);
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
		if (frappe.realtime && this._on_fleet) {
			frappe.realtime.off("gatems:fleet_update", this._on_fleet);
		}
		if (this._on_visible) {
			document.removeEventListener("visibilitychange", this._on_visible);
		}
	}

	is_current() {
		return (frappe.get_route_str() || "") === "fleet-tracker";
	}

	stop_timer() {
		if (this.timer) {
			clearTimeout(this.timer);
			this.timer = null;
		}
	}

	init_map() {
		this.map = L.map(this.$map.get(0), { zoomControl: true }).setView([20.5937, 78.9629], 5);
		L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			maxZoom: 19,
			attribution: "&copy; OpenStreetMap",
		}).addTo(this.map);
		setTimeout(() => this.map.invalidateSize(), 200);
	}

	render_list() {
		const html = this.vehicles
			.map((v) => {
				const active = this.selected === v.vehicle ? "is-active" : "";
				return `<button type="button" class="gatems-fleet-card flex flex-col gap-1 rounded-lg border p-2.5 bg-surface-gray-1 cursor-pointer w-full text-left ${active}" data-vehicle="${frappe.utils.escape_html(
					v.vehicle
				)}">
					<div class="flex justify-between items-center gap-2">
						<strong class="text-ink-base">${frappe.utils.escape_html(v.vehicle)}</strong>
						<span class="rounded-full px-2 py-0.5 ${pill_class(v.status)}">${frappe.utils.escape_html(
							v.status || "Idle"
						)}</span>
					</div>
					<div class="text-ink-gray-5">${frappe.utils.escape_html(
						[v.make, v.model].filter(Boolean).join(" ") || __("Vehicle")
					)}</div>
					<div class="flex justify-between gap-2 text-ink-gray-5">
						<span>${flt(v.speed_kmph, 0)} km/h</span>
						<span class="truncate">${frappe.utils.escape_html(v.location_name || __("Updating location"))}</span>
					</div>
				</button>`;
			})
			.join("");
		this.$list.html(html || `<div class="text-ink-gray-5 p-4 text-center">${__("No live vehicles yet")}</div>`);
		this.$list.find(".gatems-fleet-card").on("click", (e) => {
			this.focus($(e.currentTarget).data("vehicle"));
		});
	}

	render_markers() {
		const bounds = [];
		this.vehicles.forEach((v) => {
			if (!(v.latitude && v.longitude)) {
				return;
			}
			const latlng = [v.latitude, v.longitude];
			bounds.push(latlng);
			const html = `<div class="gatems-marker gatems-marker-${(v.status || "Idle").toLowerCase()}" style="transform: rotate(${
				v.heading || 0
			}deg)">➤</div>`;
			const icon = L.divIcon({
				className: "gatems-marker-wrap",
				html,
				iconSize: [28, 28],
				iconAnchor: [14, 14],
			});
			if (this.markers[v.vehicle]) {
				this.markers[v.vehicle].setLatLng(latlng);
				this.markers[v.vehicle].setIcon(icon);
				this.markers[v.vehicle].setPopupContent(this.popup_html(v));
			} else {
				this.markers[v.vehicle] = L.marker(latlng, { icon })
					.addTo(this.map)
					.bindPopup(this.popup_html(v));
			}
		});
		if (!this.fitted && bounds.length) {
			this.map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
			this.fitted = true;
		}
	}

	popup_html(v) {
		return `<div class="flex flex-col gap-1">
			<strong class="text-ink-base">${frappe.utils.escape_html(v.vehicle)}</strong>
			<span class="text-ink-gray-5">${frappe.utils.escape_html([v.make, v.model].filter(Boolean).join(" "))}</span>
			<span>${__("Speed")}: ${flt(v.speed_kmph, 1)} km/h</span>
			<span>${__("Status")}: ${frappe.utils.escape_html(v.status || "")}</span>
			<span class="text-ink-gray-5">${frappe.utils.escape_html(v.location_name || "")}</span>
		</div>`;
	}

	focus(vehicle) {
		this.selected = vehicle;
		this.render_list();
		const marker = this.markers[vehicle];
		if (marker) {
			this.map.setView(marker.getLatLng(), 14);
			marker.openPopup();
		}
	}

	schedule() {
		this.stop_timer();
		if (document.hidden) {
			return;
		}
		this.timer = setTimeout(() => this.refresh(), 4000);
	}
}

function pill_class(status) {
	return (
		{
			moving: "bg-surface-green-2 text-ink-green-8",
			idle: "bg-surface-amber-2 text-ink-amber-8",
			stopped: "bg-surface-red-2 text-ink-red-8",
			offline: "bg-surface-red-2 text-ink-red-8",
		}[String(status || "idle").toLowerCase()] || "bg-surface-gray-2 text-ink-gray-7"
	);
}
