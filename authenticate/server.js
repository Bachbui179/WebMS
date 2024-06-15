const fs = require('fs');
const bodyParser = require('body-parser');
const jsonServer = require('json-server');
const jwt = require('jsonwebtoken');

const server = jsonServer.create();
const userdb = JSON.parse(fs.readFileSync('./users.json', 'UTF-8'));

server.use(bodyParser.urlencoded({ extended: true }));
server.use(bodyParser.json());
server.use(jsonServer.defaults());

const SECRET_KEY = '123456789';
const expiresIn = '1h';

// Create a token from a payload 
function createToken(payload){
  return jwt.sign(payload, SECRET_KEY, {expiresIn});
}

// Verify the token 
function verifyToken(token){
  try {
    return jwt.verify(token, SECRET_KEY);
  } catch (err) {
    return null;
  }
}


// Check if the user exists in database
function isAuthenticated({email, password}){
  return userdb.users.findIndex(user => user.email === email && user.password === password) !== -1;
}

server.post('/auth/login', (req, res) => {
  const {email, password} = req.body;
  if (isAuthenticated({email, password}) === false) {
    const status = 401;
    const message = 'Incorrect email or password';
    res.status(status).json({status, message});
    return;
  }
  const access_token = createToken({email, password});
  res.status(200).json({access_token});
});

server.get('/auth/verify', (req, res) => {
  const authHeader = req.headers.authorization;
  if (authHeader === undefined || authHeader.split(' ')[0] !== 'Bearer') {
    const status = 401;
    const message = 'Error in authorization format';
    res.status(status).json({status, message});
    return;
  }
  const token = authHeader.split(' ')[1];
  const decoded = verifyToken(token);
  if (decoded === null) {
    const status = 401;
    const message = 'Error access_token is revoked';
    res.status(status).json({status, message});
    return;
  }
  res.status(200).json({status: "Token is valid"});
});


server.get('/auth/user', (req, res) => {
  const token = req.headers['authorization'].split(' ')[1];
  const decoded = verifyToken(token);

  if (decoded) {
      const user = userdb.users.find(user => user.email === decoded.email);
      res.status(200).json(user);
  } else {
      res.status(401).json({ error: 'Unauthorized' });
  }
});


server.use(/^(?!\/auth).*$/, (req, res, next) => {
  if (req.headers.authorization === undefined || req.headers.authorization.split(' ')[0] !== 'Bearer') {
    const status = 401;
    const message = 'Error in authorization format';
    res.status(status).json({status, message});
    return;
  }
  try {
    verifyToken(req.headers.authorization.split(' ')[1]);
    next();
  } catch (err) {
    const status = 401;
    const message = 'Error access_token is revoked';
    res.status(status).json({status, message});
    return;
  }
  next();
});


server.listen(3000, () => {
  console.log('Run Auth API Server on port 3000');
});
