"""
Test UI Component Discovery

This script verifies that the UI can successfully discover and access
all components from the builder framework without starting the web server.
"""

import sys
sys.path.insert(0, 'src')

from builder_framework import get_all_components, get_component


def test_component_discovery():
    """Test that UI can discover all components"""
    print("=" * 70)
    print("COMPONENT DISCOVERY TEST")
    print("=" * 70)
    print()

    all_components = get_all_components()

    # Check that all categories exist
    expected_categories = ['entry_pattern', 'filter', 'session', 'indicator', 'exit']
    for category in expected_categories:
        assert category in all_components, f"Missing category: {category}"
        print(f"✓ Category '{category}' found")

    print()

    # Display discovered components
    total_components = 0
    for category, components in all_components.items():
        if not components:
            print(f"\n{category.upper()}: (empty)")
            continue

        print(f"\n{category.upper()}:")
        for name, comp_data in components.items():
            metadata = comp_data['metadata']
            print(f"  ✓ {metadata.display_name} ({name})")
            print(f"    Description: {metadata.description}")
            print(f"    Parameters: {list(metadata.parameters.keys())}")

            # Verify metadata structure
            assert hasattr(metadata, 'name'), f"Missing 'name' in metadata for {name}"
            assert hasattr(metadata, 'display_name'), f"Missing 'display_name' for {name}"
            assert hasattr(metadata, 'description'), f"Missing 'description' for {name}"
            assert hasattr(metadata, 'category'), f"Missing 'category' for {name}"
            assert hasattr(metadata, 'parameters'), f"Missing 'parameters' for {name}"

            total_components += 1

    print()
    print("=" * 70)
    print(f"SUMMARY: {total_components} components discovered successfully")
    print("=" * 70)
    print()


def test_parameter_introspection():
    """Test that parameters can be introspected for UI rendering"""
    print("=" * 70)
    print("PARAMETER INTROSPECTION TEST")
    print("=" * 70)
    print()

    # Test a pattern with parameters
    sacudida = get_component('entry_pattern', 'sacudida')
    metadata = sacudida['metadata']

    print(f"Testing: {metadata.display_name}")
    print(f"Parameters: {len(metadata.parameters)}")
    print()

    for param_name, param_spec in metadata.parameters.items():
        print(f"  Parameter: {param_name}")
        print(f"    Type: {param_spec['type']}")
        print(f"    Default: {param_spec['default']}")
        print(f"    Display Name: {param_spec['display_name']}")

        # Verify required fields
        assert 'type' in param_spec, f"Missing 'type' for {param_name}"
        assert 'default' in param_spec, f"Missing 'default' for {param_name}"
        assert 'display_name' in param_spec, f"Missing 'display_name' for {param_name}"

        # Type-specific validations
        if param_spec['type'] == 'int':
            assert 'min' in param_spec, f"Missing 'min' for int parameter {param_name}"
            assert 'max' in param_spec, f"Missing 'max' for int parameter {param_name}"
            print(f"    Range: {param_spec['min']} to {param_spec['max']}")

        elif param_spec['type'] == 'float':
            assert 'min' in param_spec, f"Missing 'min' for float parameter {param_name}"
            assert 'max' in param_spec, f"Missing 'max' for float parameter {param_name}"
            print(f"    Range: {param_spec['min']} to {param_spec['max']}")

        elif param_spec['type'] == 'choice':
            assert 'options' in param_spec, f"Missing 'options' for choice parameter {param_name}"
            print(f"    Options: {param_spec['options']}")

        # Check if optimizable
        if param_spec.get('optimizable', False):
            print(f"    ✓ Optimizable")

        print()

    print("✓ All parameter metadata is valid for UI rendering")
    print()


def test_ui_readiness():
    """Test that UI has everything it needs to render dynamically"""
    print("=" * 70)
    print("UI READINESS TEST")
    print("=" * 70)
    print()

    all_components = get_all_components()

    # Count components that will appear in UI
    entry_patterns = len(all_components['entry_pattern'])
    filters = len(all_components['filter'])
    sessions = len(all_components['session'])

    print(f"UI will render:")
    print(f"  • {entry_patterns} Entry Patterns")
    print(f"  • {filters} Filters")
    print(f"  • {sessions} Trading Sessions")
    print()

    # Verify at least some components exist
    assert entry_patterns > 0, "No entry patterns found - UI will be empty!"
    assert filters > 0, "No filters found"
    assert sessions > 0, "No sessions found"

    print("✓ UI has sufficient components to render")
    print()

    # Test parameter extraction for UI
    print("Testing parameter extraction for UI widgets...")

    for category in ['entry_pattern', 'filter', 'session']:
        for name, comp_data in all_components[category].items():
            metadata = comp_data['metadata']
            func = comp_data['function']

            # Verify function is callable
            assert callable(func), f"Component {name} function is not callable"

            # Verify metadata has all required fields
            required_fields = ['name', 'display_name', 'description', 'category', 'parameters']
            for field in required_fields:
                assert hasattr(metadata, field), f"Missing {field} in {name} metadata"

    print("✓ All components have callable functions and complete metadata")
    print()


def test_ui_class_instantiation():
    """Test that UI class can be instantiated"""
    print("=" * 70)
    print("UI CLASS INSTANTIATION TEST")
    print("=" * 70)
    print()

    # Import UI class
    try:
        from ui_app import StrategyBuilderUI
        print("✓ Successfully imported StrategyBuilderUI")
    except Exception as e:
        print(f"✗ Failed to import StrategyBuilderUI: {e}")
        raise

    # Try to instantiate
    try:
        ui_instance = StrategyBuilderUI()
        print("✓ Successfully instantiated StrategyBuilderUI")
    except Exception as e:
        print(f"✗ Failed to instantiate StrategyBuilderUI: {e}")
        raise

    # Verify initial state
    assert ui_instance.selected_pattern is None, "Pattern should be None initially"
    assert len(ui_instance.selected_filters) == 0, "Filters should be empty initially"
    assert len(ui_instance.selected_sessions) == 0, "Sessions should be empty initially"
    assert len(ui_instance.components) > 0, "Components should be loaded"

    print(f"✓ UI instance has {len(ui_instance.components)} component categories loaded")
    print()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DYNAMIC UI DISCOVERY TEST SUITE" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        test_component_discovery()
        test_parameter_introspection()
        test_ui_readiness()
        test_ui_class_instantiation()

        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 22 + "ALL TESTS PASSED!" + " " * 25 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print("The Dynamic UI is ready to render components!")
        print()
        print("Next steps:")
        print("  1. Install NiceGUI: pip install nicegui>=1.4.0")
        print("  2. Run the UI: python src/ui_app.py")
        print("  3. Open browser: http://localhost:8080")
        print()

    except AssertionError as e:
        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 27 + "TEST FAILED!" + " " * 28 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print(f"Error: {e}")
        print()
        sys.exit(1)

    except Exception as e:
        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 24 + "UNEXPECTED ERROR!" + " " * 25 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        sys.exit(1)
