
import http from 'http';
import { app } from './appconfig.js';
import './routes.js';
import './api_routes.js';

var port = 80;

var server = http.createServer(app);
server.listen(port, function() {
	console.log('Listening on http://127.0.0.1:' + port);
});