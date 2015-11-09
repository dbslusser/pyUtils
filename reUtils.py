#! /usr/bin/python

"""
Description:
    Collection of commonly used regular expression patterns 

Author:
    David Slusser

Revision:
    0.0.1
"""


octet_regex = "(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])"
ip_regex = "%s\.%s\.%s\.%s" % (octet_regex, octet_regex, octet_regex, octet_regex)
cidr_regex = "^%s/(3[0-2]|[1-2][0-9]|[0-9])$" % (ip_regex) 
cidr_open_regex = "^%s/(3[0-2]|[1-2][0-9]|[0-9])" % (ip_regex)

re_patterns = {
               "octet":octet_regex,
               "ip":ip_regex,
               "cidr":cidr_regex,
               "ip_v4":"^((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))*$",
               "mac": "^(([0-9A-Fa-f]{2}[-:.]){5}[0-9A-Fa-f]{2})|(([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})|([0-9a-fA-F]{12})$",
               "vlan_id":"^([0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
               "tpid": "^0x(8100|88a8|9100|9200)$",
               "hex_value":"^#?([a-f0-9]{6}|[a-f0-9]{3})$",
               "slug":"^[a-z0-9-]+$",
               "email":"^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})*$",
               "url":"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$",
               "html_tag":"^<([a-z]+)([^<]+)*(?:>(.*)<\/\1>|\s+\/>)$",              
               "juniper_interface":"^(ge|xe|et)-\d{1,2}/\d{1,2}/\d{1,2}$",
               "juniper_lag":"^ae\d+$",
               "juniper_int_or_lag": "^((ge|xe|et)-\d{1,2}/\d{1,2}/\d{1,2})|(ae\d+)$",
               "juniper_tpid":"^0x(?:8100|88a8|9100|9200)$",
               "mask": "/(3[0-2]|[1-2][0-9]|[0-9])$",
               "cidr_open": cidr_open_regex, # same as cidr, but not closed at end of string
               "no_spaces":"^[a-zA-Z0-9_-]+$",
               "site_name":"^[a-zA-Z0-9_]+$",
               }

