import 'package:intl/intl.dart';
import 'package:flutter/material.dart';

class Portfolio extends StatefulWidget {
  const Portfolio({super.key});

  @override
  State<Portfolio> createState() => _PortfolioState();
}

class _PortfolioState extends State<Portfolio> {
  String status = '--';
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const TabBar(
            tabs: <Widget>[
              Tab(
                text: 'Holdings',
              ),
              Tab(
                text: 'Positions',
              ),
            ],
          ),
        ),
        body: TabBarView(
          children: <Widget>[
            Center(
              child: Column(
                children: [
                  SizedBox(
                    height: 120,
                    child: Card(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            margin: const EdgeInsets.symmetric(horizontal: 25),
                            child: Wrap(
                              direction: Axis.vertical,
                              children: [
                                const Text("Current:"),
                                priceText(10075.80,
                                    darkText: true, fontSize: 16),
                                const Text("Invested:"),
                                priceText(9005.10,
                                    darkText: true, fontSize: 16),
                              ],
                            ),
                          ),
                          Container(
                            margin: const EdgeInsets.symmetric(horizontal: 25),
                            child: Wrap(
                              direction: Axis.vertical,
                              children: [
                                const Text("Pnl:"),
                                priceText(1070.70),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Expanded(child: mListView()),
                ],
              ),
            ),
            Center(
              child: Column(
                children: [
                  SizedBox(
                    height: 120,
                    child: Card(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            margin: const EdgeInsets.symmetric(horizontal: 25),
                            child: Wrap(
                              direction: Axis.vertical,
                              children: [
                                const Text("Total MTM:"),
                                priceText(788.20),
                              ],
                            ),
                          ),
                          Container(
                            margin: const EdgeInsets.symmetric(horizontal: 25),
                            child: Wrap(
                              direction: Axis.vertical,
                              children: [
                                const Text("Day's MTM:"),
                                priceText(575.20),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Expanded(child: mListView()),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

final List<String> entries = <String>['A', 'B', 'C'];
final List<int> colorCodes = <int>[600, 500, 100];

Widget mListView() {
  return ListView(
    padding: const EdgeInsets.all(8),
    children: <Widget>[
      Container(
        height: 50,
        color: Colors.amber[600],
        child: const Center(child: Text('Entry A')),
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
