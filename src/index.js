
import https from 'https';
import { app, options } from './appconfig.js';
import './routes.js';
import './api_routes.js';

var port = 443;

var server = https.createServer(options, app);
server.listen(port, function() {
	console.log('Listening on http://127.0.0.1:' + port);
});