'use strict'

function changeDeliveryMethod(newMethodId){
    sendNewDeliveryMethodToServer(newMethodId);
}

function sendNewDeliveryMethodToServer(id){
    
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    delivery_method_id: id
                })
            })

            if (response.ok) {
                let cartResults = await response.json();
                resolve(cartResults);
            } else {
                reject(new Error('Произошла ошибка при обновлении метода доставки'));
            }

        }
    )

    sender
    .then((serverResponse) => updateCartResultsByServerResponse(serverResponse))
    .catch((error) => console.log(error));
}


function changePaymentMethod(newMethodId){
    sendNewPaymentMethodToServer(newMethodId);
}

function sendNewPaymentMethodToServer(id){
    
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    payment_method_id: id
                })
            })

            if (response.ok) {
                let cartResults = await response.json();
                resolve(cartResults);
            } else {
                reject(new Error('Произошла ошибка при обновлении метода доставки'));
            }

        }
    )

    sender
    .then((serverResponse) => updateCartResultsByServerResponse(serverResponse))
    .catch((error) => console.log(error));
}

function deleteItemFromCart(itemId){
    
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    delete_cart_item_id: itemId
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
            showErrorMessageInProductDiv(serverResponse['error'], itemId);
        } else {
            deletePageNodeWithCartItem(itemId);
            updateCartResultsByServerResponse(serverResponse);
        }
    })
    .catch((error) => showErrorMessageInProductDiv(error, itemId));
}


function sendNewItemCountToServer(itemId, count, inputField){
    let sender = new Promise(
        async function(resolve, reject){
            let response = await fetch('/cart/update-ajax', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify({
                    new_cart_item_count: {
                        item_id: itemId,
                        item_count: count
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

    sender
    .then((serverResponse) => {
        if (serverResponse['error']){
            showErrorMessageInProductDiv(serverResponse['error'], itemId);
        } else if (serverResponse['value_error']){
            showErrorCountMessage(serverResponse['value_error'], itemId);
            updateCartResultsByServerResponse(serverResponse);
            inputField.value = +serverResponse['available_count'];
        } else {
            deleteErrorCountMessage(itemId);
            updateCartResultsByServerResponse(serverResponse);
            inputField.value = count;
        }
    })
    .catch((error) => showErrorMessageInProductDiv(error, itemId));
}

function deletePageNodeWithCartItem(cartItemId){
    let blockForDelete = getProductBlockByItemId(cartItemId);
    blockForDelete.remove();
}

function updateCartCountIcon(newCount){

    let CartCountIcons = document.querySelectorAll('.wishlist-item-count');
    CartCountIcons.forEach((element) => {
        element.innerText = newCount;
    });
}

function updateCartResultsByServerResponse(serverResponse){
    updateDeliveryCost(serverResponse.delivery_cost);
    updateDiscountSum(serverResponse.discount_sum);
    updateProductsCost(serverResponse.products_cost);
    updateTotal(serverResponse.total);
    updateCartCountIcon(serverResponse.total_count);
}

function updateDeliveryCost(newValue){
    let deliveryCost = document.querySelector('#delivery-cost');
    deliveryCost.innerText = newValue + ' руб';
}

function updateDiscountSum(newValue){
    let discountSum = document.querySelector('#discount-sum');
    discountSum.innerText = newValue + ' руб';
}

function updateProductsCost(newValue){
    let productsCost = document.querySelector('#products-cost');
    productsCost.innerText = newValue + ' руб';
}

function updateTotal(newValue){
    let total = document.querySelector('#total');
    total.innerText = newValue + ' руб';
}

function isCorrectCountInput(cartItemId, productRow){
    let currentCount = productRow.querySelector('input').value;

    if (currentCount && Number.isInteger(+currentCount) && +currentCount >= 0){
            return true;
    } else {
        return false;
    }
}

function changeCount(cartItemId, operation, newValue=undefined){
    let productBlock = getProductBlockByItemId(cartItemId);
    let inputField = productBlock.querySelector('input');
    let currentCount = +inputField.value;

    if (operation == '+1') {
        sendNewItemCountToServer(cartItemId, currentCount + 1, inputField);
    }

    if (operation == '-1' && currentCount > 1) {
        inputField.value = currentCount - 1;
        sendNewItemCountToServer(cartItemId, currentCount - 1, inputField);
    }

    if (operation == '-1' && currentCount === 1) {
        inputField.value = 0;
        deleteItemFromCart(cartItemId);
    }

    if (operation == 'setNewValue' && newValue) {
        sendNewItemCountToServer(cartItemId, newValue, inputField);
    }
}

function setRedBorderToField(cartItemId){
    let productBlock = getProductBlockByItemId(cartItemId);
    let inputField = productBlock.querySelector('input');
    inputField.classList.add('border-danger');

}

function unSetRedBorderToField(cartItemId){
    let productBlock = getProductBlockByItemId(cartItemId);
    let inputField = productBlock.querySelector('input');
    inputField.classList.remove('border-danger');
}

function showErrorMessageInProductDiv(error, itemId){
    let productBlock = getProductBlockByItemId(itemId);
    let errorBlock = document.createElement('div');
    errorBlock.className = "alert alert-danger my-2 mx-1";
    errorBlock.role = "alert";
    let closeButton = `
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>`;
    errorBlock.innerHTML = error + closeButton;
    productBlock.after(errorBlock);


    let Timer = setInterval(() => {errorBlock.remove()}, 6000);
}

function showErrorCountMessage(message, itemId){
    let productBlock = getProductBlockByItemId(itemId);
    let divRowWithInputField = productBlock.querySelector('.balance-limit');
    setRedBorderToField(itemId);
    divRowWithInputField.innerText = message;
}

function deleteErrorCountMessage(itemId){
    let productBlock = getProductBlockByItemId(itemId);
    let divRowWithInputField = productBlock.querySelector('.balance-limit');
    divRowWithInputField.innerText = '';
}

function getProductBlockByItemId(cartItemId){
    let productBlock = document.querySelector('[data-cart-item-id="' + cartItemId + '"]');
    return productBlock;
}


function main_cart_handler(){
    let deliveryMethodRadios = document.querySelectorAll('[data-delivery-method-radio]');
    deliveryMethodRadios.forEach((elem) => {
        elem.addEventListener('change', (event) => {
            changeDeliveryMethod(event.target.value);
        });
    });

    let paymentMethodRadios = document.querySelectorAll('[data-payment-method-radio]');
    paymentMethodRadios.forEach((elem) => {
        elem.addEventListener('change', (event) => {
            changePaymentMethod(event.target.value);
        });
    });

    let deleteProductIcons = document.querySelectorAll('[data-cart-item-remove]');
    deleteProductIcons.forEach((elem) => {
        elem.addEventListener('click', (event) => {
            event.preventDefault();
            let productDiv = event.target.closest(".product-row");
            deleteItemFromCart(productDiv.dataset['cartItemId']);
        });
    });

    let countProductFields = document.querySelectorAll('[data-product-count-field]');
    countProductFields.forEach((elem) => {
        elem.addEventListener('change', (event) => {
            let productRow = event.target.closest(".product-row");
            let cartItemId = productRow.dataset['cartItemId'];
            if (isCorrectCountInput(cartItemId, productRow)){
                unSetRedBorderToField(cartItemId);
                if (+event.target.value === 0){
                    deleteItemFromCart(cartItemId);
                } else {
                    changeCount(cartItemId, 'setNewValue', event.target.value);
                }
            } else {
                // Пометить поле красным
                setRedBorderToField(cartItemId);
            }
        });
    });


    let changeCountButtons = document.querySelectorAll('.change-count-btn');
    changeCountButtons.forEach((elem) => {
        elem.addEventListener('click', (event) => {
            let productRow = event.target.closest(".product-row");
            let cartItemId = productRow.dataset['cartItemId'];
            if (isCorrectCountInput(cartItemId, productRow)){
                // Убрать из поля красный цвет
                unSetRedBorderToField(cartItemId);

                if (event.target.innerText === '+'){
                    changeCount(cartItemId, '+1');
                } else {
                    changeCount(cartItemId, '-1');
                }
            } else {
                // Пометить поле красным
                setRedBorderToField(cartItemId);
            }
        });
    });

}

document.addEventListener('DOMContentLoaded', () => main_cart_handler());
