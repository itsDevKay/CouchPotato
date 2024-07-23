// TODO: When a user starts playing a video. Create a socket that continuously checks in on what hash
// is being used. Check that inside of /tmp/webtorrent/ directory.
// For any hash that is not being used and verified through the sockets of the video playing,
// then delete from server.



import express from 'express'
import WebTorrent from 'webtorrent';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';
import TorrentSearchApi from 'torrent-search-api';
import fetch from 'node-fetch';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
dotenv.config();


const __filename = fileURLToPath(import.meta.url); // get the resolved path to the file
const __dirname = path.dirname(__filename); // get the name of the directory

var app = express();
app.use(bodyParser.urlencoded({ extended: false }));

// parse application/json
app.use(bodyParser.json());
var jsonParser = bodyParser.json();

var port = 80;

var client = new WebTorrent();

// Allow Cross-Origin requests
app.use(function(req, res, next) {
	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET, PUT, DELETE');
	res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
	next();
});

app.use(express.static(path.join(__dirname, 'app')));

var getLargestFile = async function (torrent) {
    console.log('[-] getLargestFile init');
    // console.log(torrent.files);
	var file;
	for(let i = 0; i < torrent.files.length; i++) {
		if (!file || file.length < torrent.files[i].length) {
			file = torrent.files[i];
            // console.log(torrent.files[i].name);
		}
	}
	return file;
};

var buildMagnetURI = function(infoHash) {
	return 'magnet:?xt=urn:btih:' + infoHash + '&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969';
};

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, '/index.html'));
});

app.get('/api/movies', (req, res) => {
    let page = 1;
    // images = https://images.tmdb.org/t/p/original/
    // const url = `https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=${page}&sort_by=popularity.desc`;
    const url = 'https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=1';
    const options = {
    method: 'GET',
    headers: {
        accept: 'application/json',
        Authorization: `Bearer ${process.env.tmdbAPI}`
    }
    };

    fetch(url, options)
        .then(res => res.json())
        .then(json => {
            // console.log(json)
            res.status(200).json(json);
        })
        .catch(err => console.error('error:' + err));
})

app.get('/api/movies/:page', jsonParser, (req, res) => {
    let page = req.params.page;
    // images = https://images.tmdb.org/t/p/original/
    // const url = `https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=${page}&sort_by=popularity.desc`;
    const url = `https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=${page}`;
    const options = {
    method: 'GET',
    headers: {
        accept: 'application/json',
        Authorization: `Bearer ${process.env.tmdbAPI}`
    }
    };

    fetch(url, options)
        .then(res => res.json())
        .then(json => {
            // console.log(json)
            res.status(200).json(json);
        })
        .catch(err => console.error('error:' + err));
})

app.get('/api/searchtorrent/:movie', async function(req, res) {
    console.log(`[-] searchtorrent init... Query: ${req.params.movie}`);
    TorrentSearchApi.enablePublicProviders();

    // Search '1080' in 'Movies' category and limit to 20 results
    const torrents = await TorrentSearchApi.search(req.params.movie, 'Movies', 35);
    // console.log(torrents);
    let playableTorrents = [];
    try {
        for (let i=0; i < torrents.length; i++) {
            let torrentHtmlDetail = await TorrentSearchApi.getTorrentDetails(torrents[i]);
            if (torrentHtmlDetail.includes('.mp4')) {
                playableTorrents.push({
                    torrent: torrents[i],
                    magnet: await TorrentSearchApi.getMagnet(torrents[i])
                });
            }
        }
    } catch (e) { null; }
    res.status(200).json({ torrents: playableTorrents })
});

app.get('/api/add/:infoHash', function(req, res) {
	if (typeof req.params.infoHash == 'undefined' || req.params.infoHash == '') {
		res.status(500).send('Missing infoHash parameter!'); return;
	}
    console.log('[-] Building magnet URI...');
	var torrent = buildMagnetURI(req.params.infoHash);
    
    try {
        console.log('[-] Adding torrent to client...');
		client.add(torrent, function (torrent) {
            console.log('[-] client.add init...');
			var file = getLargestFile(torrent);
            // console.log(file); // tmp/webtorrent/[file].mp4
            console.log('[-] Retrieved file. Starting swarm...');
			torrent.on('upload', function() {
                // if (torrent.progress != 1) {
                    // console.log(torrent.progress * 100);
                // }
				if (torrent.length == torrent.downloaded) {
                    // console.log('[-] Torrent downloaded. Cleaning up...');
					// // torrent.destroy();
                    // console.log('[-] Torrent destroyed');
					// torrent.discovery.stop();
				}
			});
            torrent.on('download', function (bytes) {
                // if (torrent.done) {
                //     console.log('just downloaded: ' + bytes)
                //     console.log('total downloaded: ' + torrent.downloaded)
                //     console.log('download speed: ' + torrent.downloadSpeed)
                //     console.log('progress: ' + torrent.progress)
                // }
            });
            torrent.on('done', function() {
                console.log(`[-] ${torrent.files.length} files downloaded.`);
                torrent.files.forEach(function(file) {
                    console.log(`\t[-] ${file.name}`);
                });
            });
			res.status(200).send('Added torrent!');
		});

        client.on('error', (err) => {
            // just keep swimming
        })
	} catch (err) {
        console.log(err);
		res.status(500).send('Error: ' + err.toString());
	}
});


app.get('/stream/:infoHash.mp4', function(req, res, next) {
    console.log('[-] Stream init');
	if(typeof req.params.infoHash == 'undefined' || req.params.infoHash == '') {
		res.status(500).send('Missing infoHash parameter!'); return;
	}
	var torrent = buildMagnetURI(req.params.infoHash);
    console.log('[-] torrent built');
    // for (let i=0; i < client.torrents.hashes.length; i++) {
    //     console.log(client.torrents.hashes[i]);
    // }
	try {
		client.get(torrent)
        .then(torrent => {
            getLargestFile(torrent).then(file => {
                console.log(file.name);
                var total = file.length;

                if(typeof req.headers.range != 'undefined') {
                    var range = req.headers.range;
                    var parts = range.replace(/bytes=/, "").split("-");
                    var partialstart = parts[0];
                    var partialend = parts[1];
                    var start = parseInt(partialstart, 10);
                    var end = partialend ? parseInt(partialend, 10) : total - 1;
                    var chunksize = (end - start) + 1;
                } else {
                    var start = 0; var end = total;
                }
                
                var stream = file.createReadStream({start: start, end: end});
                console.log({ 'Content-Range': 'bytes ' + start + '-' + end + '/' + total, 'Accept-Ranges': 'bytes', 'Content-Length': chunksize, 'Content-Type': 'video/mp4' });
                res.writeHead(206, { 'Content-Range': 'bytes ' + start + '-' + end + '/' + total, 'Accept-Ranges': 'bytes', 'Content-Length': chunksize, 'Content-Type': 'video/mp4' });
                stream.pipe(res);
                stream.on('error', (err) => {
                    console.log(err);
                    console.log('[-] Stream closed on error');
                });
                stream.on('data', (chunk) => {
                    console.log(`Received ${chunk.length} bytes of data.`);
                })
            });
        });
	} catch (err) {
        console.log(err);
		// res.status(500).send('Error: ' + err.toString());
	}
});


app.get('/api/delete/:infoHash', function(req, res, next) {
	if(typeof req.params.infoHash == 'undefined' || req.params.infoHash == '') {
		res.status(500).send('Missing infoHash parameter!'); return;
	}
	var torrent = buildMagnetURI(req.params.infoHash);
	try {
		var torrent = client.remove(torrent);
		res.status(200).send('Removed torrent. ');
	} catch (err) {
		res.status(500).send('Error: ' + err.toString());
	}
});

var server = http.createServer(app);
server.listen(port, function() {
	console.log('Listening on http://127.0.0.1:' + port);
});