import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:modera/constants/s3_constants.dart';
import 'package:modera/services/s3_service.dart';
import 'package:dio/dio.dart';

/// Преобразует HTTP-запрос в формат cURL для отладки
String toCurlCommand(String method, Uri url, Map<String, String> headers, String? body) {
  final command = StringBuffer('curl --request $method \\\n');
  command.write('  --url $url \\\n');
  
  headers.forEach((key, value) {
    command.write('  --header \'$key: $value\' \\\n');
  });
  
  if (body != null && body.isNotEmpty) {
    command.write('  --data \'$body\'');
  }
  
  return command.toString();
}

enum TryOnCategory {
  upperBody,
  lowerBody,
  fullBody,
}

extension TryOnCategoryExtension on TryOnCategory {
  String get apiValue {
    switch (this) {
      case TryOnCategory.upperBody:
        return 'upper_body';
      case TryOnCategory.lowerBody:
        return 'lower_body';
      case TryOnCategory.fullBody:
        return 'full_body';
    }
  }
}

class TryOnGenerationService {
  static const String baseApiUrl = 'http://api.modera.fashion/v2';
  
  // Хранит последнее сгенерированное изображение для последовательной примерки
  static String? _lastGeneratedImagePath;
  
  /// Проверяет доступность сервера
  static Future<bool> _checkServerAvailability(String host, int port) async {
    try {
      debugPrint('Проверка доступности сервера: $host:$port');
      final socket = await Socket.connect(host, port, timeout: const Duration(seconds: 5));
      debugPrint('Соединение установлено: ${socket.remoteAddress}:${socket.remotePort}');
      await socket.close();
      return true;
    } catch (e) {
      debugPrint('Ошибка при проверке доступности сервера: $e');
      return false;
    }
  }
  
  /// Запускает процесс генерации изображения примерки
  static Future<String> generateTryOn({
    required String userId,
    required String modelImagePath,
    required String garmentImagePath,
    required TryOnCategory category,
  }) async {
    try {
      // Проверяем доступность сервера
      final uri = Uri.parse(baseApiUrl);
      final isServerAvailable = await _checkServerAvailability(uri.host, uri.port == 0 ? 80 : uri.port);
      
      if (!isServerAvailable) {
        debugPrint('!!! СЕРВЕР НЕДОСТУПЕН !!!');
        throw Exception('Сервер недоступен: ${uri.host}:${uri.port == 0 ? 80 : uri.port}');
      }
      
      debugPrint('Запуск генерации изображения примерки:');
      debugPrint('userId: $userId');
      debugPrint('modelImagePath: $modelImagePath');
      debugPrint('garmentImagePath: $garmentImagePath');
      debugPrint('category: ${category.apiValue}');
      
      // Формируем полные URL для изображений
      final modelImageUrl = S3Service.getFileUrl(modelImagePath);
      final garmentImageUrl = S3Service.getFileUrl(garmentImagePath);
      
      debugPrint('modelImageUrl: $modelImageUrl');
      debugPrint('garmentImageUrl: $garmentImageUrl');
      
      // Проверяем, что URL изображений правильно сформированы
      if (!Uri.parse(modelImageUrl).isAbsolute) {
        throw Exception('Неверный URL модели: $modelImageUrl');
      }
      
      if (!Uri.parse(garmentImageUrl).isAbsolute) {
        throw Exception('Неверный URL одежды: $garmentImageUrl');
      }
      
      // Если есть предыдущее сгенерированное изображение и мы примеряем новую одежду,
      // используем его вместо модели
      final String imageToUse = _lastGeneratedImagePath != null && 
                               category != TryOnCategory.fullBody ? 
                               S3Service.getFileUrl(_lastGeneratedImagePath!) : 
                               modelImageUrl;
      
      debugPrint('imageToUse: $imageToUse');
      
      // Пробуем сначала с Dio
      try {
        debugPrint('Пробуем запустить генерацию с Dio...');
        final processId = await _startGenerationWithDio(
          userId: userId,
          modelImage: imageToUse,
          garmentImage: garmentImageUrl,
          category: category.apiValue,
        );
        
        debugPrint('Успешно получен processId с Dio: $processId');
        
        // Ждем завершения процесса и получаем путь к результату
        final resultPath = await _waitForCompletion(processId);
        
        debugPrint('Получен resultPath: $resultPath');
        
        // Сохраняем путь к сгенерированному изображению для последующих примерок
        _lastGeneratedImagePath = resultPath;
        
        return resultPath;
      } catch (dioError) {
        debugPrint('Ошибка при использовании Dio: $dioError');
        debugPrint('Пробуем стандартный HTTP-клиент...');
        
        // Если Dio не сработал, пробуем стандартный HTTP-клиент
        final processId = await _startGeneration(
          userId: userId,
          modelImage: imageToUse,
          garmentImage: garmentImageUrl,
          category: category.apiValue,
        );
        
        // Ждем завершения процесса и получаем путь к результату
        final resultPath = await _waitForCompletion(processId);
        
        debugPrint('Получен resultPath: $resultPath');
        
        // Сохраняем путь к сгенерированному изображению для последующих примерок
        _lastGeneratedImagePath = resultPath;
        
        return resultPath;
      }
    } catch (e) {
      debugPrint('Ошибка генерации изображения примерки: $e');
      rethrow;
    }
  }
  
  /// Запускает процесс генерации и возвращает ID процесса
  static Future<String> _startGeneration({
    required String userId,
    required String modelImage,
    required String garmentImage,
    required String category,
  }) async {
    final url = Uri.parse('$baseApiUrl/run');
    
    debugPrint('=== ДЕТАЛЬНАЯ ОТЛАДКА ЗАПРОСА ===');
    debugPrint('Базовый URL API: $baseApiUrl');
    debugPrint('Полный URL запроса: $url');
    debugPrint('Схема: ${url.scheme}');
    debugPrint('Хост: ${url.host}');
    debugPrint('Порт: ${url.port}');
    debugPrint('Путь: ${url.path}');
    debugPrint('Запрос: ${url.query}');
    
    final payload = {
      'user_id': userId,
      'model_image': modelImage,
      'garment_image': garmentImage,
      'category': category,
      'step': 30,
      'scale': 2.5,
      'seed': 42,
    };
    
    final headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'ModeraMobileApp/1.0',
      'Accept': 'application/json',
      'Connection': 'keep-alive',
    };
    
    final body = jsonEncode(payload);
    
    debugPrint('Отправка запроса на запуск генерации:');
    debugPrint(toCurlCommand('POST', url, headers, body));
    debugPrint('Payload: $payload');
    
    try {
      // Создаем HTTP-клиент с настройкой автоматического следования перенаправлениям
      final client = http.Client();
      
      // Выводим информацию о клиенте
      debugPrint('HTTP клиент создан: $client');
      
      final request = http.Request('POST', url);
      request.headers.addAll(headers);
      request.body = body;
      
      debugPrint('Запрос подготовлен: ${request.method} ${request.url}');
      debugPrint('Заголовки запроса: ${request.headers}');
      
      // Отправляем запрос и следуем перенаправлениям
      debugPrint('Отправка запроса...');
      final streamedResponse = await client.send(request);
      
      debugPrint('Получен ответ: ${streamedResponse.statusCode}');
      debugPrint('Заголовки ответа: ${streamedResponse.headers}');
      
      // Выводим информацию о перенаправлении
      if (streamedResponse.statusCode == 307) {
        debugPrint('!!! ОБНАРУЖЕНО ПЕРЕНАПРАВЛЕНИЕ 307 !!!');
        final location = streamedResponse.headers['location'];
        debugPrint('Новый URL: $location');
        
        // Попробуем выполнить запрос по новому URL
        if (location != null) {
          debugPrint('Пробуем выполнить запрос по новому URL: $location');
          final redirectUrl = Uri.parse(location);
          final redirectRequest = http.Request('POST', redirectUrl);
          redirectRequest.headers.addAll(headers);
          redirectRequest.body = body;
          
          final redirectResponse = await client.send(redirectRequest);
          debugPrint('Ответ после перенаправления: ${redirectResponse.statusCode}');
          
          final response = await http.Response.fromStream(redirectResponse);
          debugPrint('Тело ответа после перенаправления: ${response.body}');
          
          if (response.statusCode == 200) {
            final data = jsonDecode(response.body);
            return data['process_id'];
          }
        }
      }
      
      final response = await http.Response.fromStream(streamedResponse);
      
      debugPrint('Получен ответ с кодом: ${response.statusCode}');
      debugPrint('Тело ответа: ${response.body}');
      debugPrint('=== КОНЕЦ ОТЛАДКИ ЗАПРОСА ===');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['process_id'];
      } else {
        throw Exception('Ошибка запуска генерации: ${response.statusCode} ${response.body}');
      }
    } catch (e) {
      debugPrint('!!! ОШИБКА ПРИ ЗАПУСКЕ ГЕНЕРАЦИИ !!!');
      debugPrint('Тип ошибки: ${e.runtimeType}');
      debugPrint('Сообщение: $e');
      
      // Если это SocketException, выводим дополнительную информацию
      if (e is SocketException) {
        debugPrint('Ошибка сокета: ${e.address}, ${e.port}, ${e.osError}');
      }
      
      rethrow;
    } finally {
      debugPrint('=== КОНЕЦ ОТЛАДКИ ЗАПРОСА ===');
    }
  }
  
  /// Запускает процесс генерации с использованием Dio
  static Future<String> _startGenerationWithDio({
    required String userId,
    required String modelImage,
    required String garmentImage,
    required String category,
  }) async {
    final url = '$baseApiUrl/run';
    
    debugPrint('=== ЗАПУСК ГЕНЕРАЦИИ С DIO ===');
    debugPrint('URL: $url');
    
    final payload = {
      'user_id': userId,
      'model_image': modelImage,
      'garment_image': garmentImage,
      'category': category,
      'step': 30,
      'scale': 2.5,
      'seed': 42,
    };
    
    final dio = Dio();
    
    // Настраиваем Dio для отладки
    dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (obj) => debugPrint(obj.toString()),
    ));
    
    try {
      final response = await dio.post(
        url,
        data: payload,
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'ModeraMobileApp/1.0',
            'Accept': 'application/json',
          },
          followRedirects: true,
          validateStatus: (status) => status != null && status < 500,
        ),
      );
      
      debugPrint('Ответ Dio: ${response.statusCode}');
      debugPrint('Данные ответа: ${response.data}');
      
      if (response.statusCode == 200) {
        return response.data['process_id'];
      } else {
        throw Exception('Ошибка запуска генерации: ${response.statusCode} ${response.data}');
      }
    } catch (e) {
      debugPrint('Ошибка Dio: $e');
      if (e is DioException) {
        debugPrint('Тип ошибки Dio: ${e.type}');
        debugPrint('Сообщение: ${e.message}');
        debugPrint('URL: ${e.requestOptions.uri}');
        debugPrint('Метод: ${e.requestOptions.method}');
        debugPrint('Заголовки: ${e.requestOptions.headers}');
        debugPrint('Данные: ${e.requestOptions.data}');
        
        if (e.response != null) {
          debugPrint('Код ответа: ${e.response!.statusCode}');
          debugPrint('Данные ответа: ${e.response!.data}');
        }
      }
      rethrow;
    } finally {
      debugPrint('=== КОНЕЦ ЗАПУСКА С DIO ===');
    }
  }
  
  /// Периодически проверяет статус процесса и возвращает путь к результату
  static Future<String> _waitForCompletion(String processId) async {
    const maxAttempts = 30; // Максимальное количество попыток (60 секунд при интервале 2 секунды)
    int attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        debugPrint('Попытка #${attempts + 1} проверки статуса для processId: $processId');
        
        final status = await checkStatus(processId);
        
        debugPrint('Проверка статуса #${attempts + 1}: ${status['status']}');
        
        if (status['status'] == 'done') {
          final output = status['output'];
          debugPrint('Генерация завершена, output: $output');
          
          // Формируем полный путь к изображению в S3
          final fullPath = output;
          debugPrint('Полный путь к изображению в S3: $fullPath');
          
          // Получаем полный URL к изображению
          final imageUrl = S3Service.getFileUrl(fullPath);
          debugPrint('URL изображения: $imageUrl');
          
          return fullPath;
        } else if (status['status'] == 'error') {
          throw Exception('Ошибка генерации: ${status['message']}');
        } else {
          debugPrint('Статус генерации: ${status['status']}. Ожидаем завершения...');
        }
        
        // Ждем 2 секунды перед следующей проверкой
        debugPrint('Ожидание 2 секунды перед следующей проверкой...');
        await Future.delayed(const Duration(seconds: 2));
        attempts++;
      } catch (e) {
        debugPrint('Ошибка при проверке статуса: $e');
        rethrow;
      }
    }
    
    throw Exception('Превышено время ожидания генерации (${maxAttempts * 2} секунд)');
  }
  
  /// Проверяет статус процесса генерации с использованием Dio и GET
  static Future<Map<String, dynamic>> checkStatus(String processId) async {
    final url = '$baseApiUrl/status';
    
    debugPrint('=== ПРОВЕРКА СТАТУСА С DIO+GET ===');
    debugPrint('URL: $url');
    
    final dio = Dio();
    
    // Создаем JSON-данные для передачи process_id
    final jsonData = {
      "process_id": processId
    };
    
    // Строка JSON
    final jsonString = jsonEncode(jsonData);
    
    debugPrint('JSON данные:');
    debugPrint(jsonString);
    
    try {
      // Используем метод GET для передачи данных в теле запроса
      final response = await dio.get(
        url,
        options: Options(
          headers: {
            'Content-Type': 'application/json', // Указываем тип контента
            'User-Agent': 'insomnia/10.3.0',   // Указываем User-Agent
            'Accept': 'application/json',
          },
        ),
        data: jsonString,  // Передаем строку JSON напрямую
      );
      
      debugPrint('Ответ Dio: ${response.statusCode}');
      debugPrint('Данные ответа: ${response.data}');
      
      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Ошибка проверки статуса: ${response.statusCode} ${response.data}');
      }
    } catch (e) {
      debugPrint('!!! ОШИБКА ПРИ ПРОВЕРКЕ СТАТУСА С DIO !!!');
      debugPrint('Тип ошибки: ${e.runtimeType}');
      debugPrint('Сообщение: $e');
      
      rethrow;
    } finally {
      debugPrint('=== КОНЕЦ ПРОВЕРКИ СТАТУСА С DIO+GET ===');
    }
  }
  
  /// Сбрасывает последнее сгенерированное изображение
  static void resetLastGeneratedImage() {
    _lastGeneratedImagePath = null;
  }
  
  /// Возвращает полный URL к сгенерированному изображению
  static String getGeneratedImageUrl(String path) {
    return S3Service.getFileUrl(path);
  }
} 