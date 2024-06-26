import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class Dashboard extends StatefulWidget {
  const Dashboard({super.key});

  @override
  State<Dashboard> createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  final String assetG = 'assets/ganesh-ji.svg';
  final String assetL = 'assets/lakshmi-ji.svg';
  @override
  Widget build(BuildContext context) {
    return SizedBox.expand(
      child: Column(children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Card(
              color: const Color.fromARGB(255, 240, 240, 240),
              child: SvgPicture.asset(
                assetG,
                colorFilter: const ColorFilter.mode(
                    Color.fromARGB(255, 50, 50, 255), BlendMode.srcIn),
                width: 100,
                height: 100,
                allowDrawingOutsideViewBox: true,
              ),
            ),
            Card(
              color: const Color.fromARGB(255, 240, 240, 240),
              child: SvgPicture.asset(
                assetL,
                colorFilter: const ColorFilter.mode(
                    Color.fromARGB(255, 255, 50, 50), BlendMode.srcIn),
                width: 100,
                height: 100,
                allowDrawingOutsideViewBox: true,
              ),
            ),
          ],
        ),
        const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("ॐ गंग गणपतये नमो नमः !!"),
            Text("ॐ महा लक्ष्मी नमो नमः !!")
          ],
        )
      ]),
    );
  }
}
