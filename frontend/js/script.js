const modal = document.querySelector("#ingredient-modal");
const form = document.querySelector("#ingredient-form");
const openButton = document.querySelector("#open-modal");
const closeButton = document.querySelector("#close-modal");

openButton.addEventListener("click", () => {
    modal.showModal();
});

closeButton.addEventListener("click", () => {
    modal.close();
});

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const ingredient = Object.fromEntries(formData.entries());

    ingredient.reorder_lead_time_days = Number(
        ingredient.reorder_lead_time_days
    );

    console.log("Данные ингредиента: ", ingredient);

    form.reset();
    modal.close();
})