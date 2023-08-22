// as above, but passing the id of the div to replace as an argument
function fetchCarouselById(id, sha) {
    console.log(id, sha)
    fetch('../{sha}/sections/{id}'.replace('{sha}', sha).replace('{id}', id))
    .then(response => response.text())
    .then(data => {
        let sel_id = `#${id}`
        let [next, previous] = get_next_prev_shas(document.querySelector('#carousels').dataset.shas.split(','), sha);
        document.querySelector(sel_id).innerHTML = createCarouselById(id, data, sha, next, previous);
    });
}

// as above, but with a given id as parameter
function createCarouselById(id, data, current, next, previous) {
    console.log(id, data, current, next, previous)
    return `
    <div id="carousel">
        <div id="#${id}">
            ${data}
        </div>
        <div id="next">
            <button onclick="fetchCarouselById('${id}', '${next}')">Next</button>
        </div>
        <div id="previous">
            <button onclick="fetchCarouselById('${id}', '${previous}')">Previous</button>
        </div>
    </div>
    `
}

// on load, replace dummy divs with a carousel
document.addEventListener('DOMContentLoaded', function() {
    // get list of shas from carousels div data-shas attribute
    let shas = document.querySelector('#carousels').dataset.shas.split(',');
    let current_sha = document.querySelector('#carousels').dataset.rootsha;
    console.log(document.querySelector('#carousels').dataset)
    console.log(shas, current_sha)
    // get next and previous shas
    let [next_sha, previous_sha] = get_next_prev_shas(shas, current_sha);
    // for each div with matching class, replace with a carousel
    document.querySelectorAll('.carousel').forEach(function(div) {
        // replace div with carousel
        fetchCarouselById(div.id, current_sha);
        // div.innerHTML = createCarouselById(div.id, fetchCarouselById(div.id, current_sha), current_sha, next_sha, previous_sha);
    });
});

// take a list of slugs defined in the html, and a current slug, return next and previous slugs if they exist
function get_next_prev_shas(slugs, current) {
    console.log(slugs, current);
    let index = slugs.indexOf(current);
    console.log(index);
    if (index === 0) {
        return [slugs[index + 1], null];
    }
    if (index === slugs.length - 1) {
        return [null, slugs[index - 1]];
    }
    return [slugs[index + 1], slugs[index - 1]];
}
