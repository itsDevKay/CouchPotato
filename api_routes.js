import WebTorrent from 'webtorrent';
import TorrentSearchApi from 'torrent-search-api';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();

import { 
    getLargestFile, 
    buildMagnetURI 
} from './utils.js';

import {
    jsonParser,
    app,
    __dirname
} from './appconfig.js';

var client = new WebTorrent();

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
		client.add(torrent, {
            addUID: true, //the torrent will be stored in it's infoHash folder to prevent file name collisions
            path: process.env.TORRENT_PATH // default is /tmp/webtorrent. View README for setting up s3fs on Ubuntu
        }, function (torrent) {
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