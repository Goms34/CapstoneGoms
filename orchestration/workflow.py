"""LangGraph orchestration workflow for loan approval."""

from typing import Any
from langgraph.graph import StateGraph, END
from orchestration.state import WorkflowState, ApplicationData
from agents.applicant_profile_agent import analyze_applicant_profile
from agents.financial_risk_agent import analyze_financial_risk
from agents.loan_decision_agent import make_loan_decision
from agents.compliance_agent import execute_compliance_actions
import logging

logger = logging.getLogger(__name__)


def validate_application(state: WorkflowState) -> WorkflowState:
    """Validate application data."""
    try:
        app_data = state.application_data
        errors = []

        if app_data.age < 18 or app_data.age > 100:
            errors.append("Applicant age must be between 18 and 100")
        if app_data.annual_income <= 0:
            errors.append("Annual income must be positive")
        if app_data.credit_score < 300 or app_data.credit_score > 850:
            errors.append("Credit score must be between 300 and 850")
        if app_data.loan_amount <= 0:
            errors.append("Loan amount must be positive")

        if errors:
            state.errors.extend(errors)
            state.processing_log.append("Validation: FAILED")
            logger.error(f"Validation errors: {errors}")
            return state

        state.processing_log.append("Validation: PASSED")
        logger.info("Application validation passed")
        return state

    except Exception as e:
        state.errors.append(f"Validation error: {str(e)}")
        logger.error(f"Validation exception: {e}")
        return state


def profile_node(state: WorkflowState) -> WorkflowState:
    """Invoke Applicant Profile Agent."""
    try:
        state.processing_log.append("Profiling: Starting")
        profile_result = analyze_applicant_profile(state.application_data)
        state.profile_analysis = profile_result
        state.processing_log.append("Profiling: COMPLETED")
        logger.info("Profile analysis completed")
        return state
    except Exception as e:
        state.errors.append(f"Profile analysis error: {str(e)}")
        state.processing_log.append("Profiling: FAILED")
        logger.error(f"Profile analysis exception: {e}")
        return state


def risk_node(state: WorkflowState) -> WorkflowState:
    """Invoke Financial Risk Agent."""
    try:
        state.processing_log.append("Risk Analysis: Starting")
        risk_result = analyze_financial_risk(state.application_data)
        state.risk_analysis = risk_result
        state.processing_log.append("Risk Analysis: COMPLETED")
        logger.info("Risk analysis completed")
        return state
    except Exception as e:
        state.errors.append(f"Risk analysis error: {str(e)}")
        state.processing_log.append("Risk Analysis: FAILED")
        logger.error(f"Risk analysis exception: {e}")
        return state


def decision_node(state: WorkflowState) -> WorkflowState:
    """Invoke Loan Decision Agent."""
    try:
        state.processing_log.append("Decision: Starting")
        decision_result = make_loan_decision(
            state.application_data,
            state.profile_analysis,
            state.risk_analysis,
        )
        state.loan_decision = decision_result
        state.processing_log.append("Decision: COMPLETED")
        logger.info(f"Decision made: {decision_result.decision}")
        return state
    except Exception as e:
        state.errors.append(f"Decision making error: {str(e)}")
        state.processing_log.append("Decision: FAILED")
        logger.error(f"Decision making exception: {e}")
        return state


def compliance_node(state: WorkflowState) -> WorkflowState:
    """Invoke Compliance & Action Orchestrator Agent."""
    try:
        state.processing_log.append("Compliance: Starting")
        compliance_result = execute_compliance_actions(
            state.application_id,
            state.application_data,
            state.loan_decision,
        )
        state.compliance_action = compliance_result
        state.processing_log.append("Compliance: COMPLETED")
        logger.info("Compliance actions completed")
        return state
    except Exception as e:
        state.errors.append(f"Compliance action error: {str(e)}")
        state.processing_log.append("Compliance: FAILED")
        logger.error(f"Compliance action exception: {e}")
        return state


def should_continue(state: WorkflowState) -> str:
    """Determine next step based on state."""
    if state.errors and len(state.errors) > 0:
        # On errors, still try to continue if we can
        if len(state.errors) > 5:
            return END

    return "continue"


def create_workflow() -> StateGraph:
    """Create and compile the LangGraph workflow."""

    workflow = StateGraph(WorkflowState)

    workflow.add_node("validate", validate_application)
    workflow.add_node("profile", profile_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("compliance", compliance_node)

    workflow.set_entry_point("validate")

    workflow.add_edge("validate", "profile")
    workflow.add_edge("profile", "risk")
    workflow.add_edge("risk", "decision")
    workflow.add_edge("decision", "compliance")
    workflow.add_edge("compliance", END)

    return workflow.compile()


orchestration_graph = create_workflow()


async def process_application(
    application_id: str,
    application_data: dict,
) -> WorkflowState:
    """Process a loan application through the orchestration workflow."""

    try:
        app_data = ApplicationData(**application_data)

        initial_state = WorkflowState(
            application_id=application_id,
            application_data=app_data,
        )

        final_state = orchestration_graph.invoke(initial_state)

        logger.info(f"Application {application_id} processing complete")
        return final_state

    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise
