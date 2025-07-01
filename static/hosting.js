// step 1: get DOM
let nextDom = document.getElementById('next');
let prevDom = document.getElementById('prev');
let toggleDom = document.getElementById('stop'); // Renamed logically to reflect toggle role

let carouselDom = document.querySelector('.carousel');
let SliderDom = carouselDom.querySelector('.carousel .list');
let thumbnailBorderDom = document.querySelector('.carousel .thumbnail');
let thumbnailItemsDom = thumbnailBorderDom.querySelectorAll('.item');
let timeDom = document.querySelector('.carousel .time');

thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);

let timeRunning = 3000;
let timeAutoNext = 7000;

let isAutoRunning = true; // Auto-play is running by default
let runTimeOut;
let runNextAuto = setTimeout(() => {
    if (isAutoRunning) nextDom.click();
}, timeAutoNext);

nextDom.onclick = function () {
    showSlider('next');
};

prevDom.onclick = function () {
    showSlider('prev');
};

toggleDom.onclick = function () {
    isAutoRunning = !isAutoRunning;
    toggleDom.innerHTML = isAutoRunning
        ? `<span class="icon">😴</span> Stop`
        : `<span class="icon">🤪</span> Start`;

    clearTimeout(runNextAuto);
    if (isAutoRunning) {
        runNextAuto = setTimeout(() => {
            nextDom.click();
        }, timeAutoNext);
    }
};


function showSlider(type) {
    let SliderItemsDom = SliderDom.querySelectorAll('.carousel .list .item');
    let thumbnailItemsDom = document.querySelectorAll('.carousel .thumbnail .item');

    if (type === 'next') {
        SliderDom.appendChild(SliderItemsDom[0]);
        thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);
        carouselDom.classList.add('next');
    } else {
        SliderDom.prepend(SliderItemsDom[SliderItemsDom.length - 1]);
        thumbnailBorderDom.prepend(thumbnailItemsDom[thumbnailItemsDom.length - 1]);
        carouselDom.classList.add('prev');
    }

    clearTimeout(runTimeOut);
    runTimeOut = setTimeout(() => {
        carouselDom.classList.remove('next');
        carouselDom.classList.remove('prev');
    }, timeRunning);

    clearTimeout(runNextAuto);
    runNextAuto = setTimeout(() => {
        if (isAutoRunning) nextDom.click();
    }, timeAutoNext);
}

function openModal(src) {
    let modal = document.getElementById("myModal");
    let img = document.getElementById("img01");
    img.src = src;
    modal.style.display = "block";
}

function closeModal() {
    let modal = document.getElementById("myModal");
    modal.style.display = "none";
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        alert('Code copied to clipboard!');
    }, function (err) {
        console.error('Could not copy text: ', err);
    });
}
