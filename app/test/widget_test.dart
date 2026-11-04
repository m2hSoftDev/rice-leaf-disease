import 'package:flutter_test/flutter_test.dart';
import 'package:ricedisease/main.dart';

void main() {
  testWidgets('App skeleton smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const RiceDiseaseApp());
    expect(find.text('Rice Leaf Disease Detection App Skeleton'), findsOneWidget);
  });
}
