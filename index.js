try {
  // Simulasi error deploy
  throw new Error("Gagal connect ke server");
} catch (error) {
  console.error("🚨 Deploy gagal:", error.message);
  // Simpan error sebagai env var agar bisa digunakan di CircleCI
  const fs = require('fs');
  fs.writeFileSync('deploy-status.txt', `DEPLOY_STATUS=failed\nDEPLOY_ERROR=${error.message}`);
  process.exit(1);
}

