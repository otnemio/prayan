import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class Settings extends StatefulWidget {
  const Settings({super.key});

  @override
  State<Settings> createState() => _SettingsState();
}

class _SettingsState extends State<Settings> {
  String status = '--';
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Color.fromARGB(255, 255, 255, 255),
      child: ListView(
        padding: const EdgeInsets.all(8),
        children: <Widget>[
          Container(
            height: 50,
            color: Colors.amber[600],
            child: ElevatedButton(
              onPressed: () {
                getStatus().then((val) {
                  setState(() {
                    status = val;
                  });
                });
              },
              child: const Text('Login Status'),
            ),
          ),
          Container(
            height: 50,
            color: Colors.amber[500],
            child: Center(child: Text(status)),
          ),
          Container(
            height: 50,
            color: Colors.amber[100],
            child: const Center(child: Text('Entry C')),
          ),
        ],
      ),
    );
  }
}

Widget mSettings() {
  return Card(
    shadowColor: Colors.transparent,
    margin: const EdgeInsets.all(8.0),
    child: SizedBox.expand(
      child: Center(
        child: mListViewSettings(),
      ),
    ),
  );
}

Widget mListViewSettings() {
  return ListView(
    padding: const EdgeInsets.all(8),
    children: <Widget>[
      Container(
        height: 50,
        color: Colors.amber[600],
        child: ElevatedButton(
          onPressed: () {},
          child: const Text('Enabled'),
        ),
      ),
      Container(
        height: 50,
        color: Colors.amber[500],
        child: const Center(child: Text('Entry B')),
      ),
      Container(
        height: 50,
        color: Colors.amber[100],
        child: const Center(child: Text('Entry C')),
      ),
    ],
  );
}

Future<String> getStatus() async {
  var url = Uri.http('192.168.29.6:8080', '/loggedin');
  final response = await http.get(url);
  var jObj = jsonDecode(response.body);
  return jObj['Msg'];
}
