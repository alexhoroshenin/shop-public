document.addEventListener('DOMContentLoaded', () => mainSerchHandler());

function mainSerchHandler(){
    // По соответствию, по названию, сначала дешевле, сначала дороже

    let selectOrdering = document.querySelector('#sot-box');

    selectOrdering.addEventListener('change', (event) => {
        let url = new URL(document.location.href),
            selectedIndex = event.target.options.selectedIndex,
            selectedParam = selectOrdering.options[selectedIndex].value;

        newParamPart = addOrderingParamToUrl(url, selectedParam);
        url.search = `?${newParamPart}`;
        document.location.href = url.href;
    });
}


function addOrderingParamToUrl(url, selectedParam){
    let params = new URLSearchParams(url.search.slice(1));
    params.set('ordering', selectedParam);
    return params.toString();
}