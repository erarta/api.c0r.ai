import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:modera/services/s3_service.dart';

class S3Image extends StatelessWidget {
  final String path;
  final double? width;
  final double? height;
  final BoxFit fit;
  
  const S3Image({
    Key? key,
    required this.path,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    final imageUrl = S3Service.getFileUrl(path);
    debugPrint('Loading image from: $imageUrl');
    
    return CachedNetworkImage(
      imageUrl: imageUrl,
      width: width,
      height: height,
      fit: fit,
      placeholder: (context, url) => const Center(
        child: CircularProgressIndicator(),
      ),
      errorWidget: (context, url, error) {
        debugPrint('Error loading image: $error');
        // Пробуем загрузить локальное изображение как запасной вариант
        if (path.startsWith('assets/')) {
          return Image.asset(
            path,
            width: width,
            height: height,
            fit: fit,
            errorBuilder: (context, error, stackTrace) => _buildErrorWidget(error),
          );
        }
        return _buildErrorWidget(error);
      },
    );
  }
  
  Widget _buildErrorWidget(dynamic error) {
    return Container(
      color: Colors.grey[300],
      child: Center(
        child: SelectableText.rich(
          TextSpan(
            text: 'Ошибка загрузки изображения\n',
            style: const TextStyle(color: Colors.red),
            children: [
              TextSpan(
                text: error.toString(),
                style: const TextStyle(fontSize: 12),
              ),
            ],
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
} 