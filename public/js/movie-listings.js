let options = {
    root: document.querySelector(".item-container"),
    rootMargin: "0px",
    threshold: 1, //visibility threshold
};

let callback = (entries, observer) => {
    entries.forEach((entry) => {
        console.log(entry);
        // Each entry describes an intersection change for one observed
        // target element:
        //   entry.boundingClientRect
        //   entry.intersectionRatio
        //   entry.intersectionRect
        //   entry.isIntersecting
        //   entry.rootBounds
        //   entry.target
        //   entry.time
        if (entry.isIntersecting) {
            let elem = entry.target;

            if (entry.intersectionRatio >= 0.75) {
                intersectionCounter++;
                fetchMovies();
            }
        }
    });
};

let observer = new IntersectionObserver(callback, options);
let intersectionCounter = 1;
let currentTarget, previousTarget;


async function fetchMovies() {
    fetch(`/api/movies/${intersectionCounter}`)
    .then(response => response.json())
    .then(data => {
        let itemContainer = document.querySelector('.item-container');
        data.results.forEach((item, idx) => {
            // console.log((idx+1)*intersectionCounter);
            let iContainer = document.createElement('div');
            iContainer.style.padding = '10px';
            iContainer.id = `movieitem-${(idx+1)+(intersectionCounter*19)}`;
            
            let iAhref = document.createElement('a');
            iAhref.href = `/movies/${item.id}`;

            let i = document.createElement('div');
            i.classList.add('movie-item');
            i.setAttribute('data-original-title', item.original_title);
            i.setAttribute(
                'style', 
                `background-image:url("https://images.tmdb.org/t/p/original${item.poster_path}");height:240px; width:120px;padding-right:10px;padding-bottom:10px;border-radius: 15px;box-shadow: 0 2px 15px 2px #201f1f9e;background-size: cover;background-position: center;background-repeat: no-repeat;cursor:pointer;`
            );

            itemContainer.appendChild(iContainer);
            iContainer.appendChild(iAhref);
            iAhref.appendChild(i);
        });

        previousTarget = currentTarget;
        currentTarget = document.querySelector(`#movieitem-${(10+1)+(intersectionCounter*19)}`);
        observer.unobserve(previousTarget);
        observer.observe(currentTarget);
    })
}

// load movies
fetch('/api/movies')
.then(response => response.json())
.then(data => {
    let itemContainer = document.querySelector('.item-container');
    data.results.forEach((item, idx) => {
        let iContainer = document.createElement('div');
        iContainer.style.padding = '10px';
        iContainer.id = `movieitem-${idx}`;
        
        let iAhref = document.createElement('a');
        iAhref.href = `/movies/${item.id}`;
            
        let i = document.createElement('div');
        i.classList.add('movie-item');
        i.setAttribute('data-original-title', item.original_title);
        i.setAttribute(
            'style', 
            `background-image:url("https://images.tmdb.org/t/p/original${item.poster_path}");height:240px; width:120px;padding-right:10px;padding-bottom:10px;border-radius: 15px;box-shadow: 0 2px 15px 2px #201f1f9e;background-size: cover;background-position: center;background-repeat: no-repeat;cursor:pointer;`
        );

        itemContainer.appendChild(iContainer);
        iContainer.appendChild(iAhref);
        iAhref.appendChild(i);
    });

    currentTarget = document.querySelector(`#movieitem-${10*intersectionCounter}`);
    observer.observe(currentTarget);
});

var api = 'http://localhost/';
$('.stream').click(function() {
    window.infoHash = $('input').val().split('btih:')[1].split('&')[0];
    $.get('/api/add/' + infoHash, function(data) {
        var video = '/stream/' + infoHash + '.mp4';
        $('video').attr('src', video);
        $('.input').hide();
        $('.video').show();
    });
});
$('.stop').click(function() {
    $.get('/api/delete/' + infoHash, function(data) {
        $('video').attr('src', '');
        $('input').val('');
        window.infoHash = '';
        $('.input').show();
        $('.video').hide();
    });
});

const createResultItem = (title, seeds, magnet) => {
    // <div class="item" style="border-bottom: 1px solid #f1f1f1; height: 65px; width: 100%;">
    let item = document.createElement('div');
        item.classList.add('item');
        item.style.borderBottom = '1px solid #f1f1f1';
        item.style.height = '65px';
        item.style.cursor = 'pointer';
        item.style.width = '100%';
        item.style.display = 'flex';
        item.style.alignItems = 'center';
        item.style.justifyContent = 'justify-between';
        item.style.color = '#f1f1f1';
        item.style.padding = '0 5px';
        item.setAttribute('data-magnet', magnet);
        item.onclick = (() => {
            window.infoHash = magnet.split('btih:')[1].split('&')[0];
            $.get('/api/add/' + infoHash, function(data) {
                var video = '/stream/' + infoHash + '.mp4';
                $('video').attr('src', video);
                $('.input').hide();
                $('.video').show();
                $('.torrent-display').hide();
            });
        });

    let _title = document.createElement('p');
    _title.textContent = title;
    _title.style.width = '75%';
    _title.style.overflowWrap = 'anywhere';
    
    let seedDiv = document.createElement('div');
    seedDiv.style.color = '#f1f1f1';
    seedDiv.style.display = 'flex';
    seedDiv.style.alignItems = 'center';

    let _seedCount = document.createElement('p');
    _seedCount.textContent = `Seeds: ${seeds}`;
    _seedCount.style.paddingRight = '5px';

    let _seedIcon = document.createElement('div');

    // if height and widht has to be changed otherwise you put them directly in svg_str
    const h = 23 + 'px';
    const w = 23 + 'px';
    const fill = seeds >= 100 ? 'green' : (
        seeds < 50 ? 'red' : 'orange'
    );
    // if path is a variable otherwise you put directly in svg_str
    const path_d = "M4,14H2V2H4ZM7,5H5v9H7Zm3,3H8v6h2Zm3,3H11v3h2Z";

    let svg_str = '<svg xmlns="http://www.w3.org/2000/svg" fill="' + fill + '" width="' + w + '" height="' + h + '"><path d="' + path_d + '"/></svg>';
        
    document.querySelector('.results-container').appendChild(item);

    item.appendChild(_title);
    item.appendChild(seedDiv);

    seedDiv.appendChild(_seedCount);
    seedDiv.appendChild(_seedIcon);

    _seedIcon.innerHTML = svg_str;
}