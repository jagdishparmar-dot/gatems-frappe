# Copyright (c) 2026, GateMS and contributors
# For license information, please see license.txt

import json
import math

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


DEMO_ROUTES = {
	"MH12AB1234": {
		"location_names": ["Bandra West", "BKC", "Kurla", "Andheri East", "Juhu", "Santacruz"],
		"route": [
			(19.0596, 72.8295),
			(19.0660, 72.8500),
			(19.0728, 72.8697),
			(19.0860, 72.8880),
			(19.1136, 72.8697),
			(19.1197, 72.8464),
			(19.0810, 72.8410),
			(19.0596, 72.8295),
		],
	},
	"DL01CA4321": {
		"location_names": ["Connaught Place", "India Gate", "Khan Market", "Lodhi Garden"],
		"route": [
			(28.6315, 77.2167),
			(28.6129, 77.2295),
			(28.6006, 77.2270),
			(28.5931, 77.2197),
			(28.6127, 77.2090),
			(28.6315, 77.2167),
		],
	},
	"KA03MG2468": {
		"location_names": ["MG Road", "Indiranagar", "Koramangala", "Silk Board"],
		"route": [
			(12.9758, 77.6045),
			(12.9784, 77.6408),
			(12.9352, 77.6245),
			(12.9171, 77.6226),
			(12.9592, 77.6100),
			(12.9758, 77.6045),
		],
	},
}


def point_geojson(latitude: float, longitude: float) -> str:
	return json.dumps(
		{
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"properties": {},
					"geometry": {"type": "Point", "coordinates": [flt(longitude), flt(latitude)]},
				}
			],
		}
	)


def interpolate(start, end, t: float):
	lat = start[0] + (end[0] - start[0]) * t
	lng = start[1] + (end[1] - start[1]) * t
	return lat, lng


def bearing(start, end) -> float:
	lat1, lat2 = math.radians(start[0]), math.radians(end[0])
	dlon = math.radians(end[1] - start[1])
	x = math.sin(dlon) * math.cos(lat2)
	y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
	return (math.degrees(math.atan2(x, y)) + 360) % 360


def point_along_route(route, progress: float):
	progress = progress % 1.0
	segment_count = len(route) - 1
	if segment_count <= 0:
		return route[0], 0.0, 0
	scaled = progress * segment_count
	index = min(int(scaled), segment_count - 1)
	t = scaled - index
	position = interpolate(route[index], route[index + 1], t)
	return position, bearing(route[index], route[index + 1]), index


class VehicleLiveTrack(Document):
	def before_validate(self):
		self.geolocation = point_geojson(self.latitude, self.longitude)
		if not self.last_ping:
			self.last_ping = now_datetime()


@frappe.whitelist()
def get_fleet_positions():
	tick_demo_vehicles()
	return frappe.get_all(
		"Vehicle Live Track",
		fields=[
			"name",
			"vehicle",
			"make",
			"model",
			"status",
			"latitude",
			"longitude",
			"location_name",
			"speed_kmph",
			"heading",
			"ignition",
			"last_ping",
			"is_demo",
		],
		order_by="vehicle",
	)


def tick_demo_vehicles():
	tracks = frappe.get_all("Vehicle Live Track", filters={"is_demo": 1}, pluck="name")
	for name in tracks:
		doc = frappe.get_doc("Vehicle Live Track", name)
		config = DEMO_ROUTES.get(doc.vehicle)
		if not config:
			continue
		progress = (flt(doc.demo_progress) + 0.012) % 1.0
		(lat, lng), heading, index = point_along_route(config["route"], progress)
		names = config.get("location_names") or []
		doc.demo_progress = progress
		doc.latitude = lat
		doc.longitude = lng
		doc.heading = heading
		doc.speed_kmph = 32 + (index % 4) * 6
		doc.status = "Moving"
		doc.ignition = 1
		doc.last_ping = now_datetime()
		if names:
			doc.location_name = names[index % len(names)]
		doc.geolocation = point_geojson(lat, lng)
		doc.save(ignore_permissions=True)
	if tracks:
		frappe.db.commit()
