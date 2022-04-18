// Copyright (c) 2018, earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on('Process Definition', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Process Order'),
				function() {
					frappe.model.with_doctype('Process Order', function() {
						var doc = frappe.model.get_new_doc('Process Order');
						doc.department = frm.doc.department;
						doc.process_type = frm.doc.process_type;
						doc.process_name = frm.doc.name;
						doc.workstation = frm.doc.workstation;
						doc.ld_cnc = frm.doc.ld_cnc;
						/*var row = frappe.model.add_child(doc, 'items');
						row.item_code = dialog.get_value('item_code');
						row.f_warehouse = dialog.get_value('target');
						row.t_warehouse = dialog.get_value('target');
						row.qty = dialog.get_value('qty');
						row.conversion_factor = 1;
						row.transfer_qty = dialog.get_value('qty');
						row.basic_rate = dialog.get_value('rate');*/
						frappe.set_route('Form', doc.doctype, doc.name);
					  })
				},
				__('Create'));
			frm.page.set_inner_btn_group_as_primary(__('Create'));
		}
	},
	ld_get_sales_order_items: function(frm) {
		frappe.call({
			method: "get_open_sales_orders",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("ld_sales_order_items");
				refresh_field("materials");
			}
		});
	},
	setup: function (frm) {
		frm.set_query("workstation", function () {
			return {
				filters: {"department": frm.doc.department}
			}
		});
		frm.set_query("ld_item_code", function () {
			return {
				filters: {"item_group": 'Mamul'}
			}
		});
	},
	before_save: function(frm) {

	}
});
