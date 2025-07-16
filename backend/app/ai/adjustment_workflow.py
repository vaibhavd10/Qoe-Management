from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from dataclasses import dataclass

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain.tools import tool

from app.core.config import settings
from app.models.adjustment import AdjustmentType
from app.models.document import DocumentType


@dataclass
class AdjustmentWorkflowState:
    """State for the adjustment workflow"""
    document_data: Dict[str, Any]
    document_type: DocumentType
    project_materiality_threshold: float
    project_materiality_percentage: float
    
    # Processing state
    potential_adjustments: List[Dict[str, Any]]
    processed_adjustments: List[Dict[str, Any]]
    current_adjustment_index: int
    
    # Results
    final_adjustments: List[Dict[str, Any]]
    workflow_completed: bool
    error_message: Optional[str] = None


class AdjustmentWorkflow:
    """LangGraph workflow for processing adjustments"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize the workflow graph
        self.workflow = StateGraph(AdjustmentWorkflowState)
        self._setup_workflow()
    
    def _setup_workflow(self):
        """Setup the LangGraph workflow"""
        # Add nodes
        self.workflow.add_node("identify_adjustments", self.identify_adjustments)
        self.workflow.add_node("process_adjustment", self.process_adjustment)
        self.workflow.add_node("generate_narrative", self.generate_narrative)
        self.workflow.add_node("assess_materiality", self.assess_materiality)
        self.workflow.add_node("finalize_adjustment", self.finalize_adjustment)
        
        # Set entry point
        self.workflow.set_entry_point("identify_adjustments")
        
        # Add edges
        self.workflow.add_edge("identify_adjustments", "process_adjustment")
        self.workflow.add_conditional_edges(
            "process_adjustment",
            self.should_continue_processing,
            {
                "continue": "generate_narrative",
                "next_adjustment": "process_adjustment",
                "end": END
            }
        )
        self.workflow.add_edge("generate_narrative", "assess_materiality")
        self.workflow.add_edge("assess_materiality", "finalize_adjustment")
        self.workflow.add_conditional_edges(
            "finalize_adjustment",
            self.should_continue_processing,
            {
                "continue": "process_adjustment",
                "next_adjustment": "process_adjustment",
                "end": END
            }
        )
        
        # Compile the workflow
        self.app = self.workflow.compile()
    
    def identify_adjustments(self, state: AdjustmentWorkflowState) -> Dict[str, Any]:
        """Identify potential adjustments from document data"""
        try:
            # Create prompt for adjustment identification
            prompt = PromptTemplate(
                template="""
                You are an expert financial analyst specializing in Quality of Earnings analysis.
                
                Analyze the following financial document data and identify potential adjustments:
                
                Document Type: {document_type}
                Document Data: {document_data}
                
                Based on this data, identify potential adjustments across these 28+ categories:
                1. Revenue Recognition - timing differences, cut-off issues
                2. Expense Accruals - unrecorded expenses, timing differences
                3. Depreciation - method changes, useful life adjustments
                4. Inventory Valuation - obsolete inventory, valuation method changes
                5. Bad Debt - collectibility issues, reserve adequacy
                6. Prepaid Expenses - amortization timing, classification
                7. Accrued Liabilities - vacation accruals, bonus accruals
                8. Payroll Accruals - timing differences, accrued wages
                9. Rent Adjustments - lease accounting, prepaid rent
                10. Insurance Adjustments - prepaid insurance, claims reserves
                11. Tax Adjustments - tax provision, deferred taxes
                12. Intercompany Eliminations - related party transactions
                13. Reclassifications - balance sheet, income statement
                14. Write-offs - bad debt, inventory, assets
                15. Bonus Accruals - management bonuses, performance-based
                16. Commission Accruals - sales commissions, timing
                17. Professional Fees - legal, accounting, consulting
                18. Litigation Reserves - legal contingencies
                19. Warranty Reserves - product warranties
                20. Stock Compensation - equity compensation
                21. Goodwill Impairment - impairment testing
                22. Asset Impairment - fixed assets, intangibles
                23. Lease Adjustments - lease accounting under ASC 842
                24. Pension Adjustments - pension obligations
                25. Foreign Exchange - currency translation
                26. Restructuring - restructuring costs
                27. Acquisition Adjustments - purchase price allocation
                28. Other - miscellaneous adjustments
                
                For each potential adjustment, provide:
                - adjustment_type: The category from above
                - title: Brief descriptive title
                - description: Detailed explanation
                - estimated_amount: Numerical estimate (use 0 if unknown)
                - confidence_score: 0.0 to 1.0 confidence level
                - accounts_affected: List of account names/numbers
                - reasoning: Why this adjustment is needed
                
                Return a JSON array of adjustments. Be thorough but only include adjustments that are actually supported by the data.
                """,
                input_variables=["document_type", "document_data"]
            )
            
            # Format the document data for the prompt
            formatted_data = json.dumps(state.document_data, indent=2)
            
            # Execute the prompt
            messages = [
                SystemMessage(content="You are a financial analysis expert."),
                HumanMessage(content=prompt.format(
                    document_type=state.document_type,
                    document_data=formatted_data
                ))
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse the response
            try:
                adjustments = json.loads(response.content)
                if not isinstance(adjustments, list):
                    adjustments = [adjustments]
            except json.JSONDecodeError:
                # Fallback parsing
                adjustments = self._parse_adjustment_response(response.content)
            
            return {
                "potential_adjustments": adjustments,
                "current_adjustment_index": 0,
                "processed_adjustments": [],
                "final_adjustments": []
            }
            
        except Exception as e:
            return {
                "error_message": f"Error identifying adjustments: {str(e)}",
                "potential_adjustments": [],
                "current_adjustment_index": 0,
                "processed_adjustments": [],
                "final_adjustments": []
            }
    
    def process_adjustment(self, state: AdjustmentWorkflowState) -> Dict[str, Any]:
        """Process a single adjustment"""
        if state.current_adjustment_index >= len(state.potential_adjustments):
            return {"workflow_completed": True}
        
        current_adj = state.potential_adjustments[state.current_adjustment_index]
        
        # Validate and enhance the adjustment
        processed_adj = {
            "title": current_adj.get("title", "Unknown Adjustment"),
            "description": current_adj.get("description", ""),
            "adjustment_type": self._map_adjustment_type(current_adj.get("adjustment_type", "other")),
            "amount": float(current_adj.get("estimated_amount", 0)),
            "confidence_score": float(current_adj.get("confidence_score", 0.5)),
            "accounts_affected": current_adj.get("accounts_affected", []),
            "reasoning": current_adj.get("reasoning", ""),
            "rule_applied": f"AI_RULE_{current_adj.get('adjustment_type', 'other').upper()}",
            "debit_account": None,
            "credit_account": None,
            "account_impact": {}
        }
        
        # Determine debit/credit accounts based on adjustment type
        self._determine_accounts(processed_adj)
        
        # Add to processed adjustments
        new_processed = state.processed_adjustments + [processed_adj]
        
        return {
            "processed_adjustments": new_processed,
            "current_adjustment_index": state.current_adjustment_index + 1
        }
    
    def generate_narrative(self, state: AdjustmentWorkflowState) -> Dict[str, Any]:
        """Generate narrative explanation for the adjustment"""
        if not state.processed_adjustments:
            return {}
        
        current_adj = state.processed_adjustments[-1]
        
        try:
            prompt = PromptTemplate(
                template="""
                Generate a professional narrative explanation for this Quality of Earnings adjustment:
                
                Adjustment Type: {adjustment_type}
                Title: {title}
                Description: {description}
                Amount: ${amount:,.2f}
                Reasoning: {reasoning}
                
                Create a clear, professional narrative that explains:
                1. What the adjustment is for
                2. Why it's necessary
                3. The financial impact
                4. How it affects the Quality of Earnings
                
                The narrative should be suitable for inclusion in a client report.
                Keep it concise but comprehensive (2-3 paragraphs).
                """,
                input_variables=["adjustment_type", "title", "description", "amount", "reasoning"]
            )
            
            messages = [
                SystemMessage(content="You are a financial reporting expert."),
                HumanMessage(content=prompt.format(**current_adj))
            ]
            
            response = self.llm.invoke(messages)
            narrative = response.content.strip()
            
            # Update the adjustment with narrative
            current_adj["narrative"] = narrative
            
            return {"processed_adjustments": state.processed_adjustments}
            
        except Exception as e:
            current_adj["narrative"] = f"Standard adjustment for {current_adj['title']}. Amount: ${current_adj['amount']:,.2f}"
            return {"processed_adjustments": state.processed_adjustments}
    
    def assess_materiality(self, state: AdjustmentWorkflowState) -> Dict[str, Any]:
        """Assess materiality of the adjustment"""
        if not state.processed_adjustments:
            return {}
        
        current_adj = state.processed_adjustments[-1]
        amount = abs(current_adj["amount"])
        
        # Check materiality
        is_material = (
            amount >= state.project_materiality_threshold or
            amount >= (state.project_materiality_percentage * 1000000)  # Assume $1M base for percentage
        )
        
        current_adj["is_material"] = is_material
        
        if is_material:
            current_adj["materiality_reason"] = f"Exceeds materiality threshold of ${state.project_materiality_threshold:,.2f}"
        else:
            current_adj["materiality_reason"] = "Below materiality threshold"
        
        return {"processed_adjustments": state.processed_adjustments}
    
    def finalize_adjustment(self, state: AdjustmentWorkflowState) -> Dict[str, Any]:
        """Finalize the adjustment"""
        if not state.processed_adjustments:
            return {}
        
        current_adj = state.processed_adjustments[-1]
        
        # Add timestamp
        current_adj["processing_timestamp"] = datetime.utcnow().isoformat()
        
        # Add to final adjustments
        final_adjustments = state.final_adjustments + [current_adj]
        
        return {"final_adjustments": final_adjustments}
    
    def should_continue_processing(self, state: AdjustmentWorkflowState) -> str:
        """Determine if we should continue processing adjustments"""
        if state.workflow_completed:
            return "end"
        
        if state.current_adjustment_index < len(state.potential_adjustments):
            return "continue"
        
        return "end"
    
    def _map_adjustment_type(self, adj_type_str: str) -> AdjustmentType:
        """Map string to AdjustmentType enum"""
        mapping = {
            "revenue_recognition": AdjustmentType.REVENUE_RECOGNITION,
            "expense_accrual": AdjustmentType.EXPENSE_ACCRUAL,
            "depreciation": AdjustmentType.DEPRECIATION,
            "inventory_valuation": AdjustmentType.INVENTORY_VALUATION,
            "bad_debt": AdjustmentType.BAD_DEBT,
            "prepaid_expenses": AdjustmentType.PREPAID_EXPENSES,
            "accrued_liabilities": AdjustmentType.ACCRUED_LIABILITIES,
            "payroll_accrual": AdjustmentType.PAYROLL_ACCRUAL,
            "rent_adjustment": AdjustmentType.RENT_ADJUSTMENT,
            "insurance_adjustment": AdjustmentType.INSURANCE_ADJUSTMENT,
            "tax_adjustment": AdjustmentType.TAX_ADJUSTMENT,
            "intercompany_elimination": AdjustmentType.INTERCOMPANY_ELIMINATION,
            "reclassification": AdjustmentType.RECLASSIFICATION,
            "write_off": AdjustmentType.WRITE_OFF,
            "bonus_accrual": AdjustmentType.BONUS_ACCRUAL,
            "commission_accrual": AdjustmentType.COMMISSION_ACCRUAL,
            "professional_fees": AdjustmentType.PROFESSIONAL_FEES,
            "litigation_reserve": AdjustmentType.LITIGATION_RESERVE,
            "warranty_reserve": AdjustmentType.WARRANTY_RESERVE,
            "stock_compensation": AdjustmentType.STOCK_COMPENSATION,
            "goodwill_impairment": AdjustmentType.GOODWILL_IMPAIRMENT,
            "asset_impairment": AdjustmentType.ASSET_IMPAIRMENT,
            "lease_adjustment": AdjustmentType.LEASE_ADJUSTMENT,
            "pension_adjustment": AdjustmentType.PENSION_ADJUSTMENT,
            "foreign_exchange": AdjustmentType.FOREIGN_EXCHANGE,
            "restructuring": AdjustmentType.RESTRUCTURING,
            "acquisition_adjustment": AdjustmentType.ACQUISITION_ADJUSTMENT,
        }
        
        return mapping.get(adj_type_str.lower(), AdjustmentType.OTHER)
    
    def _determine_accounts(self, adjustment: Dict[str, Any]):
        """Determine debit and credit accounts based on adjustment type"""
        adj_type = adjustment["adjustment_type"]
        
        # Simple account mapping - in a real system, this would be more sophisticated
        account_mapping = {
            AdjustmentType.REVENUE_RECOGNITION: {
                "debit": "Accounts Receivable",
                "credit": "Revenue"
            },
            AdjustmentType.EXPENSE_ACCRUAL: {
                "debit": "Expense",
                "credit": "Accrued Liabilities"
            },
            AdjustmentType.DEPRECIATION: {
                "debit": "Depreciation Expense",
                "credit": "Accumulated Depreciation"
            },
            AdjustmentType.BAD_DEBT: {
                "debit": "Bad Debt Expense",
                "credit": "Allowance for Doubtful Accounts"
            },
            # Add more mappings as needed
        }
        
        if adj_type in account_mapping:
            adjustment["debit_account"] = account_mapping[adj_type]["debit"]
            adjustment["credit_account"] = account_mapping[adj_type]["credit"]
    
    def _parse_adjustment_response(self, response: str) -> List[Dict[str, Any]]:
        """Fallback parsing for adjustment response"""
        # Simple fallback - in a real system, this would be more robust
        return [{
            "title": "Parsing Error",
            "description": "Could not parse AI response",
            "adjustment_type": "other",
            "estimated_amount": 0,
            "confidence_score": 0.1,
            "accounts_affected": [],
            "reasoning": "Response parsing failed"
        }]
    
    def run_workflow(self, document_data: Dict[str, Any], document_type: DocumentType, 
                    materiality_threshold: float, materiality_percentage: float) -> List[Dict[str, Any]]:
        """Run the complete adjustment workflow"""
        
        initial_state = AdjustmentWorkflowState(
            document_data=document_data,
            document_type=document_type,
            project_materiality_threshold=materiality_threshold,
            project_materiality_percentage=materiality_percentage,
            potential_adjustments=[],
            processed_adjustments=[],
            current_adjustment_index=0,
            final_adjustments=[],
            workflow_completed=False
        )
        
        try:
            # Run the workflow
            result = self.app.invoke(initial_state)
            return result.get("final_adjustments", [])
        except Exception as e:
            # Return error adjustment
            return [{
                "title": "Workflow Error",
                "description": f"Error running adjustment workflow: {str(e)}",
                "adjustment_type": AdjustmentType.OTHER,
                "amount": 0,
                "confidence_score": 0.0,
                "narrative": "Error occurred during processing",
                "is_material": False,
                "materiality_reason": "Error in processing",
                "rule_applied": "ERROR_RULE",
                "error_message": str(e)
            }]


# Global workflow instance
adjustment_workflow = AdjustmentWorkflow()