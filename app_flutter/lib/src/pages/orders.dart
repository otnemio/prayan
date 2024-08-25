import 'package:flutter/material.dart';

class Orders extends StatefulWidget {
  const Orders({super.key});

  @override
  State<Orders> createState() => _OrdersState();
}

class _OrdersState extends State<Orders> {
  String mainorder = '--', trailingorder = '--';
  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color.fromARGB(255, 255, 255, 255),
      child: ListView(
        padding: const EdgeInsets.all(8),
        children: <Widget>[
          Container(
            height: 50,
            color: Colors.amber[100],
            child: Center(child: Text(mainorder)),
          ),
          Container(
            height: 50,
            color: Colors.amber[100],
            child: Center(child: Text(trailingorder)),
          ),
          Container(
            height: 50,
            color: Colors.amber[200],
            child: Center(
              child: ElevatedButton(
                onPressed: () {
                  _awaitMainReturnValueFromSecondScreen(context);
                },
                child: const Text('Create Main Order'),
              ),
            ),
          ),
          Container(
            height: 50,
            color: Colors.amber[200],
            child: Center(
              child: ElevatedButton(
                onPressed: () {
                  _awaitTrailingReturnValueFromSecondScreen(context);
                },
                child: const Text('Create Trailing Order'),
              ),
            ),
          ),
          Container(
            height: 50,
            color: Colors.green[200],
            child: Center(
              child: ElevatedButton(
                onPressed: () {},
                child: const Text('Punch'),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _awaitMainReturnValueFromSecondScreen(BuildContext context) async {
    // start the SecondScreen and wait for it to finish with a result
    final result = await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (context) => const OrderRoute(),
            settings: const RouteSettings()));

    // after the SecondScreen result comes back update the widget with it
    setState(() {
      mainorder = result;
    });
  }

  void _awaitTrailingReturnValueFromSecondScreen(BuildContext context) async {
    // start the SecondScreen and wait for it to finish with a result
    final result = await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (context) => const OrderRoute(),
            settings: const RouteSettings()));

    // after the SecondScreen result comes back update the widget with it
    setState(() {
      trailingorder = result;
    });
  }
}

class OrderRoute extends StatefulWidget {
  const OrderRoute({super.key});

  @override
  State<OrderRoute> createState() => _OrderState();
}

class _OrderState extends State<OrderRoute> {
  OrderType? _character = OrderType.equity;
  OptionType? _option = OptionType.call;
  BuySellType? _bos = BuySellType.buy;
  String dropdownValue = list.first;
  int dropdownStrikeValue = strike.first;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Order"),
      ),
      body: Center(
        child: Column(
          children: [
            Container(
              color: const Color.fromARGB(255, 255, 220, 220),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Expanded(
                    child: Column(
                      children: <Widget>[
                        RadioListTile<OrderType>(
                          title: const Text('Equity'),
                          value: OrderType.equity,
                          groupValue: _character,
                          onChanged: (OrderType? value) {
                            setState(() {
                              _character = value;
                            });
                          },
                        ),
                        RadioListTile<OrderType>(
                          title: const Text('Future'),
                          value: OrderType.future,
                          groupValue: _character,
                          onChanged: (OrderType? value) {
                            setState(() {
                              _character = value;
                            });
                          },
                        ),
                        RadioListTile<OrderType>(
                          title: const Text('Option'),
                          value: OrderType.option,
                          groupValue: _character,
                          onChanged: (OrderType? value) {
                            setState(() {
                              _character = value;
                            });
                          },
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                      child: Column(
                    children: <Widget>[
                      DropdownMenu<String>(
                        initialSelection: list.first,
                        onSelected: (String? value) {
                          // This is called when the user selects an item.
                          setState(() {
                            dropdownValue = value!;
                          });
                        },
                        dropdownMenuEntries:
                            list.map<DropdownMenuEntry<String>>((String value) {
                          return DropdownMenuEntry<String>(
                              value: value, label: value);
                        }).toList(),
                      ),
                      const TextField(
                        decoration: InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Quantity',
                        ),
                        keyboardType: TextInputType.number,
                      )
                    ],
                  ))
                ],
              ),
            ),
            Container(
              color: const Color.fromARGB(255, 215, 223, 255),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Expanded(
                    child: Column(
                      children: <Widget>[
                        RadioListTile<OptionType>(
                          title: const Text('Call'),
                          value: OptionType.call,
                          groupValue: _option,
                          onChanged: (OptionType? value) {
                            setState(() {
                              _option = value;
                            });
                          },
                        ),
                        RadioListTile<OptionType>(
                          title: const Text('Put'),
                          value: OptionType.put,
                          groupValue: _option,
                          onChanged: (OptionType? value) {
                            setState(() {
                              _option = value;
                            });
                          },
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: DropdownMenu<int>(
                      initialSelection: strike.first,
                      onSelected: (int? value) {
                        // This is called when the user selects an item.
                        setState(() {
                          dropdownStrikeValue = value!;
                        });
                      },
                      dropdownMenuEntries:
                          strike.map<DropdownMenuEntry<int>>((int value) {
                        return DropdownMenuEntry<int>(
                            value: value, label: value.toString());
                      }).toList(),
                    ),
                  )
                ],
              ),
            ),
            Container(
              color: const Color.fromARGB(255, 215, 255, 222),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Expanded(
                    child: Column(
                      children: <Widget>[
                        RadioListTile<BuySellType>(
                          title: const Text('Buy'),
                          value: BuySellType.buy,
                          groupValue: _bos,
                          onChanged: (BuySellType? value) {
                            setState(() {
                              _bos = value;
                            });
                          },
                        ),
                        RadioListTile<BuySellType>(
                          title: const Text('Sell'),
                          value: BuySellType.sell,
                          groupValue: _bos,
                          onChanged: (BuySellType? value) {
                            setState(() {
                              _bos = value;
                            });
                          },
                        ),
                      ],
                    ),
                  ),
                  const Expanded(
                    child: Column(
                      children: <Widget>[
                        TextField(
                          decoration: InputDecoration(
                            border: OutlineInputBorder(),
                            hintText: 'Trigger Price',
                          ),
                          keyboardType: TextInputType.number,
                        ),
                        TextField(
                          decoration: InputDecoration(
                            border: OutlineInputBorder(),
                            hintText: 'Price',
                          ),
                          keyboardType: TextInputType.number,
                        )
                      ],
                    ),
                  )
                ],
              ),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context, "$_bos $_option");
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }
}

enum OrderType { equity, future, option }

enum OptionType { call, put }

enum BuySellType { buy, sell }

const List<int> strike = <int>[315, 320, 325, 330, 335, 340];
const List<String> list = <String>[
  'BEL',
  'RELIANCE',
];
