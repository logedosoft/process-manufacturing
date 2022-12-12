// Copyright (c) 2018, earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on('Process Order', {
	setup: function (frm) {
		frm.set_query("workstation", function () {
			return {
				filters: {"department": frm.doc.department}
			}
		});
		frm.set_query("process_name", function () {
			return {
				filters: {"department": frm.doc.department, "process_type": frm.doc.process_type}
			}
		});
	},
	refresh: function(frm){
		if(!frm.doc.__islocal && frm.doc.status == 'Submitted'){
			var start_btn = frm.add_custom_button(__('Start'), function(){
				prompt_for_qty(frm, "materials", "Enter Raw Material Quantity", true, function () {
					process_production(frm, "Submitted");
				});
			});
			start_btn.addClass('btn-primary');
		}
		if(!frm.doc.__islocal && frm.doc.status == 'In Process'){
			var finish_btn = frm.add_custom_button(__('Complete'), function(){
				prompt_for_qty(frm, "finished_products", "Enter Produced Quantity", true, function () {
					if(frm.doc.scrap){
						prompt_for_qty(frm, "scrap", "Enter Scrap Quantity", false, function() {
							prompt_for_hours(frm, function() {
								process_production(frm, "In Process");
							});
						});
					}else {
						prompt_for_hours(frm, function() {
							process_production(frm, "In Process");
						});
					}
				});
			});
			finish_btn.addClass('btn-primary')
		}
	},
	before_save: function(frm) {
		if (!frm.doc.wip_warehouse || frm.doc.wip_warehouse.length == 0) {
			//Sometimes, somehow warehouse info is erased. We will recover it here :)
			set_warehouse_info(frm);
		}
	},
	department: function(frm){
		if(frm.doc.department){
			frappe.call({
				"method": "frappe.client.get",
				args: {
					doctype: "Manufacturing Department",
					name: frm.doc.department
				},
				callback: function (data) {
					frappe.model.set_value(frm.doctype,frm.docname, "wip_warehouse", data.message.wip_warehouse);
					frappe.model.set_value(frm.doctype,frm.docname, "fg_warehouse", data.message.fg_warehouse);
					frappe.model.set_value(frm.doctype,frm.docname, "scrap_warehouse", data.message.scrap_warehouse);
					frappe.model.set_value(frm.doctype,frm.docname, "src_warehouse", data.message.src_warehouse);
				}
			});
		}
	},
	process_name: function(frm) {
		if(frm.doc.process_name){
			set_warehouse_info(frm);
		}
	}
});

var set_warehouse_info = function(frm) {
	frappe.call({
		doc: frm.doc,
		method: "get_process_details",
		callback: function(r) {
			refresh_field("costing_method");
			refresh_field("finished_products");
			refresh_field("scrap");
			refresh_field("materials");
		}
	});
}

var prompt_for_qty = function (frm, table, title, qty_required, callback) {
	// if(table && !qty_required){
	// 	callback();
	// }
	let fields = [];
	let strLabel = "";

	$.each(frm.doc[table] || [], function(i, row) {
		if (table == "materials") {
			strLabel = __("Quality:{0}", [row.item])
		} else if (table == "finished_products") {
			strLabel = __("Reference: {0}", [row.item_reference_name])
		}

		fields.push({
			fieldtype: "Float",
			label: strLabel,//__(strLabel, [row.item_reference_name, row.item]),
			fieldname: row.name
			//value: row.quantity //value is ignored
		});
	})
	frappe.prompt(
		fields,
		function(data) {
			let item_qty = false;
			frm.doc[table].forEach(function(line) {
				if(data[line.name] > 0) { item_qty = true; }
				frappe.model.set_value(line.doctype, line.name, "quantity", flt(line.quantity) + flt(data[line.name]));
				//SavePOTimeLog(frm, data);
			});
			if (qty_required && !item_qty){
				frappe.throw(__("Cannot start/finish Process Order with zero quantity"));
			}
			callback();
		},
		__(title),
		__("Confirm")
	);
}

function SavePOTimeLog(frm, data) {
	//This will create a time log the po
	console.log("SavePOTimeLog(frm, data) started");
	let rowTimeLog;
	debugger;
	const docPOTimeLog = frappe.model.get_new_doc('Process Order Time Log');
	console.log(docPOTimeLog);
	docPOTimeLog.po_name = frm.doc.process_name;//'PO-00003';
	docPOTimeLog.workstation = frm.doc.workstation;//"Lazer-2";
	rowTimeLog = frappe.model.add_child(docPOTimeLog, 'Process Order Time Log Detail', 'po_time_log_detail');
	rowTimeLog.item = 'LZ.3237';
	rowTimeLog.thickness = 1;
	rowTimeLog.item_reference_name = "ASD";
	rowTimeLog.quantity = 22;
    /*docPOTimeLog.append("po_time_log_detail", {
		'item': 'LZ.3237',
		'thickness': 1,
		'item_reference_name': 'asd',
		'quantity': 99
	});*/
    
	frappe.db.insert(docPOTimeLog).then(function(docNewPOTimeLog) { 
       console.log(`${docNewPOTimeLog.doctype} ${docNewPOTimeLog.name} created on ${docNewPOTimeLog.creation}`);
    });

	/*
                        $.each(r.message, function(i, item) {
                            var d = frappe.model.add_child(cur_frm.doc, "Material Request Item", "items");
                            d.item_code = item.item_code;
                            d.item_name = item.item_name;
                            d.description = item.description;
                            d.warehouse = values.warehouse;
                            d.uom = item.stock_uom;
                            d.stock_uom = item.stock_uom;
                            d.conversion_factor = 1;
                            d.qty = item.qty;
                            d.project = item.project;
                        });
						*/
}

var prompt_for_hours = function(frm, callback){
	//TODO datetime diff returns 0 for minutes
	let hours = frappe.datetime.get_hour_diff(frappe.datetime.now_datetime(), frm.doc.start_dt)
	frappe.prompt(
		[{fieldtype: "Float",
			label: __("Hours"),
			fieldname: "hours",
			description: __("Hours as per start of process is {0}", [hours]),
		}],
		function(data) {
			let item_qty = false;
			frappe.model.set_value(frm.doctype, frm.doc.name, "operation_hours", data.hours);
			callback();
		},
		__("Update hours of operation"),
		__("Confirm")
	);
}

var process_production = function (frm, status) {
	frappe.call({
		doc: frm.doc,
		method: "start_finish_processing",
		args:{
			"status": status
		},
		callback: function(r) {
			if (r.message){
				var doclist = frappe.model.sync(r.message);
				console.log(doclist);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		}
	});
}
