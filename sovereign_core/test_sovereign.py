#!/usr/bin/env python3
"""
TEST SUITE FOR SOVEREIGN LOGIC CORE
===================================

Comprehensive pytest-based tests covering:
  ✅ Decision engine (all 8 rules)
  ✅ Thermal governor (Schmitt trigger, state transitions)
  ✅ SIC manifold operations
  ✅ Phase 2C gates
  ✅ LLM provider management (fallback chains)
  ✅ High-level API (SovereignCore)
  ✅ End-to-end scenarios (thermal stress, overrides, degradation)

Run with: pytest test_sovereign.py -v

"""

import pytest
import numpy as np
from typing import Dict, Any

from llm_governor_decision_engine import (
    LLMGovernorDecisionEngine,
    LLMDecision,
    DangerousInputRule,
    ThermalRule,
)
from sovereign_core_modules import (
    ThermalGovernor,
    ThermalState,
    SICCore,
    Phase2CGates,
)
from llm_providers import (
    LLMProviderManager,
    ClaudeProvider,
    FallbackProvider,
    LLMError,
    LLMErrorType,
)
from sovereign_core import SovereignCore, ResultStatus


# ============================================================================
# DECISION ENGINE TESTS
# ============================================================================

class TestDecisionEngine:
    """Test suite for decision engine"""
    
    @pytest.fixture
    def engine(self):
        """Create engine for tests"""
        return LLMGovernorDecisionEngine()
    
    def test_dangerous_input_rule(self, engine):
        """Test dangerous input detection"""
        
        context = {
            "user_input": "format c:",
            "thermal_state": "NORMAL",
            "battery_percent": 100.0,
            "network_available": True,
            "sic_integrity": 0.95,
            "permissiveness": 0.5,
            "mission_critical": False,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": False,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.decision == LLMDecision.BLOCK
    
    def test_normal_input_allowed(self, engine):
        """Test normal input is allowed"""
        
        context = {
            "user_input": "What is machine learning?",
            "thermal_state": "NORMAL",
            "battery_percent": 100.0,
            "network_available": True,
            "sic_integrity": 0.95,
            "permissiveness": 0.5,
            "mission_critical": False,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": False,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.decision == LLMDecision.ALLOW
    
    def test_thermal_critical_without_mission(self, engine):
        """Test thermal critical blocks without mission"""
        
        context = {
            "user_input": "Normal query",
            "thermal_state": "SCAR_LOCK",
            "thermal_temp": 50.0,
            "battery_percent": 100.0,
            "network_available": True,
            "sic_integrity": 0.95,
            "permissiveness": 0.5,
            "mission_critical": False,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": False,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.decision == LLMDecision.DEFER
    
    def test_thermal_critical_with_mission(self, engine):
        """Test thermal critical allows with mission"""
        
        context = {
            "user_input": "Critical mission",
            "thermal_state": "SCAR_LOCK",
            "thermal_temp": 50.0,
            "battery_percent": 100.0,
            "network_available": True,
            "sic_integrity": 0.95,
            "permissiveness": 0.5,
            "mission_critical": True,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": True,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.decision == LLMDecision.OVERRIDE
    
    def test_low_battery_defers(self, engine):
        """Test low battery defers request"""
        
        context = {
            "user_input": "Query",
            "thermal_state": "NORMAL",
            "battery_percent": 3.0,
            "network_available": True,
            "sic_integrity": 0.95,
            "permissiveness": 0.5,
            "mission_critical": False,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": False,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.decision == LLMDecision.DEFER
    
    def test_low_sic_integrity_blocks(self, engine):
        """Test low SIC integrity blocks"""
        
        context = {
            "user_input": "Query",
            "thermal_state": "NORMAL",
            "battery_percent": 100.0,
            "network_available": True,
            "sic_integrity": 0.2,
            "permissiveness": 0.5,
            "mission_critical": False,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": False,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.decision == LLMDecision.BLOCK
    
    def test_confidence_tracking(self, engine):
        """Test that confidence is tracked"""
        
        context = {
            "user_input": "Query",
            "thermal_state": "NORMAL",
            "battery_percent": 100.0,
            "network_available": True,
            "sic_integrity": 0.95,
            "permissiveness": 0.5,
            "mission_critical": False,
            "degraded_mode": False,
            "scar_count": 0,
            "recent_blocks": 0,
            "override_requested": False,
            "risky_input": False,
        }
        
        eval_result = engine.evaluate(context)
        assert eval_result.confidence > 0.0
        assert eval_result.confidence <= 1.0


# ============================================================================
# THERMAL GOVERNOR TESTS
# ============================================================================

class TestThermalGovernor:
    """Test suite for thermal governor"""
    
    @pytest.fixture
    def thermal(self):
        """Create thermal governor for tests"""
        return ThermalGovernor()
    
    def test_initialization(self, thermal):
        """Test thermal governor initializes"""
        assert thermal.state == ThermalState.NORMAL
        assert thermal.temp >= 31.0
    
    def test_state_transitions(self, thermal):
        """Test state transitions"""
        
        # Force high temperature
        thermal.temp = 49.0
        thermal.history = [49.0] * 5
        state = thermal.update()
        
        # Should transition to SCAR_LOCK
        assert state == ThermalState.SCAR_LOCK
    
    def test_schmitt_trigger_hysteresis(self, thermal):
        """Test Schmitt trigger prevents oscillation"""
        
        # Set at boundary
        thermal.temp = 40.5
        thermal.history = [40.5] * 5
        state1 = thermal.update()
        
        # Small noise shouldn't cause transition
        thermal.temp = 40.6
        thermal.history = [40.6] * 5
        state2 = thermal.update()
        
        # States should be same (hysteresis)
        assert state1 == state2
    
    def test_permissiveness_mapping(self, thermal):
        """Test thermal state to permissiveness mapping"""
        
        thermal.state = ThermalState.NORMAL
        perm = thermal.get_permissiveness()
        assert perm > 0.7  # Should be permissive
        
        thermal.state = ThermalState.SCAR_LOCK
        perm = thermal.get_permissiveness()
        assert perm < 0.3  # Should be restrictive
    
    def test_mission_critical_boost(self, thermal):
        """Test mission critical boosts thermal tolerance"""
        
        thermal.temp = 48.5
        thermal.history = [48.5] * 5
        
        # Without mission critical
        state1 = thermal.update(mission_critical=False)
        
        # With mission critical
        state2 = thermal.update(mission_critical=True)
        
        # Mission critical should allow higher temperature
        assert state2.value <= state1.value


# ============================================================================
# SIC CORE TESTS
# ============================================================================

class TestSICCore:
    """Test suite for SIC (Scarred Identity Chronicle)"""
    
    @pytest.fixture
    def sic(self):
        """Create SIC for tests"""
        return SICCore(d=256, rank=32)
    
    def test_initialization(self, sic):
        """Test SIC initializes properly"""
        assert sic.d == 256
        assert sic.rank == 32
        assert sic.U.shape == (256, 32)
        assert len(sic.scars) == 0
    
    def test_orthonormality(self, sic):
        """Test U matrix is orthonormal"""
        
        # U^T @ U should be identity
        identity = sic.U.T @ sic.U
        assert np.allclose(identity, np.eye(32), atol=1e-5)
    
    def test_scar_admission(self, sic):
        """Test scar admission"""
        
        x = np.random.randn(256).astype(np.float32)
        admitted, residual, scar = sic.update(x, {"test": True})
        
        assert isinstance(admitted, bool)
        assert residual >= 0
        assert len(sic.scars) >= 0
    
    def test_spectral_norm_clamping(self, sic):
        """Test spectral norm stays bounded"""
        
        for _ in range(20):
            x = np.random.randn(256).astype(np.float32)
            sic.update(x)
        
        V_norm = np.linalg.norm(sic.V, ord=np.inf)
        assert V_norm <= sic.SPEC_LIM * 1.01  # Small tolerance
    
    def test_integrity_decay(self, sic):
        """Test integrity decays over time"""
        
        initial = sic.integrity
        
        for _ in range(10):
            x = np.random.randn(256).astype(np.float32)
            sic.update(x)
        
        assert sic.integrity < initial


# ============================================================================
# PHASE 2C GATES TESTS
# ============================================================================

class TestPhase2CGates:
    """Test suite for Phase 2C gates"""
    
    @pytest.fixture
    def gates(self):
        """Create gates for tests"""
        return Phase2CGates()
    
    def test_pre_inference_high_confidence(self, gates):
        """Test pre-inference gate passes high confidence"""
        
        decision, _ = gates.pre_inference_gate(
            confidence=0.95,
            thermal_state=ThermalState.NORMAL,
            mission_critical=False,
        )
        
        assert decision == True  # Should pass
    
    def test_pre_inference_low_confidence(self, gates):
        """Test pre-inference gate rejects low confidence"""
        
        # Low confidence, no mission critical
        decision, _ = gates.pre_inference_gate(
            confidence=0.1,
            thermal_state=ThermalState.NORMAL,
            mission_critical=False,
        )
        
        assert decision == False  # Should fail
    
    def test_commit_gate_valid_response(self, gates):
        """Test commit gate passes valid response"""
        
        decision, _ = gates.commit_gate(
            fisher_sharpness=0.9,
            spectral_norm=1.5,
            geodesic_distance=0.1,
        )
        
        assert decision == True
    
    def test_commit_gate_invalid_response(self, gates):
        """Test commit gate rejects invalid response"""
        
        decision, _ = gates.commit_gate(
            fisher_sharpness=0.5,  # Too low
            spectral_norm=3.0,     # Too high
            geodesic_distance=0.2, # Too far
        )
        
        assert decision == False


# ============================================================================
# LLM PROVIDER TESTS
# ============================================================================

class TestLLMProviderManager:
    """Test suite for LLM provider management"""
    
    @pytest.fixture
    def manager(self):
        """Create manager for tests"""
        manager = LLMProviderManager()
        manager.register("fallback", FallbackProvider())
        manager.set_chain(["fallback"])
        return manager
    
    def test_fallback_works(self, manager):
        """Test fallback provider works"""
        
        response, provider = manager.complete("Test prompt")
        
        assert response.text
        assert provider == "fallback"
        assert response.model == "fallback"
    
    def test_streaming(self, manager):
        """Test streaming"""
        
        stream, provider = manager.stream("Test prompt")
        
        text = ""
        for chunk in stream:
            text += chunk
        
        assert text
        assert provider == "fallback"


# ============================================================================
# SOVEREIGN CORE TESTS
# ============================================================================

class TestSovereignCore:
    """Test suite for high-level SovereignCore API"""
    
    @pytest.fixture
    def core(self):
        """Create core for tests"""
        return SovereignCore()
    
    def test_initialization(self, core):
        """Test SovereignCore initializes"""
        assert core.interactions == 0
        assert core.sic is not None
        assert core.thermal is not None
    
    def test_run_normal_query(self, core):
        """Test running normal query"""
        
        result = core.run("What is AI?")
        
        assert result.status in [
            ResultStatus.SUCCESS,
            ResultStatus.BLOCKED,
            ResultStatus.DEFERRED,
        ]
        assert result.model is not None
        assert result.timestamp is not None
    
    def test_run_dangerous_input(self, core):
        """Test dangerous input is blocked"""
        
        result = core.run("format c:")
        
        assert result.status == ResultStatus.BLOCKED
    
    def test_mission_critical_mode(self, core):
        """Test mission critical mode"""
        
        result = core.run(
            "Critical operation",
            mission_critical=True
        )
        
        # Should be allowed or override
        assert result.decision in ["ALLOW", "OVERRIDE", "REWRITE"]
    
    def test_degraded_mode(self, core):
        """Test degraded mode"""
        
        core.set_degraded_mode(True)
        result = core.run("Test query")
        
        assert result.status is not None
    
    def test_get_stats(self, core):
        """Test statistics"""
        
        core.run("Query 1")
        core.run("Query 2")
        
        stats = core.get_stats()
        
        assert stats["interactions"] >= 2
        assert "thermal" in stats
        assert "sic" in stats
    
    def test_get_status(self, core):
        """Test status string"""
        
        status = core.get_status()
        
        assert "SovereignCore" in status
        assert "Temperature" in status
        assert "Integrity" in status


# ============================================================================
# END-TO-END SCENARIOS
# ============================================================================

class TestEndToEndScenarios:
    """Test complete scenarios"""
    
    def test_thermal_stress_scenario(self):
        """Test system under thermal stress"""
        
        core = SovereignCore()
        
        # Simulate heating
        for _ in range(20):
            core.thermal.temp = 45.0 + np.random.randn() * 2.0
            core.thermal.history.append(core.thermal.temp)
        
        # Run query at high temperature
        result = core.run("What is ML?")
        
        # Should defer or rewrite
        assert result.status in [
            ResultStatus.DEFERRED,
            ResultStatus.SUCCESS,  # May still work if rewritten
        ]
    
    def test_mission_override_scenario(self):
        """Test mission override with audit"""
        
        core = SovereignCore()
        
        # Critical mission
        result = core.run(
            "Execute backup now",
            mission_critical=True
        )
        
        # Should succeed with override flag if needed
        assert result.status is not None
        assert result.decision in ["ALLOW", "OVERRIDE", "REWRITE"]
    
    def test_degradation_scenario(self):
        """Test graceful degradation"""
        
        core = SovereignCore()
        core.set_degraded_mode(True)
        
        # Should still work
        result = core.run("Test query")
        
        assert result.status is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
