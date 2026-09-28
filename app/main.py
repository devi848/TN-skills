import json
import uuid

from pathlib import Path

from fastapi import (
    FastAPI,
    Request,
    Form,
    UploadFile,
    File,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.staticfiles import StaticFiles

from fastapi.templating import (
    Jinja2Templates
)

from .config import (
    APP_NAME,
    UPLOAD_DIR,
    MAX_UPLOAD_MB
)

from .db import (
    init_db,
    user_username,
    user_email,
    create_user,
    save_rec,
    recs,
    rec
)

from .auth import (
    hash_password,
    verify_password,
    token,
    set_cookie,
    current
)

from .schemas import (
    HomeBudgetInput,
    PartyBudgetInput,
    JewelryBudgetInput
)

from .ai import ai_service

from .recommendations import (
    add_links
)


app = FastAPI(
    title=APP_NAME
)


app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static"
)

app.mount(
    "/uploads",
    StaticFiles(
        directory=str(UPLOAD_DIR)
    ),
    name="uploads"
)


templates = Jinja2Templates(
    directory="templates"
)


@app.on_event("startup")
def startup():
    init_db()


def page(
    request: Request,
    template_name: str,
    **kwargs
):

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "request": request,
            "user": current(request),
            **kwargs
        }
    )


def login_redirect(
    request: Request
):

    return RedirectResponse(
        "/login?next=" +
        request.url.path,
        status_code=303
    )


@app.get(
    "/",
    response_class=HTMLResponse
)
def index(request: Request):

    return page(
        request,
        "index.html"
    )


@app.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(
    request: Request
):

    return page(
        request,
        "register.html",
        errors=[]
    )


@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(""),
    password: str = Form(...),
    confirm_password: str = Form(...)
):

    errors = []

    username_clean = username.strip()

    if len(username_clean) < 3:
        errors.append(
            "Username must be at least 3 characters."
        )

    if len(password) < 6:
        errors.append(
            "Password must be at least 6 characters."
        )

    if password != confirm_password:
        errors.append(
            "Passwords do not match."
        )

    if user_username(username):
        errors.append(
            "Username already exists."
        )

    if user_email(email):
        errors.append(
            "Email already exists."
        )

    if errors:

        return page(
            request,
            "register.html",
            errors=errors
        )

    user_id_value = create_user(
        username,
        email,
        full_name,
        hash_password(password)
    )

    response = RedirectResponse(
        "/dashboard",
        status_code=303
    )

    set_cookie(
        response,
        token(user_id_value)
    )

    return response


@app.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(
    request: Request
):

    return page(
        request,
        "login.html",
        error=None
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    user = user_username(
        username
    )

    if (
        not user
        or not verify_password(
            password,
            user["password_hash"]
        )
    ):

        return page(
            request,
            "login.html",
            error="Incorrect username or password."
        )

    response = RedirectResponse(
        "/dashboard",
        status_code=303
    )

    set_cookie(
        response,
        token(user["id"])
    )

    return response


@app.post("/logout")
def logout():

    response = RedirectResponse(
        "/",
        status_code=303
    )

    response.delete_cookie(
        "access_token"
    )

    return response


@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(
    request: Request
):

    user = current(request)

    if not user:
        return login_redirect(request)

    return page(
        request,
        "dashboard.html",
        history=recs(
            user["id"],
            6
        )
    )


@app.get(
    "/home-planner",
    response_class=HTMLResponse
)
def home_page(
    request: Request
):

    if not current(request):
        return login_redirect(request)

    return page(
        request,
        "home_planner.html"
    )


@app.get(
    "/party-planner",
    response_class=HTMLResponse
)
def party_page(
    request: Request
):

    if not current(request):
        return login_redirect(request)

    return page(
        request,
        "party_planner.html"
    )


@app.get(
    "/jewelry-planner",
    response_class=HTMLResponse
)
def jewelry_page(
    request: Request
):

    if not current(request):
        return login_redirect(request)

    return page(
        request,
        "jewelry_planner.html"
    )


def create_item(
    name,
    description,
    price,
    quantity,
    search_terms
):

    return {
        "name": name,
        "description": description,
        "estimated_price": price,
        "quantity": quantity,
        "search_terms": search_terms
    }


def fallback_home(
    data: HomeBudgetInput
):

    categories = []

    items = [
        (
            "Lighting",
            data.num_lights,
            0.12,
            "LED ceiling light"
        ),
        (
            "Fans",
            data.num_fans,
            0.14,
            "ceiling fan"
        ),
        (
            "Furniture",
            data.num_furniture,
            0.42,
            "home furniture"
        ),
        (
            "Dining",
            data.num_dining_tables,
            0.22,
            "dining table"
        )
    ]

    for (
        name,
        quantity,
        percentage,
        search_terms
    ) in items:

        if quantity > 0:

            allocation = round(
                data.total_budget *
                percentage,
                2
            )

            categories.append(
                {
                    "category": name,
                    "allocation": allocation,
                    "items": [
                        create_item(
                            search_terms.title(),
                            "Approximate Indian-market estimate.",
                            round(
                                allocation /
                                max(quantity, 1),
                                2
                            ),
                            quantity,
                            search_terms
                        )
                    ]
                }
            )

    if not categories:

        categories = [
            {
                "category": "General",
                "allocation": data.total_budget,
                "items": [
                    create_item(
                        "Home essentials",
                        "Starter home interior plan.",
                        data.total_budget,
                        1,
                        "home interior essentials"
                    )
                ]
            }
        ]

    return {
        "total_budget":
            data.total_budget,

        "budget_breakdown":
            categories,

        "summary":
            "Starter plan generated locally. "
            "Configure Gemini for richer personalization.",

        "tips": [
            "Keep a contingency amount.",
            "Compare sellers before buying.",
            "Prices are estimates, not live quotes."
        ]
    }


def fallback_party(
    data: PartyBudgetInput
):

    categories = []

    options = [
        (
            True,
            "Venue",
            0.25,
            "party venue",
            1
        ),
        (
            data.needs_catering,
            "Catering",
            0.35,
            "party catering",
            data.num_guests
        ),
        (
            data.needs_decoration,
            "Decoration",
            0.15,
            "party decoration",
            1
        ),
        (
            data.needs_entertainment,
            "Entertainment",
            0.15,
            "party entertainment",
            1
        )
    ]

    for (
        enabled,
        name,
        percentage,
        search_terms,
        quantity
    ) in options:

        if enabled:

            allocation = round(
                data.total_budget *
                percentage,
                2
            )

            categories.append(
                {
                    "category": name,
                    "allocation": allocation,
                    "items": [
                        create_item(
                            name,
                            "Approximate event allocation.",
                            allocation,
                            quantity,
                            search_terms
                        )
                    ]
                }
            )

    if not categories:

        categories = [
            {
                "category": "General",
                "allocation":
                    data.total_budget,

                "items": [
                    create_item(
                        "Party essentials",
                        "Starter party plan.",
                        data.total_budget,
                        1,
                        "party essentials"
                    )
                ]
            }
        ]

    return {
        "total_budget":
            data.total_budget,

        "budget_breakdown":
            categories,

        "summary":
            "Starter party plan generated locally.",

        "tips": [
            "Align food cost with guest count.",
            "Keep a contingency amount.",
            "Confirm service charges before payment."
        ]
    }


def fallback_jewelry(
    data: JewelryBudgetInput
):

    return {
        "total_budget":
            data.total_budget,

        "budget_breakdown": [
            {
                "category": "Jewelry",

                "allocation":
                    data.total_budget,

                "items": [
                    create_item(
                        "Budget-friendly jewelry set",

                        (
                            f"Starter suggestion for "
                            f"{data.occasion}. "
                            f"Preferences: "
                            f"{data.style_preferences or 'not specified'}."
                        ),

                        data.total_budget,
                        1,
                        "jewelry set India"
                    )
                ]
            }
        ],

        "summary":
            "Starter jewelry plan generated locally. "
            "Configure Gemini for richer recommendations "
            "and image matching.",

        "tips": [
            "Compare making charges separately.",
            "Check certification and return policies.",
            "Prices are estimates."
        ]
    }


def run_ai(
    function,
    fallback
):

    try:

        result = function()

        return (
            result.model_dump(),
            "Gemini AI"
        )

    except Exception:

        return (
            fallback,
            "Local fallback"
        )


@app.post(
    "/api/recommendations/home"
)
async def home_api(
    request: Request
):

    user = current(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Login required"
        )

    try:

        data = HomeBudgetInput.model_validate(
            await request.json()
        )

    except Exception as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    result, source = run_ai(
        lambda: ai_service.home(data),
        fallback_home(data)
    )

    result = add_links(
        result,
        "home"
    )

    recommendation_id = save_rec(
        user["id"],
        "home",
        "Home Interior Budget Plan",
        data.model_dump(),
        result
    )

    return {
        "id": recommendation_id,
        "source": source,
        "result": result
    }


@app.post(
    "/api/recommendations/party"
)
async def party_api(
    request: Request
):

    user = current(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Login required"
        )

    try:

        data = PartyBudgetInput.model_validate(
            await request.json()
        )

    except Exception as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    result, source = run_ai(
        lambda: ai_service.party(data),
        fallback_party(data)
    )

    result = add_links(
        result,
        "party"
    )

    recommendation_id = save_rec(
        user["id"],
        "party",
        "Party Budget Plan",
        data.model_dump(),
        result
    )

    return {
        "id": recommendation_id,
        "source": source,
        "result": result
    }


@app.post(
    "/api/recommendations/jewelry"
)
async def jewelry_api(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form("Birthday"),
    style_preferences: str = Form(""),
    outfit_image: UploadFile | None = File(None)
):

    user = current(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Login required"
        )

    try:

        data = JewelryBudgetInput(
            total_budget=budget,
            occasion=occasion,
            style_preferences=style_preferences
        )

    except Exception as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    image_path = None
    relative_image_path = None

    if (
        outfit_image
        and outfit_image.filename
    ):

        allowed_types = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }

        extension = allowed_types.get(
            outfit_image.content_type
        )

        if not extension:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG, or WEBP "
                    "images are supported."
                )
            )

        raw = await outfit_image.read()

        maximum_bytes = (
            MAX_UPLOAD_MB *
            1024 *
            1024
        )

        if len(raw) > maximum_bytes:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Image must be "
                    f"{MAX_UPLOAD_MB} MB or smaller."
                )
            )

        filename = (
            uuid.uuid4().hex +
            extension
        )

        image_path = str(
            UPLOAD_DIR / filename
        )

        Path(image_path).write_bytes(
            raw
        )

        relative_image_path = (
            "/uploads/" + filename
        )

    result, source = run_ai(
        lambda: ai_service.jewelry(
            data,
            image_path
        ),
        fallback_jewelry(data)
    )

    result = add_links(
        result,
        "jewelry"
    )

    recommendation_id = save_rec(
        user["id"],
        "jewelry",
        "Jewelry Budget Plan",
        data.model_dump(),
        result,
        relative_image_path
    )

    return {
        "id": recommendation_id,
        "source": source,
        "result": result,
        "image": relative_image_path
    }


@app.get(
    "/history",
    response_class=HTMLResponse
)
def history(
    request: Request
):

    user = current(request)

    if not user:
        return login_redirect(request)

    return page(
        request,
        "history.html",
        history=recs(
            user["id"]
        )
    )


@app.get(
    "/recommendation/{recommendation_id}",
    response_class=HTMLResponse
)
def detail(
    request: Request,
    recommendation_id: int
):

    user = current(request)

    if not user:
        return login_redirect(request)

    record = rec(
        user["id"],
        recommendation_id
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    result = json.loads(
        record["result_json"]
    )

    return page(
        request,
        "recommendation.html",
        record=record,
        result=result
    )


@app.get("/health")
def health():

    return {
        "status": "ok",
        "gemini_configured":
            bool(ai_service.client)
    }