import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/auth_provider.dart';
import '../providers/system_provider.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final systemProvider = Provider.of<SystemProvider>(context, listen: false);
      systemProvider.loadSystemInfo();
      systemProvider.loadAlerts();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AutoSense X'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Provider.of<AuthProvider>(context, listen: false).logout();
            },
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0a0e27),
              Color(0xFF16213e),
            ],
          ),
        ),
        child: RefreshIndicator(
          onRefresh: () async {
            final systemProvider = Provider.of<SystemProvider>(context, listen: false);
            await systemProvider.loadSystemInfo();
            await systemProvider.loadAlerts();
          },
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'System Dashboard',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF00FFFF),
                  ),
                ),
                const SizedBox(height: 16),
                Consumer<SystemProvider>(
                  builder: (context, provider, _) {
                    if (provider.isLoading) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    
                    final system = provider.systemInfo?['system'];
                    if (system == null) {
                      return const Center(child: Text('No data available'));
                    }
                    
                    return Column(
                      children: [
                        _buildStatCard(
                          'CPU',
                          '${system['cpu_percent']?.toStringAsFixed(1) ?? 0}%',
                          Icons.memory,
                          system['cpu_percent']?.toDouble() ?? 0,
                        ),
                        const SizedBox(height: 16),
                        _buildStatCard(
                          'Memory',
                          '${system['memory_percent']?.toStringAsFixed(1) ?? 0}%',
                          Icons.storage,
                          system['memory_percent']?.toDouble() ?? 0,
                        ),
                        const SizedBox(height: 16),
                        _buildStatCard(
                          'Disk',
                          '${system['disk_percent']?.toStringAsFixed(1) ?? 0}%',
                          Icons.hard_drive,
                          system['disk_percent']?.toDouble() ?? 0,
                        ),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 24),
                const Text(
                  'Quick Actions',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: _buildActionButton(
                        'Boost RAM',
                        Icons.speed,
                        () => _boostRAM(),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildActionButton(
                        'Clean Junk',
                        Icons.cleaning_services,
                        () => _cleanJunk(),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: _buildActionButton(
                    'Auto Optimize',
                    Icons.auto_fix_high,
                    () => _autoOptimize(),
                  ),
                ),
                const SizedBox(height: 24),
                Consumer<SystemProvider>(
                  builder: (context, provider, _) {
                    if (provider.alerts.isEmpty) {
                      return const SizedBox();
                    }
                    
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Alerts',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ...provider.alerts.take(5).map((alert) => _buildAlertCard(alert)),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, double percent) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF00FFFF), size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(color: Colors.white70, fontSize: 14),
                ),
                Text(
                  value,
                  style: const TextStyle(
                    color: Color(0xFF00FFFF),
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          SizedBox(
            width: 60,
            height: 60,
            child: CircularProgressIndicator(
              value: percent / 100,
              strokeWidth: 6,
              backgroundColor: Colors.white.withOpacity(0.1),
              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(String label, IconData icon, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF00FFFF),
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.black),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertCard(Map<String, dynamic> alert) {
    final type = alert['type'] ?? alert['alert_type'] ?? 'info';
    Color color;
    if (type == 'critical') {
      color = Colors.red;
    } else if (type == 'warning') {
      color = Colors.orange;
    } else {
      color = const Color(0xFF00FFFF);
    }
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(Icons.warning, color: color),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert['title'] ?? 'Alert',
                  style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  alert['message'] ?? '',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _boostRAM() async {
    final provider = Provider.of<SystemProvider>(context, listen: false);
    final success = await provider.boostRAM();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'RAM boosted successfully!' : 'Failed to boost RAM'),
        ),
      );
    }
  }

  Future<void> _cleanJunk() async {
    final provider = Provider.of<SystemProvider>(context, listen: false);
    final success = await provider.cleanJunkFiles();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'Junk files cleaned!' : 'Failed to clean junk files'),
        ),
      );
    }
  }

  Future<void> _autoOptimize() async {
    final provider = Provider.of<SystemProvider>(context, listen: false);
    final success = await provider.autoOptimize();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'System optimized!' : 'Failed to optimize'),
        ),
      );
    }
  }
}

