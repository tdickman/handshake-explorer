const Resource = require('./resource');

data = process.argv[2];
b = new Buffer.from(data, 'hex');
console.log(JSON.stringify(Resource.decode(b)));
