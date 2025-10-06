import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:modera/constants/s3_constants.dart';

class S3Service {
  // Кэш для хранения результатов проверки доступности изображений
  static final Map<String, bool> _imageAvailabilityCache = {};
  
  /// Получает URL для изображения из S3
  static String getImageUrl(String path) {
    // Убираем префикс assets/ если он есть и формируем правильный путь
    final cleanPath = path.startsWith('assets/tryon/')
        ? path
        : path;
        
    return '${S3Constants.bucketUrl}/$cleanPath';
  }
  
  /// Проверяет существование файла в S3 с использованием кэша
  static Future<bool> fileExists(String path) async {
    // Проверяем кэш
    if (_imageAvailabilityCache.containsKey(path)) {
      return _imageAvailabilityCache[path]!;
    }
    
    try {
      final url = getFileUrl(path);
      final response = await http.head(Uri.parse(url));
      final isAvailable = response.statusCode >= 200 && response.statusCode < 300;
      
      // Сохраняем результат в кэш
      _imageAvailabilityCache[path] = isAvailable;
      
      return isAvailable;
    } catch (e) {
      // Сохраняем отрицательный результат в кэш
      _imageAvailabilityCache[path] = false;
      return false;
    }
  }
  
  /// Получает список файлов из директории в S3
  static Future<List<String>> listFiles(String directory) async {
    try {
      final url = '${S3Constants.bucketUrl}/$directory';
      debugPrint('Listing files from: $url');
      final response = await http.get(Uri.parse(url));
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        final List<dynamic> data = json.decode(response.body);
        return data.cast<String>();
      }
      return [];
    } catch (e) {
      debugPrint('Error listing files: $e');
      return [];
    }
  }
  
  /// Формирует полный URL для доступа к файлу в S3 бакете
  static String getFileUrl(String filePath) {
    // Убедимся, что путь не начинается с '/'
    final normalizedPath = filePath.startsWith('/') ? filePath.substring(1) : filePath;
    return '${S3Constants.bucketUrl}/$normalizedPath';
  }
  
  /// Формирует URL для изображений примерки одежды
  static String getTryOnClothesUrl(String category, String fileName) {
    return getFileUrl('assets/tryon/clothes/$category/$fileName');
  }
  
  /// Формирует URL для изображений моделей
  static String getModelImageUrl(String fileName) {
    return getFileUrl('assets/tryon/models/$fileName');
  }
  
  /// Формирует URL для миниатюр моделей
  static String getModelThumbnailUrl(String fileName) {
    return getFileUrl('assets/tryon/models-tiles/$fileName');
  }
  
  /// Фильтрует список путей, оставляя только доступные изображения
  /// Использует параллельные запросы для ускорения
  static Future<List<String>> filterAvailableImages(List<String> paths) async {
    // Создаем список задач для параллельного выполнения
    final futures = paths.map((path) async {
      // Проверяем кэш
      if (_imageAvailabilityCache.containsKey(path)) {
        return _imageAvailabilityCache[path]! ? path : null;
      }
      
      final url = getFileUrl(path);
      try {
        final response = await http.head(Uri.parse(url));
        final isAvailable = response.statusCode >= 200 && response.statusCode < 300;
        
        // Сохраняем результат в кэш
        _imageAvailabilityCache[path] = isAvailable;
        
        return isAvailable ? path : null;
      } catch (e) {
        // Сохраняем отрицательный результат в кэш
        _imageAvailabilityCache[path] = false;
        return null;
      }
    }).toList();
    
    // Ждем завершения всех запросов
    final results = await Future.wait(futures);
    
    // Фильтруем null значения
    return results.where((path) => path != null).cast<String>().toList();
  }
} 