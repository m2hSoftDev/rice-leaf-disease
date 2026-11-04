import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'constants.dart';

final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('sharedPreferencesProvider must be overridden in ProviderScope');
});

class LocaleNotifier extends StateNotifier<Locale> {
  final SharedPreferences _prefs;

  LocaleNotifier(this._prefs) : super(_loadInitialLocale(_prefs));

  static Locale _loadInitialLocale(SharedPreferences prefs) {
    final languageCode = prefs.getString(PrefKeys.selectedLocale);
    if (languageCode == 'bn') {
      return const Locale('bn');
    }
    return const Locale('en');
  }

  Future<void> setLocale(Locale locale) async {
    if (locale.languageCode != 'en' && locale.languageCode != 'bn') return;
    state = locale;
    await _prefs.setString(PrefKeys.selectedLocale, locale.languageCode);
  }

  Future<void> toggleLocale() async {
    final next = state.languageCode == 'en' ? const Locale('bn') : const Locale('en');
    await setLocale(next);
  }
}

final localeProvider = StateNotifierProvider<LocaleNotifier, Locale>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return LocaleNotifier(prefs);
});

