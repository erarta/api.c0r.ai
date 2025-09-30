"""
Nutrition Onboarding API Routes.
Handles user questionnaire flow and preference collection for personalized meal plans.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from loguru import logger

from common.db.supabase_service import supabase_service
from common.db.client import supabase
from deps import require_auth_context, AuthContext, require_internal_auth
from onboarding.nutrition_questionnaire import (
    NutritionQuestionnaire, UserResponse, NutritionPreferences
)

router = APIRouter()
questionnaire = NutritionQuestionnaire()


class GetQuestionnaireResponse(BaseModel):
    steps: List[Dict[str, Any]]
    total_steps: int
    estimated_time_minutes: int


class SubmitResponsesRequest(BaseModel):
    responses: List[Dict[str, Any]]  # question_id, value, timestamp


class QuestionnaireStatusResponse(BaseModel):
    completed: bool
    current_step: Optional[int] = None
    completion_percentage: int
    preferences_summary: Optional[str] = None


class OnboardingProfileRequest(BaseModel):
    user_id: str = Field(description="User ID for internal API calls")


@router.get("/nutrition-onboarding/questionnaire", response_model=GetQuestionnaireResponse)
async def get_nutrition_questionnaire(auth: AuthContext = Depends(require_auth_context)):
    """Get complete nutrition questionnaire for user"""

    try:
        # Get questionnaire flow
        steps = questionnaire.get_questionnaire_flow(auth['user_id'])

        # Convert to response format
        steps_data = []
        for step in steps:
            step_data = {
                "id": step.id,
                "title": step.title,
                "subtitle": step.subtitle,
                "icon": step.icon,
                "completion_percentage": step.completion_percentage,
                "questions": []
            }

            # Convert questions to dict format
            for question in step.questions:
                question_data = {
                    "id": question.id,
                    "type": question.type,
                    "title": question.title,
                    "description": question.description,
                    "required": question.required
                }

                # Add type-specific fields
                if question.options:
                    question_data["options"] = question.options

                if question.min_value is not None:
                    question_data["min_value"] = question.min_value

                if question.max_value is not None:
                    question_data["max_value"] = question.max_value

                if question.placeholder:
                    question_data["placeholder"] = question.placeholder

                if question.skip_logic:
                    question_data["skip_logic"] = question.skip_logic

                step_data["questions"].append(question_data)

            steps_data.append(step_data)

        return GetQuestionnaireResponse(
            steps=steps_data,
            total_steps=len(steps_data),
            estimated_time_minutes=len(steps_data) * 2  # ~2 minutes per step
        )

    except Exception as e:
        logger.error(f"Failed to get nutrition questionnaire: {e}")
        raise HTTPException(status_code=500, detail="Failed to get questionnaire")


@router.post("/nutrition-onboarding/responses")
async def submit_questionnaire_responses(
    request: SubmitResponsesRequest,
    auth: AuthContext = Depends(require_auth_context)
):
    """Submit user responses to questionnaire"""

    try:
        # Convert request to UserResponse objects
        user_responses = []
        for resp_data in request.responses:
            user_response = UserResponse(
                question_id=resp_data["question_id"],
                value=resp_data["value"],
                timestamp=datetime.fromisoformat(resp_data.get("timestamp", datetime.utcnow().isoformat()))
            )
            user_responses.append(user_response)

        # Process responses into preferences
        preferences = questionnaire.process_responses(user_responses)

        # Generate preferences summary
        summary = questionnaire.generate_onboarding_summary(preferences)

        # Save to database
        await _save_user_preferences(auth['user_id'], preferences, user_responses)

        # Update user profile with onboarding completion
        await _update_user_profile_with_preferences(auth['user_id'], preferences)

        return {
            "success": True,
            "preferences_summary": summary,
            "daily_calories_target": preferences.daily_calories_target,
            "message": "Предпочтения сохранены! Теперь можем создать персонализированный план питания."
        }

    except Exception as e:
        logger.error(f"Failed to submit questionnaire responses: {e}")
        raise HTTPException(status_code=500, detail="Failed to process responses")


@router.get("/nutrition-onboarding/status", response_model=QuestionnaireStatusResponse)
async def get_onboarding_status(auth: AuthContext = Depends(require_auth_context)):
    """Get user's onboarding completion status"""

    try:
        # Check if user has completed onboarding
        user_preferences = await _get_user_preferences(auth['user_id'])

        if user_preferences:
            # User has completed onboarding
            summary = questionnaire.generate_onboarding_summary(user_preferences)
            return QuestionnaireStatusResponse(
                completed=True,
                completion_percentage=100,
                preferences_summary=summary
            )
        else:
            # Check for partial completion
            partial_responses = await _get_partial_responses(auth['user_id'])

            if partial_responses:
                # Calculate completion percentage based on responses
                total_questions = sum(len(step.questions) for step in questionnaire.get_questionnaire_flow())
                completion_pct = min(100, int((len(partial_responses) / total_questions) * 100))

                return QuestionnaireStatusResponse(
                    completed=False,
                    completion_percentage=completion_pct
                )
            else:
                # No progress yet
                return QuestionnaireStatusResponse(
                    completed=False,
                    completion_percentage=0
                )

    except Exception as e:
        logger.error(f"Failed to get onboarding status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.post("/nutrition-onboarding/adaptive-questions")
async def get_adaptive_questions(
    current_responses: List[Dict[str, Any]],
    auth: AuthContext = Depends(require_auth_context)
):
    """Get additional adaptive questions based on current responses"""

    try:
        # Convert to UserResponse objects
        user_responses = [
            UserResponse(
                question_id=resp["question_id"],
                value=resp["value"]
            )
            for resp in current_responses
        ]

        # Get adaptive questions
        adaptive_questions = questionnaire.get_adaptive_questions(user_responses)

        # Convert to response format
        questions_data = []
        for question in adaptive_questions:
            question_data = {
                "id": question.id,
                "type": question.type,
                "title": question.title,
                "description": question.description,
                "required": question.required
            }

            if question.options:
                question_data["options"] = question.options

            if question.min_value is not None:
                question_data["min_value"] = question.min_value

            if question.max_value is not None:
                question_data["max_value"] = question.max_value

            questions_data.append(question_data)

        return {
            "adaptive_questions": questions_data,
            "count": len(questions_data)
        }

    except Exception as e:
        logger.error(f"Failed to get adaptive questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get adaptive questions")


@router.post("/nutrition-onboarding/update-preferences")
async def update_user_preferences(
    preferences_update: Dict[str, Any],
    auth: AuthContext = Depends(require_auth_context)
):
    """Update specific user preferences"""

    try:
        # Get current preferences
        current_preferences = await _get_user_preferences(auth['user_id'])

        if not current_preferences:
            raise HTTPException(status_code=404, detail="User preferences not found. Complete onboarding first.")

        # Update specific fields
        for field, value in preferences_update.items():
            if hasattr(current_preferences, field):
                setattr(current_preferences, field, value)

        # Save updated preferences
        await _save_user_preferences(auth['user_id'], current_preferences, [])

        return {
            "success": True,
            "message": "Предпочтения обновлены",
            "updated_fields": list(preferences_update.keys())
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


# Internal API endpoints for bot integration

@router.post("/nutrition-onboarding/check-profile-internal")
@require_internal_auth
async def check_user_profile_internal(request: Request, payload: OnboardingProfileRequest):
    """Check if user has completed nutrition onboarding (internal)"""

    try:
        user_preferences = await _get_user_preferences(payload.user_id)

        return {
            "has_profile": user_preferences is not None,
            "needs_onboarding": user_preferences is None,
            "preferences_summary": questionnaire.generate_onboarding_summary(user_preferences) if user_preferences else None
        }

    except Exception as e:
        logger.error(f"Failed to check user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to check profile")


@router.get("/nutrition-onboarding/questionnaire-summary")
async def get_questionnaire_summary(auth: AuthContext = Depends(require_auth_context)):
    """Get quick summary of questionnaire for preview"""

    steps = questionnaire.get_questionnaire_flow()

    summary = {
        "total_steps": len(steps),
        "estimated_time": f"{len(steps) * 2} минут",
        "categories": [
            {"name": "Цели и мотивация", "icon": "🎯", "description": "Ваши цели в питании"},
            {"name": "Ограничения", "icon": "🚫", "description": "Аллергии и предпочтения"},
            {"name": "Вкусовые предпочтения", "icon": "😋", "description": "Любимые блюда и кухни"},
            {"name": "Режим питания", "icon": "⏰", "description": "Когда и как часто едите"},
            {"name": "Образ жизни", "icon": "👩‍🍳", "description": "Готовка и рабочий график"},
            {"name": "Здоровье", "icon": "🏃‍♀️", "description": "Активность и особенности"},
            {"name": "Социальные привычки", "icon": "👥", "description": "Питание в компании"}
        ],
        "benefits": [
            "Планы адаптированы под ваши вкусы",
            "Учтены все ограничения и аллергии",
            "Рецепты подобраны по времени готовки",
            "Режим питания под ваш график",
            "Рекомендации основаны на ваших целях"
        ]
    }

    return summary


# Helper functions

async def _save_user_preferences(user_id: str, preferences: NutritionPreferences, responses: List[UserResponse]) -> bool:
    """Save user preferences to database"""

    try:
        from common.db.enhanced_supabase_service import enhanced_supabase_service

        # Save preferences to user_profiles table
        preferences_data = preferences.dict()
        preferences_data["user_id"] = user_id
        preferences_data["onboarding_completed"] = True
        preferences_data["onboarding_completed_at"] = datetime.utcnow().isoformat()

        # Update user profile
        result = supabase.table("user_profiles").upsert(
            preferences_data,
            on_conflict="user_id"
        ).execute()

        # Save detailed responses for future analysis
        if responses:
            responses_data = []
            for response in responses:
                responses_data.append({
                    "user_id": user_id,
                    "question_id": response.question_id,
                    "response_value": str(response.value),
                    "response_timestamp": response.timestamp.isoformat(),
                    "created_at": datetime.utcnow().isoformat()
                })

            # Create table for responses if it doesn't exist
            supabase.table("nutrition_questionnaire_responses").upsert(
                responses_data
            ).execute()

        return bool(result.data)

    except Exception as e:
        logger.error(f"Failed to save user preferences: {e}")
        return False


async def _update_user_profile_with_preferences(user_id: str, preferences: NutritionPreferences) -> bool:
    """Update main user profile with key preferences"""

    try:
        profile_updates = {
            "goal": preferences.goal,
            "daily_calories_target": preferences.daily_calories_target,
            "activity_level": preferences.activity_level,
            "dietary_preferences": preferences.dietary_restrictions + preferences.cuisines,
            "allergies": preferences.allergies,
            "preferred_cuisines": preferences.cuisines,
            "disliked_foods": preferences.disliked_foods,
            "typical_portion_sizes": {
                "eating_frequency": preferences.eating_frequency,
                "snacking_preference": preferences.snacking_preference
            }
        }

        result = supabase.table("user_profiles").update(
            profile_updates
        ).eq("user_id", user_id).execute()

        return bool(result.data)

    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        return False


async def _get_user_preferences(user_id: str) -> Optional[NutritionPreferences]:
    """Get user preferences from database"""

    try:
        result = supabase.table("user_profiles").select(
            "*"
        ).eq("user_id", user_id).execute()

        if not result.data:
            return None

        profile_data = result.data[0]

        # Check if onboarding is completed
        if not profile_data.get("onboarding_completed"):
            return None

        # Convert database data back to NutritionPreferences
        return NutritionPreferences(
            goal=profile_data.get("goal", "health_improvement"),
            daily_calories_target=profile_data.get("daily_calories_target"),
            activity_level=profile_data.get("activity_level", "moderate"),
            dietary_restrictions=profile_data.get("dietary_preferences", []),
            allergies=profile_data.get("allergies", []),
            disliked_foods=profile_data.get("disliked_foods", []),
            favorite_foods=profile_data.get("favorite_foods", []),
            cuisines=profile_data.get("preferred_cuisines", []),
            meal_times=profile_data.get("meal_times", {}),
            eating_frequency=profile_data.get("typical_portion_sizes", {}).get("eating_frequency", "3_meals"),
            skip_meals=[],
            cooking_skill=profile_data.get("cooking_skill", "intermediate"),
            cooking_time_available=profile_data.get("cooking_time_available", "moderate"),
            work_schedule=profile_data.get("work_schedule", "office_9_5"),
            social_eating_frequency=profile_data.get("social_eating_frequency", "sometimes"),
            health_conditions=profile_data.get("health_conditions", []),
            supplements=[],
            water_intake_goal=profile_data.get("water_intake_goal", 8),
            meal_prep_preference=profile_data.get("meal_prep_preference", "some_prep"),
            snacking_preference=profile_data.get("typical_portion_sizes", {}).get("snacking_preference", "healthy_snacks"),
            weekend_eating_style=profile_data.get("weekend_eating_style", "relaxed"),
            stress_eating_tendency=profile_data.get("stress_eating_tendency", 3),
            primary_motivation=profile_data.get("primary_motivation", "progress_tracking"),
            weight_goal=profile_data.get("weight_goal"),
            timeline=profile_data.get("timeline", "3_months"),
            accountability_preference=profile_data.get("accountability_preference", "progress_tracking")
        )

    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        return None


async def _get_partial_responses(user_id: str) -> List[UserResponse]:
    """Get partial responses for incomplete onboarding"""

    try:
        result = supabase.table("nutrition_questionnaire_responses").select(
            "*"
        ).eq("user_id", user_id).execute()

        if not result.data:
            return []

        responses = []
        for row in result.data:
            response = UserResponse(
                question_id=row["question_id"],
                value=row["response_value"],
                timestamp=datetime.fromisoformat(row["response_timestamp"])
            )
            responses.append(response)

        return responses

    except Exception as e:
        logger.error(f"Failed to get partial responses: {e}")
        return []