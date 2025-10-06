import 'dart:io';
import 'dart:developer' as developer;
import 'package:dio/dio.dart';
import 'package:modera/utils/logger.dart';
import 'dart:convert' as json;

class ApiService {
  static const String baseUrl = 'http://165.232.135.9:4242/';
  
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 20),  // Increased from 10 to 20
      receiveTimeout: const Duration(seconds: 20),  // Increased from 10 to 20
    ),
  );

  ApiService() {
    _dio.interceptors.add(LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (options.data is FormData) {
          final formData = options.data as FormData;
          developer.log(
            'Multipart Form Data Details',
            name: 'ApiService',
            error: {
              'Fields': formData.fields.map((f) => '${f.key}: ${f.value}').toList(),
              'Files': formData.files.map((f) => '${f.key}: ${f.value.filename}').toList(),
            },
          );
        }
        
        _logDetailedRequest(options);
        return handler.next(options);
      },
      onResponse: (response, handler) {
        _logDetailedResponse(response);
        return handler.next(response);
      },
      onError: (DioException e, handler) {
        _logDetailedError(e);
        return handler.next(e);
      },
    ));
  }

  void _logDetailedRequest(RequestOptions options) {
    developer.log(
      'API REQUEST',
      name: 'ApiService',
      time: DateTime.now(),
      error: {
        'URL': options.uri.toString(),
        'Method': options.method,
        'Headers': options.headers,
      },
    );
    
    if (options.data != null) {
      if (options.data is FormData) {
        final formData = options.data as FormData;
        formData.fields.forEach((field) {
          developer.log(
            'Form Field: ${field.key} = ${field.value}',
            name: 'ApiService',
          );
        });
        formData.files.forEach((file) {
          developer.log(
            'File Field: ${file.key} - ${file.value.filename}',
            name: 'ApiService',
          );
        });
      } else {
        developer.log(
          'Request Data: ${options.data}',
          name: 'ApiService',
        );
      }
    }
  }

  void _logDetailedResponse(Response response) {
    developer.log(
      'API RESPONSE',
      name: 'ApiService',
      time: DateTime.now(),
      error: {
        'URL': response.requestOptions.uri.toString(),
        'Status Code': response.statusCode,
        'Response Data': response.data,
      },
    );
  }

  void _logDetailedError(DioException e) {
    developer.log(
      'API ERROR',
      name: 'ApiService',
      time: DateTime.now(),
      error: {
        'URL': e.requestOptions.uri.toString(),
        'Error Type': e.type,
        'Error Message': e.message,
        'Response Data': e.response?.data,
      },
    );
  }

  Future<Map<String, dynamic>?> sendTextMessage({
    required String userId, 
    required String userMessage,
    String path = '/api/messages',
  }) async {
    try {
      // final bodyJson = const json.JsonEncoder().convert({
      //   'user_id': userId,
      //   'user_message': userMessage,
      // });

      final formData = FormData.fromMap({
        // 'body': bodyJson,
        'user_id': userId,
        'user_message': userMessage,
      });

      developer.log(
        'Sending Text Message Form Data',
        name: 'NetworkDebug',
        error: {
          // 'body': bodyJson,
          'user_id': userId,
          'user_message': userMessage,
        },
      );

      final response = await _dio.post(
        path,
        data: formData,
        options: Options(
          contentType: Headers.multipartFormDataContentType
        ),
      );

      return response.data;
    } on DioException catch (e) {
      developer.log(
        'Dio Error Details', 
        name: 'NetworkDebug',
        error: {
          'Error Type': e.type,
          'Message': e.message,
          'Response': e.response?.data,
          'Request Data': e.requestOptions.data,
        }
      );
      return null;
    } catch (e) {
      developer.log(
        'Unexpected Error: $e', 
        name: 'NetworkDebug'
      );
      return null;
    }
  }

  Future<Map<String, dynamic>?> transcribeAudioMessage({
    required String userId, 
    required File audioFile,
    String path = '/api/messages',
  }) async {
    try {
      final fileName = audioFile.path.split('/').last;
      final fileSize = await audioFile.length();
      
      // final bodyJson = const json.JsonEncoder().convert({
      //   'user_id': userId,
      //   'user_message': null,
      // });

      final multipartFile = await MultipartFile.fromFile(
        audioFile.path, 
        filename: fileName,
      );

      final formData = FormData.fromMap({
        // 'body': bodyJson,
        'user_id': userId,
        'file': multipartFile,
      });

      developer.log(
        'Audio Transcription Request Details',
        name: 'NetworkDebug',
        error: {
          'User ID': userId,
          'File Name': fileName,
          'File Path': audioFile.path,
          'File Size': '$fileSize bytes',
          // 'Body JSON': bodyJson,
          'user_id': userId,
          'Multipart File': {
            'Name': multipartFile.filename,
            'Content Type': multipartFile.contentType?.toString(),
          },
          'Form Data Fields': formData.fields.map((f) => '${f.key}: ${f.value}').toList(),
          'Form Data Files': formData.files.map((f) => f.key).toList(),
        },
      );

      final response = await _dio.post(
        path,
        data: formData,
        options: Options(
          contentType: Headers.multipartFormDataContentType,
          headers: {
            'X-Debug-Fields': formData.fields.map((f) => '${f.key}=${f.value}').join(';'),
          },
        ),
      );

      developer.log(
        'Audio Transcription Response',
        name: 'NetworkDebug',
        error: {
          'Status Code': response.statusCode,
          'Response Data': response.data,
        },
      );

      return response.data;
    } on DioException catch (e) {
      developer.log(
        'Dio Error in Audio Transcription', 
        name: 'NetworkDebug',
        error: {
          'Error Type': e.type,
          'Message': e.message,
          'Response': e.response?.data,
          'Request Data': e.requestOptions.data,
          'Request Headers': e.requestOptions.headers,
        }
      );
      return null;
    } catch (e) {
      developer.log(
        'Unexpected Error in Audio Transcription: $e', 
        name: 'NetworkDebug',
        error: {
          'Error Details': e.toString(),
          'Error Type': e.runtimeType,
        }
      );
      return null;
    }
  }
} 