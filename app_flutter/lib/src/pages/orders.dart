import 'package:flutter/material.dart';

class Orders extends StatefulWidget {
  const Orders({super.key});

  @override
  State<Orders> createState() => _OrdersState();
}

class _OrdersState extends State<Orders> {
  Order main = Order(OrderType.option, OptionType.call, BuySellType.buy);
  Order trail = Order(OrderType.option, OptionType.call, BuySellType.sell);
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
            child: Center(child: Text(main.bos.toString())),
          ),
          Container(
            height: 50,
            color: Colors.amber[100],
            child: Center(child: Text(trail.toString())),
          ),
          Container(
            height: 50,
            color: Colors.amber[200],
            child: Center(
              child: ElevatedButton(
                onPressed: () {
                  _awaitReturnValueFromSecondScreen(context, false);
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
                  _awaitReturnValueFromSecondScreen(context, true);
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
                onPressed: () {
                  punchOrder(main, trail).then((val) {
                    setState(() {
                      print(val['Msg']);
                    });
                  });
                },
                child: const Text('Punch'),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _awaitReturnValueFromSecondScreen(
      BuildContext context, bool trailing) async {
    // start the SecondScreen and wait for it to finish with a result
    final result = await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (context) => const OrderRoute(),
            settings: const RouteSettings()));

    // after the SecondScreen result comes back update the widget with it
    setState(() {
      if (result != null) {
        if (trailing) {
          trail = result;
        } else {
          main = result;
        }
      }
    });
  }
}

class OrderRoute extends StatefulWidget {
  const OrderRoute({super.key});

  @override
  State<OrderRoute> createState() => _OrderState();
}

class _OrderState extends State<OrderRoute> {
  OrderType _type = OrderType.equity;
  OptionType _option = OptionType.call;
  BuySellType _bos = BuySellType.buy;
  String dropdownValue = listInstrument.first;
  String dropdownExpiryValue = expiry.first;
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
                          groupValue: _type,
                          onChanged: (OrderType? value) {
                            setState(() {
                              _type = value as OrderType;
                            });
                          },
                        ),
                        RadioListTile<OrderType>(
                          title: const Text('Future'),
                          value: OrderType.future,
                          groupValue: _type,
                          onChanged: (OrderType? value) {
                            setState(() {
                              _type = value as OrderType;
                            });
                          },
                        ),
                        RadioListTile<OrderType>(
                          title: const Text('Option'),
                          value: OrderType.option,
                          groupValue: _type,
                          onChanged: (OrderType? value) {
                            setState(() {
                              _type = value as OrderType;
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
                        initialSelection: listInstrument.first,
                        onSelected: (String? value) {
                          // This is called when the user selects an item.
                          setState(() {
                            dropdownValue = value!;
                          });
                        },
                        dropdownMenuEntries: listInstrument
                            .map<DropdownMenuEntry<String>>((String value) {
                          return DropdownMenuEntry<String>(
                              value: value, label: value);
                        }).toList(),
                      ),
                      DropdownMenu<String>(
                        initialSelection: expiry.first,
                        onSelected: (String? value) {
                          // This is called when the user selects an item.
                          setState(() {
                            dropdownExpiryValue = value!;
                          });
                        },
                        dropdownMenuEntries: expiry
                            .map<DropdownMenuEntry<String>>((String value) {
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
                              _option = value as OptionType;
                            });
                          },
                        ),
                        RadioListTile<OptionType>(
                          title: const Text('Put'),
                          value: OptionType.put,
                          groupValue: _option,
                          onChanged: (OptionType? value) {
                            setState(() {
                              _option = value as OptionType;
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
                              _bos = value as BuySellType;
                            });
                          },
                        ),
                        RadioListTile<BuySellType>(
                          title: const Text('Sell'),
                          value: BuySellType.sell,
                          groupValue: _bos,
                          onChanged: (BuySellType? value) {
                            setState(() {
                              _bos = value as BuySellType;
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
                Navigator.pop(context,
                    Order.complete(_type, _option, _bos, dropdownExpiryValue));
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
const List<String> expiry = <String>['AUG', 'SEP', 'OCT'];

const List<String> listInstrument = <String>[
  'BEL',
  'RELIANCE',
];

class Order {
  OrderType efo;
  OptionType pall;
  BuySellType bos;
  late String expiry;
  Order(this.efo, this.pall, this.bos);
  Order.complete(this.efo, this.pall, this.bos, this.expiry);
  @override
  String toString() {
    switch (efo) {
      case OrderType.option:
        return "${bos == BuySellType.buy ? 'Buy' : 'Sell'} "
            "n quantities of "
            "${pall == OptionType.call ? 'Call' : 'Put'} option "
            "of strike price f "
            "having expiry $expiry. "
            "Trigger price: tp, Price: p.";
      default:
        return "None";
    }
  }
}

Future<dynamic> punchOrder(mainorder, trailingorder) async {
  final queryParameters = {
    'main': mainorder,
    'trail': trailingorder,
  };
  var url = Uri.http('192.168.29.6:8080', '/login', queryParameters);
  // final response = await http.get(url);
  // var jObj = jsonDecode(response.body);
  return "hello";
}
