import 'package:flutter/material.dart';
Widget mPortfolio(){
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
                                    margin: const EdgeInsets.symmetric(
                                        horizontal: 25),
                                    child: const Wrap(
                                      direction: Axis.vertical,
                                      children: [
                                        Text("Current:"),
                                        Text("10075.80"),
                                        Text("Invested:"),
                                        Text("9005.10"),
                                      ],
                                    ),
                                  ),
                                  Container(
                                    margin: const EdgeInsets.symmetric(
                                        horizontal: 25),
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
                                    margin: const EdgeInsets.symmetric(
                                        horizontal: 25),
                                    child: Wrap(
                                      direction: Axis.vertical,
                                      children: [
                                        const Text("Total MTM:"),
                                        priceText(788.20),
                                      ],
                                    ),
                                  ),
                                  Container(
                                    margin: const EdgeInsets.symmetric(
                                        horizontal: 25),
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
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
}


Widget priceText(text) {
  return Text(
    text.toString(),
    style: TextStyle(
      color: text<0 ? Colors.red : Colors.green,
      fontSize: 22,
    ),
  );
}