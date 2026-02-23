"""
Unit tests: YAML Rules Loading

Tests that all YAML files load correctly and have required structure.
"""

import pytest
import yaml
from pathlib import Path


@pytest.mark.unit
class TestYAMLLoading:
    """Test YAML file loading and validation."""
    
    def test_global_yaml_loads(self, rules_dir):
        """Test that global.yaml loads without errors."""
        with open(rules_dir / "global.yaml") as f:
            rules = yaml.safe_load(f)
        
        assert rules is not None
        assert "philosophy" in rules
        assert "straight_logic" in rules
    
    def test_beginner_yaml_loads(self, rules_dir):
        """Test that beginner.yaml loads."""
        with open(rules_dir / "beginner.yaml") as f:
            rules = yaml.safe_load(f)
        
        assert rules is not None
        assert "era_logic" in rules
        assert "safety_logic" in rules
    
    def test_intermediate_yaml_loads(self, rules_dir):
        """Test that intermediate.yaml loads."""
        with open(rules_dir / "intermediate.yaml") as f:
            rules = yaml.safe_load(f)
        
        assert rules is not None
        assert "era_logic" in rules
    
    def test_pro_yaml_loads(self, rules_dir):
        """Test that pro.yaml loads."""
        with open(rules_dir / "pro.yaml") as f:
            rules = yaml.safe_load(f)
        
        assert rules is not None
        assert "era_logic" in rules
    
    def test_diagnostic_maps_loads(self, data_dir):
        """Test that diagnostic_maps.yaml loads."""
        with open(data_dir / "diagnostic_maps.yaml") as f:
            maps = yaml.safe_load(f)
        
        assert maps is not None
        assert "symptom_maps" in maps
        assert len(maps["symptom_maps"]) > 0
    
    def test_safety_logic_in_all_modes(self, rules_dir):
        """Test that all mode files have safety_logic."""
        for mode_file in ["beginner.yaml", "intermediate.yaml", "pro.yaml"]:
            with open(rules_dir / mode_file) as f:
                rules = yaml.safe_load(f)
            
            assert "safety_logic" in rules, f"{mode_file} missing safety_logic"
            assert "interrupt_triggers" in rules["safety_logic"]


@pytest.mark.unit
class TestSymptomMaps:
    """Test diagnostic symptom maps."""
    
    def test_all_symptoms_have_stf(self, data_dir):
        """Test all symptoms have Straight/True/Flush structure."""
        with open(data_dir / "diagnostic_maps.yaml") as f:
            maps = yaml.safe_load(f)
        
        for symptom_id, symptom_data in maps["symptom_maps"].items():
            assert "stf" in symptom_data, f"{symptom_id} missing STF structure"
            assert "straight" in symptom_data["stf"]
            assert "true" in symptom_data["stf"]
            assert "flush" in symptom_data["stf"]
    
    def test_symptom_checks_have_required_fields(self, data_dir):
        """Test that each check has id and action."""
        with open(data_dir / "diagnostic_maps.yaml") as f:
            maps = yaml.safe_load(f)
        
        for symptom_id, symptom_data in maps["symptom_maps"].items():
            for stage in ["straight", "true", "flush"]:
                checks = symptom_data["stf"][stage].get("checks", [])
                for check in checks:
                    assert "id" in check, f"{symptom_id}/{stage} check missing id"
                    assert "action" in check, f"{symptom_id}/{stage} check missing action"
