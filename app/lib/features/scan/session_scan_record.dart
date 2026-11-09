import 'dart:typed_data';
import 'package:ricedisease/services/inference_service.dart';

/// Computes standard FIPS 180-4 SHA-256 hex digest of [data].
String computeSha256(Uint8List data) {
  final initialHash = <int>[
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ];

  final k = <int>[
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ];

  int rotr(int x, int n) => ((x >>> n) | (x << (32 - n))) & 0xFFFFFFFF;

  final bitLength = data.length * 8;
  final padLength = (data.length + 9) % 64 == 0 ? 0 : 64 - ((data.length + 9) % 64);
  final totalLength = data.length + 1 + padLength + 8;
  final padded = Uint8List(totalLength);
  padded.setRange(0, data.length, data);
  padded[data.length] = 0x80;

  final byteData = ByteData.sublistView(padded);
  byteData.setUint64(totalLength - 8, bitLength, Endian.big);

  final h = List<int>.from(initialHash);
  final w = List<int>.filled(64, 0);

  for (var i = 0; i < totalLength; i += 64) {
    for (var t = 0; t < 16; t++) {
      w[t] = byteData.getUint32(i + t * 4, Endian.big);
    }
    for (var t = 16; t < 64; t++) {
      final s0 = rotr(w[t - 15], 7) ^ rotr(w[t - 15], 18) ^ (w[t - 15] >>> 3);
      final s1 = rotr(w[t - 2], 17) ^ rotr(w[t - 2], 19) ^ (w[t - 2] >>> 10);
      w[t] = (w[t - 16] + s0 + w[t - 7] + s1) & 0xFFFFFFFF;
    }

    var a = h[0];
    var b = h[1];
    var c = h[2];
    var d = h[3];
    var e = h[4];
    var f = h[5];
    var g = h[6];
    var hVar = h[7];

    for (var t = 0; t < 64; t++) {
      final s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      final ch = (e & f) ^ (~e & g);
      final temp1 = (hVar + s1 + ch + k[t] + w[t]) & 0xFFFFFFFF;
      final s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      final maj = (a & b) ^ (a & c) ^ (b & c);
      final temp2 = (s0 + maj) & 0xFFFFFFFF;

      hVar = g;
      g = f;
      f = e;
      e = (d + temp1) & 0xFFFFFFFF;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) & 0xFFFFFFFF;
    }

    h[0] = (h[0] + a) & 0xFFFFFFFF;
    h[1] = (h[1] + b) & 0xFFFFFFFF;
    h[2] = (h[2] + c) & 0xFFFFFFFF;
    h[3] = (h[3] + d) & 0xFFFFFFFF;
    h[4] = (h[4] + e) & 0xFFFFFFFF;
    h[5] = (h[5] + f) & 0xFFFFFFFF;
    h[6] = (h[6] + g) & 0xFFFFFFFF;
    h[7] = (h[7] + hVar) & 0xFFFFFFFF;
  }

  final buffer = StringBuffer();
  for (final word in h) {
    buffer.write(word.toRadixString(16).padLeft(8, '0'));
  }
  return buffer.toString();
}

/// In-memory record of an analyzed photo for the current session.
class SessionScanRecord {
  final String filename;
  final int byteSize;
  final String sha256;
  final DateTime timestamp;
  final InferenceResult result;

  const SessionScanRecord({
    required this.filename,
    required this.byteSize,
    required this.sha256,
    required this.timestamp,
    required this.result,
  });

  /// Factory creating record from image bytes and prediction result.
  factory SessionScanRecord.create({
    required String filename,
    required Uint8List bytes,
    required InferenceResult result,
    DateTime? timestamp,
  }) {
    return SessionScanRecord(
      filename: filename,
      byteSize: bytes.lengthInBytes,
      sha256: computeSha256(bytes),
      timestamp: timestamp ?? DateTime.now(),
      result: result,
    );
  }
}

/// Navigation arguments passed to ResultScreen.
class ResultScreenArguments {
  final InferenceResult result;
  final SessionScanRecord? sessionRecord;

  const ResultScreenArguments({
    required this.result,
    this.sessionRecord,
  });
}

/// In-memory storage for session scan records (kept only during process lifetime).
class SessionScanStore {
  static final List<SessionScanRecord> _records = [];

  static List<SessionScanRecord> get records => List.unmodifiable(_records);

  static void addRecord(SessionScanRecord record) {
    _records.add(record);
  }

  static void clear() {
    _records.clear();
  }
}
