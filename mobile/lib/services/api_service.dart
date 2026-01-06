import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }

  static Future<Map<String, String>> getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'username=$username&password=$password',
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Login failed');
    }
  }

  static Future<Map<String, dynamic>> getSystemInfo() async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/api/system/info'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load system info');
    }
  }

  static Future<Map<String, dynamic>> getAIPrediction() async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/api/ai/predict'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to get AI prediction');
    }
  }

  static Future<Map<String, dynamic>> getAlerts() async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/api/alerts'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load alerts');
    }
  }

  static Future<Map<String, dynamic>> boostRAM() async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/api/boost-ram'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to boost RAM');
    }
  }

  static Future<Map<String, dynamic>> cleanJunkFiles() async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/api/junk-files/clean'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to clean junk files');
    }
  }

  static Future<Map<String, dynamic>> autoOptimize() async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/api/ai/auto-optimize'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to auto optimize');
    }
  }
}

