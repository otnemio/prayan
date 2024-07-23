import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/sparkcharts.dart';

class Watchlist extends StatefulWidget {
  const Watchlist({super.key});

  @override
  State<Watchlist> createState() => _WatchlistState();
}

class _WatchlistState extends State<Watchlist> {
  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        SizedBox(
          child: Card(
            child: ListTile(
              title: const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("BEL"),
                    Text("0.53%"),
                    Text("325.15"),
                  ]),
              subtitle: SizedBox(
                height: 50,
                child: SfSparkLineChart(
                    width: 1,
                    axisLineWidth: 1,
                    data: const [50, 20, 30, -40, -10, 25, 30, 33, 20, 8, 11]),
              ),
            ),
          ),
        ),
        SizedBox(
          height: 120,
          child: Card(
            child: ListTile(
              title: Column(children: [
                const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("ZOMATO"),
                      Text("225.84"),
                    ]),
                const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(""),
                      Text("1.8%"),
                    ]),
                SizedBox(
                  height: 50,
                  child: SfSparkLineChart(
                      width: 1,
                      axisLineWidth: 1,
                      data: const [-3, 1, -8, 5, -1, 5, -2, 2, 3, -5, 8, 7]),
                ),
              ]),
            ),
          ),
        ),
        SizedBox(
          height: 120,
          child: Card(
            child: ListTile(
              title: Column(children: [
                const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("ZOMATO"),
                      Text("225.84"),
                    ]),
                const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(""),
                      Text("1.8%"),
                    ]),
                SizedBox(
                  height: 50,
                  child: SfSparkLineChart(
                      width: 1,
                      axisLineWidth: 1,
                      data: const [-3, 1, -8, 5, -1, 5, -2, 2, 3, -5, 8, 7]),
                ),
              ]),
            ),
          ),
        ),
        SizedBox(
          height: 120,
          child: Card(
            child: ListTile(
              title: Column(children: [
                const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("ZOMATO"),
                      Text("225.84"),
                    ]),
                const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(""),
                      Text("1.8%"),
                    ]),
                SizedBox(
                  height: 50,
                  child: SfSparkLineChart(
                      width: 1,
                      axisLineWidth: 1,
                      data: const [-3, 1, -8, 5, -1, 5, -2, 2, 3, -5, 8, 7]),
                ),
              ]),
            ),
          ),
        ),
      ],
    );
  }
}
