#!/usr/bin/env python3
"""
SOVEREIGN CORE - HIGH-LEVEL PUBLIC API
=======================================

Clean, simple public API that hides all internal complexity.

Simple interface:
    core = SovereignCore()
    result = core.run("Your prompt", mission_critical=True)

But internally manages:
  ✅ All 40+ artifacts
  ✅ Decision engine with 8 weighted rules
  ✅ Thermal governor with Schmitt trigger
  ✅ SIC manifold operations
  ✅ Phase 2C gates
  ✅ Multiple LLM providers with fallback
  ✅ Retry logic and health checking
  ✅ Complete audit trail

"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from llm_providers import (
    LLMProviderManager,
    ClaudeProvider,
    GPTProvider,
    FallbackProvider,
    LLMError,
)
from llm_governor_decision_engine import LLMGovernorDecisionEngine
from sovereign_core_modules import (
    ThermalGovernor,
    SICCore,
    Phase2CGates,
)


# ============================================================================
# RESULT TYPES
# ============================================================================

class ResultStatus(Enum):
    """Result status"""
    SUCCESS = "success"
    DEFERRED = "deferred"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class SovereignResult:
    """Result from SovereignCore.run()"""
    
    status: ResultStatus
    response: str
    model: str
    confidence: float
    decision: str
    thermal_state: str
    scar_admitted: bool
    tokens_input: int
    tokens_output: int
    reasoning: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "response": self.response,
            "model": self.model,
            "confidence": self.confidence,
            "decision": self.decision,
            "thermal_state": self.thermal_state,
            "scar_admitted": self.scar_admitted,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
            },
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
        }


# ============================================================================
# SOVEREIGN CORE
# ============================================================================

class SovereignCore:
    """
    High-level public API for Sovereign Logic Core.
    
    Simple usage:
        core = SovereignCore()
        result = core.run("Your prompt", mission_critical=False)
        print(result.response)
    
    Everything else is hidden:
    - Decision engine
    - Thermal governance
    - SIC manifold
    - Phase 2C gates
    - LLM provider management
    - Retry logic
    - Health checking
    - Audit trails
    """
    
    def __init__(self,
                 claude_api_key: Optional[str] = None,
                 gpt_api_key: Optional[str] = None,
                 thermal_model: str = "s25_ultra",
                 logger: Optional[logging.Logger] = None):
        """
        Initialize Sovereign Core.
        
        Args:
            claude_api_key: Claude API key (optional)
            gpt_api_key: GPT API key (optional)
            thermal_model: Thermal model ("s25_ultra", "generic", etc.)
            logger: Custom logger
        """
        
        self.logger = logger or self._setup_logger()
        
        # Core components
        self.decision_engine = LLMGovernorDecisionEngine(logger=self.logger)
        self.thermal = ThermalGovernor(logger=self.logger)
        self.sic = SICCore(d=512, rank=64, logger=self.logger)
        self.gates = Phase2CGates(logger=self.logger)
        
        # LLM providers
        self.llm_manager = LLMProviderManager(logger=self.logger)
        self.llm_manager.register("claude", ClaudeProvider(claude_api_key))
        self.llm_manager.register("gpt", GPTProvider(gpt_api_key))
        self.llm_manager.register("fallback", FallbackProvider())
        self.llm_manager.set_chain(["claude", "gpt", "fallback"])
        
        # State
        self.mode_mission_critical = False
        self.mode_degraded = False
        self.interactions = 0
        
        self.logger.info("SovereignCore initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("SovereignCore")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - SovereignCore - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def run(self,
            prompt: str,
            mission_critical: bool = False,
            system_prompt: str = "",
            max_tokens: int = 1024,
            temperature: float = 0.7) -> SovereignResult:
        """
        Run prompt through Sovereign Logic Core.
        
        This is the main entry point. Everything is orchestrated here.
        
        Args:
            prompt: User prompt
            mission_critical: Enable mission override authority
            system_prompt: Optional system prompt
            max_tokens: Max tokens for LLM
            temperature: Temperature for LLM
        
        Returns:
            SovereignResult with response + metadata
        """
        
        self.interactions += 1
        timestamp = datetime.now().isoformat()
        
        try:
            self.logger.info(f"Processing request #{self.interactions}")
            
            # Step 1: Update thermal state
            self.thermal.update(mission_critical)
            thermal_state = self.thermal.state.name
            permissiveness = self.thermal.get_permissiveness()
            
            self.logger.debug(f"Thermal: {thermal_state} ({self.thermal.temp:.1f}°C)")
            
            # Step 2: Build decision context
            context = {
                "user_input": prompt,
                "thermal_state": thermal_state,
                "thermal_temp": self.thermal.temp,
                "battery_percent": 75.0,  # Simulate
                "network_available": True,
                "sic_integrity": float(self.sic.integrity),
                "permissiveness": permissiveness,
                "mission_critical": mission_critical,
                "degraded_mode": self.mode_degraded,
                "scar_count": len(self.sic.scars),
                "recent_blocks": 0,
                "override_requested": mission_critical,
                "risky_input": self._is_risky_input(prompt),
            }
            
            # Step 3: Make decision with decision engine
            evaluation = self.decision_engine.evaluate(context)
            decision = evaluation.decision.name
            confidence = evaluation.confidence
            
            self.logger.debug(
                f"Decision: {decision} (confidence: {confidence:.2f})"
            )
            
            # Step 4: Handle blocked/deferred requests
            if decision == "BLOCK":
                return SovereignResult(
                    status=ResultStatus.BLOCKED,
                    response="Request blocked by governance filter",
                    model="none",
                    confidence=confidence,
                    decision=decision,
                    thermal_state=thermal_state,
                    scar_admitted=False,
                    tokens_input=0,
                    tokens_output=0,
                    reasoning=evaluation.reasoning,
                    timestamp=timestamp,
                )
            
            if decision == "DEFER":
                return SovereignResult(
                    status=ResultStatus.DEFERRED,
                    response="Request deferred - try again later",
                    model="none",
                    confidence=confidence,
                    decision=decision,
                    thermal_state=thermal_state,
                    scar_admitted=False,
                    tokens_input=0,
                    tokens_output=0,
                    reasoning=evaluation.reasoning,
                    timestamp=timestamp,
                )
            
            # Step 5: Query LLM with governance context
            system_with_context = self._build_system_prompt(
                system_prompt, context, decision
            )
            
            try:
                llm_response, llm_provider = self.llm_manager.complete(
                    prompt,
                    system=system_with_context,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                self.logger.info(f"LLM response from {llm_provider}")
            
            except LLMError as e:
                return SovereignResult(
                    status=ResultStatus.ERROR,
                    response=f"LLM error: {e.message}",
                    model="none",
                    confidence=0.0,
                    decision=decision,
                    thermal_state=thermal_state,
                    scar_admitted=False,
                    tokens_input=0,
                    tokens_output=0,
                    reasoning={"error": e.message, "error_type": e.error_type.value},
                    timestamp=timestamp,
                )
            
            # Step 6: Apply response adaptation
            response_text = llm_response.text
            
            if decision == "REWRITE":
                response_text = self._rewrite_response(response_text, context)
            
            if decision == "OVERRIDE":
                response_text += "\n[MISSION-CRITICAL OVERRIDE]"
            
            # Step 7: Pre-inference gate
            pre_gate_pass, pre_gate_info = self.gates.pre_inference_gate(
                confidence=confidence,
                thermal_state=self.thermal.state,
                mission_critical=mission_critical,
            )
            
            if not pre_gate_pass:
                self.logger.warning("Pre-inference gate rejected")
                return SovereignResult(
                    status=ResultStatus.BLOCKED,
                    response="Response rejected by pre-inference gate",
                    model=llm_response.model,
                    confidence=confidence,
                    decision=decision,
                    thermal_state=thermal_state,
                    scar_admitted=False,
                    tokens_input=llm_response.tokens_input,
                    tokens_output=llm_response.tokens_output,
                    reasoning=pre_gate_info,
                    timestamp=timestamp,
                )
            
            # Step 8: Commit gate
            fisher_sharpness = 0.82  # Simulate
            spectral_norm = 1.5  # Simulate
            geodesic_distance = 0.12  # Simulate
            
            commit_gate_pass, commit_gate_info = self.gates.commit_gate(
                fisher_sharpness=fisher_sharpness,
                spectral_norm=spectral_norm,
                geodesic_distance=geodesic_distance,
            )
            
            if not commit_gate_pass:
                self.logger.warning("Commit gate rejected")
                return SovereignResult(
                    status=ResultStatus.BLOCKED,
                    response="Response rejected by commit gate",
                    model=llm_response.model,
                    confidence=confidence,
                    decision=decision,
                    thermal_state=thermal_state,
                    scar_admitted=False,
                    tokens_input=llm_response.tokens_input,
                    tokens_output=llm_response.tokens_output,
                    reasoning=commit_gate_info,
                    timestamp=timestamp,
                )
            
            # Step 9: Update SIC (Scar Protocol)
            import numpy as np
            x = np.random.randn(512).astype(np.float32)
            scar_admitted, residual, scar = self.sic.update(x, {
                "input": prompt[:100],
                "model": llm_response.model,
                "decision": decision,
                "thermal": thermal_state,
                "timestamp": timestamp,
            })
            
            if scar_admitted:
                self.logger.info(f"Scar admitted (residual: {residual:.4f})")
            
            # Step 10: Return success
            return SovereignResult(
                status=ResultStatus.SUCCESS,
                response=response_text,
                model=llm_response.model,
                confidence=confidence,
                decision=decision,
                thermal_state=thermal_state,
                scar_admitted=scar_admitted,
                tokens_input=llm_response.tokens_input,
                tokens_output=llm_response.tokens_output,
                reasoning=evaluation.reasoning,
                timestamp=timestamp,
            )
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return SovereignResult(
                status=ResultStatus.ERROR,
                response=f"Internal error: {str(e)}",
                model="none",
                confidence=0.0,
                decision="ERROR",
                thermal_state="UNKNOWN",
                scar_admitted=False,
                tokens_input=0,
                tokens_output=0,
                reasoning={"error": str(e)},
                timestamp=timestamp,
            )
    
    def _is_risky_input(self, text: str) -> bool:
        """Check if input is risky"""
        risky_words = ["hack", "bypass", "exploit", "jailbreak", "override"]
        return any(word in text.lower() for word in risky_words)
    
    def _build_system_prompt(self,
                           custom_system: str,
                           context: Dict[str, Any],
                           decision: str) -> str:
        """Build context-aware system prompt"""
        
        system = "You are Claude, operating under Sovereign Logic Core governance.\n\n"
        
        if custom_system:
            system += f"Additional context: {custom_system}\n\n"
        
        # Add thermal context
        if context.get("thermal_state") in ["THROTTLE", "SCAR_LOCK"]:
            system += "Device thermal state is elevated. Keep responses concise.\n"
        
        # Add mission context
        if context.get("mission_critical"):
            system += "Mission critical mode: Prioritize task completion.\n"
        
        # Add decision context
        if decision == "REWRITE":
            system += "Your response may be adapted for current conditions.\n"
        
        system += "\nRespond appropriately for these conditions."
        
        return system
    
    def _rewrite_response(self, text: str, context: Dict[str, Any]) -> str:
        """Rewrite response for constraints"""
        
        # Thermal constraint: shorten
        if context.get("thermal_state") in ["THROTTLE", "SCAR_LOCK"]:
            sentences = text.split(".")
            text = ".".join(sentences[:2]) + "."
        
        # Battery constraint: minimize
        if context.get("battery_percent", 100) < 20:
            text = text[:200] if len(text) > 200 else text
        
        # Degraded mode: simplify
        if context.get("degraded_mode"):
            lines = text.split("\n")
            text = "\n".join(lines[:3])
        
        return text
    
    def set_mission_critical(self, enabled: bool) -> None:
        """Enable/disable mission critical mode"""
        self.mode_mission_critical = enabled
        self.logger.info(f"Mission critical: {enabled}")
    
    def set_degraded_mode(self, enabled: bool) -> None:
        """Enable/disable degraded mode"""
        self.mode_degraded = enabled
        self.logger.info(f"Degraded mode: {enabled}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "interactions": self.interactions,
            "mission_critical": self.mode_mission_critical,
            "degraded_mode": self.mode_degraded,
            "thermal": {
                "temp": self.thermal.temp,
                "state": self.thermal.state.name,
                "changes": len(self.thermal.state_changes),
            },
            "sic": self.sic.get_state(),
            "gates": self.gates.get_stats(),
            "decision_engine": self.decision_engine.get_stats(),
            "llm_health": self.llm_manager.get_health(),
        }
    
    def get_status(self) -> str:
        """Get human-readable status"""
        stats = self.get_stats()
        return (
            f"SovereignCore Status:\n"
            f"  Mode: {'MISSION_CRITICAL' if self.mode_mission_critical else 'NORMAL'}\n"
            f"  Interactions: {stats['interactions']}\n"
            f"  Temperature: {stats['thermal']['temp']:.1f}°C ({stats['thermal']['state']})\n"
            f"  SIC Integrity: {stats['sic']['integrity']:.2f}\n"
            f"  Scars Admitted: {stats['sic']['scars_admitted']}\n"
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("SOVEREIGN CORE - HIGH-LEVEL API".center(100))
    print("="*100 + "\n")
    
    # Initialize
    core = SovereignCore()
    print("✓ SovereignCore initialized\n")
    
    # Test 1: Normal query
    print("Test 1: Normal query")
    result = core.run("What is machine learning?")
    print(f"  Status: {result.status.value}")
    print(f"  Decision: {result.decision}")
    print(f"  Response: {result.response[:100]}...\n")
    
    # Test 2: Mission critical
    print("Test 2: Mission critical")
    result = core.run(
        "Execute critical operation",
        mission_critical=True
    )
    print(f"  Status: {result.status.value}")
    print(f"  Decision: {result.decision}")
    print(f"  Response: {result.response[:100]}...\n")
    
    # Stats
    print("System Statistics:")
    stats = core.get_stats()
    print(f"  Interactions: {stats['interactions']}")
    print(f"  Temperature: {stats['thermal']['temp']:.1f}°C")
    print(f"  SIC Integrity: {stats['sic']['integrity']:.2f}")
    
    print("\n" + "="*100)
    print("✓ SovereignCore operational".center(100))
    print("="*100 + "\n")
