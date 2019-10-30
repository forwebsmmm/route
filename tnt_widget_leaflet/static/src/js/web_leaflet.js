odoo.define('web_widget_leaflet', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');
    var widgetRegistry = require('web.widget_registry');

    var map_data = {};

    /* leaflet_marker */
    var LeafletMarker = Widget.extend({
        template: 'leaflet_marker',

        init: function (view, record, node) {
            this._super(view, record, node);
            this.field_lat = node.attrs.lat;
            this.field_lng = node.attrs.lng;
            this.field_str = node.attrs.str;
            this.field_mapid = node.attrs.mapid;
            this.shown = $.Deferred();
            this.data = record.data;
            this.mode = view.mode || 'readonly';
            this.record = record;
            this.view = view;
            var self = this;

            /*
            self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['google_maps_api_key']
                }).then(function (key) {
                    self.google_maps_api_key = key;
                    $.getScript('https://maps.googleapis.com/maps/api/js?callback=ginit&key=' + self.google_maps_api_key);
            });
            */
        },

        start: function() {
            var self = this;
            if (typeof L == 'undefined') {
                window.ginit = this.on_ready;
                // maps.google.com/maps/api/js?key=#{google_maps_api_key}
                // $.getScript('http://maps.googleapis.com/maps/api/js?sensor=false&callback=ginit');
            }
            else {
                setTimeout(function () { self.on_ready(); }, 1000);
            }
            return this._super();
        },

        on_ready: function(){
            var lat = this.data[this.field_lat];
            var lng = this.data[this.field_lng];
            var str = this.data[this.field_str];

            var div_map = this.$el[0];

            map_data.map = L.map(div_map).setView([lat, lng], 10);
            L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                maxZoom: 18,
                id: 'mapbox.streets',
                accessToken: 'pk.eyJ1IjoiZGltZ3VubmVyIiwiYSI6ImNrMHV2b3l5ZTBxYmYzb3FyZjMyNWViZWQifQ.UYReY5yOa8p-cbbt6SjdXQ'
            }).addTo(map_data.map);
            map_data.marker = L.marker([lat, lng]).addTo(map_data.map);
            map_data.marker.bindPopup(str).openPopup();

            /*
            map_data.map = L.map(mapid).setView([lat, lng], 16);
            if (typeof map_data.map == 'undefined') {
            }
            else {
                map_data.map.panTo([lat, lng], 16);
                map_data.marker.setLatLng([lat, lng]);
            }
            */

            /*
            this.view.on("field_changed:"+this.field_lat, this, this.display_result);
            this.view.on("field_changed:"+this.field_lng, this, this.display_result);
            */

            /*
            google.maps.event.trigger( map, 'resize')
            */
        },
    });

    core.form_custom_registry.add('leaflet_marker', LeafletMarker);
    widgetRegistry.add('leaflet_marker', LeafletMarker);
 
    /* leaflet_monitor */
    var monitor_data = {};
    var LeafletMonitor = Widget.extend({
        template: 'leaflet_monitor',

        init: function (view, record, node) {
            this._super(view, record, node);

            this.shown = $.Deferred();
            this.data = record.data;
            this.mode = view.mode || 'readonly';
            this.record = record;
            this.view = view;

            var self = this;

            this.map_data = {
                markers: [],
                polylines: [],
            };

            this.field_ids = node.attrs.ids;
            this.field_from = node.attrs.ts_from;
            this.field_to = node.attrs.ts_to;
        },

        start: function() {
            var self = this;
            if (typeof L == 'undefined') {
                window.ginit = this.on_ready;
            }
            else {
                setTimeout(function () { self.on_ready(); }, 1000);
            }
            return this._super();
        },

        destroy: function(){
            clearInterval(this.map_data.interval);
            return this._super();
        },

        init_map: function(){
            this.map_data.map = L.map(this.$el[0]).setView([51.505, -0.09], 13);
            L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                maxZoom: 18,
                id: 'mapbox.streets',
                accessToken: 'pk.eyJ1IjoiZGltZ3VubmVyIiwiYSI6ImNrMHV2b3l5ZTBxYmYzb3FyZjMyNWViZWQifQ.UYReY5yOa8p-cbbt6SjdXQ'
            }).addTo(this.map_data.map);
        },

        update_map: function(fit_bounds){
            var self = this;

            var params = {
                ids: [],
                ts_from: this.data[this.field_from],
                ts_to: this.data[this.field_to],
            };

            $(this.data[this.field_ids].data).each(function() {
                params.ids.push((this).data.id);
            });

            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: '/flespi/monitor',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': params,
                }),
                success: function (data) {
                    var b = [],
                        markers = [],
                        polylines = [];

                    $(data.result).each(function(i, e) {
                        b.push([e.pos_lat, e.pos_lon]);

                        var t = [];
                        $(e.data).each(function(i, e) {
                            b.push([e.pos_lat, e.pos_lon]);
                            t.push([e.pos_lat, e.pos_lon]);
                        });

                        markers.push({
                            'name': e.name,
                            'marker': L.marker([
                                e.pos_lat,
                                e.pos_lon
                            ]),
                            'polyline': L.polyline(t, {color: 'blue'}),
                        });
                    });

                    // remove old markers
                    $(self.map_data.markers).each(function(i, e) {
                        self.map_data.map.removeLayer(e.marker);
                        polylines.push(e.polyline);
                    });

                    self.map_data.markers = markers;

                    // add new markers & polylines
                    $(self.map_data.markers).each(function(i, e) {
                        e.marker.addTo(self.map_data.map).bindPopup(e.name);  // .openPopup()
                        e.polyline.addTo(self.map_data.map);
                    });

                    // remove old polylines
                    $(polylines).each(function(i, e) {
                        self.map_data.map.removeLayer(e);
                    });

                    if (fit_bounds && (b.length > 0)) {
                        self.map_data.map.fitBounds(b);
                    }
                },
            });
        },

        on_ready: function(){
            var self = this;

            if (typeof this.map_data.map == 'undefined') {
                this.init_map();
            }

            self.update_map(true);

            this.map_data.interval = setInterval(function() {
                self.update_map();
            }, 10000);
        },
    });

    core.form_custom_registry.add('leaflet_monitor', LeafletMonitor);
    widgetRegistry.add('leaflet_monitor', LeafletMonitor);

    return {
        leaflet_marker: LeafletMarker,
        leaflet_monitor: LeafletMonitor,
    };
});
