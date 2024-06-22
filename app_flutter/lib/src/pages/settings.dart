import 'dart:convert';
import 'package:flutter/widgets.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class YellowBird extends StatefulWidget {
  const YellowBird({super.key});

  @override
  State<YellowBird> createState() => _YellowBirdState();
}

class _YellowBirdState extends State<YellowBird> {
  String status = '--';
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Color.fromARGB(139, 90, 81, 11),
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
              child: const Text('Enabled'),
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
