import path from 'path';
import {
    jsonParser,
    app,
    __dirname
} from './appconfig.js';
// import fs from 'fs';

// var tailwindcss = {
//     style : fs.readFileSync('./style.css','utf8')
// };

app.get('/', function(req, res) {
    res.render(path.join(__dirname, './views/index.ejs'));
});

app.get('/movies/:tmdbID', function(req, res) {
    const tmdbID = req.params.tmdbID;
    const title = req.query.t ? req.query.t : '_404_no_title_present'; // ?t= 
    res.render(path.join(__dirname, 'views/movies.ejs'), { 
        tmdbID, title, bgid: 'tmU7GeKVybMWFButWEGl2M4GeiP' 
    });
});