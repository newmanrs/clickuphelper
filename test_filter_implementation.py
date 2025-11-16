#!/usr/bin/env python
"""
Simple test to verify FilterOperator and CustomFieldFilter implementation
"""
import sys
sys.path.insert(0, '.')

# Test imports
print("Testing imports...")
try:
    from clickuphelper import FilterOperator, CustomFieldFilter
    print("✓ FilterOperator and CustomFieldFilter imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test FilterOperator enum
print("\nTesting FilterOperator enum...")
operators = [
    FilterOperator.EQUALS,
    FilterOperator.NOT_EQUALS,
    FilterOperator.GREATER_THAN,
    FilterOperator.LESS_THAN,
    FilterOperator.GREATER_THAN_OR_EQUAL,
    FilterOperator.LESS_THAN_OR_EQUAL,
    FilterOperator.CONTAINS,
    FilterOperator.STARTS_WITH,
    FilterOperator.REGEX,
    FilterOperator.IN,
    FilterOperator.IS_SET,
    FilterOperator.IS_NOT_SET
]

for op in operators:
    print(f"  • {op.name}: {op.value}")

print("✓ All FilterOperator values accessible")

# Test CustomFieldFilter class
print("\nTesting CustomFieldFilter class...")
try:
    # Test with value
    filter1 = CustomFieldFilter("test_field", FilterOperator.EQUALS, "test_value")
    assert filter1.field_name == "test_field"
    assert filter1.operator == FilterOperator.EQUALS
    assert filter1.value == "test_value"
    print("✓ CustomFieldFilter with value created successfully")
    
    # Test without value (for IS_SET/IS_NOT_SET)
    filter2 = CustomFieldFilter("test_field", FilterOperator.IS_SET)
    assert filter2.field_name == "test_field"
    assert filter2.operator == FilterOperator.IS_SET
    assert filter2.value is None
    print("✓ CustomFieldFilter without value created successfully")
    
except Exception as e:
    print(f"✗ CustomFieldFilter test failed: {e}")
    sys.exit(1)

# Test that Tasks class has the new method
print("\nTesting Tasks class has filter_by_custom_fields method...")
try:
    from clickuphelper import Tasks
    assert hasattr(Tasks, 'filter_by_custom_fields')
    print("✓ Tasks.filter_by_custom_fields method exists")
    
    assert hasattr(Tasks, '_evaluate_filter')
    print("✓ Tasks._evaluate_filter helper method exists")
    
except Exception as e:
    print(f"✗ Tasks class test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("All implementation tests passed successfully!")
print("=" * 70)
