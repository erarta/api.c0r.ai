import 'package:flutter/material.dart';
import 'package:modera/services/s3_service.dart';
import 'package:modera/widgets/s3_image.dart';

class S3ImageWithCheck extends StatefulWidget {
  final String path;
  final double? width;
  final double? height;
  final BoxFit fit;
  
  const S3ImageWithCheck({
    Key? key,
    required this.path,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
  }) : super(key: key);
  
  @override
  State<S3ImageWithCheck> createState() => _S3ImageWithCheckState();
}

class _S3ImageWithCheckState extends State<S3ImageWithCheck> {
  bool _isLoading = true;
  bool _isAvailable = false;
  
  @override
  void initState() {
    super.initState();
    _checkImageAvailability();
  }
  
  Future<void> _checkImageAvailability() async {
    final isAvailable = await S3Service.fileExists(widget.path);
    
    if (mounted) {
      setState(() {
        _isAvailable = isAvailable;
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return SizedBox(
        width: widget.width,
        height: widget.height,
      );
    }
    
    if (!_isAvailable) {
      return const SizedBox.shrink();
    }
    
    return S3Image(
      path: widget.path,
      width: widget.width,
      height: widget.height,
      fit: widget.fit,
    );
  }
} 