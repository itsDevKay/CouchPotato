import express from 'express'
import path from 'path';
import { fileURLToPath } from 'url';
import bodyParser from 'body-parser';
import ejs from 'ejs';
import dotenv from 'dotenv';
import fs from 'fs';
import cors from 'cors';
dotenv.config();


const __filename = fileURLToPath(import.meta.url); // get the resolved path to the file

export const __dirname = path.dirname(__filename); // get the name of the directory
export let app = express();
export let jsonParser = bodyParser.json();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static('public'));
app.use(cors());

// Allow Cross-Origin requests
app.use(function(req, res, next) {
	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET, PUT, DELETE');
	res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    // res.set('Permissions-Policy', 'autoplay=self');
    res.setHeader(
        "Permissions-Policy",
        'autoplay=(self "https://localhost")'
    );
	next();
});

app.use(express.static(path.join(__dirname, 'app')));

app.set('views', __dirname + '/views');
app.engine('html', ejs.renderFile);
app.set('view engine', 'html');

export const options = {
    key: fs.readFileSync(path.join(__dirname, 'key.pem')),
    cert: fs.readFileSync(path.join(__dirname,'cert.pem'))
};

// parse application/json
app.use(bodyParser.json());

