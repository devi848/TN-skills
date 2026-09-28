const escapeHtml = (value) => {
    return String(value ?? "").replace(
        /[&<>"']/g,
        (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[character])
    );
};


const money = (value) => {
    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(value);
};


function renderRecommendation(output, payload) {

    const result = payload.result;

    let html = `
        <div class="result">

            <h2>
                Budget Plan
                <small>
                    ${escapeHtml(payload.source)}
                </small>
            </h2>

            <p>
                ${escapeHtml(result.summary)}
            </p>

            <div class="total">
                Total:
                ${money(result.total_budget)}
            </div>
    `;


    (
        result.budget_breakdown || []
    ).forEach((category) => {

        html += `
            <article class="rec">

                <div class="row">

                    <h3>
                        ${escapeHtml(
                            category.category
                        )}
                    </h3>

                    <b>
                        ${money(
                            category.allocation
                        )}
                    </b>

                </div>
        `;


        (
            category.items || []
        ).forEach((item) => {

            html += `
                <div class="item">

                    <div>

                        <h4>
                            ${escapeHtml(
                                item.name
                            )}
                        </h4>

                        <p>
                            ${escapeHtml(
                                item.description
                            )}
                        </p>

                        <small>
                            Qty ${item.quantity}
                            · Est.
                            ${money(
                                item.estimated_price
                            )}
                        </small>

                    </div>

                    <div>
            `;


            Object.entries(
                item.shopping_links || {}
            ).forEach(
                ([platform, url]) => {

                    html += `
                        <a
                            class="chip"
                            href="${url}"
                            target="_blank"
                            rel="noopener"
                        >
                            ${escapeHtml(platform)}
                        </a>
                    `;
                }
            );


            html += `
                    </div>

                </div>
            `;
        });


        html += `
            </article>
        `;
    });


    if (
        result.tips &&
        result.tips.length
    ) {

        html += `
            <div class="tips">

                <b>Tips</b>

                <ul>
                    ${result.tips
                        .map(
                            (tip) =>
                                `<li>${escapeHtml(tip)}</li>`
                        )
                        .join("")
                    }
                </ul>

            </div>
        `;
    }


    html += `
        </div>
    `;


    output.innerHTML = html;
}


function checked(form, name) {

    return (
        form.querySelector(
            `[name="${name}"]`
        )?.checked || false
    );
}


function numberValue(form, name) {

    return Number(
        form.querySelector(
            `[name="${name}"]`
        ).value
    );
}


async function postJson(
    url,
    data
) {

    const response = await fetch(
        url,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify(data)
        }
    );


    const json =
        await response.json();


    if (!response.ok) {

        throw new Error(
            json.detail ||
            "Request failed"
        );
    }


    return json;
}


function setupHomePlanner() {

    const form =
        document.querySelector(
            "#home-form"
        );

    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const output =
                document.querySelector(
                    "#home-result"
                );

            output.innerHTML =
                "<p>Generating your budget plan...</p>";


            try {

                const payload =
                    await postJson(
                        "/api/recommendations/home",
                        {
                            total_budget:
                                numberValue(
                                    form,
                                    "total_budget"
                                ),

                            num_lights:
                                numberValue(
                                    form,
                                    "num_lights"
                                ),

                            num_fans:
                                numberValue(
                                    form,
                                    "num_fans"
                                ),

                            num_furniture:
                                numberValue(
                                    form,
                                    "num_furniture"
                                ),

                            num_dining_tables:
                                numberValue(
                                    form,
                                    "num_dining_tables"
                                ),

                            has_living_room:
                                checked(
                                    form,
                                    "has_living_room"
                                ),

                            has_kitchen:
                                checked(
                                    form,
                                    "has_kitchen"
                                ),

                            has_bedroom:
                                checked(
                                    form,
                                    "has_bedroom"
                                ),

                            additional_requirements:
                                form.querySelector(
                                    '[name="additional_requirements"]'
                                ).value
                        }
                    );


                renderRecommendation(
                    output,
                    payload
                );

            } catch (error) {

                output.innerHTML = `
                    <p class="error">
                        ${escapeHtml(
                            error.message
                        )}
                    </p>
                `;
            }
        }
    );
}


function setupPartyPlanner() {

    const form =
        document.querySelector(
            "#party-form"
        );

    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const output =
                document.querySelector(
                    "#party-result"
                );

            output.innerHTML =
                "<p>Generating your party budget plan...</p>";


            try {

                const payload =
                    await postJson(
                        "/api/recommendations/party",
                        {
                            total_budget:
                                numberValue(
                                    form,
                                    "total_budget"
                                ),

                            num_guests:
                                numberValue(
                                    form,
                                    "num_guests"
                                ),

                            party_type:
                                form.querySelector(
                                    '[name="party_type"]'
                                ).value,

                            venue_type:
                                form.querySelector(
                                    '[name="venue_type"]'
                                ).value,

                            needs_catering:
                                checked(
                                    form,
                                    "needs_catering"
                                ),

                            needs_decoration:
                                checked(
                                    form,
                                    "needs_decoration"
                                ),

                            needs_entertainment:
                                checked(
                                    form,
                                    "needs_entertainment"
                                ),

                            additional_requirements:
                                form.querySelector(
                                    '[name="additional_requirements"]'
                                ).value
                        }
                    );


                renderRecommendation(
                    output,
                    payload
                );

            } catch (error) {

                output.innerHTML = `
                    <p class="error">
                        ${escapeHtml(
                            error.message
                        )}
                    </p>
                `;
            }
        }
    );
}


function setupJewelryPlanner() {

    const form =
        document.querySelector(
            "#jewelry-form"
        );

    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const output =
                document.querySelector(
                    "#jewelry-result"
                );

            output.innerHTML =
                "<p>Generating jewelry recommendations...</p>";


            try {

                const response =
                    await fetch(
                        "/api/recommendations/jewelry",
                        {
                            method: "POST",
                            body:
                                new FormData(form)
                        }
                    );


                const payload =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        payload.detail ||
                        "Request failed"
                    );
                }


                renderRecommendation(
                    output,
                    payload
                );

            } catch (error) {

                output.innerHTML = `
                    <p class="error">
                        ${escapeHtml(
                            error.message
                        )}
                    </p>
                `;
            }
        }
    );
}


function setup() {

    setupHomePlanner();

    setupPartyPlanner();

    setupJewelryPlanner();
}


document.addEventListener(
    "DOMContentLoaded",
    setup
);