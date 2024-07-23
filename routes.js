import path from 'path';
import {
    jsonParser,
    app,
    __dirname
} from './appconfig.js';

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, './views/index.html'));
});

app.get('/movies', function(req, res) {
    res.render(path.join(__dirname, 'views/movies.html'), { d: [1,2,3,4,5,6,7,8,9,0] });
});