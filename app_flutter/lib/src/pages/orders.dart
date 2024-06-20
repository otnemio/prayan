import 'package:flutter/material.dart';
Widget mOrders(){
return DefaultTabController(
              length: 2,
              child: Scaffold(
                appBar: AppBar(
                  title: const TabBar(
                    tabs: <Widget>[
                      Tab(
                        text: 'Open',
                      ),
                      Tab(
                        text: 'Complete',
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
                                    child: const Wrap(
                                      direction: Axis.vertical,
                                      children: [
                                        Text("Pnl:"),
                                        Text("Pnl:"),
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
                                    child: const Wrap(
                                      direction: Axis.vertical,
                                      children: [
                                        Text("Pnl:"),
                                        Text("Pnl:"),
                                      ],
                                    ),
                                  ),
                                  Container(
                                    margin: const EdgeInsets.symmetric(
                                        horizontal: 25),
                                    child: const Wrap(
                                      direction: Axis.vertical,
                                      children: [
                                        Text("Pnl:"),
                                        Text("Pnl:"),
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
