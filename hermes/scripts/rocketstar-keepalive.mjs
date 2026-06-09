/**
 * Script de Keep-Alive para MongoDB Atlas
 * 
 * Este script pinga o banco MongoDB periodicamente para evitar que
 * o cluster gratuito (M0) seja pausado por inatividade.
 * 
 * O MongoDB Atlas free tier pausa clusters inativos por mais de 60 dias.
 * Executar este script 1x por semana é suficiente para manter ativo.
 * 
 * Uso:
 *   node scripts/keep-alive.mjs
 * 
 * Ou via cron (recomendado):
 *   0 9 * * 1 node /caminho/para/scripts/keep-alive.mjs
 */

const MONGODB_URI = process.env.MONGODB_URI;

async function keepAlive() {
  if (!MONGODB_URI) {
    console.error('❌ MONGODB_URI não configurada. Defina a variável de ambiente.');
    process.exit(1);
  }

  let mongoose;
  try {
    // Import dinâmico para não exigir mongoose como dependência obrigatória
    mongoose = await import('mongoose');
  } catch {
    console.error('❌ mongoose não instalado. Execute: npm install mongoose');
    process.exit(1);
  }

  const start = Date.now();

  try {
    await mongoose.default.connect(MONGODB_URI, {
      serverSelectionTimeoutMS: 10000,
      connectTimeoutMS: 10000,
    });

    // Ping: lista databases (operação leve)
    const admin = mongoose.default.connection.db.admin();
    const result = await admin.listDatabases();

    const elapsed = ((Date.now() - start) / 1000).toFixed(2);
    const dbNames = result.databases.map((d) => d.name).join(', ');

    console.log(`✅ Keep-alive OK (${elapsed}s)`);
    console.log(`   Bancos: ${dbNames}`);
  } catch (err) {
    console.error(`❌ Erro ao conectar: ${err.message}`);
    process.exit(1);
  } finally {
    if (mongoose) {
      await mongoose.default.disconnect();
    }
  }
}

keepAlive();
