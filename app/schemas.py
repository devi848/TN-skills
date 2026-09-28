from pydantic import BaseModel, Field


class HomeBudgetInput(BaseModel):
    total_budget: float = Field(gt=0)

    num_lights: int = Field(
        ge=0,
        le=100
    )

    num_fans: int = Field(
        ge=0,
        le=100
    )

    num_furniture: int = Field(
        ge=0,
        le=100
    )

    num_dining_tables: int = Field(
        ge=0,
        le=50
    )

    has_living_room: bool = False
    has_kitchen: bool = False
    has_bedroom: bool = False

    additional_requirements: str = ""


class PartyBudgetInput(BaseModel):
    total_budget: float = Field(gt=0)

    num_guests: int = Field(
        ge=1,
        le=10000
    )

    party_type: str = "Birthday"

    venue_type: str = "Home"

    needs_catering: bool = False
    needs_decoration: bool = False
    needs_entertainment: bool = False

    additional_requirements: str = ""


class JewelryBudgetInput(BaseModel):
    total_budget: float = Field(gt=0)

    occasion: str = "Birthday"

    style_preferences: str = ""


class Item(BaseModel):
    name: str

    description: str

    estimated_price: float = Field(
        ge=0
    )

    quantity: int = Field(
        ge=1
    )

    search_terms: str

    shopping_links: dict[str, str] = {}


class Category(BaseModel):
    category: str

    allocation: float = Field(
        ge=0
    )

    items: list[Item] = []


class RecommendationResponse(BaseModel):
    total_budget: float = Field(
        ge=0
    )

    budget_breakdown: list[Category] = []

    summary: str = ""

    tips: list[str] = []