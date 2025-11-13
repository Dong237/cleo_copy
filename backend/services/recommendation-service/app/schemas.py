"""
Pydantic schemas for Recommendation Service
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    """Recommendation details"""
    id: UUID
    user_id: UUID
    recommendation_type: str
    category: str
    title: str
    description: str
    priority: str
    estimated_savings: Optional[Decimal] = None
    confidence_score: Decimal
    action_items: List[str]
    status: str
    viewed: bool
    acted_on: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SpendingRecommendation(BaseModel):
    """Spending-specific recommendation"""
    category: str
    title: str
    description: str
    current_monthly_spending: Decimal
    recommended_monthly_spending: Decimal
    potential_savings: Decimal
    difficulty: str
    tips: List[str]


class SavingsRecommendation(BaseModel):
    """Savings-specific recommendation"""
    title: str
    description: str
    recommended_monthly_amount: Decimal
    potential_annual_savings: Decimal
    strategy: str
    steps: List[str]
    timeline: str


# Pattern Schemas
class SpendingPatternResponse(BaseModel):
    """Spending pattern"""
    id: UUID
    pattern_type: str
    category: str
    description: str
    frequency: Optional[str] = None
    average_amount: Decimal
    trend: Optional[str] = None
    confidence: Decimal
    first_detected: datetime

    class Config:
        from_attributes = True


# Opportunity Schemas
class SavingsOpportunityResponse(BaseModel):
    """Savings opportunity"""
    id: UUID
    opportunity_type: str
    title: str
    description: str
    estimated_monthly_savings: Decimal
    estimated_annual_savings: Decimal
    confidence: Decimal
    difficulty: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Insight Schemas
class SpendingInsight(BaseModel):
    """Spending insight"""
    insight_type: str
    title: str
    message: str
    category: Optional[str] = None
    amount: Optional[Decimal] = None
    comparison: Optional[str] = None
    trend: Optional[str] = None


class BudgetOptimization(BaseModel):
    """Budget optimization suggestion"""
    category: str
    current_budget: Decimal
    current_spending: Decimal
    recommended_budget: Decimal
    reason: str
    confidence: Decimal


class FinancialGoalRecommendation(BaseModel):
    """Financial goal recommendation"""
    goal_type: str
    title: str
    description: str
    target_amount: Decimal
    recommended_monthly_contribution: Decimal
    timeline_months: int
    priority: str


# Feedback Schemas
class FeedbackCreate(BaseModel):
    """Create feedback"""
    recommendation_id: UUID
    helpful: bool
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None
    action_taken: bool = False
    action_description: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response"""
    id: UUID
    user_id: UUID
    recommendation_id: UUID
    helpful: bool
    rating: Optional[int] = None
    action_taken: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Wellness Schemas
class FinancialWellnessScore(BaseModel):
    """Financial wellness score"""
    overall_score: int = Field(..., ge=0, le=100)
    grade: str
    message: str
    components: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    trend: str  # improving, declining, stable


class PersonalizedTip(BaseModel):
    """Personalized financial tip"""
    tip_id: str
    category: str
    title: str
    content: str
    priority: str
    estimated_impact: str
    difficulty: str
