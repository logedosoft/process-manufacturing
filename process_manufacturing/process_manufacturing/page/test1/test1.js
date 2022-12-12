frappe.pages['test1'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Test-1',
		single_column: true
	});
}