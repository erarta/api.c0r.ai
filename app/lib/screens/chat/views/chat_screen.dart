import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/components/product/product_card.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:modera/constants.dart';
import 'package:modera/theme/input_decoration_theme.dart';
import 'package:modera/utils/logger.dart';
import 'package:path_provider/path_provider.dart';
import 'package:modera/services/api_service.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'dart:developer' as developer;

import 'components/support_person_info.dart';
import 'components/text_message.dart';
import 'components/product_message.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  String? _recordPath;
  final TextEditingController _messageController = TextEditingController();
  final ApiService _apiService = ApiService();
  final _supabase = Supabase.instance.client;
  List<dynamic> _messages = [];
  bool _isLoading = true;
  String? _currentUserId;
  bool _isProcessing = false;  // New flag for processing state
  bool _isTyping = false;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _initializeChat();
    
    // Add listener to scroll when keyboard appears
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollToBottom();
    });
  }

  Future<void> _initializeChat() async {
    try {
      // Get current user
      _currentUserId = _supabase.auth.currentUser?.id;

      if (_currentUserId == null) {
        AppLogger.log(
          'No authenticated user found',
          level: LogLevel.error,
        );
        return;
      }

      // Fetch initial messages
      await _fetchMessages();

      // Set up real-time listener for the current user's messages
      _supabase
          .from('chat_messages')
          .stream(primaryKey: ['id'])
          .eq('user_id', _currentUserId!) // Filter by current user
          .listen(_onMessageReceived);
    } catch (e) {
      AppLogger.log(
        'Chat initialization error: $e',
        level: LogLevel.error,
      );
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _fetchMessages() async {
    try {
      final response = await _supabase
          .from('chat_messages')
          .select('*')
          .eq('user_id', _currentUserId!)
          .order('created_at');

      final List<dynamic> data = response;

      // Sort messages by created_at in ascending order
      data.sort((a, b) {
        final dateA = DateTime.parse(a['created_at']);
        final dateB = DateTime.parse(b['created_at']);
        return dateA.compareTo(dateB);
      });

      AppLogger.log(
        'Fetched ${data.length} messages',
        level: LogLevel.network,
      );

      setState(() {
        _messages = data.expand((msg) {
          final List<dynamic> messages = [];

          // Add the text message
          messages.add(TextMessage(
            message: msg['content'] ?? '',
            time: _formatTimestamp(msg['created_at']),
            isSender: msg['role'] == 'user',
            isSent: true,
            isRead: true,
          ));

          // Check for metadata and recommendations
          if (msg['metadata'] != null && msg['metadata']['recommendations'] != null) {
            final recommendations = msg['metadata']['recommendations'];

            // Add the product message to the chat
            messages.add(ProductMessage(
              message: '', // Empty message for product cards
              products: recommendations,
            ));
          }

          return messages;
        }).toList();

        _isLoading = false;
      });
    } catch (e) {
      AppLogger.log(
        'Error fetching messages: $e',
        level: LogLevel.error,
      );
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _onMessageReceived(List<Map<String, dynamic>> data) {
    if (data.isEmpty) return;

    final newMessage = data.last;

    final textMessage = TextMessage(
      message: newMessage['content'] ?? '',
      time: _formatTimestamp(newMessage['created_at']),
      isSender: newMessage['role'] == 'user',
      isSent: true,
      isRead: true,
    );

    setState(() {
      _messages.add(textMessage);
    });
    
    // Check for additional_info and recommendations
    if (newMessage['additional_info'] != null && newMessage['additional_info']['recommendations'] != null) {
      final recommendations = newMessage['additional_info']['recommendations'];

      // Add the product message to the chat
      setState(() {
        _messages.add(ProductMessage(
          message: '', // Empty message for product cards
          products: recommendations,
        ));
      });
    }

    _scrollToBottom();
  }

  Future<void> _sendTextMessage(String message) async {
    if (message.trim().isEmpty || _currentUserId == null) return;

    try {
      // Immediately add user's message to the chat
      final userMessage = TextMessage(
        message: message,
        time: _getCurrentTime(),
        isSender: true,
        isSent: true,
        isRead: true,
      );

      setState(() {
        _messages.add(userMessage);
        _messageController.clear();
        _isProcessing = true;
      });

      // Show typing indicator
      _showTypingIndicator();
      _scrollToBottom();

      // Call API to send text message
      final apiResponse = await _apiService.sendTextMessage(
        userId: _currentUserId!, 
        userMessage: message
      );

      // Hide typing indicator
      _hideTypingIndicator();

      // Check for recommendations in the response
      
      if (apiResponse != null && apiResponse['additional_info'] != null && apiResponse['additional_info']['recommendations'] != null) {
        final recommendations = apiResponse['additional_info']['recommendations'];

        // Add the product message to the chat
        setState(() {
          _messages.add(ProductMessage(
            message: '', // Empty message for product cards
            products: recommendations,
          ));
        });
      }

      // If API returns a response, add it to messages
      if (apiResponse != null && apiResponse['role'] == 'assistant') {
        // Create assistant message
        final assistantMessage = TextMessage(
          message: apiResponse['content'] ?? '',
          time: _getCurrentTime(),
          isSender: false,
          isSent: true,
          isRead: false,
        );

        // Scroll to bottom after adding message
      _scrollToBottomWithKeyboard();

        // Add assistant message to the chat
        setState(() {
          _messages.add(assistantMessage);
        });
      }

      // Clear processing state
      setState(() {
        _isProcessing = false;
      });

    } catch (e) {
      // Hide typing indicator in case of error
      _hideTypingIndicator();

      setState(() {
        _isProcessing = false;
      });

      developer.log(
        'Text Message Sending Error',
        name: 'ChatScreen',
        error: e,
        stackTrace: StackTrace.current,
      );
    }
  }

  String _formatTimestamp(String? timestamp) {
    if (timestamp == null) return '';
    final dateTime = DateTime.parse(timestamp);
    return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<bool> _checkMicrophonePermission() async {
    final status = await Permission.microphone.status;
    return status.isGranted;
  }

  Future<void> _requestMicrophonePermission() async {
    final status = await Permission.microphone.request();
    if (!status.isGranted) {
      _showPermissionDeniedDialog();
    }
  }

  Future<String> _getAudioFilePath() async {
    // Get temporary directory for storing audio files
    final Directory tempDir = await getTemporaryDirectory();
    
    // Create a unique filename with timestamp
    final String timestamp = DateTime.now().millisecondsSinceEpoch.toString();
    return '${tempDir.path}/recording_$timestamp.aac';
  }

  Future<void> _toggleRecording() async {
    bool hasPermission = await _checkMicrophonePermission();

    if (!hasPermission) {
      await _showMicrophonePermissionDialog();
      return;
    }

    try {
      if (_isRecording) {
        // Stop recording immediately
        String? path = await _audioRecorder.stop();
        
        setState(() {
          _isRecording = false;
          _isProcessing = true;  // Start processing state
        });

        // Process audio in background
        _processRecordedAudio();
      } else {
        // Start recording
        final String audioPath = await _getAudioFilePath();


       await _audioRecorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          bitRate: 128000
        ),
        path: audioPath
      );

      setState(() {
        _isRecording = true;
      });
      }
    } catch (e) {
      setState(() {
        _isRecording = false;
        _isProcessing = false;
      });
      
      AppLogger.log(
        'Recording error: $e',
        level: LogLevel.error,
      );
      _showRecordingErrorDialog(e.toString());
    }
  }

  Future<void> _processRecordedAudio() async {
    if (_recordPath == null || _currentUserId == null) return;

    try {
      final audioFile = File(_recordPath!);
      
      // Stop recording and reset recording state
      String? path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
        _recordPath = null;
      });

      // Add initial audio message placeholder
      final audioMessage = TextMessage(
        message: 'Voice message',
        time: _getCurrentTime(),
        isSender: true,
        isSent: true,
        isRead: true,
      );

      // Show typing indicator
      _showTypingIndicator();
      _scrollToBottom();

      setState(() {
        _messages.add(audioMessage);
        _isProcessing = true;
      });

      // Transcribe audio message
      final response = await _apiService.transcribeAudioMessage(
        userId: _currentUserId!, 
        audioFile: audioFile,
      );

      _hideTypingIndicator();

      // If transcription is successful, replace the audio message with transcribed text
      if (response != null && response['user_message'] != null) {
        // Remove the previous audio message placeholder
        _messages.removeWhere((message) => message.message == 'Voice message');

        // Add transcribed user message
        final transcribedMessage = TextMessage(
          message: response['user_message'],
          time: _getCurrentTime(),
          isSender: true,
          isSent: true,
          isRead: true,
        );

        setState(() {
          _messages.add(transcribedMessage);
        });
      }

      // If API returns a text response, add it to messages
      if (response != null && response['role'] == 'assistant') {
        final assistantMessage = TextMessage(
          message: response['content'] ?? '',
          time: _getCurrentTime(),
          isSender: false,
          isSent: true,
          isRead: false,
        );

        setState(() {
          _messages.add(assistantMessage);
        });
      }

      // Check for recommendations in the response
      if (response != null && response['additional_info'] != null && response['additional_info']['recommendations'] != null) {
        final recommendations = response['additional_info']['recommendations'];

        // Add the product message to the chat
        setState(() {
          _messages.add(ProductMessage(
            message: '', // Empty message for product cards
            products: recommendations,
          ));
        });
      }
      // Clear processing state
      setState(() {
        _isProcessing = false;
      });

      // Scroll to bottom after adding message
      _scrollToBottom();
    } catch (e) {
      // Reset processing state in case of error
      setState(() {
        _isProcessing = false;
      });

      developer.log(
        'Audio Processing Error',
        name: 'ChatScreen',
        error: e,
        stackTrace: StackTrace.current,
      );
    }
  }

  void _addMessageToChat(String message) {
    developer.log(
      '_addMessageToChat called',
      name: 'ChatScreen',
      error: {'message': message},
    );
    
    final newMessage = TextMessage(
      message: message,
      time: _getCurrentTime(),
      isSender: true,
      isSent: true,
      isRead: false,
    );

    setState(() {
      _messages.add(newMessage);
      developer.log(
        'Messages after add',
        name: 'ChatScreen',
        error: {'count': _messages.length},
      );
    });
  }

  String _getCurrentTime() {
    final now = DateTime.now();
    return '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
  }

  // Optional: Upload method (placeholder)
  Future<void> _uploadAudioToServer(File audioFile) async {
    // Implement your audio upload logic here
    // This could involve Supabase storage, Firebase, or your custom backend
  }

  Future<void> _showRecordingErrorDialog(String errorMessage) async {
    return showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Recording Error'),
          content: Text(
            'Unable to start recording. Please try again.\n\nError: $errorMessage',
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('OK'),
              onPressed: () => Navigator.of(context).pop(),
            ),
          ],
        );
      },
    );
  }

  Future<bool?> _showMicrophonePermissionDialog() {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Microphone Access'),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.of(context).pop(false),
              ),
            ],
          ),
          content: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: Text(
              'Modera needs microphone access to record voice messages.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          actions: <Widget>[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: Center(
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(200, 50),
                  ),
                  child: const Text('Allow'),
                  onPressed: () {
                    Navigator.of(context).pop(true);
                    _requestMicrophonePermission();
                  },
                ),
              ),
            ),
          ],
          actionsAlignment: MainAxisAlignment.center,
          contentPadding: const EdgeInsets.fromLTRB(24.0, 20.0, 24.0, 0.0),
        );
      },
    );
  }

  void _showPermissionDeniedDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Microphone Access Denied'),
          content: const Text(
            'Microphone permission was denied.',
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('OK'),
              onPressed: () => Navigator.of(context).pop(),
            ),
          ],
        );
      },
    );
  }

  void _sendMessage(String message) {
    if (message.trim().isNotEmpty) {
      developer.log(
        'Sending message',
        name: 'ChatScreen',
        error: {'message': message},
      );
    }
  }

  // Method to show typing indicator
  void _showTypingIndicator() {
    setState(() {
      _isTyping = true;
    });
  }

  // Method to hide typing indicator
  void _hideTypingIndicator() {
    setState(() {
      _isTyping = false;
    });
  }

  // Animated typing indicator widget
  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Text(
            'Typing',
            style: TextStyle(
              color: Colors.grey[600],
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(width: 4),
          _AnimatedDots(),
        ],
      ),
    );
  }

  // Method to scroll to the bottom of the chat
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        // Calculate the maximum scroll extent more precisely
        final maxScrollExtent = _scrollController.position.maxScrollExtent;
        
        _scrollController.animateTo(
          maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.fastLinearToSlowEaseIn,
        );
      }
    });
  }

  // Method to scroll with keyboard
  void _scrollToBottomWithKeyboard() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        // Get the current context's render box
        final RenderBox? renderBox = context.findRenderObject() as RenderBox?;
        final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
        
        // Calculate precise scroll extent
        final maxScrollExtent = _scrollController.position.maxScrollExtent;
        final screenHeight = renderBox?.size.height ?? MediaQuery.of(context).size.height;
        
        // Add a small buffer for keyboard and padding
        final targetScrollPosition = maxScrollExtent + (keyboardHeight * 0.5);
        
        _scrollController.animateTo(
          targetScrollPosition,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOutQuad,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Support chat"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/info.svg",
              colorFilter: ColorFilter.mode(
                Theme.of(context).iconTheme.color!,
                BlendMode.srcIn,
              ),
            ),
          ),
        ],
      ),
      body: GestureDetector(
        onTap: () {
          // Dismiss keyboard when tapping outside
          FocusScope.of(context).unfocus();
        },
        child: Column(
          children: [
            const SupportPersonInfo(
              image: "https://lh3.googleusercontent.com/fife/ALs6j_E-_eyMVNrwnkSC0l_5YUrEV0zIT91dToif8ZVK6c2Fi2okgshTr3sC8kV9-5lzzeMgWiuqT-KGo4ZfjOrna3T4tTGDvYQsG8JdOduAImuZh98R_dGF7RHhrciqxW98I_xN4RPZHMyb-YW1MQZyOPPQ8xLa5LUxuM9QWDiQkDaexBG4u0L_wSd7P52WpjWob12i1Kppg04UR-8acqEXgxBw5obEA9hO1D8KDV6FZ8IK9P0dalHoQqASFnqRj1dm7-vDMDuXpMjMLUCC2xfdE-9PvLQ_WtssyEm7cyLL1OVXM_wQ4oPNAr1ZK0ibSx7sZV43GZMJyTENXxIweWVPrHnjh8mZFC_xK_lyt7aaAykW6FrdFFc6jPa4P3O2drUiaiIBA9flDWdVw9wDy-JTsiT4s2uh7I2Nvp8wsSbr9x-CAcZiJKpaZm11Gr4MxpsTIYHyqvKDS-FvWhkSmJLx6l6sW057d4YkGSd6gDWuc9zsBA0WgqxasI-wo1iuFUUizZ65R12Y9bmLACw8Zi9ZK5xK6FROzdkw2H8WDbN-wYvwAcvV5WQFH8_yKkiMgrvV5U7GynI43qpBCB41gfndDgjPQko-CZ9ZDXTqN6sfILBugwH35yxx168TgfQolkTI_HbTUc2bDF1rE45Z6fZCASHManL4BUhBjMgJ-q6OBrVsVIcG9rEhatqLbnwcQKDEW0haHiGabcqVwP3t7AOLDZt6oZrqmXDoURa9JXpbh5OHTR44hQG0OPgU_9Gt7w7OTCYg3aZhVZPrIA3wmLEgVo_dfXiExjNQNR8sZzJKUbDqnfs5Io74HIMCGgIV2JXFZxW2Fp-0ESO9t6ojkFELIeI6DlJ4oMtVA-jee3_RSu5PQIUzI83YRgMpFVbV0geh0Z7Gncia_82WmxS1ZEC85ScUVLsN-9_283fDuEdheOJEyr4kfJrrKOJ7som7RKhy8l3S0RoR94fEJBwHn4pd6O9ToWa9rY5mATurJ7qmIv2uu47arb_iZT2-eipD7vEDwqcS_6t8Il1a7HC-ZRy9iW_KWcnYqtRZ46Soh7-PDaKG_YUI1_iy6almGua17M72n6_hemKlgQczEn99qoGwq1ir0Ed9A-vZawb8GK_9en_8yKLIDAzMkUQ8OwaJLPHbFfnghfjdbhab-CKG5dFg9vMuQZySLNcMQB9gEB3uFOFwK9uw6wEAuh-2cOcxFxMTq20Kn8ry_WkZTtd6AhWmRVwG9Wnr44QxMFvTKxcck17Kto-XxaTNH-7sJVf7_d3cjPayEkl1g_wRDj3ILuyk5w1blPS9gBbsjrGHL_gX9jMh3_E2Gq5SUV6bja07J1JwjYHgJ4U6c_719_pGpIYPiCGCNTOzR-_zQT3vNfzDDVwso6HIQUG2Iq1E6_PIiZlGMivr34Bmoi7bMuln2CpPszLG_FCx02BwmzW2I5uRa1DzXKyU0Xa3lYR5YqzthQDbrHQbkyqFEOu5zzGrBQSLrJ_UQV-dd-4OXrVS5Uo4x9gxm9ukkOrpV4iRMeM3B62kqz_l0xECNL6gdLbDx-LuCbiLrRKv2lztNgl7foQlIJoBjG_c40aXUa6W_xZXW_XD-smbUcNH3hyHN1Idsis=w1621-h1186",
              name: "Evgeniy Dubskiy",
              isConnected: true,
              isActive: true,
              // isTyping: true,
            ),

            // For Better perfromance use [ListView.builder]
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: defaultPadding, 
                        vertical: defaultPadding
                      ),
                      child: _messages.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.chat_bubble_outline,
                                    size: 80,
                                    color: Colors.grey[300],
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'No messages yet',
                                    style: TextStyle(
                                      fontSize: 18,
                                      color: Colors.grey[600],
                                      fontWeight: FontWeight.w300,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Start a conversation by sending a message',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey[500],
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : ListView.builder(
                              controller: _scrollController,
                              physics: const AlwaysScrollableScrollPhysics(), // Ensures scrollability
                              itemCount: _messages.length + (_isTyping ? 1 : 0),
                              itemBuilder: (context, index) {
                                if (index < _messages.length) {
                                  return _messages[index];
                                } else if (_isTyping) {
                                  return _buildTypingIndicator();
                                }
                                return null;
                              },
                            ),
                    ),
            ),
            // Text Field
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: defaultPadding, vertical: defaultPadding / 2),
                child: Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        decoration: InputDecoration(
                          filled: false,
                          hintText: "Write a message...",
                          border: secodaryOutlineInputBorder(context),
                          enabledBorder: secodaryOutlineInputBorder(context),
                          focusedBorder: focusedOutlineInputBorder,
                          suffixIcon: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              // Voice Recording Icon
                              AnimatedMicrophoneIcon(
                                isRecording: _isRecording,
                                onTap: _toggleRecording,
                              ),
                              
                              // Send Message Button
                              IconButton(
                                icon: Icon(
                                  Icons.send,
                                  color: Theme.of(context).primaryColor,
                                ),
                                onPressed: () {
                                  _sendTextMessage(_messageController.text);
                                },
                              ),
                            ],
                          ),
                        ),
                        controller: _messageController,
                      ),
                    ),
                  ],
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}

class AnimatedMicrophoneIcon extends StatefulWidget {
  final bool isRecording;
  final VoidCallback onTap;

  const AnimatedMicrophoneIcon({
    super.key, 
    required this.isRecording, 
    required this.onTap,
  });

  @override
  _AnimatedMicrophoneIconState createState() => _AnimatedMicrophoneIconState();
}

class _AnimatedMicrophoneIconState extends State<AnimatedMicrophoneIcon> {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
        decoration: BoxDecoration(
          color: widget.isRecording 
              ? Colors.red.withOpacity(0.9) 
              : Colors.transparent,
          shape: BoxShape.circle,
          border: Border.all(
            color: widget.isRecording 
                ? Colors.red.withOpacity(0.5) 
                : Colors.transparent,
            width: 2,
          ),
          boxShadow: widget.isRecording
              ? [
                  BoxShadow(
                    color: Colors.red.withOpacity(0.3),
                    blurRadius: 10,
                    spreadRadius: 5,
                  )
                ]
              : [],
        ),
        padding: const EdgeInsets.all(12.0),
        child: Icon(
          Icons.mic,
          color: widget.isRecording 
              ? Colors.white 
              : Theme.of(context).iconTheme.color,
          size: 24,
        ),
      ),
    );
  }
}

// Animated Dots Widget
class _AnimatedDots extends StatefulWidget {
  @override
  __AnimatedDotsState createState() => __AnimatedDotsState();
}

class __AnimatedDotsState extends State<_AnimatedDots> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<int> _dotsAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat();

    _dotsAnimation = IntTween(begin: 1, end: 3).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _dotsAnimation,
      builder: (context, child) {
        return Text(
          '.' * _dotsAnimation.value,
          style: TextStyle(
            color: Colors.grey[600],
            fontWeight: FontWeight.bold,
          ),
        );
      },
    );
  }
}
