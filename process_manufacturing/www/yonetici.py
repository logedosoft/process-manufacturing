# -*- coding: utf-8 -*-
# LOGEDOSOFT

from __future__ import unicode_literals
import frappe, json
from frappe import msgprint, _
#from six import string_types, iteritems

no_cache = 1

def get_context(context):

	filters = dict(company='Yonca Tekstil')

	data = frappe.db.sql(
	"""
SELECT FORMAT(IFNULL(SUM(PAYMENT_ENTRY.paid_amount), 0), 2, 'tr_TR') AS TUTAR, 0 AS MIKTAR, 'GUNLUK_TAHSILAT' AS TIP
FROM
	`tabPayment Entry` PAYMENT_ENTRY
WHERE
	PAYMENT_ENTRY.docstatus = 1 
	AND PAYMENT_ENTRY.company = 'Yonca Tekstil'
	AND PAYMENT_ENTRY.posting_date = CURDATE()
	
UNION ALL

SELECT FORMAT(IFNULL(SUM(PAYMENT_ENTRY.paid_amount), 0), 2, 'tr_TR'), 0 AS MIKTAR, 'HAFTALIK_TAHSILAT'
FROM
	`tabPayment Entry` PAYMENT_ENTRY
WHERE
	PAYMENT_ENTRY.docstatus = 1 
	AND PAYMENT_ENTRY.company = 'Yonca Tekstil'
	AND WEEK(PAYMENT_ENTRY.posting_date, 3) = WEEK(CURDATE(), 3)
	
UNION ALL

SELECT FORMAT(IFNULL(SUM(PAYMENT_ENTRY.paid_amount), 0), 2, 'tr_TR'), 0 AS MIKTAR, 'AYLIK_TAHSILAT'
FROM
	`tabPayment Entry` PAYMENT_ENTRY
WHERE
	PAYMENT_ENTRY.docstatus = 1 
	AND PAYMENT_ENTRY.company = 'Yonca Tekstil'
	AND MONTH(PAYMENT_ENTRY.posting_date) = MONTH(CURDATE())

UNION ALL

SELECT FORMAT(IFNULL(SUM(PAYMENT_ENTRY.paid_amount), 0), 2, 'tr_TR'), 0 AS MIKTAR, 'YILLIK_TAHSILAT'
FROM
	`tabPayment Entry` PAYMENT_ENTRY
WHERE
	PAYMENT_ENTRY.docstatus = 1 
	AND PAYMENT_ENTRY.company = 'Yonca Tekstil'
	AND YEAR(PAYMENT_ENTRY.posting_date) = YEAR(CURDATE())

UNION ALL 

SELECT FORMAT(IFNULL(SUM(DELIVERY_NOTE.net_total), 0), 2, 'tr_TR') AS SEVKIYAT_TUTARI, FORMAT(IFNULL(SUM(DELIVERY_NOTE.total_qty), 0), 2, 'tr_TR') AS SEVKIYAT_MIKTARI, 'GUNLUK_SEVKIYAT'
FROM
	`tabDelivery Note` DELIVERY_NOTE
WHERE
	DELIVERY_NOTE.docstatus = 1 
	AND DELIVERY_NOTE.company = 'Yonca Tekstil'
	AND DELIVERY_NOTE.posting_date = CURDATE()

UNION ALL 

SELECT FORMAT(IFNULL(SUM(DELIVERY_NOTE.net_total), 0), 2, 'tr_TR') AS SEVKIYAT_TUTARI, FORMAT(IFNULL(SUM(DELIVERY_NOTE.total_qty), 0), 2, 'tr_TR') AS SEVKIYAT_MIKTARI, 'HAFTALIK_SEVKIYAT'
FROM
	`tabDelivery Note` DELIVERY_NOTE
WHERE
	DELIVERY_NOTE.docstatus = 1 
	AND DELIVERY_NOTE.company = 'Yonca Tekstil'
	AND WEEK(DELIVERY_NOTE.posting_date, 3) = WEEK(CURDATE(), 3)
	
UNION ALL 

SELECT FORMAT(IFNULL(SUM(DELIVERY_NOTE.net_total), 0), 2, 'tr_TR') AS SEVKIYAT_TUTARI, FORMAT(IFNULL(SUM(DELIVERY_NOTE.total_qty), 0), 2, 'tr_TR') AS SEVKIYAT_MIKTARI, 'AYLIK_SEVKIYAT'
FROM
	`tabDelivery Note` DELIVERY_NOTE
WHERE
	DELIVERY_NOTE.docstatus = 1 
	AND DELIVERY_NOTE.company = 'Yonca Tekstil'
	AND MONTH(DELIVERY_NOTE.posting_date) = MONTH(CURDATE())
	
UNION ALL 

SELECT FORMAT(IFNULL(SUM(DELIVERY_NOTE.net_total), 0), 2, 'tr_TR') AS SEVKIYAT_TUTARI, FORMAT(IFNULL(SUM(DELIVERY_NOTE.total_qty), 0), 2, 'tr_TR') AS SEVKIYAT_MIKTARI, 'YILLIK_SEVKIYAT'
FROM
	`tabDelivery Note` DELIVERY_NOTE
WHERE
	DELIVERY_NOTE.docstatus = 1 
	AND DELIVERY_NOTE.company = 'Yonca Tekstil'
	AND YEAR(DELIVERY_NOTE.posting_date) = YEAR(CURDATE())
		
	""", filters, as_dict=0)

	context.bugun_tahsilat_tutar=data[0][0]
	context.bugun_sevkiyat_tutar=data[4][0]
	context.bugun_sevkiyat_miktar=data[4][1]
	context.hafta_tahsilat_tutar=data[1][0]
	context.hafta_sevkiyat_tutar=data[5][0]
	context.hafta_sevkiyat_miktar=data[5][1]
	context.ay_tahsilat_tutar=data[2][0]
	context.ay_sevkiyat_tutar=data[6][0]
	context.ay_sevkiyat_miktar=data[6][1]
	context.yil_tahsilat_tutar=data[3][0]
	context.yil_sevkiyat_tutar=data[7][0]
	context.yil_sevkiyat_miktar=data[7][1]

	return context