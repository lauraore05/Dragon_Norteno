// Configuración de API
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? `http://${window.location.hostname}:5000` 
    : "https://dragon-nortenio.onrender.com"; // URL detectada en tu Render Backend

console.log("Sistema de Pedidos: Conectando a API en:", API_URL);


// State
let currentUser = null;
let currentSucursal = null;
let categories = [];
let products = [];
let mesas = [];
let cart = [];
let activeCategory = null;
let selectedMesa = null;

// DOM Elements
const body = document.body;
const loader = document.getElementById('loader');
const authContainer = document.getElementById('auth-container');
const mainApp = document.getElementById('main-app');
const viewSucursal = document.getElementById('view-sucursal');
const viewLogin = document.getElementById('view-login');
const sucursalesList = document.getElementById('sucursales-list');
const loginForm = document.getElementById('login-form');
const btnBackSucursal = document.getElementById('btn-back-sucursal');
const userDisplay = document.getElementById('user-display');
const btnLogout = document.getElementById('btn-logout');

// Main Navigation Elements
const views = document.querySelectorAll('.view');
const navItems = document.querySelectorAll('.nav-item');
const categoriesContainer = document.getElementById('categories-container');
const productsContainer = document.getElementById('products-container');
const selectMesa = document.getElementById('select-mesa');
const cartDrawer = document.getElementById('cart-drawer');
const openCartBtn = document.getElementById('open-cart');
const closeCartBtn = document.getElementById('close-cart');
const cartItemsContainer = document.getElementById('cart-items');
const cartCount = document.getElementById('cart-count');
const cartMesaDisplay = document.getElementById('cart-mesa-display');
const btnEnviarPedido = document.getElementById('btn-enviar-pedido');
const ordersContainer = document.getElementById('orders-container');
const salesContainer = document.getElementById('sales-container');

function setupCategoriesScroll() {
    const strip = document.getElementById('categories-container');
    const arrow = document.getElementById('scroll-right');
    
    if (arrow) {
        arrow.onclick = () => {
            strip.scrollBy({ left: 200, behavior: 'smooth' });
        };
        
        // Ocultar si al inicio no hay scroll
        strip.onscroll = () => {
            if (strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 10) {
                arrow.style.opacity = '0';
                arrow.style.pointerEvents = 'none';
            } else {
                arrow.style.opacity = '1';
                arrow.style.pointerEvents = 'auto';
            }
        };
    }
}

// Init
window.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupAuthListeners();
    setupNavigation();
    setupCartActions();
    setupCategoriesScroll();
});

// --- AUTH LOGIC ---

function checkSession() {
    const savedUser = localStorage.getItem('dragon_user');
    const savedSucursal = localStorage.getItem('dragon_sucursal');
    
    if (savedUser && savedSucursal) {
        currentUser = JSON.parse(savedUser);
        currentSucursal = JSON.parse(savedSucursal);
        showMainApp();
    } else {
        fetchSucursales();
    }
}

async function fetchSucursales(retries = 2) {
    showLoader(true);
    console.log("Intentando cargar sucursales desde:", `${API_URL}/sucursales`);
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout
        
        const res = await fetch(`${API_URL}/sucursales`, {
            signal: controller.signal,
            headers: { 'Accept': 'application/json' }
        });
        clearTimeout(timeoutId);
        
        if (!res.ok) throw new Error(`Status: ${res.status}`);
        const data = await res.json();
        console.log("Sucursales cargadas:", data);
        renderSucursales(data);
    } catch (err) {
        console.error("Error cargando sucursales:", err);
        if (retries > 0) {
            console.log(`Reintentando... (${retries} intentos restantes)`);
            showToast("Conectando con el servidor...", "error");
            setTimeout(() => fetchSucursales(retries - 1), 3000);
            return;
        }
        showToast("Error conectando con el servidor. Verifica tu conexión.", "error");
    } finally {
        showLoader(false);
    }
}

function renderSucursales(list) {
    sucursalesList.innerHTML = '';
    list.forEach(s => {
        const div = document.createElement('div');
        div.className = 'sucursal-item';
        div.innerHTML = `<strong>${s.nombre}</strong><br><small>${s.direccion}</small>`;
        div.onclick = () => {
            currentSucursal = s;
            document.getElementById('login-branch-name').textContent = s.nombre;
            viewSucursal.classList.remove('active');
            viewLogin.classList.add('active');
        };
        sucursalesList.appendChild(div);
    });
}

function setupAuthListeners() {
    btnBackSucursal.onclick = () => {
        viewLogin.classList.remove('active');
        viewSucursal.classList.add('active');
    };

    loginForm.onsubmit = async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        showLoader(true);
        try {
            const res = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, id_sucursal: currentSucursal.id_sucursal })
            });

            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                localStorage.setItem('dragon_user', JSON.stringify(currentUser));
                localStorage.setItem('dragon_sucursal', JSON.stringify(currentSucursal));
                showMainApp();
                showToast(`Bienvenido, ${currentUser.username}`);
            } else {
                showToast(data.error, "error");
            }
        } catch (err) {
            showToast("Error en el login", "error");
        } finally {
            showLoader(false);
        }
    };

    btnLogout.onclick = () => {
        localStorage.clear();
        location.reload();
    };

    // Mobile logout
    const btnLogoutMobile = document.getElementById('btn-logout-mobile');
    if (btnLogoutMobile) {
        btnLogoutMobile.onclick = () => {
            localStorage.clear();
            location.reload();
        };
    }
}

function showMainApp() {
    authContainer.classList.add('hidden');
    mainApp.classList.remove('hidden');
    userDisplay.textContent = `${currentUser.username} (${currentUser.rol})`;
    
    // Mobile topbar user display
    const mobileUserDisplay = document.getElementById('user-display-mobile');
    if (mobileUserDisplay) {
        mobileUserDisplay.textContent = `${currentUser.username} (${currentUser.rol})`;
    }
    
    // Role based restrictions
    if (currentUser.rol === 'mesero') {
        document.getElementById('nav-sales').classList.add('hidden');
    } else if (currentUser.rol === 'cocina') {
        document.getElementById('nav-menu').classList.add('hidden');
        document.getElementById('nav-sales').classList.add('hidden');
        // Auto go to orders
        document.getElementById('nav-orders').click();
    }
    
    fetchInitialData();
}

// --- APP CORE LOGIC ---

async function fetchInitialData() {
    showLoader(true);
    try {
        const [catRes, prodRes, mesaRes] = await Promise.all([
            fetch(`${API_URL}/categorias`),
            fetch(`${API_URL}/productos`),
            fetch(`${API_URL}/mesas/${currentSucursal.id_sucursal}`)
        ]);

        categories = await catRes.json();
        products = await prodRes.json();
        mesas = await mesaRes.json();

        renderCategories();
        renderMesas();
        renderProducts(products);
    } catch (err) {
        showToast("Error de conexión", "error");
    } finally {
        showLoader(false);
    }
}

function setupNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewId = item.getAttribute('data-view');
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(`view-${viewId}`).classList.add('active');

            if (viewId === 'orders') fetchActiveOrders();
            if (viewId === 'sales') fetchSalesReport();
        });
    });
}

function setupCartActions() {
    openCartBtn.addEventListener('click', () => cartDrawer.classList.add('open'));
    closeCartBtn.addEventListener('click', () => cartDrawer.classList.remove('open'));
    
    selectMesa.addEventListener('change', (e) => {
        selectedMesa = e.target.value;
        const mesa = mesas.find(m => m.id_mesa == selectedMesa);
        cartMesaDisplay.textContent = mesa ? `Mesa ${mesa.numero}` : "Ninguna";
    });

    btnEnviarPedido.addEventListener('click', enviarPedido);
}

// Rendering
function renderCategories() {
    categoriesContainer.innerHTML = '';
    const todasBtn = createCategoryTag({ id_categoria: null, nombre: "Todas" });
    todasBtn.classList.add('active');
    categoriesContainer.appendChild(todasBtn);

    categories.forEach(cat => {
        categoriesContainer.appendChild(createCategoryTag(cat));
    });
}

function createCategoryTag(cat) {
    const div = document.createElement('div');
    div.className = 'category-tag';
    div.textContent = cat.nombre;
    div.onclick = () => {
        document.querySelectorAll('.category-tag').forEach(t => t.classList.remove('active'));
        div.classList.add('active');
        activeCategory = cat.id_categoria;
        const filtered = activeCategory ? products.filter(p => p.id_categoria === activeCategory) : products;
        renderProducts(filtered);
    };
    return div;
}

function renderMesas() {
    selectMesa.innerHTML = '<option value="">Seleccionar...</option>';
    mesas.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id_mesa;
        opt.textContent = `Mesa ${m.numero} ${m.estado === 'ocupada' ? '(OCUPADA)' : ''}`;
        if(m.estado === 'ocupada') opt.classList.add('mesa-ocupada');
        selectMesa.appendChild(opt);
    });
}

function renderProducts(items) {
    productsContainer.innerHTML = '';
    items.forEach(p => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `<h3>${p.nombre}</h3><button class="product-btn" onclick="addToCart(${p.id_producto})">Agregar <i class="fas fa-plus"></i></button>`;
        productsContainer.appendChild(card);
    });
}

window.addToCart = (id) => {
    const product = products.find(p => p.id_producto === id);
    const existing = cart.find(item => item.id_producto === id);
    existing ? existing.cantidad++ : cart.push({ ...product, cantidad: 1 });
    updateCartUI();
    showToast(`${product.nombre} agregado`);
};

function updateCartUI() {
    cartCount.textContent = cart.reduce((acc, obj) => acc + obj.cantidad, 0);
    cartItemsContainer.innerHTML = '';
    cart.forEach(item => {
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `<div class="cart-item-info"><h4>${item.nombre}</h4><p>x${item.cantidad}</p></div><button class="btn-remove" onclick="removeFromCart(${item.id_producto})"><i class="fas fa-trash"></i></button>`;
        cartItemsContainer.appendChild(div);
    });
}

window.removeFromCart = (id) => {
    cart = cart.filter(p => p.id_producto !== id);
    updateCartUI();
};

async function enviarPedido() {
    if (!selectedMesa) return showToast("Selecciona una mesa", "error");
    if (cart.length === 0) return showToast("El carrito está vacío", "error");

    showLoader(true);
    try {
        const res = await fetch(`${API_URL}/pedido`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_mesa: selectedMesa,
                id_sucursal: currentSucursal.id_sucursal,
                productos: cart.map(item => ({ id_producto: item.id_producto, cantidad: item.cantidad }))
            })
        });
        if (res.ok) {
            showToast("Pedido enviado");
            cart = []; updateCartUI(); cartDrawer.classList.remove('open');
            fetchInitialData();
        }
    } catch (err) { showToast("Error enviando pedido", "error"); }
    finally { showLoader(false); }
}

async function fetchActiveOrders() {
    const res = await fetch(`${API_URL}/pedidos/${currentSucursal.id_sucursal}`);
    const data = await res.json();
    renderOrders(data);
}

function renderOrders(orders) {
    ordersContainer.innerHTML = '';
    if (orders.length === 0) { ordersContainer.innerHTML = '<p class="text-muted">Sin pedidos.</p>'; return; }
    orders.forEach(o => {
        const card = document.createElement('div');
        card.className = 'order-card';
        const itemsList = o.items.map(i => `<li>${i.cantidad}x ${i.producto}</li>`).join('');
        const mesaNum = mesas.find(m => m.id_mesa == o.id_mesa)?.numero || o.id_mesa;
        
        card.innerHTML = `
            <div class="order-card-header"><strong>Mesa ${mesaNum}</strong><span class="order-status status-${o.estado}">${o.estado}</span></div>
            <ul class="order-items">${itemsList}</ul>
            <div class="order-actions">
                ${(currentUser.rol === 'admin' || currentUser.rol === 'cocina') && o.estado === 'pendiente' ? `<button onclick="updateStatus(${o.id_pedido}, 'servido')" class="btn-action">Servido</button>` : ''}
                ${(currentUser.rol === 'admin' || currentUser.rol === 'mesero') && o.estado === 'servido' ? `<button onclick="updateStatus(${o.id_pedido}, 'pagado')" class="btn-action">Pagado</button>` : ''}
                ${currentUser.rol === 'admin' ? `<button onclick="eliminarPedido(${o.id_pedido})" class="btn-delete"><i class="fas fa-trash"></i></button>` : ''}
            </div>
        `;
        ordersContainer.appendChild(card);
    });
}

window.updateStatus = async (id, estado) => {
    await fetch(`${API_URL}/pedido/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado })
    });
    fetchActiveOrders(); fetchInitialData();
};

window.eliminarPedido = async (id) => {
    if(!confirm("¿Eliminar pedido?")) return;
    await fetch(`${API_URL}/pedido/${id}`, { method: 'DELETE' });
    fetchActiveOrders(); fetchInitialData();
};

async function fetchSalesReport() {
    const res = await fetch(`${API_URL}/reporte/ventas-hoy/${currentSucursal.id_sucursal}`);
    const data = await res.json();
    salesContainer.innerHTML = `<table class="sales-table"><thead><tr><th>Producto</th><th>Vendidos</th></tr></thead><tbody>${data.map(r => `<tr><td>${r.nombre}</td><td><strong>${r.total_vendido}</strong></td></tr>`).join('')}</tbody></table>`;
}

function showLoader(show) { loader.classList.toggle('hidden', !show); }
function showToast(msg, type = "success") {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    if (type === 'error') toast.style.backgroundColor = "#ff4444";
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
