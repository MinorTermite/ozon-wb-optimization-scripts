const demoProducts = [
    {
        id: 296459803,
        title: "Браслет с гравировкой Подарок сыну 2026",
        price: 1428,
        img: "https://images.unsplash.com/photo-1611085583191-a3b1a6200fdc?auto=format&fit=crop&q=80"
    },
    {
        id: 296459804,
        title: "Армейский жетон подвеска с гравировкой",
        price: 990,
        img: "https://images.unsplash.com/photo-1598565793102-86cdc7104b21?auto=format&fit=crop&q=80"
    },
    {
        id: 296459805,
        title: "Брелок на ключи авто со знаком зодиака",
        price: 550,
        img: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80"
    }
];

function renderProducts() {
    const grid = document.getElementById('productGrid');
    if (!grid) return;

    grid.innerHTML = '';
    
    demoProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-img">
                <img src="${product.img}" alt="${product.title}">
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-price">${product.price} ₽</div>
                <div style="margin-top: 15px;">
                    <button class="btn btn-primary" style="padding: 8px 20px; font-size: 12px; width: 100%;">Заказать напрямую</button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('scroll', () => {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.style.padding = '10px 0';
            header.style.background = 'rgba(13, 13, 13, 0.98)';
        } else {
            header.style.padding = '0';
            header.style.background = 'rgba(13, 13, 13, 0.95)';
        }
    });

    renderProducts();
});
