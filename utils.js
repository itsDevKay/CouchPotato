export let getLargestFile = async function (torrent) {
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

export let buildMagnetURI = function(infoHash) {
	return 'magnet:?xt=urn:btih:' + infoHash + '&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969';
};