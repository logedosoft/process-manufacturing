frappe.pages['test2'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Test-2',
		single_column: true
	});
}