import 'package:flutter/material.dart';

import 'features/run_analysis/run_analysis_page.dart';

class AppShell extends StatelessWidget {
  const AppShell({super.key});

  @override
  Widget build(BuildContext context) {
    final baseTextTheme = Typography.material2021().black;

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Edge Workspace Studio',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme:
            ColorScheme.fromSeed(
              seedColor: const Color(0xFF0F766E),
              brightness: Brightness.light,
              surface: const Color(0xFFF8F4EC),
            ).copyWith(
              primary: const Color(0xFF0F766E),
              secondary: const Color(0xFFE07A5F),
              tertiary: const Color(0xFFF2CC8F),
              surface: const Color(0xFFF8F4EC),
              onSurface: const Color(0xFF1F2933),
            ),
        scaffoldBackgroundColor: const Color(0xFFF3EDE1),
        textTheme: baseTextTheme.copyWith(
          displayLarge: const TextStyle(
            fontSize: 54,
            fontWeight: FontWeight.w700,
            letterSpacing: -1.8,
          ),
          displayMedium: const TextStyle(
            fontSize: 34,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.8,
          ),
          titleLarge: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.4,
          ),
          bodyLarge: baseTextTheme.bodyLarge?.copyWith(
            fontSize: 16,
            height: 1.45,
            color: const Color(0xFF425466),
          ),
          bodyMedium: baseTextTheme.bodyMedium?.copyWith(
            fontSize: 14,
            height: 1.45,
            color: const Color(0xFF52606D),
          ),
        ),
      ),
      home: const RunAnalysisPage(),
    );
  }
}
