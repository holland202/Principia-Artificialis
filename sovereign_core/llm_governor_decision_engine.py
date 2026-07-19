#!/usr/bin/env python3
"""
LLM GOVERNOR DECISION ENGINE
=============================

Sophisticated, extensible decision logic for LLM governance.

Replaces simple rule-based approach with:
  ✅ Scoring system (not early returns)
  ✅ Weighted rules
  ✅ Decision confidence
  ✅ Rule extensibility
  ✅ Decision reasoning & tracing
  ✅ Adaptive thresholds
  ✅ Context-aware evaluation

"""

import numpy as np
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import logging


# ============================================================================
# DECISION TYPES & ENUMS
# ============================================================================

class LLMDecision(Enum):
    """LLM Decision outcomes"""
    ALLOW = 1.0
    REWRITE = 0.75
    DEFER = 0.5
    BLOCK = 0.0
    OVERRIDE = 0.95


# ============================================================================
# DECISION RULE FRAMEWORK
# ============================================================================

@dataclass
class DecisionRule(ABC):
    """Base class for extensible decision rules"""
    
    name: str
    weight: float = 1.0
    enabled: bool = True
    priority: int = 0  # Lower = evaluated first
    veto: bool = False  # FIX: if True, a near-zero score hard-blocks the
                         # whole decision instead of being averaged away by
                         # other rules. Needed for genuine safety gates --
                         # verified by direct test that without this, a
                         # rule correctly scoring 0.0/BLOCK on "rm -rf" still
                         # produced a final ALLOW decision, because 7 other
                         # unrelated rules (thermal, battery, network...)
                         # outvoted it in the weighted average.
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate this rule.
        
        Returns:
            (score: 0-1, reasoning: dict)
        
        Score meaning:
            1.0 = ALLOW
            0.75 = REWRITE
            0.5 = DEFER
            0.0 = BLOCK
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get rule metadata"""
        return {
            "name": self.name,
            "weight": self.weight,
            "enabled": self.enabled,
            "priority": self.priority,
            "veto": self.veto,
        }


# ============================================================================
# CONCRETE DECISION RULES
# ============================================================================

class DangerousInputRule(DecisionRule):
    """Rule 1: Block dangerous input patterns"""
    
    def __init__(self):
        super().__init__(
            name="DangerousInput",
            weight=1.0,
            priority=0,  # Highest priority
            veto=True,   # FIX: this rule must hard-block, not get averaged
        )
        self.dangerous_patterns = [
            "format c:", "rm -rf", "wipe", "shutdown",
            "DELETE *", "DROP TABLE", "sys.exit",
            "/bin/rm", "format /", "destroy",
        ]
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        user_input = context.get("user_input", "").lower()
        
        # FIX: patterns list contains "DELETE *" and "DROP TABLE" in
        # uppercase, but user_input is lowercased above -- those two
        # patterns could never match. Confirmed by direct test: an input
        # of "DROP TABLE users;" produced zero matches. Lowercasing the
        # pattern at comparison time (not the stored list, in case it's
        # inspected/logged elsewhere) fixes this without changing intent.
        matches = [p for p in self.dangerous_patterns if p.lower() in user_input]
        
        if matches:
            return 0.0, {
                "rule": self.name,
                "decision": "BLOCK",
                "reason": f"Dangerous patterns detected: {matches}",
                "confidence": 1.0,
            }
        
        return 1.0, {
            "rule": self.name,
            "decision": "PASS",
            "reason": "No dangerous patterns",
            "confidence": 1.0,
        }


class ThermalRule(DecisionRule):
    """Rule 2: Thermal state constraints"""
    
    def __init__(self):
        super().__init__(
            name="ThermalConstraint",
            weight=0.9,
            priority=1
        )
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        thermal_state = context.get("thermal_state")
        mission_critical = context.get("mission_critical", False)
        thermal_temp = context.get("thermal_temp", 40.0)
        
        # Map thermal state to score
        # Vocabulary matches ThermalGovernor's ACTUAL states (fix 2026-07-18:
        # the old map spoke WARNING/CRITICAL/LOCKED — states the governor never
        # emits — so SCAR_LOCK fell through to a neutral default and the engine
        # failed OPEN on its own most severe thermal state).
        scores = {
            "NORMAL": 1.0,
            "WARNING": 0.85,     # legacy alias
            "THROTTLE": 0.65,
            "CRITICAL": 0.4,     # legacy alias for SCAR_LOCK severity
            "SCAR_LOCK": 0.4,    # defer-not-block: recoverable by cooling
            "LOCKED": 0.0,
            "ABORT": 0.0,
        }
        
        # Unknown state = fail CLOSED, never neutral.
        base_score = scores.get(thermal_state, 0.0)
        
        # Mission critical boosts thermal allowance
        if mission_critical and thermal_state in ("CRITICAL", "SCAR_LOCK"):
            base_score = 0.95  # OVERRIDE
        elif mission_critical and thermal_state == "THROTTLE":
            base_score = 0.8  # REWRITE
        
        # Adaptive threshold based on scar history
        recent_scars = context.get("scar_count", 0)
        if recent_scars > 100:
            base_score *= 0.95  # Slightly more conservative
        
        return base_score, {
            "rule": self.name,
            "decision": self._score_to_decision(base_score),
            "thermal_state": thermal_state,
            "thermal_temp": thermal_temp,
            "mission_critical": mission_critical,
            "reason": f"Thermal {thermal_state}: score {base_score:.2f}",
            "confidence": 0.95,
        }
    
    @staticmethod
    def _score_to_decision(score: float) -> str:
        if score >= 0.9:
            return "ALLOW"
        elif score >= 0.7:
            return "REWRITE"
        elif score >= 0.4:
            return "DEFER"
        else:
            return "BLOCK"


class BatteryRule(DecisionRule):
    """Rule 3: Battery constraints"""
    
    def __init__(self):
        super().__init__(
            name="BatteryConstraint",
            weight=0.8,
            priority=2
        )
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        battery_percent = context.get("battery_percent", 100.0)
        mission_critical = context.get("mission_critical", False)
        
        # Score based on battery level
        if battery_percent > 50:
            score = 1.0
        elif battery_percent > 20:
            score = 0.85
        elif battery_percent > 5:
            score = 0.5 if not mission_critical else 0.75
        else:
            # Empty battery is a recoverable condition: DEFER, don't BLOCK.
            score = 0.4 if not mission_critical else 0.5
        
        return score, {
            "rule": self.name,
            "decision": self._score_to_decision(score),
            "battery_percent": battery_percent,
            "mission_critical": mission_critical,
            "reason": f"Battery {battery_percent:.1f}%: score {score:.2f}",
            "confidence": 0.9,
        }
    
    @staticmethod
    def _score_to_decision(score: float) -> str:
        if score >= 0.9:
            return "ALLOW"
        elif score >= 0.7:
            return "REWRITE"
        elif score >= 0.4:
            return "DEFER"
        else:
            return "BLOCK"


class NetworkRule(DecisionRule):
    """Rule 4: Network availability"""
    
    def __init__(self):
        super().__init__(
            name="NetworkConstraint",
            weight=0.85,
            priority=3
        )
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        network_available = context.get("network_available", True)
        degraded_mode = context.get("degraded_mode", False)
        
        if network_available:
            return 1.0, {
                "rule": self.name,
                "decision": "ALLOW",
                "reason": "Network available",
                "confidence": 1.0,
            }
        elif degraded_mode:
            return 0.7, {
                "rule": self.name,
                "decision": "REWRITE",
                "reason": "Network down, using degraded mode",
                "confidence": 0.95,
            }
        else:
            return 0.5, {
                "rule": self.name,
                "decision": "DEFER",
                "reason": "Network unavailable, no degraded mode",
                "confidence": 0.95,
            }


class SICIntegrityRule(DecisionRule):
    """Rule 5: SIC manifold integrity"""
    
    def __init__(self):
        super().__init__(
            name="SICIntegrity",
            weight=0.9,
            priority=4
        )
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        sic_integrity = context.get("sic_integrity", 0.95)
        mission_critical = context.get("mission_critical", False)
        
        # Score based on integrity
        if sic_integrity > 0.8:
            score = 1.0
        elif sic_integrity > 0.6:
            score = 0.85
        elif sic_integrity > 0.4:
            score = 0.5 if not mission_critical else 0.8
        else:
            score = 0.0 if not mission_critical else 0.4
        
        return score, {
            "rule": self.name,
            "decision": self._score_to_decision(score),
            "sic_integrity": sic_integrity,
            "mission_critical": mission_critical,
            "reason": f"SIC integrity {sic_integrity:.2f}: score {score:.2f}",
            "confidence": 0.9,
        }
    
    @staticmethod
    def _score_to_decision(score: float) -> str:
        if score >= 0.9:
            return "ALLOW"
        elif score >= 0.7:
            return "REWRITE"
        elif score >= 0.4:
            return "DEFER"
        else:
            return "BLOCK"


class PermissivenessRule(DecisionRule):
    """Rule 6: System permissiveness level"""
    
    def __init__(self):
        super().__init__(
            name="Permissiveness",
            weight=0.85,
            priority=5
        )
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        permissiveness = context.get("permissiveness", 0.5)
        risky_input = context.get("risky_input", False)
        mission_critical = context.get("mission_critical", False)
        
        # Base score from permissiveness level
        if permissiveness >= 0.75:
            score = 1.0
        elif permissiveness >= 0.5:
            score = 0.85
        elif permissiveness >= 0.25:
            score = 0.7
        else:
            score = 0.4
        
        # Penalize if risky input and strict permissiveness
        if risky_input and permissiveness < 0.25:
            score *= 0.5
        
        # Mission override boosts
        if mission_critical:
            score = min(1.0, score + 0.15)
        
        return score, {
            "rule": self.name,
            "decision": self._score_to_decision(score),
            "permissiveness": permissiveness,
            "risky_input": risky_input,
            "mission_critical": mission_critical,
            "reason": f"Permissiveness {permissiveness:.2f}, risky={risky_input}: score {score:.2f}",
            "confidence": 0.85,
        }
    
    @staticmethod
    def _score_to_decision(score: float) -> str:
        if score >= 0.9:
            return "ALLOW"
        elif score >= 0.7:
            return "REWRITE"
        elif score >= 0.4:
            return "DEFER"
        else:
            return "BLOCK"


class RecentBlocksRule(DecisionRule):
    """Rule 7: Too many recent blocks (cooldown)"""
    
    def __init__(self):
        super().__init__(
            name="RecentBlocksCooldown",
            weight=0.7,
            priority=6
        )
        self.block_cooldown_threshold = 10
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        recent_blocks = context.get("recent_blocks", 0)
        
        if recent_blocks > self.block_cooldown_threshold:
            return 0.5, {
                "rule": self.name,
                "decision": "DEFER",
                "reason": f"Too many recent blocks ({recent_blocks}), cooling down",
                "confidence": 0.9,
            }
        
        return 1.0, {
            "rule": self.name,
            "decision": "PASS",
            "reason": f"Block cooldown OK ({recent_blocks} recent)",
            "confidence": 0.9,
        }


class MissionOverrideRule(DecisionRule):
    """Rule 8: Explicit mission override request"""
    
    def __init__(self):
        super().__init__(
            name="MissionOverride",
            weight=1.0,
            priority=7  # Lowest priority (last to check)
        )
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        override_requested = context.get("override_requested", False)
        mission_critical = context.get("mission_critical", False)
        
        if override_requested and mission_critical:
            return 0.95, {
                "rule": self.name,
                "decision": "OVERRIDE",
                "reason": "Mission override requested and enabled",
                "confidence": 1.0,
                "requires_audit": True,
            }
        
        return 1.0, {
            "rule": self.name,
            "decision": "PASS",
            "reason": "No override requested",
            "confidence": 1.0,
        }


# ============================================================================
# DECISION ENGINE
# ============================================================================

@dataclass
class DecisionEvaluation:
    """Result of decision evaluation"""
    
    decision: LLMDecision
    confidence: float
    reasoning: Dict[str, Any]
    rule_scores: Dict[str, Tuple[float, Dict]] = field(default_factory=dict)
    weighted_score: float = 0.0
    audit_required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.name,
            "confidence": self.confidence,
            "weighted_score": self.weighted_score,
            "reasoning": self.reasoning,
            "rule_scores": {k: v[0] for k, v in self.rule_scores.items()},
            "audit_required": self.audit_required,
        }


class LLMGovernorDecisionEngine:
    """
    Sophisticated decision engine with:
    - Multiple weighted rules
    - Extensible architecture
    - Decision confidence tracking
    - Detailed reasoning
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or self._default_logger()
        self.rules: List[DecisionRule] = []
        self.decision_history: List[DecisionEvaluation] = []
        
        # Register default rules
        self._register_default_rules()
    
    def _default_logger(self) -> logging.Logger:
        """Create default logger"""
        logger = logging.getLogger("LLMGovernor")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _register_default_rules(self):
        """Register all default rules"""
        self.register_rule(DangerousInputRule())
        self.register_rule(ThermalRule())
        self.register_rule(BatteryRule())
        self.register_rule(NetworkRule())
        self.register_rule(SICIntegrityRule())
        self.register_rule(PermissivenessRule())
        self.register_rule(RecentBlocksRule())
        self.register_rule(MissionOverrideRule())
    
    def register_rule(self, rule: DecisionRule) -> None:
        """Register new rule"""
        if not rule.enabled:
            return
        
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
        self.logger.info(f"Registered rule: {rule.name} (priority: {rule.priority})")
    
    def disable_rule(self, rule_name: str) -> None:
        """Disable a rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                self.logger.info(f"Disabled rule: {rule_name}")
                return
    
    def enable_rule(self, rule_name: str) -> None:
        """Enable a rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                self.logger.info(f"Enabled rule: {rule_name}")
                return
    
    def evaluate(self, context: Dict[str, Any]) -> DecisionEvaluation:
        """
        Evaluate all rules and make decision.
        
        Returns: DecisionEvaluation with decision + confidence + reasoning
        """
        
        try:
            # Evaluate each rule
            rule_scores = {}
            rule_reasoning = {}
            
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                try:
                    score, reasoning = rule.evaluate(context)
                    rule_scores[rule.name] = (score, reasoning)
                    rule_reasoning[rule.name] = reasoning
                    
                    self.logger.debug(
                        f"Rule {rule.name}: score={score:.2f}, "
                        f"decision={reasoning.get('decision')}"
                    )
                except Exception as e:
                    self.logger.error(f"Error evaluating rule {rule.name}: {e}")
                    rule_scores[rule.name] = (0.5, {"error": str(e)})

            # FIX: veto check runs BEFORE weighted averaging. Without this,
            # a rule correctly scoring 0.0 (e.g. DangerousInput on "rm -rf")
            # gets diluted into an overall ALLOW by unrelated rules (thermal,
            # battery, network...) all scoring near 1.0. A veto rule scoring
            # near-zero ends the decision immediately, full stop -- it does
            # not participate in the average at all.
            VETO_THRESHOLD = 0.05
            for rule in self.rules:
                if not rule.enabled or not rule.veto:
                    continue
                score, reasoning = rule_scores.get(rule.name, (1.0, {}))
                if score <= VETO_THRESHOLD:
                    evaluation = DecisionEvaluation(
                        decision=LLMDecision.BLOCK,
                        confidence=1.0,
                        reasoning={
                            "vetoed_by": rule.name,
                            "veto_reasoning": reasoning,
                            "rule_details": rule_reasoning,
                            "timestamp": datetime.now().isoformat(),
                        },
                        rule_scores=rule_scores,
                        weighted_score=0.0,
                        audit_required=True,
                    )
                    self.decision_history.append(evaluation)
                    self.logger.info(
                        f"Decision: BLOCK (vetoed by {rule.name}, confidence: 1.00)"
                    )
                    return evaluation
            
            # Compute weighted score
            total_weight = 0
            weighted_sum = 0
            
            for rule in self.rules:
                if not rule.enabled or rule.name not in rule_scores:
                    continue
                
                score, _ = rule_scores[rule.name]
                weighted_sum += score * rule.weight
                total_weight += rule.weight
            
            weighted_score = weighted_sum / total_weight if total_weight > 0 else 0.5
            
            # Map score to decision
            decision, confidence = self._score_to_decision(
                weighted_score, bool(context.get("mission_critical", False)))
            
            # WEAKEST-GATE FLOOR (fix 2026-07-18): the final decision can never
            # be more permissive than the worst safety-critical rule's verdict.
            # A weighted average lets healthy factors outvote a critical one;
            # safety gates are minima, not votes.
            _gate_names = ("Thermal", "Battery", "SIC")
            _gate_scores = [
                s for name, (s, _) in rule_scores.items()
                if any(g in name for g in _gate_names)
            ]
            if _gate_scores:
                _g = min(_gate_scores)
                if _g < 0.4 and decision != LLMDecision.BLOCK:
                    decision, confidence = LLMDecision.BLOCK, 0.95
                elif _g < 0.7 and decision in (LLMDecision.ALLOW, LLMDecision.REWRITE):
                    decision, confidence = LLMDecision.DEFER, 0.9
            
            # Check if audit is required
            audit_required = any(
                v[1].get("requires_audit", False) 
                for v in rule_scores.values()
            )
            
            # Build evaluation
            evaluation = DecisionEvaluation(
                decision=decision,
                confidence=confidence,
                reasoning={
                    "weighted_score": weighted_score,
                    "rule_details": rule_reasoning,
                    "timestamp": datetime.now().isoformat(),
                },
                rule_scores=rule_scores,
                weighted_score=weighted_score,
                audit_required=audit_required,
            )
            
            self.decision_history.append(evaluation)
            
            self.logger.info(
                f"Decision: {decision.name} (confidence: {confidence:.2f}, "
                f"score: {weighted_score:.2f})"
            )
            
            return evaluation
        
        except Exception as e:
            self.logger.error(f"Error in decision evaluation: {e}")
            return DecisionEvaluation(
                decision=LLMDecision.DEFER,
                confidence=0.5,
                reasoning={"error": str(e)},
                audit_required=True,
            )
    
    @staticmethod
    def _score_to_decision(score: float, mission_override: bool = False) -> Tuple[LLMDecision, float]:
        """
        Map score (0-1) to decision with confidence.
        
        1.0 → ALLOW (confidence: high)
        0.75 → REWRITE (confidence: high)
        0.5 → DEFER (confidence: high)
        0.0 → BLOCK (confidence: high)
        0.95 → OVERRIDE (confidence: high)
        """
        
        # Fix 2026-07-18 (defect C): OVERRIDE means "allowed BECAUSE an
        # override is active" — it requires mission context, never score
        # alone. Benign inputs scoring 0.95+ are ALLOW.
        if score >= 0.90:
            if score >= 0.95 and mission_override:
                return LLMDecision.OVERRIDE, 1.0
            return LLMDecision.ALLOW, 0.95
        
        # Map score ranges
        if score >= 0.80:
            return LLMDecision.ALLOW, min(1.0, score)
        elif score >= 0.60:
            return LLMDecision.REWRITE, score
        elif score >= 0.35:
            return LLMDecision.DEFER, score
        else:
            return LLMDecision.BLOCK, min(1.0, 1.0 - score)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get decision statistics"""
        if not self.decision_history:
            return {"total_decisions": 0}
        
        decisions = [d.decision for d in self.decision_history]
        
        return {
            "total_decisions": len(decisions),
            "allows": decisions.count(LLMDecision.ALLOW),
            "rewrites": decisions.count(LLMDecision.REWRITE),
            "defers": decisions.count(LLMDecision.DEFER),
            "blocks": decisions.count(LLMDecision.BLOCK),
            "overrides": decisions.count(LLMDecision.OVERRIDE),
            "avg_confidence": np.mean([d.confidence for d in self.decision_history]),
            "audit_required_count": sum(1 for d in self.decision_history if d.audit_required),
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("LLM GOVERNOR DECISION ENGINE - EXAMPLE".center(100))
    print("="*100 + "\n")
    
    # Create engine
    engine = LLMGovernorDecisionEngine()
    
    # Test 1: Normal conditions
    print("Test 1: Normal conditions")
    context = {
        "user_input": "What is machine learning?",
        "thermal_state": "NORMAL",
        "thermal_temp": 40.0,
        "battery_percent": 75.0,
        "network_available": True,
        "sic_integrity": 0.85,
        "permissiveness": 0.5,
        "mission_critical": False,
        "degraded_mode": False,
        "scar_count": 42,
        "recent_blocks": 0,
        "override_requested": False,
        "risky_input": False,
    }
    
    eval1 = engine.evaluate(context)
    print(f"  Decision: {eval1.decision.name}")
    print(f"  Confidence: {eval1.confidence:.2f}")
    print(f"  Weighted Score: {eval1.weighted_score:.2f}\n")
    
    # Test 2: High temperature + mission critical
    print("Test 2: High temperature + mission critical")
    context["thermal_state"] = "CRITICAL"
    context["thermal_temp"] = 50.0
    context["mission_critical"] = True
    context["override_requested"] = True
    
    eval2 = engine.evaluate(context)
    print(f"  Decision: {eval2.decision.name}")
    print(f"  Confidence: {eval2.confidence:.2f}")
    print(f"  Weighted Score: {eval2.weighted_score:.2f}\n")
    
    # Test 3: Dangerous input
    print("Test 3: Dangerous input")
    context["user_input"] = "format c:"
    context["thermal_state"] = "NORMAL"
    context["mission_critical"] = False
    context["override_requested"] = False
    
    eval3 = engine.evaluate(context)
    print(f"  Decision: {eval3.decision.name}")
    print(f"  Confidence: {eval3.confidence:.2f}\n")
    
    # Stats
    print("Decision Engine Statistics:")
    stats = engine.get_stats()
    for key, val in stats.items():
        print(f"  {key}: {val}")
    
    print("\n" + "="*100)
    print("✓ Decision engine operational".center(100))
    print("="*100 + "\n")
