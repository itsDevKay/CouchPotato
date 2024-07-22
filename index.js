import express from 'express'
import WebTorrent from 'webtorrent';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';

const __filename = fileURLToPath(import.meta.url); // get the resolved path to the file
const __dirname = path.dirname(__filename); // get the name of the directory

var app = express();

var port = 9111;

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

app.get('/api/add/:infoHash', function(req, res) {
	if(typeof req.params.infoHash == 'undefined' || req.params.infoHash == '') {
		res.status(500).send('Missing infoHash parameter!'); return;
	}
    console.log('[-] Building magnet URI...');
	var torrent = buildMagnetURI(req.params.infoHash);
    // console.log(torrent);
	try {
        // console.log(client);
        console.log('[-] Adding torrent to client...');
		client.add(torrent, function (torrent) {
            console.log('[-] client.add init...');
			var file = getLargestFile(torrent);
            // console.log(file); // tmp/webtorrent/[file].mp4
            console.log('[-] Retrieved file. Starting swarm...');
			torrent.on('upload', function() {
                // if (torrent.progress != 1) {
                    console.log(torrent.progress * 100);
                // }
				if (torrent.length == torrent.downloaded) {
                    // console.log('[-] Torrent downloaded. Cleaning up...')
					// torrent.swarm.destroy();
					// torrent.discovery.stop();
				}
			});
            torrent.on('download', function (bytes) {
                if (!torrent.done) {
                    console.log('just downloaded: ' + bytes)
                    console.log('total downloaded: ' + torrent.downloaded)
                    console.log('download speed: ' + torrent.downloadSpeed)
                    console.log('progress: ' + torrent.progress)
                }
            });
            torrent.on('done', function(){
                console.log('torrent finished downloading')
                torrent.files.forEach(function(file){
                   // do something with file
                   console.log(file.name);
                });
            });
			res.status(200).send('Added torrent!');
		});
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
            var file = getLargestFile(torrent).then(file => {
                console.log(file.name);
                var total = file.length;

                if(typeof req.headers.range != 'undefined') {
                    var range = req.headers.range;
                    console.log(`Range: ${range}`);
                    var parts = range.replace(/bytes=/, "").split("-");
                    console.log(`Parts: ${parts}`);
                    var partialstart = parts[0];
                    var partialend = parts[1];
                    var start = parseInt(partialstart, 10);
                    var end = partialend ? parseInt(partialend, 10) : total - 1;
                    var chunksize = (end - start) + 1;
                } else {
                    var start = 0; var end = total;
                }
                
                var stream = file.createReadStream({start: start, end: end});
                res.writeHead(206, { 'Content-Range': 'bytes ' + start + '-' + end + '/' + total, 'Accept-Ranges': 'bytes', 'Content-Length': chunksize, 'Content-Type': 'video/mp4' });
                stream.pipe(res);
            });
        });
	} catch (err) {
        console.log(err);
		res.status(500).send('Error: ' + err.toString());
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