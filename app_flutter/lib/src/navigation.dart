import 'package:flutter/material.dart';
import 'menu.dart';
import 'dart:math';
import 'pages/dashboard.dart';
import 'pages/portfolio.dart';
import 'pages/settings.dart';

class NavigationWidget extends StatefulWidget {
  const NavigationWidget({super.key});

  @override
  State<NavigationWidget> createState() => _NavigationWidgetState();
}

class _NavigationWidgetState extends State<NavigationWidget> {
  int currentPageIndex = 0;
  String data = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: NavigationBar(
        onDestinationSelected: (int index) async {
          setState(() {
            currentPageIndex = index;
          });
          data = await refresh(context, index);
        },
        selectedIndex: currentPageIndex,
        destinations: const <Widget>[
          NavigationDestination(
            selectedIcon: Icon(Icons.bookmark_rounded),
            icon: Icon(Icons.bookmark_outline),
            label: 'Watchlist',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.library_books_rounded),
            icon: Icon(Icons.library_books_outlined),
            label: 'Orders',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.home_rounded),
            icon: Icon(Icons.home_outlined),
            label: 'Dashboard',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.cases_rounded),
            icon: Icon(Icons.cases_outlined),
            label: 'Portfolio',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.settings_rounded),
            icon: Icon(Icons.settings_outlined),
            label: 'Settings',
          ),
        ],
      ),
      body: SafeArea(
        child: <Widget>[
          /// Home page
          mScaffold(context, 'Watchlist', data),
          mScaffold(context, 'Orders', data),
          mScaffold(context, 'Dashboard', data),
          mScaffold(context, 'Portfolio', data),
          mScaffold(context, 'Settings', data),
        ][currentPageIndex],
      ),
    );
  }
}

Widget mScaffold(context, String titleText, String data) {
  return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const SecondRoute()),
            );
          },
        ),
        title: Text(titleText),
      ),
      body: mPage(titleText, data));
}

Widget mPage(String titleText, String data) {
  switch (titleText) {
    case 'Dashboard':
      return const Dashboard();
    case 'Portfolio':
      return const Portfolio();

    case 'Settings':
      return const Settings();

    default:
      return Card(
        shadowColor: Colors.transparent,
        margin: const EdgeInsets.all(8.0),
        child: SizedBox.expand(
          child: Center(
            child: Text(
              data,
            ),
          ),
        ),
      );
  }
}

refresh(context, index) async {
  var rng = Random();
  // switch (index) {
  //   case 3:
  //   // var h = await getHoldings();
  //   // Logger().d(h);
  // }
  int i = rng.nextInt(100);
  // ScaffoldMessenger.of(context).showSnackBar(
  //     SnackBar(content: Text('Data reloaded. Data for $index is $i')));
  return "Data for $index is $i";
}
