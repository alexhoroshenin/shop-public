function showErrorMessageInProductBox(error, productBox){

    let errorMessage = document.createElement('div');
    errorMessage.className = 'alert alert-danger';
    errorMessage.role = 'alert';
    errorMessage.innerText = error;
    errorMessage.id = 'errorMessage';

    let link = productBox.querySelector('.product__link');
    link.after(errorMessage);

    let Timer = setInterval(() => {errorMessage.remove()}, 7000);
}

function showErrorMessageInProductView(error){
    existsErrorMessage = document.querySelector('#errorMessage');
    if (existsErrorMessage){
        existsErrorMessage.classList.remove('hidden');
    } else {
        var btn = document.querySelector('#add_item_to_cart_btn_success');
        var btnParent = btn.parentNode;

        var errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger';
        errorMessage.role = 'alert';
        errorMessage.innerText = error;
        errorMessage.id = 'errorMessage';

        btnParent.insertBefore(errorMessage, btn)
    }
}


function replaceBtnsInProductBox(itemId){
    let purchaseBtns = document.querySelectorAll(`[data-product-id="${itemId}"] .btn:not(.disabled)`);

    purchaseBtns.forEach((element) => {
        let successBtn = element.cloneNode();
        successBtn.className = `btn btn-outline-success btn-product-box 
        btn--box btn--small btn--uppercase btn--weight disabled btn-disabled`;
        successBtn.innerText = 'В КОРЗИНЕ';
        element.replaceWith(successBtn);
    });
    

}

function replaceBloksOnProductView(){
    let productNotInCartDiv = document.querySelector('.product-not-in-cart'),
        productInCartDiv = document.querySelector('.product-in-cart');
   
    productNotInCartDiv.classList.remove('d-flex');
    productNotInCartDiv.classList.add("d-md-none", "d-lg-none", "d-none");

    productInCartDiv.classList.add('d-flex');
    productInCartDiv.classList.remove("d-md-none", "d-lg-none", "d-none");

}


function updateCartCountIcon(newCount){

    let CartCountIcons = document.querySelectorAll('.wishlist-item-count');
    CartCountIcons.forEach((element) => {
        element.innerText = newCount;
    });
}

function addProductInCartFromProductBox(productId, productBox){

    sender = sendActionToServer(productId);

    sender
    .then((serverResponse) => {

        if (serverResponse['error']){
            reject(new Error(serverResponse['error']));
        } else {
            replaceBtnsInProductBox(productId);
            updateCartCountIcon(serverResponse['total_count']);
        }
    })
    .catch((error) => showErrorMessageInProductBox(error, productBox));
}

function addProductInCartOnProductView(productId){
    sender = sendActionToServer(productId);

    sender
    .then((serverResponse) => {

        if (serverResponse['error']){
            reject(new Error(serverResponse['error']));
        } else {
            replaceBloksOnProductView();
            updateCartCountIcon(serverResponse['total_count']);
        }
    })
    .catch((error) => showErrorMessageInProductView(error));
}

function sendActionToServer(productId){
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    append_product_id: productId
                })
            })

            if (response.ok) {
                let cartResults = await response.json();
                resolve(cartResults);
            } else {
                reject(new Error('Произошла ошибка при добавлении товара в корзину'));
            }

        }
    );

    return sender;
}


function main_product_btn_handler(){
    // Обработчик кнопrи В КОРЗИНУ в превью товара
    let btns = document.querySelectorAll('btn, .btn-product-box:not(.disabled)');
    btns.forEach((element) => {
        element.addEventListener('click', (event) => {
            event.preventDefault();
            let productId = event.target.dataset.productId;
            let productBox = event.target.parentNode.parentNode;
            addProductInCartFromProductBox(productId, productBox);
        });
    });

    // Обработчик кнопки В КОРЗИНУ на странице товара
    let productViewBtn = document.querySelector('.product-view-btn');
    if (productViewBtn){
        productViewBtn.addEventListener('click', (event) => {
            event.preventDefault();
            let productId = event.target.dataset.productId;
            addProductInCartOnProductView(productId);
        });

    }
}

document.addEventListener('DOMContentLoaded', () => main_product_btn_handler());
