const mongoose = require('/usr/lib/node_modules/mongoose');

const MONGODB_URI = 'mongodb+srv://rocketuser:r2r8x4r5@cluster0.vth613o.mongodb.net/rocketstarDB?appName=Cluster0';

async function ping() {
  const start = Date.now();
  await mongoose.connect(MONGODB_URI, { serverSelectionTimeoutMS: 15000 });
  const admin = mongoose.connection.db.admin();
  await admin.ping();
  const elapsed = ((Date.now() - start) / 1000).toFixed(2);
  console.log(`[rocketstar-keepalive] OK (${elapsed}s) - ${new Date().toISOString()}`);
  await mongoose.disconnect();
}

ping().catch(err => {
  console.error(`[rocketstar-keepalive] ERRO: ${err.message}`);
  process.exit(1);
});
