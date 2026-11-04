import 'dart:typed_data';
import 'package:image/image.dart' as img;
import 'package:image_picker/image_picker.dart';

/// Exception thrown when an image exceeds the 10 MB limit (F-02).
class ImageTooLargeException implements Exception {
  final String message;
  const ImageTooLargeException(this.message);
  @override
  String toString() => message;
}

/// Exception thrown when an unsupported image format is provided (JPG and PNG only).
class InvalidImageFormatException implements Exception {
  final String message;
  const InvalidImageFormatException(this.message);
  @override
  String toString() => message;
}

/// Exception thrown when image decoding fails.
class ImageDecodeException implements Exception {
  final String message;
  const ImageDecodeException(this.message);
  @override
  String toString() => message;
}

/// Image picking and preprocessing service implementing Section 8.1 contract:
/// - Manual bilinear resize to 224x224 with exact TensorFlow 2 half-pixel-centers mapping
/// - RGB color space
/// - Normalization: (x / 127.5) - 1.0 matching mobilenet_v2.preprocess_input
/// - EXIF orientation handling
/// - Output shape: [1, 224, 224, 3] Float32List in HWC order
class PreprocessService {
  /// 10 MB limit in bytes per requirement F-02
  static const int maxFileSizeBytes = 10 * 1024 * 1024;
  static const int targetWidth = 224;
  static const int targetHeight = 224;
  static const int numChannels = 3;
  static const int outputElementCount = 1 * targetHeight * targetWidth * numChannels;

  final ImagePicker _picker;

  PreprocessService({ImagePicker? picker}) : _picker = picker ?? ImagePicker();

  /// Picks an image from the given [source] (Camera or Gallery) with 10 MB validation.
  Future<XFile?> pickImage({required ImageSource source}) async {
    final xFile = await _picker.pickImage(source: source);
    if (xFile == null) {
      return null;
    }

    // Validate extension
    final ext = xFile.name.split('.').last.toLowerCase();
    if (ext != 'jpg' && ext != 'jpeg' && ext != 'png') {
      throw const InvalidImageFormatException(
        'Unsupported file format. Only JPG and PNG images are accepted.',
      );
    }

    // Enforce 10 MB limit
    final length = await xFile.length();
    if (length > maxFileSizeBytes) {
      final sizeMb = (length / (1024 * 1024)).toStringAsFixed(2);
      throw ImageTooLargeException(
        'Image exceeds the 10 MB limit ($sizeMb MB). Please select an image under 10 MB.',
      );
    }

    return xFile;
  }

  /// Validates format magic bytes (JPG or PNG) and file size.
  void validateBytes(Uint8List bytes, {String? filename}) {
    if (bytes.lengthInBytes > maxFileSizeBytes) {
      final sizeMb = (bytes.lengthInBytes / (1024 * 1024)).toStringAsFixed(2);
      throw ImageTooLargeException(
        'Image exceeds the 10 MB limit ($sizeMb MB). Please select an image under 10 MB.',
      );
    }

    if (bytes.length < 4) {
      throw const InvalidImageFormatException(
        'File is too small to be a valid image.',
      );
    }

    final isJpeg = bytes[0] == 0xFF && bytes[1] == 0xD8;
    final isPng = bytes[0] == 0x89 &&
        bytes[1] == 0x50 &&
        bytes[2] == 0x4E &&
        bytes[3] == 0x47;

    if (!isJpeg && !isPng) {
      throw const InvalidImageFormatException(
        'Unsupported file format. Only JPG and PNG images are accepted.',
      );
    }
  }

  /// Manual bilinear resize and normalization matching TensorFlow 2.x `tf.image.resize`
  /// default behavior (`method="bilinear"`, `half_pixel_centers=True`, `antialias=False`).
  ///
  /// Coordinate mapping formula:
  ///   src = (dst + 0.5) * (srcSize / dstSize) - 0.5
  ///
  /// Clamped to [0, srcSize - 1] at image boundaries.
  static Float32List resizeBilinearTf(
    img.Image src,
    int dstHeight,
    int dstWidth,
  ) {
    final srcH = src.height;
    final srcW = src.width;
    final scaleY = srcH / dstHeight;
    final scaleX = srcW / dstWidth;

    final output = Float32List(1 * dstHeight * dstWidth * numChannels);
    int offset = 0;

    for (int dstY = 0; dstY < dstHeight; dstY++) {
      final srcY = (dstY + 0.5) * scaleY - 0.5;
      final yFloor = srcY.floor();
      final y0 = yFloor.clamp(0, srcH - 1);
      final y1 = (srcY.ceil()).clamp(0, srcH - 1);
      double dy = srcY - yFloor;
      if (srcY < 0.0) {
        dy = 0.0;
      } else if (srcY > srcH - 1) {
        dy = 0.0;
      }

      for (int dstX = 0; dstX < dstWidth; dstX++) {
        final srcX = (dstX + 0.5) * scaleX - 0.5;
        final xFloor = srcX.floor();
        final x0 = xFloor.clamp(0, srcW - 1);
        final x1 = (srcX.ceil()).clamp(0, srcW - 1);
        double dx = srcX - xFloor;
        if (srcX < 0.0) {
          dx = 0.0;
        } else if (srcX > srcW - 1) {
          dx = 0.0;
        }

        final p00 = src.getPixel(x0, y0);
        final p01 = src.getPixel(x1, y0);
        final p10 = src.getPixel(x0, y1);
        final p11 = src.getPixel(x1, y1);

        final topR = p00.r * (1.0 - dx) + p01.r * dx;
        final botR = p10.r * (1.0 - dx) + p11.r * dx;
        final valR = topR * (1.0 - dy) + botR * dy;

        final topG = p00.g * (1.0 - dx) + p01.g * dx;
        final botG = p10.g * (1.0 - dx) + p11.g * dx;
        final valG = topG * (1.0 - dy) + botG * dy;

        final topB = p00.b * (1.0 - dx) + p01.b * dx;
        final botB = p10.b * (1.0 - dx) + p11.b * dx;
        final valB = topB * (1.0 - dy) + botB * dy;

        output[offset++] = (valR / 127.5) - 1.0;
        output[offset++] = (valG / 127.5) - 1.0;
        output[offset++] = (valB / 127.5) - 1.0;
      }
    }

    return output;
  }

  /// Preprocesses image bytes to a normalized [1, 224, 224, 3] Float32List in HWC order.
  ///
  /// [applyExifOrientation] defaults to true so images taken by phone cameras or selected
  /// from gallery are displayed and classified upright.
  /// Set to false only when strict parity with raw sensor rasters is needed.
  Float32List preprocess(
    Uint8List bytes, {
    bool applyExifOrientation = true,
    String? filename,
  }) {
    // 1. Validation
    validateBytes(bytes, filename: filename);

    // 2. Decode
    img.Image? image = img.decodeImage(bytes);
    if (image == null) {
      throw const ImageDecodeException('Failed to decode image data.');
    }

    // 3. EXIF orientation
    if (applyExifOrientation) {
      // In package:image, JPEGs are baked on decode; bakeOrientation ensures any other format
      // with orientation tags is also rotated upright.
      image = img.bakeOrientation(image);
    } else {
      // If the caller explicitly requests unbaked/raw orientation, reverse any baked 90 CW rotation.
      final isJpeg = bytes[0] == 0xFF && bytes[1] == 0xD8;
      if (isJpeg) {
        final decoder = img.JpegDecoder();
        final info = decoder.startDecode(bytes);
        if (info != null && image.height > image.width) {
          image = img.copyRotate(image, angle: 270);
          image.exif.clear();
        }
      }
    }

    // 4. Resize to 224x224 with exact TensorFlow 2 half-pixel-centers bilinear mapping & normalize
    return resizeBilinearTf(image, targetHeight, targetWidth);
  }
}
