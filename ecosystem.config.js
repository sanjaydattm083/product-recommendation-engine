module.exports = {
  apps: [
    {
      name: 'repeatorder-api',
      cwd: '/home/ubuntu/product-recommendation-engine',
      script: '/home/ubuntu/product-recommendation-engine/venv/bin/uvicorn',
      args: 'api:app --host 127.0.0.1 --port 8000',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1500M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
    },
  ],
};
