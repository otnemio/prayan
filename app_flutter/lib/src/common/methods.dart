import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:flutter/material.dart';

Widget priceText(text, {bool darkText = false, double fontSize = 22}) {
  var formatter = NumberFormat('#,##,000.00');
  return Text(
    formatter.format(text),
    style: TextStyle(
      color: darkText
          ? Colors.black
          : text < 0
              ? Colors.red
              : Colors.green,
      fontSize: fontSize,
    ),
  );
}

String displayAmt(String str) {
  var formatter = NumberFormat('#,##,000.00');
  return formatter.format(double.parse(str)).padLeft(12);
}

Future<Map<String, dynamic>> getHoldings() async {
  var url = Uri.http('192.168.29.6:8080', '/holdings');
  final response = await http.get(url);
  var jObj = jsonDecode(response.body);
  return jObj;
}

Future<Map<String, dynamic>> getLimits() async {
  var url = Uri.http('192.168.29.6:8080', '/limits');
  final response = await http.get(url);
  var jObj = jsonDecode(response.body);
  return jObj;
}
