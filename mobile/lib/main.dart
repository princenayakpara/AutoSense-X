import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';
import 'providers/auth_provider.dart';
import 'providers/system_provider.dart';

void main() {
  runApp(const AutoSenseXApp());
}

class AutoSenseXApp extends StatelessWidget {
  const AutoSenseXApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => SystemProvider()),
      ],
      child: MaterialApp(
        title: 'AutoSense X',
        theme: ThemeData(
          brightness: Brightness.dark,
          primaryColor: const Color(0xFF00FFFF),
          scaffoldBackgroundColor: const Color(0xFF0a0e27),
          cardColor: const Color(0x1AFFFFFF),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF16213e),
            elevation: 0,
          ),
        ),
        home: const AuthWrapper(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    
    if (authProvider.isAuthenticated) {
      return const DashboardScreen();
    } else {
      return const LoginScreen();
    }
  }
}

