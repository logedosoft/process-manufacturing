# -*- coding: utf-8 -*-
# Copyright (c) 2018, earthians and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext import get_default_company

class ProcessDefinition(Document):
	@frappe.whitelist()
	def get_open_sales_orders(self):
		""" Pull sales orders  which are pending to deliver based on criteria selected"""
		if self.ld_item_code:
			open_so = self.get_sales_orders()

			if open_so:
				self.add_so_in_table(open_so)
				#prepare raw materials
				print("TS" + self.ld_item_code[self.ld_item_code.find('.'):])
				self.set('materials', [])

				self.append('materials', {
					'item': "TS" + self.ld_item_code[self.ld_item_code.find('.'):]
				})
			else:
				frappe.msgprint(_("Sales orders are not available for production"))
		else:
			frappe.msgprint(_("Please select an item!"))

	def get_sales_orders(self):
		so_filter = item_filter = ""

		"""date_field_mapper = {
			'from_date': ('>=', 'so.transaction_date'),
			'to_date': ('<=', 'so.transaction_date'),
			'from_delivery_date': ('>=', 'so_item.delivery_date'),
			'to_delivery_date': ('<=', 'so_item.delivery_date')
		}

		for field, value in date_field_mapper.items():
			if self.get(field):
				so_filter += f" and {value[1]} {value[0]} %({field})s"

		for field in ['customer', 'project', 'sales_order_status']:
			if self.get(field):
				so_field = 'status' if field == 'sales_order_status' else field
				so_filter += f" and so.{so_field} = %({field})s" """

		if self.ld_item_code and frappe.db.exists('Item', self.ld_item_code):
			item_filter += " and so_item.item_code = %(item_code)s"

		if self.get("ld_customer"):
			so_filter += " and so.customer = %(customer)s"

		if self.get("ld_thickness"):
			so_filter += " and so_item.ld_kalinlik = %(thickness)s"

		open_so = frappe.db.sql(f"""
			select
				distinct so.name, so_item.name as so_item_name, so.transaction_date, so.customer, so.base_grand_total,
				so_item.item_code, so_item.ld_musteri_urun_adi, so_item.qty, so_item.ld_kalinlik as thickness, 
				so_item.uom, so_item.delivery_date, so_item.ld_rota,
				SUM(IFNULL(pdso.qty, 0)) AS pdso_qty, so_item.qty - SUM(IFNULL(pdso.qty, 0)) as req_qty
			from
				`tabSales Order` so
				INNER JOIN `tabSales Order Item` so_item ON so_item.parent = so.name AND so_item.parentfield = 'items'
				LEFT JOIN `tabProcess Definition Sales Order Details` pdso ON pdso.so_detail = so_item.name AND pdso.docstatus < 2
			where
				so_item.parent = so.name
				and so.docstatus = 1 and so.status not in ("Stopped", "Closed")
				and so.company = %(company)s
				{so_filter} {item_filter}
			GROUP BY
				so.name, so_item.name, so.transaction_date, so.customer, so.base_grand_total,
				so_item.item_code, so_item.ld_musteri_urun_adi, so_item.qty, so_item.ld_kalinlik, 
				so_item.uom, so_item.delivery_date, so_item.ld_rota
			HAVING
				so_item.qty > SUM(IFNULL(pdso.qty, 0))
			""", {
				"company": get_default_company(),
				"customer": self.ld_customer,
				"item_code": self.ld_item_code,
				"thickness": self.ld_thickness
			}, as_dict=1)

		return open_so

	def add_so_in_table(self, open_so):
		""" Add sales orders in the table"""
		self.set('ld_sales_order_items', []) #Silmeden ekleme yapmak icin kaldirildi

		for data in open_so:
			self.append('ld_sales_order_items', {
				'sales_order': data.name,
				'so_detail': data.so_item_name,
				'sales_order_date': data.transaction_date,
				'customer': data.customer,
				'item': data.item_code,
				'item_reference_name': data.ld_musteri_urun_adi,
				'qty': data.qty,
				'thickness': data.thickness,
				'uom': data.uom,
				'due_date': data.delivery_date,
				'route': data.ld_rota
			})

	def before_save(self):
		self.set("finished_products", [])
		for item in self.ld_sales_order_items:
			blnItemFound = False
			for fg_item in self.finished_products:
				if fg_item.item == item.item:
					blnItemFound = True
					fg_item.quantity += item.qty

   			#Add new line if item not found
			if blnItemFound == False:
				fg_item = self.append("finished_products", {})
				fg_item.item = item.item
				fg_item.quantity = item.qty
    
	def validate(self):
		if len(self.ld_sales_order_items) > 0:
			flThickness = self.ld_sales_order_items[0].thickness
			strItem = self.ld_sales_order_items[0].item
			for item in self.ld_sales_order_items:
				if item.thickness != flThickness:
					frappe.throw(_("Thickness should be same for all sales orders!"))
				if item.item != strItem:
					frappe.throw(_("Quality should be same for all sales orders."))