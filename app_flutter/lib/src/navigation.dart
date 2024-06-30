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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: NavigationBar(
        backgroundColor: Color.fromARGB(255, 187, 211, 255),
        onDestinationSelected: (int index) {
          setState(() {
            currentPageIndex = index;
          });
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
          mScaffold(context, 'Watchlist'),
          mScaffold(context, 'Orders'),
          mScaffold(context, 'Dashboard'),
          mScaffold(context, 'Portfolio'),
          mScaffold(context, 'Settings'),
        ][currentPageIndex],
      ),
    );
  }
}

Widget mScaffold(context, String titleText) {
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
      body: mPage(titleText));
}

Widget mPage(String titleText) {
  switch (titleText) {
    case 'Dashboard':
      return const Dashboard();
    case 'Portfolio':
      return const Portfolio();
    case 'Settings':
      return const Settings();

    default:
      return const Card(
        shadowColor: Colors.transparent,
        margin: EdgeInsets.all(8.0),
        child: SizedBox.expand(
          child: Center(
            child: Text(
              "Hello",
            ),
          ),
        ),
      );
  }
}
