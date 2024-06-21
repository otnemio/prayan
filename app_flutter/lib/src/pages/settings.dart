import 'package:flutter/material.dart';

Widget mSettings() {
  return Card(
    shadowColor: Colors.transparent,
    margin: const EdgeInsets.all(8.0),
    child: SizedBox.expand(
      child: Center(
        child: IconButton(
          iconSize: 72,
          icon: const Icon(Icons.favorite),
          onPressed: () {},
        ),
      ),
    ),
  );
}
