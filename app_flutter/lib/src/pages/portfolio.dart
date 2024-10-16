import '../common/methods.dart';
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
                      color: const Color.fromARGB(255, 255, 229, 229),
                      margin: const EdgeInsets.only(left: 8, right: 8, top: 4),
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
                        itemCount: holdings.length + 3,
                        separatorBuilder: (BuildContext context, int index) =>
                            const Divider(
                              height: 1,
                            ),
                        itemBuilder: (BuildContext context, int index) {
                          if (index == 0 || index == holdings.length + 2) {
                            return const SizedBox.shrink();
                          }
                          if (index == 1) {
                            return const ListTile(
                              tileColor: Color.fromARGB(255, 247, 220, 235),
                              // height: 44,
                              title: Column(children: [
                                Row(children: [
                                  Align(
                                    alignment: Alignment.centerLeft,
                                    child: SizedBox(
                                        child: Text(
                                      "SYMBOL",
                                      style: TextStyle(
                                          fontWeight: FontWeight.bold),
                                    )),
                                  ),
                                ]),
                                Row(
                                  children: [
                                    Text("Qty @ Avg"),
                                  ],
                                )
                              ]),
                            );
                          }
                          return ListTile(
                            onTap: () {
                              Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                      builder: (context) =>
                                          const InstrumentRoute(),
                                      settings: RouteSettings(
                                          arguments: ScreenArguments(
                                              holdings[index - 2].$1))));
                            },
                            title: Column(children: [
                              Row(children: [
                                Align(
                                  alignment: Alignment.centerLeft,
                                  child: SizedBox(
                                      child: Text(
                                    holdings[index - 2].$1,
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold),
                                  )),
                                ),
                              ]),
                              Row(
                                children: [
                                  Text(
                                      '${holdings[index - 2].$2} @ ${holdings[index - 2].$3}'),
                                ],
                              )
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
                      color: const Color.fromARGB(255, 255, 229, 229),
                      margin: const EdgeInsets.only(left: 8, right: 8, top: 4),
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

class ScreenArguments {
  final String title;

  ScreenArguments(this.title);
}

class InstrumentRoute extends StatelessWidget {
  const InstrumentRoute({super.key});

  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)!.settings.arguments as ScreenArguments;
    return Scaffold(
      appBar: AppBar(
        title: Text(args.title),
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

final List<String> entries = <String>['A', 'B', 'C', 'D', 'E'];
final List<int> colorCodes = <int>[600, 500, 100, 200, 300];
