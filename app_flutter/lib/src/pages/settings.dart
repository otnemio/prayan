import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class Settings extends StatefulWidget {
  const Settings({super.key});

  @override
  State<Settings> createState() => _SettingsState();
}

class _SettingsState extends State<Settings> {
  String serverstatus = '--', loginstatus = '--';
  final totpController = TextEditingController();
  @override
  void initState() {
    super.initState();
    getServerStatus().then((val) {
      setState(() {
        serverstatus = val;
      });
    });
    if (serverstatus != 'NOK') {
      getLoginStatus().then((val) {
        setState(() {
          loginstatus = val;
        });
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color.fromARGB(255, 255, 255, 255),
      child: ListView(
        padding: const EdgeInsets.all(8),
        children: <Widget>[
          Container(
            height: 50,
            color: Colors.amber[500],
            child: Center(child: Text(serverstatus)),
          ),
          Container(
            height: 50,
            color: Colors.amber[100],
            child: Center(child: Text(loginstatus)),
          ),
          Container(
            height: 50,
            color: Colors.amber[100],
            child: Row(
              children: [
                Flexible(
                  child: TextField(
                    controller: totpController,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: 'TOTP',
                    ),
                    keyboardType: TextInputType.number,
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    setLoginTOTP(totpController.text).then((val) {
                      setState(() {
                        loginstatus = val['Msg'];
                      });
                    });
                  },
                  child: const Text('Okay'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

Future<String> getLoginStatus() async {
  var url = Uri.http('192.168.29.6:8080', '/loggedin');
  final response = await http.get(url);
  var jObj = jsonDecode(response.body);
  return jObj['Msg'];
}

Future<dynamic> setLoginTOTP(String tOTP) async {
  final queryParameters = {
    'totp': '$tOTP',
  };
  var url = Uri.http('192.168.29.6:8080', '/login', queryParameters);
  final response = await http.get(url);
  var jObj = jsonDecode(response.body);
  return jObj;
}

Future<String> getServerStatus() async {
  try {
    var url = Uri.http('192.168.29.6:8080', '/');
    final response = await http.get(url);
    var jObj = jsonDecode(response.body);
    return jObj['Msg'];
  } catch (e) {
    return 'NOK';
  }
}
