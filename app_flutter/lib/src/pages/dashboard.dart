import 'dart:async';
import 'dart:ffi';

import '../common/methods.dart';
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
  late String cash = '--', cbu = '--', coll = '--', avl = '--';

  @override
  Widget build(BuildContext context) {
    return SizedBox.expand(
      child: Column(children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Card(
              color: const Color.fromARGB(255, 240, 240, 240),
              child: GestureDetector(
                onTap: () {
                  getLimits().then((val) {
                    setState(() {
                      if (val['Msg'].containsKey('cash')) {
                        cash = displayAmt(val['Msg']['cash']);
                      }
                      if (val['Msg'].containsKey('collateral')) {
                        coll = displayAmt(val['Msg']['collateral']);
                      }
                      if (val['Msg'].containsKey('cbu')) {
                        cbu = displayAmt(val['Msg']['cbu']);
                      }

                      double avlAmt = double.parse(val['Msg']['cash']) +
                          double.parse(val['Msg']['collateral']);
                      avl = displayAmt(avlAmt.toString());
                    });
                  });
                  getHoldings().then((val) {
                    setState(() {
                      for (var i = 0; i < val['Msg'].length; i++) {
                        print(val['Msg'][i]);
                      }
                    });
                  });
                },
                child: SvgPicture.asset(
                  assetG,
                  colorFilter: const ColorFilter.mode(
                      Color.fromARGB(255, 50, 50, 255), BlendMode.srcIn),
                  width: 100,
                  height: 100,
                  allowDrawingOutsideViewBox: true,
                ),
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
            Text("ॐ गं गणपतये नमो नमः!!"),
            Text("ॐ महा लक्ष्मी नमो नमः!!")
          ],
        ),
        Text(
          '''
-----------------------------------------
    Equity
    ------
    Invested            : 12,570.50
    Current             : 18,540.60
    Gain/Loss           : 1,021.00
    
    Margin
    ------
    Available           : $avl
            Cash        : $cash
            Collateral  : $coll
    Used                :
    
    MTM
    ------
    PnL                 :
-----------------------------------------
''',
          style: const TextStyle(fontFamily: "monospace"),
        ),
      ]),
    );
  }
}
