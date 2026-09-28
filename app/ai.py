from typing import Optional

from PIL import Image

from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from .schemas import (
    HomeBudgetInput,
    PartyBudgetInput,
    JewelryBudgetInput,
    RecommendationResponse
)


try:
    from google import genai
except ImportError:
    genai = None


class AIService:

    def __init__(self):

        if (
            genai is not None
            and GEMINI_API_KEY
        ):
            self.client = genai.Client(
                api_key=GEMINI_API_KEY
            )
        else:
            self.client = None

    def generate(
        self,
        prompt: str,
        image_path: Optional[str] = None
    ):

        if not self.client:
            raise RuntimeError(
                "Gemini API is not configured"
            )

        contents = [prompt]

        if image_path:

            with Image.open(
                image_path
            ) as image:

                contents.append(
                    image.copy()
                )

        response = (
            self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config={
                    "response_mime_type":
                        "application/json",

                    "response_schema":
                        RecommendationResponse,

                    "temperature":
                        0.4,

                    "max_output_tokens":
                        5000
                }
            )
        )

        if getattr(
            response,
            "parsed",
            None
        ):
            return RecommendationResponse.model_validate(
                response.parsed
            )

        return RecommendationResponse.model_validate_json(
            response.text
        )

    def home(
        self,
        data: HomeBudgetInput
    ):

        rooms = ", ".join(
            [
                name
                for name, enabled in [
                    (
                        "Living Room",
                        data.has_living_room
                    ),
                    (
                        "Kitchen",
                        data.has_kitchen
                    ),
                    (
                        "Bedroom",
                        data.has_bedroom
                    )
                ]
                if enabled
            ]
        ) or "General home"

        prompt = f"""
You are PocketSmart AI,
a budget recommendation assistant
for users in India.

Create a practical home interior
shopping plan in Indian Rupees.

Budget:
₹{data.total_budget:.2f}

Required counts:

Lights:
{data.num_lights}

Fans:
{data.num_fans}

Furniture pieces:
{data.num_furniture}

Dining tables:
{data.num_dining_tables}

Rooms:
{rooms}

Additional requirements:
{data.additional_requirements or "None"}

Requirements:

1. Keep the total allocation at or
   below the user's budget.

2. Use realistic approximate Indian
   market prices.

3. Suggest practical product types.

4. Provide useful search terms.

5. Give a concise summary.

6. Give practical shopping tips.

7. Return only the requested JSON
   schema.
"""

        return self.generate(prompt)

    def party(
        self,
        data: PartyBudgetInput
    ):

        prompt = f"""
You are PocketSmart AI for the
Indian market.

Create a practical party budget
plan in Indian Rupees.

Budget:
₹{data.total_budget:.2f}

Number of guests:
{data.num_guests}

Party type:
{data.party_type}

Venue:
{data.venue_type}

Catering required:
{data.needs_catering}

Decoration required:
{data.needs_decoration}

Entertainment required:
{data.needs_entertainment}

Additional requirements:
{data.additional_requirements or "None"}

Requirements:

1. Keep allocations within budget.

2. Use approximate Indian costs.

3. Consider the number of guests.

4. Provide useful search terms.

5. Provide practical budget categories.

6. Give useful tips.

7. Return only the requested JSON schema.
"""

        return self.generate(prompt)

    def jewelry(
        self,
        data: JewelryBudgetInput,
        image_path: Optional[str] = None
    ):

        prompt = f"""
You are PocketSmart AI for
Indian jewelry shopping.

Create a budget-aware jewelry
recommendation plan.

Budget:
₹{data.total_budget:.2f}

Occasion:
{data.occasion}

Style preferences:
{data.style_preferences or "Not specified"}

Prices are approximate estimates,
not live quotations.

Suggest:

- affordable jewelry options
- suitable materials
- suitable styles
- useful Indian search terms
- budget allocation
- shopping tips

If an outfit image is supplied,
use it only to improve style and
color matching.

Return only the requested
JSON schema.
"""

        return self.generate(
            prompt,
            image_path
        )


ai_service = AIService()