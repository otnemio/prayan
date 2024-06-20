import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

FlutterTts flutterTts = FlutterTts();

Widget mSettings() {
  return Card(
    shadowColor: Colors.transparent,
    margin: const EdgeInsets.all(8.0),
    child: SizedBox.expand(
      child: Center(
        child: IconButton(
          iconSize: 72,
          icon: const Icon(Icons.favorite),
          onPressed: () async{
            
            await configureTts();
            speakText("Hello");
          },
        ),
      ),
    ),
  );
}

Future<void> configureTts() async {
  await flutterTts.setLanguage('en-US');
  await flutterTts.setSpeechRate(1.0);
  await flutterTts.setVolume(1.0);
}
void speakText(String text) async {
  await flutterTts.speak(text);
}

void stopSpeaking() async {
  await flutterTts.stop();
}