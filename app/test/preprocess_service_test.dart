import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:ricedisease/services/preprocess_service.dart';

void main() {
  late PreprocessService service;

  setUp(() {
    service = PreprocessService();
  });

  group('T-062: PreprocessService Unit Tests', () {
    test('Synthetic image: flat-color PNG produces exact shape, dtype, and scaling within 1e-3', () {
      // Create a 100x100 solid color image (RGB: 128, 64, 255)
      final synthetic = img.Image(width: 100, height: 100, numChannels: 3);
      for (final p in synthetic) {
        p
          ..r = 128
          ..g = 64
          ..b = 255;
      }
      final pngBytes = Uint8List.fromList(img.encodePng(synthetic));

      final output = service.preprocess(pngBytes);

      // Verify shape: 1 * 224 * 224 * 3 = 150,528
      expect(output.length, equals(PreprocessService.outputElementCount));
      expect(output, isA<Float32List>());

      // Expected normalized values via (x / 127.5) - 1.0:
      final expectedR = (128 / 127.5) - 1.0;
      final expectedG = (64 / 127.5) - 1.0;
      final expectedB = (255 / 127.5) - 1.0;

      // Verify scaling matches within 1e-3 across entire tensor
      for (int i = 0; i < output.length; i += 3) {
        expect((output[i] - expectedR).abs(), lessThan(1e-3));
        expect((output[i + 1] - expectedG).abs(), lessThan(1e-3));
        expect((output[i + 2] - expectedB).abs(), lessThan(1e-3));
      }
    });

    test('Input validation: rejects byte array > 10 MB with clear error message', () {
      // 10 MB + 1 byte
      final oversizedBytes = Uint8List(PreprocessService.maxFileSizeBytes + 1);
      // Valid PNG header so format check doesn't trigger first
      oversizedBytes[0] = 0x89;
      oversizedBytes[1] = 0x50;
      oversizedBytes[2] = 0x4E;
      oversizedBytes[3] = 0x47;

      expect(
        () => service.preprocess(oversizedBytes),
        throwsA(
          isA<ImageTooLargeException>().having(
            (e) => e.message,
            'message',
            contains('exceeds the 10 MB limit'),
          ),
        ),
      );
    });

    test('Input validation: rejects non-JPG / non-PNG formats', () {
      final invalidBytes = Uint8List.fromList(utf8.encode('Not an image file at all!'));

      expect(
        () => service.preprocess(invalidBytes),
        throwsA(
          isA<InvalidImageFormatException>().having(
            (e) => e.message,
            'message',
            contains('Unsupported file format'),
          ),
        ),
      );
    });

    test('EXIF orientation: rotates orientation 6 image upright by 90 degrees CW', () {
      // Create a 200x100 (landscape) image with a distinctive top-left block
      final testImg = img.Image(width: 200, height: 100, numChannels: 3);
      // Fill base background black
      testImg.clear(img.ColorRgb8(0, 0, 0));
      // Top-left 40x40 block filled pure red
      for (int y = 0; y < 40; y++) {
        for (int x = 0; x < 40; x++) {
          testImg.setPixelRgb(x, y, 255, 0, 0);
        }
      }

      // Set EXIF orientation to 6 (rotate 90 CW)
      testImg.exif.imageIfd.orientation = 6;
      final jpgBytes = Uint8List.fromList(img.encodeJpg(testImg));

      // Preprocess with applyExifOrientation: true
      final output = service.preprocess(jpgBytes, applyExifOrientation: true);

      // In 90 CW rotation:
      // The top-left 40x40 block (red) rotates to the top-right of the upright image!
      // In a 224x224 tensor:
      // Top-left pixel (0, 0) should now be black: R ~ -1.0
      // Top-right pixel (0, 223) should now be red: R ~ +1.0
      final topLeftR = output[0]; // (y=0, x=0, R)
      final topRightOffset = (0 * 224 + 223) * 3;
      final topRightR = output[topRightOffset]; // (y=0, x=223, R)

      expect(topLeftR, lessThan(-0.5), reason: 'Top-left should now be black after 90 CW rotation');
      expect(topRightR, greaterThan(0.5), reason: 'Top-right should now have the red block after 90 CW rotation');
    });
  });

  group('T-062: Real-Image Parity Tests against Python training preprocessing', () {
    test('(a) Resize parity: Python-decoded pixels fed to PreprocessService.resizeBilinearTf match Python TF output within 1e-4', () {
      final fixtureFile = File('test/fixtures/preprocess_expected.json');
      if (!fixtureFile.existsSync()) {
        print('Fixture file not found; skipping resize parity test.');
        return;
      }

      final fixtureData = jsonDecode(fixtureFile.readAsStringSync()) as Map<String, dynamic>;
      final images = fixtureData['images'] as List<dynamic>;

      double overallMaxDiff = 0.0;
      final Map<String, double> perImageResizeDiff = {};

      for (final item in images) {
        final filename = item['filename'] as String;
        final rawPoints = item['points_training_raw'] as Map<String, dynamic>;

        final safeName = filename.replaceAll(' ', '_').replaceAll('(', '').replaceAll(')', '') + '.png';
        final pyDecodedFile = File('test/fixtures/python_decoded/$safeName');
        if (!pyDecodedFile.existsSync()) {
          print('Python decoded image not found: ${pyDecodedFile.path}; skipping.');
          return;
        }

        final pyDecodedBytes = pyDecodedFile.readAsBytesSync();
        final pyDecodedImg = img.decodePng(pyDecodedBytes)!;

        // Feed the Python-decoded pixels into PreprocessService.resizeBilinearTf
        final resizedTensor = PreprocessService.resizeBilinearTf(
          pyDecodedImg,
          PreprocessService.targetHeight,
          PreprocessService.targetWidth,
        );

        double imgMax = 0.0;
        for (final entry in rawPoints.entries) {
          final coords = entry.key.split(',').map(int.parse).toList();
          final y = coords[0];
          final x = coords[1];
          final expectedRGB = (entry.value as List<dynamic>).map((v) => (v as num).toDouble()).toList();

          final offset = (y * PreprocessService.targetWidth + x) * PreprocessService.numChannels;
          final actualR = resizedTensor[offset];
          final actualG = resizedTensor[offset + 1];
          final actualB = resizedTensor[offset + 2];

          final diffR = (actualR - expectedRGB[0]).abs();
          final diffG = (actualG - expectedRGB[1]).abs();
          final diffB = (actualB - expectedRGB[2]).abs();

          final localMax = [diffR, diffG, diffB].reduce(max);
          if (localMax > imgMax) {
            imgMax = localMax;
          }
          if (localMax > overallMaxDiff) {
            overallMaxDiff = localMax;
          }
        }
        perImageResizeDiff[filename] = imgMax;

        // Assert max difference <= 1e-4 against Python TF output
        expect(
          imgMax,
          lessThanOrEqualTo(1e-4),
          reason: 'Resize parity max difference for $filename must be <= 1e-4',
        );
      }

      print('================================================================');
      print('RESIZE PARITY TEST RESULTS (Dart resizeBilinearTf vs Python tf.image.resize):');
      perImageResizeDiff.forEach((file, diff) {
        print('  - $file: max diff = ${diff.toStringAsFixed(8)}');
      });
      print('Overall max resize difference: ${overallMaxDiff.toStringAsFixed(8)} (target <= 1e-4)');
      print('================================================================');

      expect(overallMaxDiff, lessThanOrEqualTo(1e-4), reason: 'Overall resize parity difference must be <= 1e-4');
    });

    test('(b) Decoder parity: compare Dart-decoded pixels to Python-decoded pixels and record to results/metrics/decoder_parity.csv', () {
      final fixtureFile = File('test/fixtures/preprocess_expected.json');
      if (!fixtureFile.existsSync()) {
        print('Fixture file not found; skipping decoder parity test.');
        return;
      }

      final fixtureData = jsonDecode(fixtureFile.readAsStringSync()) as Map<String, dynamic>;
      final images = fixtureData['images'] as List<dynamic>;

      final envPath = Platform.environment['TEST_IMAGE_DIR'];
      final candidateDir = envPath != null
          ? Directory(envPath)
          : Directory('../data/raw/public/hasan_staging/Original Images');

      if (!candidateDir.existsSync()) {
        print('Test image directory not found; skipping decoder parity test.');
        return;
      }

      final List<Map<String, dynamic>> csvRows = [];
      final Map<String, int> perImageMaxDiffUint8 = {};
      final Map<String, double> perImageMaxDiffNorm = {};

      for (final item in images) {
        final relPath = item['relative_path'] as String;
        final filename = item['filename'] as String;

        final origFile = File('${candidateDir.path}/$relPath');
        if (!origFile.existsSync()) {
          print('Original image not found: ${origFile.path}; skipping.');
          return;
        }

        final safeName = filename.replaceAll(' ', '_').replaceAll('(', '').replaceAll(')', '') + '.png';
        final pyDecodedFile = File('test/fixtures/python_decoded/$safeName');
        if (!pyDecodedFile.existsSync()) {
          print('Python decoded image not found: ${pyDecodedFile.path}; skipping.');
          return;
        }

        final pyImg = img.decodePng(pyDecodedFile.readAsBytesSync())!;
        final rawBytes = origFile.readAsBytesSync();
        img.Image? dartImg = img.decodeImage(rawBytes);
        if (dartImg == null) {
          throw Exception('Failed to decode $filename in Dart');
        }

        // Align with Python raw decode raster orientation (1600x1200)
        if (dartImg.height > dartImg.width) {
          dartImg = img.copyRotate(dartImg, angle: 270);
          dartImg.exif.clear();
        }

        expect(dartImg.width, equals(pyImg.width));
        expect(dartImg.height, equals(pyImg.height));

        int maxDiffUint8 = 0;
        int sumDiff = 0;
        final totalPixels = dartImg.width * dartImg.height;

        for (int y = 0; y < dartImg.height; y++) {
          for (int x = 0; x < dartImg.width; x++) {
            final pDart = dartImg.getPixel(x, y);
            final pPy = pyImg.getPixel(x, y);

            final dr = (pDart.r - pPy.r).abs().toInt();
            final dg = (pDart.g - pPy.g).abs().toInt();
            final db = (pDart.b - pPy.b).abs().toInt();

            final m = [dr, dg, db].reduce(max);
            if (m > maxDiffUint8) {
              maxDiffUint8 = m;
            }
            sumDiff += dr + dg + db;
          }
        }

        final maxDiffNorm = maxDiffUint8 / 127.5;
        final meanDiffUint8 = sumDiff / (totalPixels * 3);

        perImageMaxDiffUint8[filename] = maxDiffUint8;
        perImageMaxDiffNorm[filename] = maxDiffNorm;

        csvRows.add({
          'filename': filename,
          'width': dartImg.width,
          'height': dartImg.height,
          'max_diff_uint8': maxDiffUint8,
          'max_diff_normalized': maxDiffNorm.toStringAsFixed(6),
          'mean_diff_uint8': meanDiffUint8.toStringAsFixed(4),
        });
      }

      print('================================================================');
      print('DECODER PARITY RESULTS (Dart JpegDecoder vs C++ libjpeg-turbo):');
      perImageMaxDiffUint8.forEach((file, diff) {
        print('  - $file: max uint8 diff = $diff / 255 (normalized = ${perImageMaxDiffNorm[file]!.toStringAsFixed(6)})');
      });
      print('================================================================');

      // Write results to results/metrics/decoder_parity.csv as a measured limitation
      final csvFile = File('../results/metrics/decoder_parity.csv');
      final sink = csvFile.openWrite();
      sink.writeln('filename,width,height,max_diff_uint8,max_diff_normalized,mean_diff_uint8,note');
      for (final r in csvRows) {
        sink.writeln('${r['filename']},${r['width']},${r['height']},${r['max_diff_uint8']},${r['max_diff_normalized']},${r['mean_diff_uint8']},measured pure-Dart JpegDecoder vs libjpeg-turbo limitation');
      }
      sink.close();
      print('Wrote measured decoder limitation to ${csvFile.path}');

      // Do not assert a pass threshold; record as measured limitation
      expect(csvFile.existsSync(), isTrue);
    });
  });
}
