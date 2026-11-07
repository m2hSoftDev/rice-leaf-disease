import 'package:flutter/material.dart';
import 'package:ricedisease/app/theme.dart';

/// Animated confidence bar with accessible percentage label.
/// Duration is 300 ms, dropping to 0 ms when reduce-motion is enabled.
class ConfidenceBar extends StatefulWidget {
  final double confidence; // 0.0 to 1.0
  final String? label;

  const ConfidenceBar({
    super.key,
    required this.confidence,
    this.label,
  });

  @override
  State<ConfidenceBar> createState() => _ConfidenceBarState();
}

class _ConfidenceBarState extends State<ConfidenceBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: AppTheme.motionStandard,
    );
    _animation = Tween<double>(begin: 0.0, end: widget.confidence).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _controller.forward();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final effectiveDuration = AppTheme.motionDuration(
      context,
      AppTheme.motionStandard,
    );
    if (effectiveDuration == Duration.zero) {
      _controller.duration = Duration.zero;
      _controller.value = 1.0;
    } else {
      _controller.duration = effectiveDuration;
    }
  }

  @override
  void didUpdateWidget(covariant ConfidenceBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.confidence != widget.confidence) {
      _animation = Tween<double>(
        begin: _animation.value,
        end: widget.confidence,
      ).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
      );
      _controller.forward(from: 0.0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final percentText = '${(widget.confidence * 100).toStringAsFixed(1)}%';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              widget.label ?? 'Confidence',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              percentText,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: widget.confidence >= 0.60
                    ? theme.colorScheme.primary
                    : theme.colorScheme.error,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        AnimatedBuilder(
          animation: _animation,
          builder: (context, child) {
            return ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: _animation.value,
                minHeight: 12,
                backgroundColor: theme.colorScheme.surfaceVariant,
                valueColor: AlwaysStoppedAnimation<Color>(
                  widget.confidence >= 0.60
                      ? theme.colorScheme.primary
                      : theme.colorScheme.error,
                ),
              ),
            );
          },
        ),
      ],
    );
  }
}
