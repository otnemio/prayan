import 'package:intl/intl.dart';
import 'package:flutter/material.dart';

class Portfolio extends StatefulWidget {
  const Portfolio({super.key});

  @override
  State<Portfolio> createState() => _PortfolioState();
}

class _PortfolioState extends State<Portfolio> {
  List<(String, int, double)> holdings = [
    ('BEL', 50, 284.3),
    ('ZOMATO', 120, 171.1),
    ('JIOFIN', 150, 254.7)
  ];
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
                  Expanded(
                    child: ListView.separated(
                        padding: const EdgeInsets.all(8),
                        itemCount: holdings.length,
                        separatorBuilder: (BuildContext context, int index) =>
                            const Divider(),
                        itemBuilder: (BuildContext context, int index) {
                          return SizedBox(
                            height: 50,
                            child: Column(children: [
                              Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceEvenly,
                                  children: [
                                    Text(holdings[index].$1),
                                    Text('${holdings[index].$2}'),
                                  ]),
                            ]),
                          );
                        }),
                  ),
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
                  Expanded(
                    child: ListView.builder(
                        padding: const EdgeInsets.all(8),
                        itemCount: entries.length,
                        itemBuilder: (BuildContext context, int index) {
                          return Container(
                            height: 50,
                            color: Colors.amber[colorCodes[index]],
                            child:
                                Center(child: Text('Entry ${entries[index]}')),
                          );
                        }),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

final List<String> entries = <String>['A', 'B', 'C', 'D', 'E'];
final List<int> colorCodes = <int>[600, 500, 100, 200, 300];

Widget mListView() {
  return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: entries.length,
      itemBuilder: (BuildContext context, int index) {
        return Container(
          height: 50,
          color: Colors.amber[colorCodes[index]],
          child: Center(child: Text('Entry ${entries[index]}')),
        );
      });
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
