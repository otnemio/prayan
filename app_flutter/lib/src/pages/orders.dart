import 'package:flutter/material.dart';

class Orders extends StatefulWidget {
  const Orders({super.key});

  @override
  State<Orders> createState() => _OrdersState();
}

class _OrdersState extends State<Orders> {
  String serverstatus = '--', loginstatus = '--';
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
            child: Center(
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const OrderRoute(),
                          settings: const RouteSettings()));
                },
                child: const Text('Punch Order'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class OrderRoute extends StatelessWidget {
  const OrderRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Order"),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
          },
          child: const Text('Go back!'),
        ),
      ),
    );
  }
}
