import 'package:flutter/material.dart';

class TextMessage extends StatelessWidget {
  final String message;
  final String time;
  final bool isSender;
  final bool isSent;
  final bool isRead;

  const TextMessage({
    Key? key,
    required this.message,
    required this.time,
    required this.isSender,
    required this.isSent,
    required this.isRead,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isSender ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 5, horizontal: 10),
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: isSender ? Colors.blueAccent : Colors.grey[300],
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          crossAxisAlignment: isSender ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Text(
              message,
              style: TextStyle(
                color: isSender ? Colors.white : Colors.black,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              time,
              style: TextStyle(
                color: isSender ? Colors.white70 : Colors.black54,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
