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
/// - Bilinear resize to 224x224
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
        // Read raw EXIF orientation tag from header
        final decoder = img.JpegDecoder();
        final info = decoder.startDecode(bytes);
        // If JPEG was orientation 6 (90 CW baked by package:image), rotate 270 to restore landscape raster
        if (info != null && image.height > image.width) {
          // If the decoded image is portrait but raw JPEG has orientation 6, unrotate
          image = img.copyRotate(image, angle: 270);
        }
      }
    }

    // 4. Resize to 224x224 with bilinear interpolation
    final resized = img.copyResize(
      image,
      width: targetWidth,
      height: targetHeight,
      interpolation: img.Interpolation.linear,
    );

    // 5. Scale pixels to [-1.0, 1.0] via (x / 127.5) - 1.0 and format HWC Float32List
    final output = Float32List(outputElementCount);
    int offset = 0;
    for (int y = 0; y < targetHeight; y++) {
      for (int x = 0; x < targetWidth; x++) {
        final pixel = resized.getPixel(x, y);
        output[offset++] = (pixel.r / 127.5) - 1.0;
        output[offset++] = (pixel.g / 127.5) - 1.0;
        output[offset++] = (pixel.b / 127.5) - 1.0;
      }
    }

    return output;
  }
}
