#!/usr/bin/env python3
"""
Test script to verify the module version and capabilities documentation implementation.
"""

import clickuphelper

def test_version():
    """Test that __version__ is accessible and correct"""
    assert hasattr(clickuphelper, '__version__'), "Module should have __version__ attribute"
    assert clickuphelper.__version__ == "0.4.0", f"Version should be 0.4.0, got {clickuphelper.__version__}"
    print("✓ __version__ is accessible and set to 0.4.0")

def test_get_capabilities():
    """Test that get_capabilities() returns structured data"""
    assert hasattr(clickuphelper, 'get_capabilities'), "Module should have get_capabilities function"
    
    caps = clickuphelper.get_capabilities()
    
    # Check structure
    assert isinstance(caps, dict), "get_capabilities() should return a dictionary"
    assert 'version' in caps, "Capabilities should include version"
    assert 'classes' in caps, "Capabilities should include classes"
    assert 'functions' in caps, "Capabilities should include functions"
    assert 'filtering' in caps, "Capabilities should include filtering info"
    
    print("✓ get_capabilities() returns structured dictionary")
    
    # Check version matches
    assert caps['version'] == clickuphelper.__version__, "Version in capabilities should match __version__"
    print("✓ Version in capabilities matches __version__")
    
    # Check all required classes are documented
    required_classes = ['Task', 'Tasks', 'List', 'Teams', 'Spaces', 'Folders', 'SpaceLists', 'FolderLists']
    for cls in required_classes:
        assert cls in caps['classes'], f"Class {cls} should be documented"
        assert 'description' in caps['classes'][cls], f"Class {cls} should have description"
        assert 'key_methods' in caps['classes'][cls], f"Class {cls} should have key_methods"
        assert 'use_cases' in caps['classes'][cls], f"Class {cls} should have use_cases"
    
    print(f"✓ All {len(required_classes)} required classes are documented")
    
    # Check all required functions are documented
    required_functions = ['get_all_lists', 'get_space_tags', 'create_space_tag', 'get_list_id', 
                         'get_list_tasks', 'get_task_count', 'post_task', 'display_tree']
    for func in required_functions:
        assert func in caps['functions'], f"Function {func} should be documented"
        assert 'description' in caps['functions'][func], f"Function {func} should have description"
        assert 'parameters' in caps['functions'][func], f"Function {func} should have parameters"
        assert 'returns' in caps['functions'][func], f"Function {func} should have returns"
    
    print(f"✓ All {len(required_functions)} required functions are documented")
    
    # Check filtering capabilities
    assert 'operators' in caps['filtering'], "Filtering should document operators"
    assert 'custom_field_types' in caps['filtering'], "Filtering should document custom field types"
    assert len(caps['filtering']['operators']) > 0, "Should document filter operators"
    assert len(caps['filtering']['custom_field_types']) > 0, "Should document custom field types"
    
    print(f"✓ Filtering capabilities documented ({len(caps['filtering']['operators'])} operators, {len(caps['filtering']['custom_field_types'])} field types)")

def test_print_capabilities():
    """Test that print_capabilities() works without errors"""
    assert hasattr(clickuphelper, 'print_capabilities'), "Module should have print_capabilities function"
    
    # Just verify it runs without error
    try:
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        clickuphelper.print_capabilities()
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Check that output contains expected sections
        assert 'ClickUp Helper Module' in output, "Output should contain module name"
        assert 'Version 0.4.0' in output, "Output should contain version"
        assert 'CLASSES' in output, "Output should contain CLASSES section"
        assert 'FUNCTIONS' in output, "Output should contain FUNCTIONS section"
        assert 'FILTERING CAPABILITIES' in output, "Output should contain FILTERING section"
        
        print("✓ print_capabilities() produces formatted output")
        
    except Exception as e:
        print(f"✗ print_capabilities() failed: {e}")
        raise

def main():
    print("Testing module version and capabilities documentation...")
    print()
    
    test_version()
    test_get_capabilities()
    test_print_capabilities()
    
    print()
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print()
    print("Summary:")
    print("  - __version__ variable is set to 0.4.0")
    print("  - get_capabilities() returns structured dictionary")
    print("  - All required classes are documented")
    print("  - All required functions are documented")
    print("  - Filtering capabilities are documented")
    print("  - print_capabilities() produces human-readable output")

if __name__ == '__main__':
    main()
