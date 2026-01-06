import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class SystemProvider with ChangeNotifier {
  Map<String, dynamic>? _systemInfo;
  Map<String, dynamic>? _aiPrediction;
  List<dynamic> _alerts = [];
  bool _isLoading = false;

  Map<String, dynamic>? get systemInfo => _systemInfo;
  Map<String, dynamic>? get aiPrediction => _aiPrediction;
  List<dynamic> get alerts => _alerts;
  bool get isLoading => _isLoading;

  Future<void> loadSystemInfo() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      _systemInfo = await ApiService.getSystemInfo();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading system info: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadAIPrediction() async {
    try {
      final response = await ApiService.getAIPrediction();
      if (response['success'] == true) {
        _aiPrediction = response['prediction'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading AI prediction: $e');
    }
  }

  Future<void> loadAlerts() async {
    try {
      final response = await ApiService.getAlerts();
      if (response['success'] == true) {
        _alerts = [
          ...(response['current_alerts'] ?? []),
          ...(response['stored_alerts'] ?? []),
        ];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading alerts: $e');
    }
  }

  Future<bool> boostRAM() async {
    try {
      final response = await ApiService.boostRAM();
      if (response['success'] == true) {
        await loadSystemInfo();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<bool> cleanJunkFiles() async {
    try {
      final response = await ApiService.cleanJunkFiles();
      if (response['success'] == true) {
        await loadSystemInfo();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<bool> autoOptimize() async {
    try {
      final response = await ApiService.autoOptimize();
      if (response['success'] == true) {
        await loadSystemInfo();
        await loadAIPrediction();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}

