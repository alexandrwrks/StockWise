import { api, login, logout, register } from "./auth.js";

const $ = (selector) => document.querySelector(selector);
const roles = { owner: "Владелец", admin: "Администратор", employee: "Сотрудник" };
const memberStatuses = { active: "Активен", blocked: "Заблокирован", invited: "Приглашён" };
const statuses = { draft: "Черновик", received: "Принята", canceled: "Отменена" };
const units = { gr: "г", ml: "мл", pcs: "шт." };

let user;
let organizations = [];
let organizationId;
let tab = "ingredients";
let viewVersion = 0;
let registering = false;

const selected = () => organizations.find(({ organization_id }) => organization_id === organizationId);
const canManage = () => ["owner", "admin"].includes(selected()?.role);
const isOwner = () => selected()?.role === "owner";
const orgPath = () => `/organizations/${organizationId}`;
const ingredientsPath = () => `/${organizationId}/ingredients`;
const purchasesPath = () => `/purchase/${organizationId}/purchases`;

function element(tag, properties = {}, ...children) {
    const node = Object.assign(document.createElement(tag), properties);
    node.append(...children.flat());
    return node;
}

function button(text, action, className = "") {
    return element("button", { type: "button", textContent: text, onclick: action, className });
}

function select(name, options, value = "") {
    const control = element("select", { name, required: true },
        options.map(([key, label]) => element("option", { value: key }, label)));
    control.value = value;
    return control;
}

function field(label, name, value = "", attributes = {}) {
    return element("label", {}, label, element("input", {
        name, value: value ?? "", required: true, ...attributes,
    }));
}

const decimal = { type: "number", min: "0", step: "0.001", max: "999999999.999" };
const formValues = (form) => Object.fromEntries(new FormData(form));
const formatDate = (value) => new Date(value).toLocaleString("ru");
const change = (path, method, data, key = "body") => api(path, { method, [key]: data });

function notice(message = "") {
    $("#notice").textContent = message;
    $("#notice").hidden = !message;
}

async function run(action) {
    notice();
    try {
        await action();
    } catch (error) {
        if (error.status !== 401 || !$("#notice").textContent) notice(error.message);
    }
}

function renderAuth() {
    $("#auth-title").textContent = registering ? "Создать аккаунт" : "Вход в StockWise";
    $("#auth-toggle").textContent = registering ? "Уже есть аккаунт" : "Создать аккаунт";
    $("#auth-form").replaceChildren(
        ...(registering ? [field("Имя", "fullname", "", { autocomplete: "name" })] : []),
        field("Email", "email", "", { type: "email", autocomplete: "username" }),
        field("Пароль", "password", "", {
            type: "password",
            autocomplete: registering ? "new-password" : "current-password",
        }),
        element("button", { type: "submit" }, registering ? "Зарегистрироваться" : "Войти"),
    );
}

function signedOut() {
    user = null;
    organizations = [];
    organizationId = undefined;
    viewVersion++;
    $("#editor").close();
    $("#content").replaceChildren();
    $("#account").hidden = true;
    $("#workspace").hidden = true;
    $("#auth").hidden = false;
    registering = false;
    renderAuth();
}

async function signedIn() {
    user = await api("/auth/me");
    $("#auth-form").reset();
    $("#auth").hidden = true;
    $("#account").hidden = false;
    $("#workspace").hidden = false;
    await loadOrganizations();
}

$("#auth-toggle").onclick = () => {
    registering = !registering;
    notice();
    renderAuth();
};

$("#auth-form").onsubmit = (event) => {
    event.preventDefault();
    const data = formValues(event.currentTarget);
    const submit = event.submitter;
    submit.disabled = true;
    $("#auth-toggle").disabled = true;
    void run(async () => {
        if (registering) await register(data);
        await login({ email: data.email, password: data.password });
        await signedIn();
    }).finally(() => {
        submit.disabled = false;
        $("#auth-toggle").disabled = false;
    });
};

$("#logout").onclick = async (event) => {
    const control = event.currentTarget;
    control.disabled = true;
    try {
        await run(async () => {
            await logout();
            signedOut();
        });
    } finally {
        control.disabled = false;
    }
};

window.addEventListener("session-expired", () => {
    signedOut();
    notice("Сессия истекла. Войдите снова.");
});

const dialog = $("#editor");
const editorForm = $("#editor-form");
$("#close-editor").onclick = () => dialog.close();
dialog.addEventListener("cancel", (event) => {
    if (editorForm.querySelector('button[type="submit"]:disabled')) event.preventDefault();
});

function edit(title, fields, save, submitLabel = "Сохранить") {
    $("#editor-title").textContent = title;
    $("#editor-error").textContent = "";
    const submit = element("button", { type: "submit" }, submitLabel);
    editorForm.replaceChildren(...fields, submit);
    editorForm.onsubmit = async (event) => {
        event.preventDefault();
        submit.disabled = true;
        $("#close-editor").disabled = true;
        $("#editor-error").textContent = "";
        try {
            const afterSave = await save(formValues(editorForm));
            dialog.close();
            if (afterSave) await run(afterSave);
        } catch (error) {
            $("#editor-error").textContent = error.message;
        } finally {
            submit.disabled = false;
            $("#close-editor").disabled = false;
        }
    };
    if (!dialog.open) dialog.showModal();
}

$("#profile").onclick = () => {
    edit("Профиль", [
        field("Имя", "fullname", user.fullname),
        field("Email", "email", user.email, { type: "email" }),
        button("Изменить пароль", editPassword, "text-button"),
    ], async (data) => {
        user = await change("/auth/me", "PATCH", data);
    });
};

function editPassword() {
    const password = { type: "password", minLength: 8, autocomplete: "new-password" };
    edit("Изменить пароль", [
        field("Новый пароль", "new_password", "", password),
        field("Повторите пароль", "password_retry", "", password),
    ], async (data) => {
        if (data.new_password !== data.password_retry) throw new Error("Пароли не совпадают.");
        await change("/auth/change-password", "POST", data);
        return () => notice("Пароль изменён.");
    });
}

async function loadOrganizations(preferred = organizationId) {
    organizations = await api("/organizations/");
    organizationId = organizations.find((org) => org.organization_id === preferred)?.organization_id
        ?? organizations[0]?.organization_id;
    const picker = $("#org-select");
    picker.replaceChildren(...organizations.map((org) =>
        element("option", { value: org.organization_id }, org.name)));
    picker.value = organizationId ?? "";
    picker.parentElement.hidden = organizations.length === 0;
    await renderWorkspace();
}

$("#org-select").onchange = (event) => {
    organizationId = event.target.value;
    void run(renderWorkspace);
};

$("#create-org").onclick = () => editOrganization();

function editOrganization(org) {
    const path = org ? orgPath() : "/organizations/";
    edit(org ? "Редактировать организацию" : "Новая организация", [
        field("Название", "name", org?.name, { maxLength: 200 }),
        element("label", {}, "Описание", element("textarea", {
            name: "description", maxLength: 2000, value: org?.description ?? "",
        })),
    ], async (data) => {
        data.name = data.name.trim();
        if (!data.name) throw new Error("Введите название организации.");
        const saved = await change(path, org ? "PATCH" : "POST", data, "query");
        return () => loadOrganizations(saved.id);
    });
}

const panels = {
    ingredients: ["Ингредиенты", showIngredients],
    purchases: ["Закупки", showPurchases],
    members: ["Участники", showMembers],
    organization: ["Организация", showOrganization],
};

async function renderWorkspace() {
    const version = ++viewVersion;
    const content = $("#content");
    const nav = $("#navigation");
    const org = selected();
    $("#org-heading").textContent = org?.name ?? "Организации";
    $("#org-description").textContent = org ? roles[org.role] ?? org.role : "";
    nav.hidden = !org;
    if (!org) {
        content.textContent = "Создайте организацию, чтобы вести остатки и закупки.";
        return;
    }

    const tabs = canManage() ? Object.keys(panels) : ["ingredients", "organization"];
    if (!tabs.includes(tab)) tab = "ingredients";
    nav.replaceChildren(...tabs.map((name) => {
        const link = button(panels[name][0], () => {
            tab = name;
            void run(renderWorkspace);
        });
        if (name === tab) link.setAttribute("aria-current", "page");
        return link;
    }));

    await displayPanel(version, panels[tab][1]);
}

async function displayPanel(version, load) {
    const content = $("#content");
    content.textContent = "Загрузка…";
    try {
        const view = await load();
        if (version === viewVersion) content.replaceChildren(view);
    } catch (error) {
        if (version !== viewVersion) return;
        content.replaceChildren(element("p", { className: "error" }, error.message),
            button("Повторить", () => void run(renderWorkspace)));
    }
}

function heading(title, ...actions) {
    return element("div", { className: "section-header" }, element("h2", {}, title),
        element("div", { className: "actions" }, actions));
}

function table(columns, rows, empty) {
    if (!rows.length) return element("p", { className: "muted" }, empty);
    return element("div", { className: "table-scroll" }, element("table", {},
        element("thead", {}, element("tr", {}, columns.map((name) => element("th", { scope: "col" }, name)))),
        element("tbody", {}, rows.map((row) =>
            element("tr", {}, row.map((value) => element("td", {}, value ?? "—"))))),
    ));
}

async function showOrganization() {
    const org = await api(orgPath());
    return element("div", {},
        heading("Организация", ...(isOwner() ? [button("Редактировать", () => editOrganization(org))] : [])),
        element("p", {}, org.description || "Описание отсутствует."));
}

async function showMembers() {
    const path = `${orgPath()}/members`;
    const members = await api(path);
    return element("div", {},
        heading("Участники"),
        element("p", { className: "muted" }, "Приглашения пока недоступны."),
        table(["Пользователь", "Роль", "Статус", "Действия"], members.map((member) => [
            member.user_id === user.id ? `${user.fullname} (вы)` : member.user_id,
            roles[member.role] ?? member.role,
            memberStatuses[member.status] ?? member.status,
            isOwner() && member.role !== "owner" && member.status === "active"
                ? element("div", { className: "actions" },
                    button("Изменить роль", () => edit("Роль участника", [
                        element("label", {}, "Роль", select("new_role",
                            [["admin", roles.admin], ["employee", roles.employee]], member.role)),
                    ], async (data) => {
                        await change(`${path}/${member.user_id}`, "PATCH", data, "query");
                        return renderWorkspace;
                    })),
                    button("Заблокировать", () => confirmAction("Заблокировать участника?",
                        () => api(`${path}/${member.user_id}`, { method: "DELETE" })), "danger"))
                : "—",
        ]), "В организации пока нет участников."));
}

function confirmAction(title, action, afterSave = renderWorkspace) {
    edit(title, [], async () => {
        await action();
        return afterSave;
    }, "Подтвердить");
}

async function showIngredients() {
    const path = ingredientsPath();
    const ingredients = await api(path);
    return element("div", {},
        heading("Ингредиенты", ...(canManage() ? [button("Добавить ингредиент", () => editIngredient(), "primary")] : [])),
        table(["Название", "SKU", "Остаток", "Минимум", "Цена за ед.", "Статус"], ingredients.map((item) => [
            button(item.name, () => void run(async () => {
                const ingredient = await api(`${path}/${item.id}`);
                if (path === ingredientsPath() && tab === "ingredients") showIngredient(ingredient);
            }), "text-button"),
            item.sku, `${item.current_stock} ${units[item.unit]}`,
            item.minimum_stock, item.unit_price,
            !item.is_active ? "Архив" : Number(item.current_stock) < Number(item.minimum_stock) ? "Ниже минимума" : "Активен",
        ]), "В этой организации пока нет ингредиентов."));
}

function showIngredient(item) {
    edit(item.name, [
        element("p", {}, `Артикул: ${item.sku}. Остаток: ${item.current_stock} ${units[item.unit]}.`),
        element("p", {}, `Минимум: ${item.minimum_stock}. Срок поставки: ${item.reorder_lead_time_days} дн.`),
        ...(canManage() && item.is_active ? [
            button("Редактировать", () => editIngredient(item)),
            button("Архивировать", () => confirmAction("Архивировать ингредиент?",
                () => api(`${ingredientsPath()}/${item.id}`, { method: "DELETE" })), "danger"),
        ] : []),
    ], async () => {}, "Готово");
}

function editIngredient(item) {
    const path = item ? `${ingredientsPath()}/${item.id}` : ingredientsPath();
    edit(item ? "Редактировать ингредиент" : "Добавить ингредиент", [
        field("Название", "name", item?.name, { maxLength: 150 }),
        field("Артикул", "sku", item?.sku, { maxLength: 50 }),
        ...(!item ? [
            element("label", {}, "Единица измерения", select("unit", Object.entries(units), "gr")),
            field("Начальный остаток", "current_stock", "0", decimal),
            field("Минимальный остаток", "minimum_stock", "0", decimal),
        ] : []),
        field("Цена за единицу", "unit_price", item?.unit_price ?? "0", decimal),
        field("Срок поставки, дней", "reorder_lead_time_days", item?.reorder_lead_time_days ?? "0",
            { type: "number", min: "0", step: "1", max: "2147483647" }),
    ], async (data) => {
        await change(path, item ? "PATCH" : "POST", data, "query");
        return renderWorkspace;
    });
}

async function showPurchases() {
    const path = purchasesPath();
    const [purchases, ingredients] = await Promise.all([api(path), api(ingredientsPath())]);
    return element("div", {},
        heading("Закупки", button("Новая закупка", () => editPurchase(path, ingredients), "primary")),
        table(["Создана", "Статус", "Комментарий", "Действия"], purchases.map((purchase) => [
            formatDate(purchase.created_at),
            element("span", { className: `badge ${purchase.status}` }, statuses[purchase.status] ?? purchase.status),
            purchase.comment || "—",
            button("Открыть", () => void run(async () => {
                const detail = await api(`${path}/${purchase.id}`);
                if (path === purchasesPath() && tab === "purchases") showPurchase(path, ingredients, detail);
            })),
        ]), "В этой организации пока нет закупок."));
}

function showPurchase(path, ingredients, purchase) {
    const detailPath = `${path}/${purchase.id}`;
    const byId = new Map(ingredients.map((item) => [item.id, item]));
    const transition = (action, title) => confirmAction(title,
        () => api(`${detailPath}/${action}`, { method: "POST" }));
    edit("Закупка", [
        element("p", { className: "muted" }, `${statuses[purchase.status]} · ${formatDate(purchase.created_at)}`),
        ...(purchase.comment ? [element("p", {}, purchase.comment)] : []),
        table(["Ингредиент", "Количество", "Цена за ед."], purchase.items.map((item) => {
            const ingredient = byId.get(item.ingredient_id);
            return [ingredient?.name ?? item.ingredient_id,
                `${item.quantity} ${units[ingredient?.unit] ?? ""}`, item.unit_price];
        }), "В закупке нет позиций."),
        ...(purchase.status === "draft" ? [
            element("div", { className: "actions" },
                button("Редактировать", () => editPurchase(path, ingredients, purchase)),
                button("Принять на склад", () => transition("receive", "Принять закупку и пополнить остатки?")),
                button("Отменить закупку", () => transition("cancel", "Отменить закупку?"), "danger")),
        ] : []),
    ], async () => {}, "Закрыть");
}

function editPurchase(path, ingredients, purchase) {
    const active = ingredients.filter(({ is_active }) => is_active);
    if (!purchase && !active.length) {
        notice("Сначала добавьте активный ингредиент.");
        return;
    }
    const byId = new Map(ingredients.map((item) => [item.id, item]));
    const lines = element("div", { className: "purchase-lines" });
    const removed = new Set();
    let index = 0;
    let itemsChanged = false;

    function addLine(item) {
        const key = index++;
        const options = active.map(({ id, name, unit }) => [id, `${name} · ${units[unit]}`]);
        if (item && !active.some(({ id }) => id === item.ingredient_id)) {
            options.push([item.ingredient_id, byId.get(item.ingredient_id)?.name ?? item.ingredient_id]);
        }
        const picker = select(`ingredient_${key}`, [["", "Выберите ингредиент"], ...options], item?.ingredient_id);
        const row = element("div", { className: "purchase-line" },
            element("label", {}, "Ингредиент", picker),
            field("Количество", `quantity_${key}`, item?.quantity ?? "1", { ...decimal, min: "0.001" }));
        if (purchase) {
            row.append(field("Цена за единицу", `price_${key}`, item?.unit_price ?? "", {
                ...decimal, min: "0.001", required: false,
            }));
        }
        picker.onchange = () => {
            if (purchase) row.querySelector(`[name="price_${key}"]`).value = byId.get(picker.value)?.unit_price ?? "";
        };
        row.oninput = () => { itemsChanged = true; };
        row.append(button("Убрать", () => {
            if (lines.childElementCount === 1) return;
            removed.add(key);
            itemsChanged = true;
            row.remove();
        }));
        lines.append(row);
    }

    if (purchase) purchase.items.forEach(addLine);
    else addLine();

    edit(purchase ? "Редактировать закупку" : "Новая закупка", [
        lines,
        button("Добавить позицию", () => {
            addLine();
            itemsChanged = true;
        }),
        ...(purchase ? [element("label", {}, "Комментарий", element("textarea", {
            name: "comment", maxLength: 1000, value: purchase.comment ?? "",
        }))] : []),
    ], async (data) => {
        const items = [];
        if (!purchase || itemsChanged) {
            for (let key = 0; key < index; key++) {
                if (removed.has(key)) continue;
                const ingredient_id = data[`ingredient_${key}`];
                if (items.some((item) => item.ingredient_id === ingredient_id)) {
                    throw new Error("Каждый ингредиент можно добавить только один раз.");
                }
                const item = { ingredient_id, quantity: data[`quantity_${key}`] };
                if (purchase) {
                    item.unit_price = data[`price_${key}`];
                    if (!item.unit_price) throw new Error("Укажите цену для каждой позиции.");
                }
                items.push(item);
            }
        }
        const saved = purchase
            ? await change(`${path}/${purchase.id}`, "PATCH", {
                comment: data.comment.trim() || null,
                ...(itemsChanged ? { items } : {}),
            })
            : await change(path, "POST", items);
        return async () => {
            await renderWorkspace();
            if (user && path === purchasesPath()) showPurchase(path, ingredients, saved);
        };
    }, purchase ? "Сохранить" : "Создать черновик");
}

signedOut();
