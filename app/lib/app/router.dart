import 'package:flutter/material.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/features/about/about_screen.dart';
import 'package:ricedisease/features/history/history_screen.dart';
import 'package:ricedisease/features/home/home_screen.dart';
import 'package:ricedisease/features/onboarding/onboarding_screen.dart';
import 'package:ricedisease/features/result/result_screen.dart';
import 'package:ricedisease/features/splash/splash_screen.dart';

/// App router handling route mapping across the 6 application screens.
class AppRouter {
  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.splash:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => const SplashScreen(),
        );
      case AppRoutes.onboarding:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => const OnboardingScreen(),
        );
      case AppRoutes.home:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => const HomeScreen(),
        );
      case AppRoutes.result:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => const ResultScreen(),
        );
      case AppRoutes.history:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => const HistoryScreen(),
        );
      case AppRoutes.about:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => const AboutScreen(),
        );
      default:
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => Scaffold(
            body: Center(
              child: Text('No route defined for ${settings.name}'),
            ),
          ),
        );
    }
  }
}

