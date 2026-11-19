#!/usr/bin/env python3
"""
Validate a FedRAMP AI Agent Compliance Manifest against Draft 2020-12 structural rules
and FedRAMP Consolidated Rules 2026 (CR-26, version 2026.11.02.01) Class C / Class D
semantic invariants.

Zero mandatory third-party dependencies (runs in pure Python 3.11+ standard library).
Optionally runs `jsonschema` Draft202012Validator if installed in the environment.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CR26_DATASET_VERSION = "2026.11.02.01"

# Official CoSAI Risk Map IDs from secure-ai-tooling/risk-map/yaml/{components,controls}.yaml
VALID_COSAI_COMPONENT_IDS: frozenset[str] = frozenset(
    {
        "componentsInfrastructure",
        "componentsData",
        "componentsDeployment",
        "componentsRegistries",
        "componentsIdentity",
        "componentsModel",
        "componentsModelTraining",
        "componentsModelCore",
        "componentsOrchestration",
        "componentsApplication",
        "componentsAgent",
        "componentsApplicationCore",
        "componentsExternalTools",
        "componentsToolNetworkControls",
        "componentsToolInvocationPath",
        "componentDataSources",
        "componentDataFilteringAndProcessing",
        "componentTrainingData",
        "componentDataStorage",
        "componentModelFrameworksAndCode",
        "componentModelEvaluation",
        "componentModelTrainingTuning",
        "componentModelStorage",
        "componentModelServing",
        "componentModelRegistry",
        "componentTheModel",
        "componentApplication",
        "componentApplicationOutputHandling",
        "componentApplicationInputHandling",
        "componentReasoningCore",
        "componentOrchestrationOutputHandling",
        "componentOrchestrationInputHandling",
        "componentTools",
        "componentToolRegistry",
        "componentMemory",
        "componentRAGContent",
        "componentAgentUserQuery",
        "componentAgentSystemInstruction",
        "componentAgentInputHandling",
        "componentAgentOutputHandling",
        "componentIdentityProvider",
        "componentAuthorizationPolicyDecisionPoint",
        "componentAgentConsentSurface",
        "componentIsolationRuntime",
        "componentToolServer",
        "componentAgentToolTransport",
        "mcp-spec-overview",
        "jsonrpc-2-0",
        "componentFederationProxy",
        "componentAgentNetworkPolicyEnforcementPoint",
        "componentAuthorizationPolicyEnforcementPoint",
        "componentToolNetworkPolicyEnforcementPoint",
        "componentApplicationConsentSurface",
        "componentApplicationNetworkPolicyEnforcementPoint",
        "componentToolHosting",
        "componentRuntimeHosting",
        "componentToolInputHandling",
        "componentToolOutputHandling",
        "componentAuditRecordRepository",
    }
)

VALID_COSAI_CONTROL_IDS: frozenset[str] = frozenset(
    {
        "controlsData",
        "controlsInfrastructure",
        "controlsModel",
        "controlsApplication",
        "controlsAssurance",
        "controlsGovernance",
        "controlModelPrivacyEnhancingTechnologies",
        "controlRuntimePrivacyEnhancingTechnologies",
        "controlTrainingDataManagement",
        "controlTrainingDataSanitization",
        "controlUserDataManagement",
        "controlModelAndDataInventoryManagement",
        "controlModelAndDataAccessControls",
        "controlModelAndDataIntegrityManagement",
        "controlModelAndDataExecutionIntegrity",
        "controlSecureByDefaultMLTooling",
        "controlInputValidationAndSanitization",
        "controlOutputValidationAndSanitization",
        "controlAdversarialTrainingAndTesting",
        "controlApplicationAccessManagement",
        "controlUserTransparencyAndControls",
        "controlAgentPluginUserControl",
        "controlAgentPluginPermissions",
        "controlRedTeaming",
        "controlVulnerabilityManagement",
        "controlThreatDetection",
        "controlIncidentResponseManagement",
        "controlUserPoliciesAndEducation",
        "controlInternalPoliciesAndEducation",
        "controlProductGovernance",
        "controlRiskGovernance",
        "controlAgentObservability",
        "controlIsolatedConfidentialComputing",
        "controlRetrievalAndVectorSystemIntegrity",
        "controlOrchestratorAndRouteIntegrity",
        "controlAgentInventoryManagement",
        "controlAgentIntegrityManagement",
        "controlAgentCredentialIsolation",
        "controlInterComponentTransportSecurity",
        "controlComponentIdentityProvenance",
        "controlAgentExecutionBounds",
        "controlModelRegistryIntegrity",
        "controlToolRegistryAndDiscoveryIntegrity",
    }
)

PENDING_20X_CLASS_D_KSIS: tuple[str, ...] = (
    "KSI-CNA-EIS",
    "KSI-MLA-ALA",
    "KSI-SVC-PRR",
    "KSI-SVC-RUD",
    "KSI-SVC-VCM",
)

REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "schema_version",
    "agent_id",
    "name",
    "version",
    "owner",
    "fedramp",
    "agent_profile",
    "data_classification",
    "model_serving",
    "cryptography",
    "identity_access",
    "tool_boundaries",
    "observability",
    "tpirs",
    "lifecycle",
)

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?(?:\+[A-Za-z0-9.-]+)?$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_US_RESIDENCY_RE = re.compile(
    r"\b(?:US|U\.S\.|United\s+States|CONUS|GovCloud)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    """A single validation finding (ERROR or WARNING) tied to a CR-26 or CoSAI rule ID."""

    severity: str  # "ERROR" | "WARNING"
    rule_id: str
    field: str
    message: str


@dataclass
class ValidationResult:
    """Aggregate result of validating an agent manifest."""

    manifest_path: str
    agent_id: str | None
    service_class: str | None
    certification_tracks: list[str]
    passed: bool
    errors: list[Finding]
    warnings: list[Finding]
    jsonschema_backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_path": self.manifest_path,
            "cr26_dataset_version": CR26_DATASET_VERSION,
            "agent_id": self.agent_id,
            "service_class": self.service_class,
            "certification_tracks": self.certification_tracks,
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "jsonschema_backend": self.jsonschema_backend,
            "errors": [asdict(e) for e in self.errors],
            "warnings": [asdict(w) for w in self.warnings],
        }


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def _try_optional_jsonschema(manifest: dict[str, Any], schema_path: Path, errors: list[Finding]) -> str:
    """Optionally run third-party jsonschema Draft 2020-12 validator if installed."""
    try:
        import jsonschema  # type: ignore[import-not-found]
    except ImportError:
        return "stdlib-draft-2020-12 (jsonschema package not installed)"

    if not schema_path.is_file():
        return "stdlib-draft-2020-12 (schema file not found for optional jsonschema pass)"

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator_cls = getattr(jsonschema, "Draft202012Validator", None)
        if validator_cls is None:
            return "stdlib-draft-2020-12"
        validator = validator_cls(schema)
        for err in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
            loc = ".".join(str(p) for p in err.path) or "<root>"
            errors.append(
                Finding(
                    severity="ERROR",
                    rule_id="SCHEMA-DRAFT-2020-12",
                    field=loc,
                    message=err.message,
                )
            )
        return "jsonschema.Draft202012Validator + stdlib-semantic"
    except Exception as exc:  # pragma: no cover
        return f"stdlib-draft-2020-12 (optional jsonschema error: {exc})"


def _check_exact_keys(
    obj: dict[str, Any],
    required_keys: tuple[str, ...],
    prefix: str,
    errors: list[Finding],
) -> bool:
    """Verify required keys exist and no unknown additionalProperties are present."""
    ok = True
    for key in required_keys:
        if key not in obj:
            field_path = f"{prefix}.{key}" if prefix else key
            errors.append(
                Finding(
                    severity="ERROR",
                    rule_id="SCHEMA-REQUIRED-FIELD",
                    field=field_path,
                    message=f"Missing required field '{field_path}'.",
                )
            )
            ok = False
    allowed = set(required_keys)
    for key in obj:
        if key not in allowed:
            field_path = f"{prefix}.{key}" if prefix else key
            errors.append(
                Finding(
                    severity="ERROR",
                    rule_id="SCHEMA-ADDITIONAL-PROPERTIES",
                    field=field_path,
                    message=f"Unexpected additional property '{field_path}' is not permitted by schema.",
                )
            )
            ok = False
    return ok


def validate_manifest_data(
    manifest: Any,
    manifest_path: str = "<memory>",
    schema_path: Path | None = None,
) -> ValidationResult:
    """Validate parsed manifest dictionary against schema structure and CR-26 Class C/D rules."""
    errors: list[Finding] = []
    warnings: list[Finding] = []

    if schema_path is None:
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "agent-manifest.schema.json"

    if not isinstance(manifest, dict):
        errors.append(
            Finding(
                severity="ERROR",
                rule_id="SCHEMA-TYPE",
                field="<root>",
                message="Manifest root must be a JSON object.",
            )
        )
        return ValidationResult(
            manifest_path=manifest_path,
            agent_id=None,
            service_class=None,
            certification_tracks=[],
            passed=False,
            errors=errors,
            warnings=warnings,
            jsonschema_backend="stdlib-draft-2020-12",
        )

    backend = _try_optional_jsonschema(manifest, schema_path, errors)

    _check_exact_keys(manifest, REQUIRED_TOP_LEVEL_KEYS, "", errors)

    # 1. Top-level scalars
    schema_version = manifest.get("schema_version")
    if not _is_non_empty_str(schema_version) or not _SEMVER_RE.match(str(schema_version)):
        errors.append(
            Finding(
                severity="ERROR",
                rule_id="SCHEMA-VERSION",
                field="schema_version",
                message="schema_version must be a valid semantic version string (e.g., '1.0.0').",
            )
        )

    agent_id = manifest.get("agent_id")
    if not _is_non_empty_str(agent_id) or not _SLUG_RE.match(str(agent_id)):
        errors.append(
            Finding(
                severity="ERROR",
                rule_id="SCHEMA-AGENT-ID",
                field="agent_id",
                message="agent_id must be a lowercase kebab-case slug (e.g., 'procurement-research-agent-c').",
            )
        )

    if not _is_non_empty_str(manifest.get("name")):
        errors.append(
            Finding(
                severity="ERROR",
                rule_id="SCHEMA-NAME",
                field="name",
                message="name must be a non-empty string.",
            )
        )

    version = manifest.get("version")
    if not _is_non_empty_str(version) or not _SEMVER_RE.match(str(version)):
        errors.append(
            Finding(
                severity="ERROR",
                rule_id="SCHEMA-AGENT-VERSION",
                field="version",
                message="version must be a valid semantic version string.",
            )
        )

    agent_profile = manifest.get("agent_profile")
    if agent_profile not in ("runtime-cso", "internal-devsecops"):
        errors.append(
            Finding(
                severity="ERROR",
                rule_id="SCHEMA-AGENT-PROFILE",
                field="agent_profile",
                message="agent_profile must be either 'runtime-cso' or 'internal-devsecops'.",
            )
        )

    # 2. owner
    owner = manifest.get("owner")
    if isinstance(owner, dict):
        _check_exact_keys(owner, ("team", "responsible_official", "contact_email"), "owner", errors)
        if not _is_non_empty_str(owner.get("team")):
            errors.append(
                Finding("ERROR", "CPO-CSO-OVR", "owner.team", "owner.team must be a non-empty string.")
            )
        if not _is_non_empty_str(owner.get("responsible_official")):
            errors.append(
                Finding(
                    "ERROR",
                    "CPO-CSO-OVR",
                    "owner.responsible_official",
                    "owner.responsible_official must identify a responsible official (CPO-CSO-OVR).",
                )
            )
        contact_email = owner.get("contact_email")
        if not _is_non_empty_str(contact_email) or not _EMAIL_RE.match(str(contact_email)):
            errors.append(
                Finding(
                    "ERROR",
                    "CPO-CSO-OVR",
                    "owner.contact_email",
                    "owner.contact_email must be a valid email address.",
                )
            )
    else:
        errors.append(Finding("ERROR", "SCHEMA-TYPE", "owner", "owner must be an object."))

    # 3. fedramp
    fedramp = manifest.get("fedramp")
    service_class: str | None = None
    cert_tracks: list[str] = []
    in_mas: bool | None = None

    if isinstance(fedramp, dict):
        _check_exact_keys(
            fedramp,
            (
                "service_class",
                "certification_tracks",
                "certification_path",
                "cso_package_id",
                "in_minimum_assessment_scope",
            ),
            "fedramp",
            errors,
        )
        sc = fedramp.get("service_class")
        if sc in ("C", "D"):
            service_class = sc
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "SCHEMA-SERVICE-CLASS",
                    "fedramp.service_class",
                    "fedramp.service_class must be 'C' or 'D'.",
                )
            )

        raw_tracks = fedramp.get("certification_tracks")
        if isinstance(raw_tracks, list) and len(raw_tracks) >= 1:
            for idx, tr in enumerate(raw_tracks):
                if tr not in ("20x", "Rev5"):
                    errors.append(
                        Finding(
                            "ERROR",
                            "SCHEMA-CERT-TRACK",
                            f"fedramp.certification_tracks[{idx}]",
                            "Each certification track must be '20x' or 'Rev5'.",
                        )
                    )
                elif tr not in cert_tracks:
                    cert_tracks.append(tr)
            if len(set(raw_tracks)) != len(raw_tracks):
                errors.append(
                    Finding(
                        "ERROR",
                        "SCHEMA-CERT-TRACK",
                        "fedramp.certification_tracks",
                        "fedramp.certification_tracks must not contain duplicate entries.",
                    )
                )
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "SCHEMA-CERT-TRACK",
                    "fedramp.certification_tracks",
                    "fedramp.certification_tracks must be a non-empty list of '20x' and/or 'Rev5'.",
                )
            )

        if fedramp.get("certification_path") not in ("Program", "Agency", "Hybrid"):
            errors.append(
                Finding(
                    "ERROR",
                    "SCHEMA-CERT-PATH",
                    "fedramp.certification_path",
                    "fedramp.certification_path must be 'Program', 'Agency', or 'Hybrid'.",
                )
            )

        if not _is_non_empty_str(fedramp.get("cso_package_id")):
            errors.append(
                Finding(
                    "ERROR",
                    "CDS-CSO-FID",
                    "fedramp.cso_package_id",
                    "fedramp.cso_package_id must be a non-empty FedRAMP package identifier.",
                )
            )

        raw_mas = fedramp.get("in_minimum_assessment_scope")
        if _is_bool(raw_mas):
            in_mas = raw_mas
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-IIR",
                    "fedramp.in_minimum_assessment_scope",
                    "fedramp.in_minimum_assessment_scope must be a boolean.",
                )
            )
    else:
        errors.append(Finding("ERROR", "SCHEMA-TYPE", "fedramp", "fedramp must be an object."))

    # 4. data_classification
    data_class = manifest.get("data_classification")
    handles_fcd = False
    handles_meta = False
    residency_boundary = ""

    if isinstance(data_class, dict):
        _check_exact_keys(
            data_class,
            (
                "handles_federal_customer_data",
                "handles_sensitive_metadata",
                "fips199_level",
                "residency_boundary",
            ),
            "data_classification",
            errors,
        )
        raw_fcd = data_class.get("handles_federal_customer_data")
        if _is_bool(raw_fcd):
            handles_fcd = raw_fcd
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-IIR",
                    "data_classification.handles_federal_customer_data",
                    "handles_federal_customer_data must be a boolean.",
                )
            )

        raw_meta = data_class.get("handles_sensitive_metadata")
        if _is_bool(raw_meta):
            handles_meta = raw_meta
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-MDI",
                    "data_classification.handles_sensitive_metadata",
                    "handles_sensitive_metadata must be a boolean.",
                )
            )

        fips_level = data_class.get("fips199_level")
        if fips_level not in ("Moderate", "High"):
            errors.append(
                Finding(
                    "ERROR",
                    "SCHEMA-FIPS199",
                    "data_classification.fips199_level",
                    "data_classification.fips199_level must be 'Moderate' or 'High'.",
                )
            )
        elif service_class == "D" and fips_level != "High":
            errors.append(
                Finding(
                    "ERROR",
                    "FRC-CSO-CAT",
                    "data_classification.fips199_level",
                    "Class D service offerings MUST declare data_classification.fips199_level as 'High'.",
                )
            )

        raw_residency = data_class.get("residency_boundary")
        if _is_non_empty_str(raw_residency):
            residency_boundary = str(raw_residency)
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.SA.SA-09-05",
                    "data_classification.residency_boundary",
                    "data_classification.residency_boundary must be a non-empty string.",
                )
            )
    else:
        errors.append(
            Finding("ERROR", "SCHEMA-TYPE", "data_classification", "data_classification must be an object.")
        )

    # MAS invariant: If handles_federal_customer_data or handles_sensitive_metadata is true,
    # in_minimum_assessment_scope MUST be true (MAS-CSO-IIR / MAS-CSO-MDI).
    if (handles_fcd or handles_meta) and in_mas is False:
        rule_id = "MAS-CSO-IIR" if handles_fcd else "MAS-CSO-MDI"
        errors.append(
            Finding(
                severity="ERROR",
                rule_id=rule_id,
                field="fedramp.in_minimum_assessment_scope",
                message=(
                    "When handles_federal_customer_data or handles_sensitive_metadata is true, "
                    "fedramp.in_minimum_assessment_scope MUST be true (MAS-CSO-IIR / MAS-CSO-MDI)."
                ),
            )
        )

    # 5. model_serving
    model_serving = manifest.get("model_serving")
    us_jurisdiction_only: bool | None = None
    if isinstance(model_serving, dict):
        _check_exact_keys(
            model_serving,
            (
                "inference_provider",
                "fedramp_certified_tpir_id",
                "model_reachability_pep",
                "us_jurisdiction_only",
            ),
            "model_serving",
            errors,
        )
        if not _is_non_empty_str(model_serving.get("inference_provider")):
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-TPR",
                    "model_serving.inference_provider",
                    "model_serving.inference_provider must be a non-empty string.",
                )
            )
        tpir_id = model_serving.get("fedramp_certified_tpir_id")
        if tpir_id is not None and not _is_non_empty_str(tpir_id):
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-TPR",
                    "model_serving.fedramp_certified_tpir_id",
                    "model_serving.fedramp_certified_tpir_id must be a non-empty string or null.",
                )
            )
        reach_pep = model_serving.get("model_reachability_pep")
        if not _is_bool(reach_pep) or reach_pep is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "KSI-CNA-EIS",
                    "model_serving.model_reachability_pep",
                    "model_serving.model_reachability_pep MUST be true (CoSAI ADR-030 componentModelServing PEP).",
                )
            )
        raw_us_jur = model_serving.get("us_jurisdiction_only")
        if _is_bool(raw_us_jur):
            us_jurisdiction_only = raw_us_jur
        else:
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.SA.SA-09-05",
                    "model_serving.us_jurisdiction_only",
                    "model_serving.us_jurisdiction_only must be a boolean.",
                )
            )
    else:
        errors.append(Finding("ERROR", "SCHEMA-TYPE", "model_serving", "model_serving must be an object."))

    # Class D residency invariant (CTL.SA.SA-09-05)
    if service_class == "D":
        if us_jurisdiction_only is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.SA.SA-09-05",
                    "model_serving.us_jurisdiction_only",
                    "Class D requires model_serving.us_jurisdiction_only to be true (CTL.SA.SA-09-05).",
                )
            )
        if handles_fcd and not _US_RESIDENCY_RE.search(residency_boundary):
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.SA.SA-09-05",
                    "data_classification.residency_boundary",
                    (
                        "Class D agents handling Federal Customer Data MUST specify a U.S. / U.S. Territories / "
                        "U.S. jurisdiction residency_boundary (CTL.SA.SA-09-05)."
                    ),
                )
            )

    # 6. cryptography
    crypto = manifest.get("cryptography")
    if isinstance(crypto, dict):
        _check_exact_keys(crypto, ("fips_140_3_validated_modules", "modules"), "cryptography", errors)
        fips_mod = crypto.get("fips_140_3_validated_modules")
        if not _is_bool(fips_mod):
            errors.append(
                Finding(
                    "ERROR",
                    "CMU-CSO-UVM",
                    "cryptography.fips_140_3_validated_modules",
                    "cryptography.fips_140_3_validated_modules must be a boolean.",
                )
            )
        else:
            if service_class == "D" and fips_mod is not True:
                errors.append(
                    Finding(
                        "ERROR",
                        "CMU-CSO-UVM",
                        "cryptography.fips_140_3_validated_modules",
                        (
                            "Class D strictly requires cryptography.fips_140_3_validated_modules = true "
                            "(CMU-CSO-UVM has RFC-2119 force MUST for Class D)."
                        ),
                    )
                )
            elif service_class == "C" and fips_mod is False:
                warnings.append(
                    Finding(
                        "WARNING",
                        "CMU-CSO-UVM",
                        "cryptography.fips_140_3_validated_modules",
                        (
                            "CMU-CSO-UVM has RFC-2119 force SHOULD for Class C; setting "
                            "fips_140_3_validated_modules = false requires documented rationale and "
                            "compensating controls in the Security Decision Record (SDR-CSO-FRR)."
                        ),
                    )
                )

        modules = crypto.get("modules")
        if not isinstance(modules, list) or len(modules) == 0:
            errors.append(
                Finding(
                    "ERROR",
                    "CMU-CSO-CMD",
                    "cryptography.modules",
                    "cryptography.modules MUST be a non-empty list of cryptographic modules (CMU-CSO-CMD).",
                )
            )
        else:
            for idx, mod in enumerate(modules):
                m_prefix = f"cryptography.modules[{idx}]"
                if not isinstance(mod, dict):
                    errors.append(Finding("ERROR", "CMU-CSO-CMD", m_prefix, "Module entry must be an object."))
                    continue
                _check_exact_keys(
                    mod,
                    ("name", "module_id", "validation_status", "purpose"),
                    m_prefix,
                    errors,
                )
                for mkey in ("name", "module_id", "validation_status", "purpose"):
                    if not _is_non_empty_str(mod.get(mkey)):
                        errors.append(
                            Finding(
                                "ERROR",
                                "CMU-CSO-CMD",
                                f"{m_prefix}.{mkey}",
                                f"{m_prefix}.{mkey} must be a non-empty string (CMU-CSO-CMD).",
                            )
                        )
    else:
        errors.append(Finding("ERROR", "SCHEMA-TYPE", "cryptography", "cryptography must be an object."))

    # 7. identity_access
    iam = manifest.get("identity_access")
    if isinstance(iam, dict):
        _check_exact_keys(
            iam,
            (
                "digital_identity_level",
                "sso_protocol",
                "encrypted_assertions",
                "local_password_bypass_disabled",
                "delegation_model",
            ),
            "identity_access",
            errors,
        )
        ial = iam.get("digital_identity_level")
        if ial not in ("IAL2/AAL2/FAL2", "IAL3/AAL3/FAL3"):
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.IA.IA-05",
                    "identity_access.digital_identity_level",
                    "digital_identity_level must be 'IAL2/AAL2/FAL2' (minimum for Class C) or 'IAL3/AAL3/FAL3' (required for Class D) per CTL.IA.IA-05.",
                )
            )
        elif service_class == "D" and ial != "IAL3/AAL3/FAL3":
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.IA.IA-05",
                    "identity_access.digital_identity_level",
                    "Class D strictly requires identity_access.digital_identity_level = 'IAL3/AAL3/FAL3' (CTL.IA.IA-05 Class D).",
                )
            )

        if iam.get("sso_protocol") not in ("OIDC", "SAML"):
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.IA.IA-05",
                    "identity_access.sso_protocol",
                    "identity_access.sso_protocol must be 'OIDC' or 'SAML'.",
                )
            )

        enc_assert = iam.get("encrypted_assertions")
        if not _is_bool(enc_assert) or enc_assert is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.IA.IA-05",
                    "identity_access.encrypted_assertions",
                    "identity_access.encrypted_assertions MUST be true (JWE or SAML XML-Enc per CTL.IA.IA-05).",
                )
            )

        no_bypass = iam.get("local_password_bypass_disabled")
        if not _is_bool(no_bypass) or no_bypass is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "KSI-IAM-MFA",
                    "identity_access.local_password_bypass_disabled",
                    "identity_access.local_password_bypass_disabled MUST be true (KSI-IAM-MFA / KSI-IAM-SFA).",
                )
            )

        if not _is_non_empty_str(iam.get("delegation_model")):
            errors.append(
                Finding(
                    "ERROR",
                    "KSI-IAM-ATP",
                    "identity_access.delegation_model",
                    "identity_access.delegation_model must be a non-empty string documenting token delegation.",
                )
            )
    else:
        errors.append(
            Finding("ERROR", "SCHEMA-TYPE", "identity_access", "identity_access must be an object.")
        )

    # 8. tool_boundaries
    tb = manifest.get("tool_boundaries")
    if isinstance(tb, dict):
        _check_exact_keys(
            tb,
            (
                "network_egress_pep",
                "authorization_pep",
                "tool_registry_allowlist",
                "third_party_tool_isolation",
                "consent_surface_dual_mode",
                "allowed_tools",
            ),
            "tool_boundaries",
            errors,
        )
        for pep_key, rule_id in (
            ("network_egress_pep", "KSI-CNA-EIS"),
            ("authorization_pep", "KSI-IAM-ATP"),
            ("tool_registry_allowlist", "SCG-CSO-SDF"),
        ):
            val = tb.get(pep_key)
            if not _is_bool(val) or val is not True:
                errors.append(
                    Finding(
                        "ERROR",
                        rule_id,
                        f"tool_boundaries.{pep_key}",
                        f"tool_boundaries.{pep_key} MUST be true.",
                    )
                )
        for bool_key in ("third_party_tool_isolation", "consent_surface_dual_mode"):
            if not _is_bool(tb.get(bool_key)):
                errors.append(
                    Finding(
                        "ERROR",
                        "SCHEMA-TYPE",
                        f"tool_boundaries.{bool_key}",
                        f"tool_boundaries.{bool_key} must be a boolean.",
                    )
                )
        allowed_tools = tb.get("allowed_tools")
        if not isinstance(allowed_tools, list) or any(not _is_non_empty_str(t) for t in allowed_tools):
            errors.append(
                Finding(
                    "ERROR",
                    "SCG-CSO-SDF",
                    "tool_boundaries.allowed_tools",
                    "tool_boundaries.allowed_tools must be a list of non-empty tool identifier strings.",
                )
            )
    else:
        errors.append(
            Finding("ERROR", "SCHEMA-TYPE", "tool_boundaries", "tool_boundaries must be an object.")
        )

    # 9. tpirs (parsed before observability check so we can inspect telemetry TPIR usage)
    tpirs = manifest.get("tpirs")
    has_external_telemetry_tpir = False
    if isinstance(tpirs, list):
        for idx, tpir in enumerate(tpirs):
            t_prefix = f"tpirs[{idx}]"
            if not isinstance(tpir, dict):
                errors.append(Finding("ERROR", "MAS-CSO-TPR", t_prefix, "TPIR entry must be an object."))
                continue
            _check_exact_keys(
                tpir,
                ("name", "certified", "fedramp_package_id", "use_case", "mitigations"),
                t_prefix,
                errors,
            )
            t_name = tpir.get("name")
            if not _is_non_empty_str(t_name):
                errors.append(
                    Finding("ERROR", "MAS-CSO-TPR", f"{t_prefix}.name", "TPIR name must be a non-empty string.")
                )
            t_cert = tpir.get("certified")
            t_pkg = tpir.get("fedramp_package_id")
            t_use = tpir.get("use_case")
            t_mit = tpir.get("mitigations")

            if not _is_bool(t_cert):
                errors.append(
                    Finding(
                        "ERROR",
                        "MAS-CSO-TPR",
                        f"{t_prefix}.certified",
                        "TPIR certified field must be a boolean.",
                    )
                )
            else:
                if t_cert is True and not _is_non_empty_str(t_pkg):
                    errors.append(
                        Finding(
                            "ERROR",
                            "MAS-CSO-TPR",
                            f"{t_prefix}.fedramp_package_id",
                            "Certified TPIRs MUST include a non-empty fedramp_package_id (MAS-CSO-TPR).",
                        )
                    )
                if t_cert is False and not _is_non_empty_str(t_mit):
                    errors.append(
                        Finding(
                            "ERROR",
                            "MAS-CSO-TPR",
                            f"{t_prefix}.mitigations",
                            "Non-certified TPIRs MUST include non-empty mitigations (MAS-CSO-TPR).",
                        )
                    )

            if not _is_non_empty_str(t_use):
                errors.append(
                    Finding(
                        "ERROR",
                        "MAS-CSO-TPR",
                        f"{t_prefix}.use_case",
                        "TPIR use_case must be a non-empty string.",
                    )
                )
            elif re.search(r"\b(?:telemetry|observability|logging|monitoring|siem|apm)\b", str(t_use), re.I):
                has_external_telemetry_tpir = True

            if not _is_non_empty_str(t_mit):
                errors.append(
                    Finding(
                        "ERROR",
                        "MAS-CSO-TPR",
                        f"{t_prefix}.mitigations",
                        "TPIR mitigations must be a non-empty string (MAS-CSO-TPR).",
                    )
                )
    else:
        errors.append(Finding("ERROR", "MAS-CSO-TPR", "tpirs", "tpirs must be an array."))

    # 10. observability
    obs = manifest.get("observability")
    if isinstance(obs, dict):
        _check_exact_keys(
            obs,
            (
                "tamper_evident_audit_repo",
                "prompt_response_redacted_from_external_telemetry",
                "audit_control_plane_separated",
            ),
            "observability",
            errors,
        )
        tamper = obs.get("tamper_evident_audit_repo")
        if not _is_bool(tamper) or tamper is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "CTL.AU.AU-09",
                    "observability.tamper_evident_audit_repo",
                    "observability.tamper_evident_audit_repo MUST be true (CTL.AU.AU-09 / KSI-MLA-ALA).",
                )
            )
        redacted = obs.get("prompt_response_redacted_from_external_telemetry")
        if not _is_bool(redacted):
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-MDI",
                    "observability.prompt_response_redacted_from_external_telemetry",
                    "prompt_response_redacted_from_external_telemetry must be a boolean.",
                )
            )
        elif (handles_fcd or handles_meta or has_external_telemetry_tpir) and redacted is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "MAS-CSO-MDI",
                    "observability.prompt_response_redacted_from_external_telemetry",
                    (
                        "prompt_response_redacted_from_external_telemetry MUST be true when Federal Customer Data, "
                        "sensitive metadata, or an external telemetry TPIR is used (MAS-CSO-MDI)."
                    ),
                )
            )
        sep = obs.get("audit_control_plane_separated")
        if not _is_bool(sep):
            errors.append(
                Finding(
                    "ERROR",
                    "SCHEMA-TYPE",
                    "observability.audit_control_plane_separated",
                    "observability.audit_control_plane_separated must be a boolean.",
                )
            )
    else:
        errors.append(Finding("ERROR", "SCHEMA-TYPE", "observability", "observability must be an object."))

    # 11. lifecycle
    lc = manifest.get("lifecycle")
    if isinstance(lc, dict):
        _check_exact_keys(
            lc,
            (
                "vdr_triage_sla_days",
                "scn_change_channel",
                "iec_incident_channel",
                "per_service_certification_artifacts",
                "portable_eval_paths",
                "cosai_component_ids",
                "cosai_control_ids",
            ),
            "lifecycle",
            errors,
        )
        sla = lc.get("vdr_triage_sla_days")
        if not _is_int(sla) or sla < 1:
            errors.append(
                Finding(
                    "ERROR",
                    "VER-TFR-EVU",
                    "lifecycle.vdr_triage_sla_days",
                    "lifecycle.vdr_triage_sla_days must be a positive integer.",
                )
            )
        else:
            if service_class == "C" and sla > 5:
                errors.append(
                    Finding(
                        "ERROR",
                        "VER-TFR-EVU",
                        "lifecycle.vdr_triage_sla_days",
                        f"Class C requires lifecycle.vdr_triage_sla_days <= 5 (got {sla}) per VER-TFR-EVU.",
                    )
                )
            elif service_class == "D" and sla > 2:
                errors.append(
                    Finding(
                        "ERROR",
                        "VER-TFR-EVU",
                        "lifecycle.vdr_triage_sla_days",
                        f"Class D strictly requires lifecycle.vdr_triage_sla_days <= 2 (got {sla}) per VER-TFR-EVU.",
                    )
                )

        if not _is_non_empty_str(lc.get("scn_change_channel")):
            errors.append(
                Finding(
                    "ERROR",
                    "SCN-ADP-NTF",
                    "lifecycle.scn_change_channel",
                    "lifecycle.scn_change_channel must be a non-empty string.",
                )
            )

        if not _is_non_empty_str(lc.get("iec_incident_channel")):
            errors.append(
                Finding(
                    "ERROR",
                    "IEC-CSO-IIR",
                    "lifecycle.iec_incident_channel",
                    "lifecycle.iec_incident_channel must be a non-empty string.",
                )
            )

        psm = lc.get("per_service_certification_artifacts")
        if not _is_bool(psm):
            errors.append(
                Finding(
                    "ERROR",
                    "CDS-CSO-PSM",
                    "lifecycle.per_service_certification_artifacts",
                    "lifecycle.per_service_certification_artifacts must be a boolean.",
                )
            )
        elif service_class == "D" and psm is not True:
            errors.append(
                Finding(
                    "ERROR",
                    "CDS-CSO-PSM",
                    "lifecycle.per_service_certification_artifacts",
                    (
                        "Class D strictly requires lifecycle.per_service_certification_artifacts = true "
                        "(CDS-CSO-PSM has RFC-2119 force MUST for Class D)."
                    ),
                )
            )

        eval_paths = lc.get("portable_eval_paths")
        if (
            not isinstance(eval_paths, list)
            or len(eval_paths) == 0
            or any(not _is_non_empty_str(p) for p in eval_paths)
        ):
            errors.append(
                Finding(
                    "ERROR",
                    "COSAI-ADR-033-D6",
                    "lifecycle.portable_eval_paths",
                    "lifecycle.portable_eval_paths MUST be a non-empty list of portable evaluation suite paths (CoSAI ADR-033 D6).",
                )
            )

        comp_ids = lc.get("cosai_component_ids")
        if not isinstance(comp_ids, list) or len(comp_ids) == 0:
            errors.append(
                Finding(
                    "ERROR",
                    "COSAI-ADR-030",
                    "lifecycle.cosai_component_ids",
                    "lifecycle.cosai_component_ids must be a non-empty list of CoSAI component IDs.",
                )
            )
        else:
            for idx, cid in enumerate(comp_ids):
                if not _is_non_empty_str(cid) or str(cid) not in VALID_COSAI_COMPONENT_IDS:
                    errors.append(
                        Finding(
                            "ERROR",
                            "COSAI-ADR-030",
                            f"lifecycle.cosai_component_ids[{idx}]",
                            f"Unknown CoSAI component ID {cid!r}; must match official CoSAI Risk Map components.yaml.",
                        )
                    )

        ctrl_ids = lc.get("cosai_control_ids")
        if not isinstance(ctrl_ids, list) or len(ctrl_ids) == 0:
            errors.append(
                Finding(
                    "ERROR",
                    "COSAI-RISK-MAP",
                    "lifecycle.cosai_control_ids",
                    "lifecycle.cosai_control_ids must be a non-empty list of CoSAI control IDs.",
                )
            )
        else:
            for idx, ctrl_id in enumerate(ctrl_ids):
                if not _is_non_empty_str(ctrl_id) or str(ctrl_id) not in VALID_COSAI_CONTROL_IDS:
                    errors.append(
                        Finding(
                            "ERROR",
                            "COSAI-RISK-MAP",
                            f"lifecycle.cosai_control_ids[{idx}]",
                            f"Unknown CoSAI control ID {ctrl_id!r}; must match official CoSAI Risk Map controls.yaml.",
                        )
                    )
    else:
        errors.append(Finding("ERROR", "SCHEMA-TYPE", "lifecycle", "lifecycle must be an object."))

    # Non-fatal warning when Class D includes "20x" track
    if service_class == "D" and "20x" in cert_tracks:
        warnings.append(
            Finding(
                severity="WARNING",
                rule_id="CR26-20X-CLASS-D-2027",
                field="fedramp.certification_tracks",
                message=(
                    "Class D manifest includes '20x' track: FedRAMP 20x Class D is targeted for 2027, and "
                    f"5 KSIs ({', '.join(PENDING_20X_CLASS_D_KSIS)}) plus VDR-TFR-MVX omit Class D variants "
                    f"in CR-26 {CR26_DATASET_VERSION}. Ensure Rev5 High Baseline controls remain primary and "
                    "do not fabricate 20x Class D statements."
                ),
            )
        )

    passed = len(errors) == 0
    return ValidationResult(
        manifest_path=manifest_path,
        agent_id=str(agent_id) if _is_non_empty_str(agent_id) else None,
        service_class=service_class,
        certification_tracks=cert_tracks,
        passed=passed,
        errors=errors,
        warnings=warnings,
        jsonschema_backend=backend,
    )


def validate_manifest_file(path: Path, schema_path: Path | None = None) -> ValidationResult:
    """Load a manifest JSON file from disk and validate it."""
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return ValidationResult(
            manifest_path=str(path),
            agent_id=None,
            service_class=None,
            certification_tracks=[],
            passed=False,
            errors=[
                Finding(
                    severity="ERROR",
                    rule_id="FILE-READ-ERROR",
                    field="<file>",
                    message=f"Unable to read manifest file '{path}': {exc}",
                )
            ],
            warnings=[],
            jsonschema_backend="stdlib-draft-2020-12",
        )

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return ValidationResult(
            manifest_path=str(path),
            agent_id=None,
            service_class=None,
            certification_tracks=[],
            passed=False,
            errors=[
                Finding(
                    severity="ERROR",
                    rule_id="JSON-PARSE-ERROR",
                    field="<file>",
                    message=f"Invalid JSON in '{path}': {exc}",
                )
            ],
            warnings=[],
            jsonschema_backend="stdlib-draft-2020-12",
        )

    return validate_manifest_data(data, manifest_path=str(path), schema_path=schema_path)


def _format_human(result: ValidationResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    tracks = ",".join(result.certification_tracks) if result.certification_tracks else "none"
    lines = [
        f"[{status}] FedRAMP CR-26 ({CR26_DATASET_VERSION}) Manifest Validation: {result.manifest_path}",
        f"  Agent ID: {result.agent_id or '<unknown>'} | Service Class: {result.service_class or '<invalid>'} | Tracks: {tracks}",
        f"  Validator Backend: {result.jsonschema_backend}",
    ]
    for warning in result.warnings:
        lines.append(f"  [WARNING] [{warning.rule_id}] {warning.field}: {warning.message}")
    for error in result.errors:
        lines.append(f"  [ERROR]   [{error.rule_id}] {error.field}: {error.message}")
    lines.append(
        f"  Summary: {len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a FedRAMP AI Agent Compliance Manifest against CR-26 Class C / Class D rules."
    )
    parser.add_argument("manifest", help="Path to the agent-manifest.json file to validate.")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit structured JSON validation result to stdout.",
    )
    parser.add_argument(
        "--schema",
        default=None,
        help="Optional explicit path to agent-manifest.schema.json.",
    )
    args = parser.parse_args(argv)

    schema_path = Path(args.schema) if args.schema else None
    result = validate_manifest_file(Path(args.manifest), schema_path=schema_path)

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        output = _format_human(result)
        stream = sys.stdout if result.passed else sys.stderr
        print(output, file=stream)

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
