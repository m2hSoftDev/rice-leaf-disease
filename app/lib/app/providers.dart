import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/services/preprocess_service.dart';

/// Riverpod provider for [PreprocessService].
final preprocessServiceProvider = Provider<PreprocessService>((ref) {
  return PreprocessService();
});
