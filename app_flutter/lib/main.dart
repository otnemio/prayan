import 'package:flutter/material.dart';
import 'src/app.dart';

void main() {
  runApp(MaterialApp(
    home: const MainApp(),
    theme: ThemeData(
      scaffoldBackgroundColor: const Color.fromARGB(255, 255, 255, 255),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: Color.fromARGB(255, 165, 229, 255),
        indicatorColor: Color.fromARGB(141, 41, 120, 173),
      ),
      cardTheme: const CardTheme(
        color: Color.fromARGB(255, 255, 233, 236),
      ),
    ),
  ));
}
