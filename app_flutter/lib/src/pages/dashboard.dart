import 'package:flutter/widgets.dart';

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
  String? cash, cbu, coll, brkg, brkgei, brkgec, brkgdm, premium, urmtom;
  late double gl = 0;

  @override
  void initState() {
    super.initState();
    getLimits().then((val) {
      setState(() {
        cash = getLimit(val, 'cash');
        coll = getLimit(val, 'collateral');
        cbu = getLimit(val, 'cbu');
        brkg = getLimit(val, 'brokerage');
        brkgei = getLimit(val, 'brkage_e_i');
        brkgec = getLimit(val, 'brkage_e_c');
        brkgdm = getLimit(val, 'brkage_d_m');
        premium = getLimit(val, 'premium');
        urmtom = getLimit(val, 'urmtom');
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox.expand(
      child: Column(children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Card(
              color: const Color.fromARGB(255, 216, 216, 255),
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
              color: const Color.fromARGB(255, 255, 216, 216),
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
        SizedBox(
            width: 350,
            child: Card(
                color: const Color.fromARGB(255, 255, 255, 236),
                child: Text(
                  '''
 Equity
    Invested            : 12,570.50
    Current             : 18,540.60
    Gain/Loss           : 1,021.00
 Margin
    Available           : 
          Cash          : $cash
          Collateral    : $coll
    Used                :
 PnL
    Premium             : $premium
    UrMtoM              : $urmtom
 Brokarage
    Total               : $brkg
      Equity Intraday   : $brkgei
      Equity CAC        : $brkgec
      Derivative Margin : $brkgdm
''',
                  style: const TextStyle(fontFamily: "monospace"),
                ))),
        const SizedBox(
            width: 350,
            height: 64,
            child: Card(
                color: Color.fromARGB(255, 184, 245, 241),
                child: Padding(
                    padding: EdgeInsets.all(8),
                    child:
                        Text("Learn from trading and non-trading mistakes."))))
      ]),
    );
  }
}
