/*LOGEODOSOFT 2022*/

frappe.ui.form.on("Stock Entry", {
	refresh: (frm) => {
		frm.set_query('batch_no', 'items', function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			if (in_list(["Material Transfer for Manufacture", "Manufacture", "Repack", "Send to Subcontractor"], doc.purpose)) {
				var filters = {
					'item_code': row.item_code,
					'posting_date': frm.doc.posting_date || frappe.datetime.nowdate(),
					'thickness': row.ld_thickness,
					'width': row.ld_width,
					'length': row.ld_length
				}
			} else {
				var filters = {
					'item_code': row.item_code,
					'thickness': row.ld_thickness,
					'width': row.ld_width,
					'length': row.ld_length
				}
			}
			return {
				//query : "erpnext.controllers.queries.get_batch_no",
				query : "jetlazer.jl_utils.get_batch_no",
				filters: filters
			}
		});
		/*frm.fields_dict['items'].grid.get_field('batch_no').get_query = function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {    
				filters:[
					['item', '=', row.item_code],
					['ld_thickness', '=', row.ld_thickness],
					['ld_width', '=', row.ld_width],
					['ld_length', '=', row.ld_length]
				]
			}
		}*/
		/*frm.set_query("batch_no", "items", function(doc, cdt, cdn) {
			console.log(doc);
			console.log(cdt);
			console.log(cdn);
			return {
				"filters" : {"ld_thickness" : "10"}
			}
		});*/
	}
});