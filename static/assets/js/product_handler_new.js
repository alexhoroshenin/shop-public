'use strict'


function deleteProductFromCart(productId){
    
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    delete_product_from_cart_by_product_id: productId
                })
            })

            if (response.ok) {
                let cartResults = await response.json();
                resolve(cartResults);
            } else {
                reject(new Error('Произошла ошибка при удалении товара из корзины'));
            }
        }
    )

    sender
    .then((serverResponse) => {

        if (serverResponse['error']){
            showErrorMessageInProductDiv(serverResponse['error']);
        } else {
            hideNodeWithCount(productId);
            showNodeWithCartButton(productId);
            updateCartResultsByServerResponse(serverResponse);
        }
    })
    .catch((error) => showErrorMessageInProductDiv(error));
}


function sendNewProductCountToServer(productId, count, inputField){
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    new_product_count: {
                        product_id: productId,
                        product_count: count
                    }
                })
            })

            if (response.ok) {
                let cartResults = await response.json();
                resolve(cartResults);
            } else {
                reject(new Error('Произошла ошибка при изменении количество товара.'));
            }
        }
    )

    sender.then((serverResponse) => {
        if (serverResponse['error']){
            showErrorMessageInProductDiv(serverResponse['error']);
        } else if (serverResponse['value_error']){
            showErrorCountMessage(serverResponse['value_error'], inputField);
            updateCartResultsByServerResponse(serverResponse);
            inputField.value = +serverResponse['available_count'];
        } else {
            deleteErrorCountMessage();
            updateCartResultsByServerResponse(serverResponse);
            inputField.value = count;
        }
    })
    .catch((error) => showErrorMessageInProductDiv(error));
}

function hideNodeWithCount(productId){
    let targets = document.querySelectorAll(`[data-product-id="${productId}"] .product-in-cart`);

    targets.forEach( target => {
        target.querySelector('input').value = 1;
        target.classList.add('d-none');
    });
    
}

function showNodeWithCartButton(productId){
    let targets = document.querySelectorAll(`[data-product-id="${productId}"] .product-not-in-cart`);
    targets.forEach(target => {
        target.classList.remove('d-md-none', 'd-lg-none', 'd-sm-none', 'd-none');
    });
    
}

function updateCartResultsByServerResponse(serverResponse){
    updateCartCountIcon(serverResponse.total_count);
}

function isCorrectCountInput(currentCount){

    if (currentCount && Number.isInteger(+currentCount) && +currentCount >= 0){
            return true;
    } else {
        return false;
    }
}

function changeCount(inputField, productId, operation, newValue=undefined){
    let currentCount = +inputField.value;

    if (operation == '+1_byProductId') {
        sendNewProductCountToServer(productId, currentCount + 1, inputField);
    }

    if (operation == '-1_byProductId' && currentCount > 1) {
        inputField.value = currentCount - 1;
        sendNewProductCountToServer(productId, currentCount - 1, inputField);
    }

    if (operation == '-1_byProductId' && currentCount === 1) {
        deleteProductFromCart(productId);
    }

    if (operation == 'setNewValue_ByProductId' && newValue) {
        sendNewProductCountToServer(productId, newValue, inputField);
    }
}

function setRedBorderToField(countProductField){
    countProductField.classList.add('border-danger');

}

function unSetRedBorderToField(inputField){
    inputField.classList.remove('border-danger');
}

function showErrorMessageInProductDiv(error){
    let productInCartBlock = document.querySelector(".product-in-cart");
    let errorBlock = document.createElement('div');
    errorBlock.className = "alert alert-danger my-2 mx-1";
    errorBlock.role = "alert";
    let closeButton = `
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>`;
    errorBlock.innerHTML = error + closeButton;
    productInCartBlock.after(errorBlock);


    let Timer = setInterval(() => {errorBlock.remove()}, 6000);
}

function showErrorCountMessage(message, inputField){

    let balanceLimitRow = inputField.closest('.product-in-cart').querySelector('.balance-limit');
    setRedBorderToField(inputField);
    balanceLimitRow.innerText = message;
}

function deleteErrorCountMessage(){
    let divRowWithInputField = document.querySelector('.balance-limit');
    divRowWithInputField.innerText = '';
}

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
    let purchaseBtnsBlocks = document.querySelectorAll(`[data-product-id="${itemId}"] .product-not-in-cart`);

    purchaseBtnsBlocks.forEach((element) => {
        // Скрыть блоки с кнопками В КОРЗИНУ
        element.classList.add('d-none');
        // let successBtn = element.cloneNode();
        // successBtn.className = `btn btn-outline-success btn-product-box 
        // btn--box btn--small btn--uppercase btn--weight disabled btn-disabled`;
        // successBtn.innerText = 'В КОРЗИНЕ';
        // element.replaceWith(successBtn);

        // Открыть блоки с кнопками изменения количества
        let parent = element.parentNode,
            buttonsBlock = parent.querySelector('.product-in-cart');

        buttonsBlock.classList.remove('d-none');

    });

    

}

function replaceBloksOnProductView(){
    let productNotInCartDiv = document.querySelector('.product-not-in-cart'),
        productInCartDiv = document.querySelector('.product-in-cart');
   
    productNotInCartDiv.classList.add("d-md-none", "d-lg-none", "d-none");

    productInCartDiv.classList.remove("d-md-none", "d-lg-none", "d-none");

}


function updateCartCountIcon(newCount){

    let CartCountIcons = document.querySelectorAll('.wishlist-item-count');
    CartCountIcons.forEach((element) => {
        element.innerText = newCount;
    });
}


function sendActionToServer(message){
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify(message)
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


function addProductInCartFromProductBox(productId, productBox){

    let sender = sendActionToServer({append_product_id: productId});

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


function addProductInCartFromProductView(productId){
    let sender = sendActionToServer({append_product_id: productId});

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


function getProductId(event){
    // ID продукта будет получен из дата-атрибута .product__box - для превью товара
    // или .product-details - для страницы товара

    let productDetailsDiv = document.querySelector('.product-details');

    if (productDetailsDiv){
        return productDetailsDiv.dataset['productId'];
    } else {
        return event.target.closest('.product__box').dataset['productId'];
    }

}


function getNeighbourCountField(elem){
    return elem.parentNode.querySelector('input');
}


function main_product_handler(){

    // Обработчик кнопки В КОРЗИНУ в превью товара
    let AddIntoCartPreveiwBtn = document.querySelectorAll('.btn-add-into-cart');
    AddIntoCartPreveiwBtn.forEach((element) => {
        element.addEventListener('click', (event) => {
            event.preventDefault();
            let productId = event.target.dataset.productId;
            let productBox = event.target.parentNode.parentNode;
            addProductInCartFromProductBox(productId, productBox);
        });
    });

    // Обработчик кнопки В КОРЗИНУ на странице товара
    let AddIntoCartProductPageBtn = document.querySelector('.product-view-btn');
    if (AddIntoCartProductPageBtn){
        AddIntoCartProductPageBtn.addEventListener('click', (event) => {
            event.preventDefault();
            let productId = event.target.dataset.productId;
            addProductInCartFromProductView(productId);
        });

    }

    // Обработчик события - изменение количество товара в поле
    let countProductFields = document.querySelectorAll('[data-product-count-field]');
    countProductFields.forEach(elem => {
        elem.addEventListener('change', (event) => {
            let currentCount = event.target.value;
    
            if (isCorrectCountInput(currentCount)){

                let productId = getProductId(event);

                if (+currentCount === 0){
                    deleteProductFromCart(productId);
                } else {
                    unSetRedBorderToField(elem);
                    changeCount(elem, productId, 'setNewValue_ByProductId', currentCount);
                }

            } else {
                // Пометить поле красным
                setRedBorderToField(elem);
            }
        });
    })


    // Обработчик кнопок изменения количества
    let changeCountButtons = document.querySelectorAll('.change-count-btn');
    changeCountButtons.forEach((elem) => {
        elem.addEventListener('click', (event) => {

            let countField = getNeighbourCountField(event.target),
                currentCount = countField.value;

            if (isCorrectCountInput(currentCount)){
                // Убрать из поля красный цвет
                unSetRedBorderToField(countField);

                let productId = getProductId(event);

                if (event.target.innerText === '+'){
                    changeCount(countField, productId, '+1_byProductId');
                } else {
                    changeCount(countField, productId, '-1_byProductId');
                }
            } else {
                // Пометить поле красным
                setRedBorderToField(countField);
            }
        });
    });

}


document.addEventListener('DOMContentLoaded', () => main_product_handler());


    

